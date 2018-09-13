from geoffrey.DatabaseInterface import *


class Commands:
    def __init__(self, bot_config, debug=False):
        self.bot_config = bot_config
        self.interface = DatabaseInterface(bot_config, debug)

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
                raise PlayerInDBError
            except PlayerNotFound:
                player = self.interface.add_player(session, player_name, discord_uuid)
                player_name = player.name

        finally:
            session.close()

        return player_name

    def add_base(self, x_pos, z_pos, base_name=None, discord_uuid=None, mc_uuid=None):

        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid, mc_uuid)

            if len(self.interface.find_location_by_owner(session, player, loc_type=Base)) == 0:
                if base_name is None:
                    base_name = "{}'s Base".format(player.name)
            elif base_name is None:
                raise EntryNameNotUniqueError

            base = self.interface.add_loc(session, player, base_name, x_pos, z_pos, loc_type=Base)

            base_str = base.__str__()
        finally:
            session.close()

        return base_str

    def add_shop(self, x_pos, z_pos, shop_name=None, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid, mc_uuid)

            if len(self.interface.find_location_by_owner(session, player, loc_type=Shop)) == 0:
                if shop_name is None:
                    shop_name = "{}'s Shop".format(player.name)
            elif shop_name is None:
                raise EntryNameNotUniqueError

            shop = self.interface.add_loc(session, player, shop_name, x_pos, z_pos, loc_type=Shop)

            shop_name = shop.__str__()
        finally:
            session.close()

        return shop_name

    def add_tunnel(self, tunnel_color, tunnel_number, location_name=None, discord_uuid=None, mc_uuid=None):

        session = self.interface.database.Session()
        try:

            player = self.get_player(session, discord_uuid, mc_uuid)
            if location_name is None:
                location_list = self.interface.find_location_by_owner(session, player)

                if len(location_list) > 1:
                    raise EntryNameNotUniqueError

                location_name = location_list[0].name

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

    def find_around(self, x_pos, z_pos, radius=200, dimension='Overworld'):

        session = self.interface.database.Session()

        try:
            loc_list = self.interface.find_location_around(session, x_pos, z_pos, radius, dimension)
        finally:
            session.close()

        return loc_list

    def add_item(self, item_name, quantity, diamond_price, shop_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()
        try:
            player = self.get_player(session, discord_uuid, mc_uuid)
            shop_list = self.interface.find_location_by_owner(session, player, loc_type=Shop)

            if shop_name is None:
                if len(shop_list) == 1:
                    shop_name = shop_list[0].name
                elif len(shop_list) == 0:
                    raise NoLocationsInDatabase
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

            if len(shop_list) == 0:
                raise ItemNotFound
        finally:
            session.close()

        return shop_list

    def info(self, location_name):
        session = self.interface.database.Session()
        try:
            loc = self.interface.find_location_by_name(session, location_name)[0].full_str(self.bot_config)
        finally:
            session.close()

        return loc

    def tunnel(self, player_name):
        session = self.interface.database.Session()

        try:
            tunnel_list = self.interface.find_tunnel_by_owner_name(session, player_name)

            if len(tunnel_list) == 0:
                raise LocationLookUpError

            tunnel_str = ''

            for tunnel in tunnel_list:
                tunnel_str = '{}\n{}'.format(tunnel_str, tunnel.full_str())

        finally:
            session.close()

        return tunnel_str

    def edit_pos(self, x, z, loc_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid=discord_uuid, mc_uuid=mc_uuid)
            if loc_name is None:
                loc_list = self.interface.find_location_by_owner(session, player)

                if len(loc_list) == 0:
                    raise LocationLookUpError
                elif len(loc_list) > 1:
                    raise EntryNameNotUniqueError
                else:
                    location = loc_list[0]
            else:
                location = self.interface.find_location_by_name_and_owner(session, player, loc_name)[0]

            location.x = x
            location.z = z

            session.commit()

            loc_str = location.__str__()
        except IntegrityError:
            session.rollback()
            raise EntryNameNotUniqueError
        except DataError:
            session.rollback()
            raise DatabaseValueError
        except IndexError:
            raise LocationLookUpError
        finally:
            session.close()

        return loc_str

    def edit_tunnel(self, tunnel_color, tunnel_number, loc_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid=discord_uuid, mc_uuid=mc_uuid)
            location = self.interface.find_location_by_name_and_owner(session, player, loc_name)[0]

            if location.tunnel is not None:
                location.tunnel.tunnel_direction = TunnelDirection.str_to_tunnel_dir(tunnel_color)
                location.tunnel.tunnel_number = tunnel_number
            else:
                self.interface.add_tunnel(session, player, tunnel_color, tunnel_number, loc_name)

            loc_str = location.__str__()

            session.commit()
        except IntegrityError:
            session.rollback()
            raise EntryNameNotUniqueError
        except DataError:
            session.rollback()
            raise DatabaseValueError
        except IndexError:
            raise LocationLookUpError
        finally:
            session.close()

        return loc_str

    def edit_name(self, new_name, loc_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid=discord_uuid, mc_uuid=mc_uuid)
            if loc_name is None:
                loc_list = self.interface.find_location_by_owner(session, player)

                if len(loc_list) == 0:
                    raise LocationLookUpError
                elif len(loc_list) > 1:
                    raise EntryNameNotUniqueError
                else:
                    location = loc_list[0]
            else:
                location = self.interface.find_location_by_name_and_owner(session, player, loc_name)[0]

            location.name = new_name
            loc_str = location.__str__()
            session.commit()

        except IntegrityError:
            session.rollback()
            raise EntryNameNotUniqueError
        except DataError:
            session.rollback()
            raise DatabaseValueError
        except IndexError:
            raise LocationLookUpError
        finally:
            session.close()

        return loc_str

    def delete_item(self, item, shop_name, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid=discord_uuid, mc_uuid=mc_uuid)

            if shop_name is None:
                shop_list = self.interface.find_location_by_owner(session, player, loc_type=Shop)

                if len(shop_list) == 0:
                    raise LocationLookUpError
                elif len(shop_list) > 1:
                    raise EntryNameNotUniqueError
                else:
                    shop = shop_list[0]

            else:
                try:
                    shop = self.interface.find_location_by_name_and_owner(session, player, shop_name, loc_type=Shop)[0]
                except IndexError:
                    raise LocationLookUpError

            expr = (ItemListing.name == item) & (ItemListing.shop == shop)
            self.interface.database.delete_entry(session, ItemListing, expr)

            shop_str = shop.name
        finally:
            session.close()

        return shop_str

    def me(self, discord_uuid=None, mc_uuid=None):
        session = self.interface.database.Session()

        try:
            player = self.get_player(session, discord_uuid=discord_uuid, mc_uuid=mc_uuid)

            loc_list = self.interface.find_location_by_owner(session, player)

            if len(loc_list) == 0:
                raise PlayerNotFound

            loc_str = list_to_string(loc_list)
        finally:
            session.close()

        return loc_str

    def update_mc_uuid(self, discord_uuid, mc_uuid):
        session = self.interface.database.Session()

        try:
            player = self.interface.find_player_by_discord_uuid(session, discord_uuid)

            player.mc_uuid = mc_uuid

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_discord_uuid(self, old_discord_uuid, new_discord_uuid):
        session = self.interface.database.Session()

        try:
            player = self.interface.find_player_by_discord_uuid(session, old_discord_uuid)

            player.discord_uuid = new_discord_uuid

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_mc_name(self, discord_uuid):
        session = self.interface.database.Session()

        try:
            player = self.interface.find_player_by_discord_uuid(session, discord_uuid)

            player.name = grab_playername(player.mc_uuid)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
