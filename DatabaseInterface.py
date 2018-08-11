from DatabaseModels import *


class DatabaseInterface:

    def __init__(self, engine_args=None):
        if engine_args is None:
            self.database = GeoffreyDatabase()
        else:
            self.database = GeoffreyDatabase(engine_args)

    def add_base(self, session, owner, name, x_pos, z_pos, dimension=None):
        base = Base(name, x_pos, z_pos, owner, dimension)
        self.database.add_object(session, base)
        return base

    def add_shop(self, session, owner, name, x_pos, z_pos, dimension=None):
        shop = Shop(name, x_pos, z_pos, owner, dimension)
        self.database.add_object(session, shop)
        return shop

    def add_tunnel(self, session, owner, color, number, location_name):
        tunnels = self.find_tunnel_by_owner(session, owner)
        if location_name is None:
            if len(tunnels):
                raise EntryNameNotUniqueError
            else:
                location = None
        else:
            try:
                location = self.find_location_by_name_and_owner(session, owner, location_name)[0]

                if location.tunnel is not None:
                    raise LocationHasTunnelError

            except IndexError:
                raise LocationLookUpError

        tunnel = Tunnel(owner, color, number, location)
        self.database.add_object(session, tunnel)

        return tunnel

    def add_item(self, session, owner, shop_name, item_name, price, amount):
        try:
            shop = self.find_shop_by_name_and_owner(session, owner, shop_name)

            item = ItemListing(item_name, price, amount, shop[0])
            self.database.add_object(session, item)
        except IndexError:
            raise LocationLookUpError

        return item

    def add_player(self, session, player_name, discord_uuid=None):
        try:
            player = self.find_player(session, player_name)
        except PlayerNotFound:
            mc_uuid = grab_UUID(player_name)
            try:
                player = self.find_player_by_mc_uuid(session, mc_uuid)
                player.name = player_name
            except PlayerNotFound:
                player = Player(player_name, discord_uuid)
                self.database.add_object(session, player)

        return player

    def find_location_by_name(self, session, name):
        expr = Location.name.ilike('%{}%'.format(name))
        return self.database.query_by_filter(session, Location, expr)

    def find_shop_by_name(self, session, name):
        expr = Location.name.ilike('%{}%'.format(name))
        return self.database.query_by_filter(session, Shop, expr)

    def find_location_by_owner(self, session, owner):
        expr = Location.owner == owner
        return self.database.query_by_filter(session, Location, expr)

    def find_shop_by_owner(self, session, owner):
        expr = Shop.owner == owner
        return self.database.query_by_filter(session, Shop, expr)

    def find_location_by_owner_name(self, session, owner_name):
        expr = Location.owner.has(Player.name.ilike(owner_name))
        return self.database.query_by_filter(session, Location, expr)

    def find_shop_by_name_and_owner(self, session, owner, name):
        expr = (Shop.owner == owner) & (Shop.name.ilike(name))
        return self.database.query_by_filter(session, Shop, expr)

    def find_location_by_name_and_owner(self, session, owner, name):
        expr = (Location.owner == owner) & (Location.name.ilike(name))
        return self.database.query_by_filter(session, Location, expr)

    def find_location_around(self, session, x_pos, z_pos, radius, dimension):
        dimension_obj = Dimension.str_to_dimension(dimension)
        expr = (Location.x < x_pos + radius + 1) & (Location.x > x_pos - radius - 1) & (Location.z < z_pos + radius + 1) \
               & (Location.z > z_pos - radius - 1) & (Location.dimension == dimension_obj)

        return list_to_string(self.database.query_by_filter(session, Location, expr))

    def find_tunnel_by_owner(self, session, owner):
        expr = Tunnel.owner == owner

        return self.database.query_by_filter(session, Tunnel, expr)

    def find_tunnel_by_owner_name(self, session, owner_name):
        expr = Tunnel.owner.has(Player.name.ilike('%{}%'.format(owner_name)))
        return self.database.query_by_filter(session, Tunnel, expr)

    def find_item(self, session, item_name):
        expr = ItemListing.name.ilike('%{}%'.format(item_name))
        return self.database.query_by_filter(session, ItemListing, expr)

    def find_shop_selling_item(self, session, item_name):
        listings = self.find_item(session, item_name)
        return list_to_string(listings)

    def find_player(self, session, player_name):
        expr = Player.name.ilike(player_name)

        try:
            player = self.database.query_by_filter(session, Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_mc_uuid(self, session, uuid):
        expr = Player.id == uuid

        try:
            player = self.database.query_by_filter(session, Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_discord_uuid(self, session, uuid):
        expr = Player.discord_uuid == uuid

        try:
            player = self.database.query_by_filter(session, Player, expr)[0]

        except IndexError:
            raise PlayerNotFound
        return player

    def search_all_fields(self, session, search):
        loc_string = ''
        limit = 10

        expr = Location.owner.has(Player.name.ilike('%{}%'.format(search))) | Location.name.ilike('%{}%'.format(search))
        locations = self.database.query_by_filter(session, Location, expr, limit=limit)

        if len(locations) > 0:
            loc_string = loc_string + '\n**Locations:**'

            for loc in locations:
                loc_string = "{}\n{}".format(loc_string, loc)

            if len(locations) == limit:
                loc_string = loc_string + '\n**. . .**'

        expr = Tunnel.owner.has(Player.name.ilike('%{}%'.format(search))) & Tunnel.location is None
        tunnels = self.database.query_by_filter(session, Tunnel, expr)

        if len(tunnels) > 0:
            loc_string = loc_string + '\n\n**Tunnels:**'
            for tunnel in tunnels:
                loc_string = "{}\n{}".format(loc_string, tunnel.full_str())

            if len(tunnels) == limit:
                loc_string = loc_string + '\n**. . .**'

        if len(tunnels) + len(locations) == 0:
            raise LocationLookUpError
        else:
            return loc_string

    def delete_location(self, session, owner, name):
        expr = (Location.owner == owner) & (Location.name == name)
        self.database.delete_entry(session, Location, expr)


def check_similarity(a, b):
    ratio = SequenceMatcher(None, a, b).ratio()

    if (ratio > 0.6) or (a[0] == b[0]):
        return True
    else:
        return False


def list_to_string(loc_list, str_format='{}\n{}'):
    loc_string = ''

    for loc in loc_list:
        loc_string = str_format.format(loc_string, loc)

    return loc_string
