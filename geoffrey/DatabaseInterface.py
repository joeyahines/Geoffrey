from geoffrey.DatabaseModels import *


class DatabaseInterface:

    def __init__(self, bot_config, debug=False):
        self.database = GeoffreyDatabase(bot_config, debug)

    def add_loc(self, session, owner, name, x_pos, z_pos, dimension=None, loc_type=Location):
        if loc_type == Base:
            loc = Base(name, x_pos, z_pos, owner, dimension)
        elif loc_type == Shop:
            loc = Shop(name, x_pos, z_pos, owner, dimension)
        else:
            loc = Location(name, x_pos, z_pos, owner, dimension)

        self.database.add_object(session, loc)
        return loc

    def add_tunnel(self, session, owner, direction, number, location_name):
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

        tunnel = Tunnel(owner, direction, number, location)
        self.database.add_object(session, tunnel)

        return tunnel

    def add_item(self, session, owner, shop_name, item_name, price, amount):
        try:
            shop = self.find_location_by_name_and_owner(session, owner, shop_name, loc_type=Shop)

            item = ItemListing(item_name, price, amount, shop[0])
            self.database.add_object(session, item)
        except IndexError:
            raise LocationLookUpError

        return item

    def add_player(self, session, player_name, discord_uuid=None):
        try:
            self.find_player(session, player_name)
            raise PlayerInDBError
        except PlayerNotFound:
            mc_uuid = grab_UUID(player_name)
            try:
                self.find_player_by_mc_uuid(session, mc_uuid)
                raise PlayerInDBError
            except PlayerNotFound:
                player = Player(player_name, discord_uuid)
                self.database.add_object(session, player)

        return player

    def find_location_by_name(self, session, name, loc_type=Location):
        expr = loc_type.name.ilike('%{}%'.format(name))
        return self.database.query_by_filter(session, loc_type, expr)

    def find_location_by_owner(self, session, owner, loc_type=Location):
        expr = loc_type.owner == owner
        return self.database.query_by_filter(session, loc_type, expr)

    def find_location_by_owner_name(self, session, owner_name, loc_type=Location):
        expr = loc_type.owner.has(Player.name.ilike(owner_name))
        return self.database.query_by_filter(session, loc_type, expr)

    def find_location_by_name_and_owner(self, session, owner, name, loc_type=Location):
        expr = (loc_type.owner == owner) & (loc_type.name.ilike(name))
        return self.database.query_by_filter(session, loc_type, expr)

    def find_location_around(self, session, x_pos, z_pos, radius, dimension, loc_type=Location):
        dimension_obj = Dimension.str_to_dimension(dimension)
        expr = (loc_type.x < x_pos + radius + 1) & (loc_type.x > x_pos - radius - 1) & \
               (loc_type.z < z_pos + radius + 1) \
               & (loc_type.z > z_pos - radius - 1) & (loc_type.dimension == dimension_obj)

        return self.database.query_by_filter(session, Location, expr)

    def find_tunnel_by_owner(self, session, owner):
        expr = Tunnel.owner == owner

        return self.database.query_by_filter(session, Tunnel, expr)

    def find_tunnel_by_owner_name(self, session, owner_name):
        expr = Tunnel.owner.has(Player.name.ilike('%{}%'.format(owner_name)))
        return self.database.query_by_filter(session, Tunnel, expr)

    def find_item(self, session, item_name):
        expr = ItemListing.name.ilike('%{}%'.format(item_name))
        return self.database.query_by_filter(session, ItemListing, expr, sort=ItemListing.normalized_price)

    def find_shop_selling_item(self, session, item_name):
        return self.find_item(session, item_name)

    def find_player(self, session, player_name):
        expr = Player.name.ilike(player_name)

        try:
            player = self.database.query_by_filter(session, Player, expr)[0]
        except IndexError:
            raise PlayerNotFound

        return player

    def find_player_by_mc_uuid(self, session, uuid):
        expr = Player.mc_uuid == uuid

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

    def search_all_fields(self, session, search, limit=25):
        expr = Location.owner.has(Player.name.ilike('%{}%'.format(search))) | Location.name.ilike('%{}%'.format(search))
        locations = self.database.query_by_filter(session, Location, expr, limit=limit)

        return locations

    def delete_location(self, session, owner, name):
        expr = (Location.owner == owner) & (Location.name == name)
        self.database.delete_entry(session, Location, expr)

    def delete_item(self, session, shop, item_name):
        expr = (ItemListing.name == item_name) & (ItemListing.shop == shop)
        self.database.delete_entry(session, ItemListing, expr)
