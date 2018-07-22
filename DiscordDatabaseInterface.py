from DatabaseModels import *
from DatabaseInterface import DatabaseInterface


class DiscordDatabaseInterface(DatabaseInterface):

    def add_location(self, session, owner_uuid, name, x_pos, z_pos, dimension=None):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.add_location(self, session, owner, name, x_pos, z_pos, dimension)

    def add_shop(self, session, owner_uuid, name, x_pos, z_pos, dimension=None):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.add_shop(self, session, owner, name, x_pos, z_pos, dimension)

    def add_tunnel(self, session, owner_uuid, color, number, location_name=""):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.add_tunnel(self, session, owner, color, number, location_name)

    def add_item(self, session, owner_uuid, shop_name, item_name, price, amount):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.add_item(self, session, owner, shop_name, item_name, price, amount)

    def add_player(self, session, player_name, discord_id):
        try:
            player = self.find_player(session, player_name)
        except PlayerNotFound:
            try:
                uuid = grab_UUID(player_name)
                player = self.find_player_by_mc_uuid(session, uuid)
            except PlayerNotFound:
                player = Player(player_name, discord_id)
                self.database.add_object(session, player)
            finally:
                player.name = player_name
        return player

    def find_location_by_owner_uuid(self, session, owner_uuid):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.find_location_by_owner(self, session, owner)

    def find_shop_by_owner_uuid(self, session, owner_uuid):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.find_shop_by_owner(self, session, owner)

    def find_shop_by_name_and_owner_uuid(self, session, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.find_shop_by_name_and_owner(self, session, owner, name)

    def find_location_by_name_and_owner_uuid(self, session, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.find_location_by_name_and_owner(self, session, owner, name)

    def delete_location(self, session, owner_uuid, name):
        owner = DatabaseInterface.find_player_by_discord_uuid(self, session, owner_uuid)
        return DatabaseInterface.delete_location(self, session, owner, name)