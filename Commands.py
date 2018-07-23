from DatabaseInterface import *


class Commands:

    def __init__(self, db_engine_arg):
        self.interface = DatabaseInterface(db_engine_arg)

    def get_player(self, session, discord_uuid=None, mc_uuid=None):
        if discord_uuid is not None:
            player = self.interface.find_player_by_discord_uuid(session, discord_uuid)
        elif mc_uuid is not None:
            player = self.interface.find_player_by_mc_uuid(session, mc_uuid)
        else:
            raise AttributeError

        return player

    def register(self, player_name, discord_uuid):

        session = self.interface.database.Session()

        try:
            try:
                self.interface.find_player(session, player_name)
                raise PlayerInDB
            except PlayerNotFound:
                player = self.interface.add_player(session, player_name, discord_uuid)
                player_name = player.name
        finally:
            session.close()

        return player_name

    def addbase(self, x_pos, z_pos, base_name=None, discord_uuid=None, mc_uuid=None):

        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid, mc_uuid)

            if len(self.interface.find_location_by_owner(session, player)) == 0:
                if base_name is None:
                    base_name = "{}'s Base".format()
            elif base_name is None:
                raise EntryNameNotUniqueError

            base = self.interface.add_base(session, player, base_name, x_pos, z_pos)

            base_name = base.name
        finally:
            session.close()

        return base_name

    def addshop(self, x_pos, z_pos, shop_name=None, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid, mc_uuid)

            if len(self.interface.find_shop_by_owner(session, player)) == 0:
                if shop_name is None:
                    shop_name = "{}'s Shop".format()
            elif shop_name is None:
                raise EntryNameNotUniqueError

            shop = self.interface.add_shop(session, player, shop_name, x_pos, z_pos)

            shop_name = shop.name
        finally:
            session.close()

        return shop_name

    def tunnel(self, tunnel_color, tunnel_number, location_name, discord_uuid=None, mc_uuid=None):

        session = self.interface.database.Session()
        try:

            player = self.get_player(session, discord_uuid, mc_uuid)

            tunnel = self.interface.add_tunnel(session, player, tunnel_color, tunnel_number, location_name)
            tunnel_info = tunnel.__str__()
        finally:
            session.close()

        return tunnel_info

    def find(self, search):
        session = self.interface.database.Session()
        try:
            result = self.interface.search_all_fields(session, search)
        finally:
            session.close()

        return result

    def delete(self, name, discord_uuid=None, mc_uuid=None):

        session = self.interface.database.Session()
        try:
            player = self.get_player(session, discord_uuid, mc_uuid)
            self.interface.delete_location(session, player, name)
        finally:
            session.close()

    def findaround(self, x_pos, z_pos, radius=200, dimension='Overworld'):

        session = self.interface.database.Session()

        try:
            loc_list = self.interface.find_location_around(session, x_pos, z_pos, radius, dimension)
        finally:
            session.close()

        return loc_list

    def additem(self, item_name, quantity, diamond_price, shop_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()
        try:
            player = self.get_player(session, discord_uuid, mc_uuid)
            shop_list = self.interface.find_shop_by_owner(session, player)

            if shop_name is None:
                if len(shop_list) == 1:
                    shop_name = shop_list[0].name
                else:
                    raise LocationInitError

            item_listing = self.interface.add_item(session, player, shop_name, item_name, diamond_price, quantity)
            item_listing_str = item_listing.__str__()
        finally:
            session.close()

        return item_listing_str

    def selling(self, item_name: str):
        session = self.interface.database.Session()

        try:
            shop_list = self.interface.find_shop_selling_item(session, item_name)
        finally:
            session.close()

        return shop_list

    def info(self, location_name):
        session = self.interface.database.Session()
        try:
            loc = self.interface.find_location_by_name(session, location_name)[0].full_str()
        finally:
            session.close()

        return loc
