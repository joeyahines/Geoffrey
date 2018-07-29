from unittest import TestCase
from Commands import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from BotConfig import *


class TestGeoffreyDatabase(TestCase):
    def setUp(self):
        config = read_config()

        engine_arg = config['SQL']['test_args']
        self.commands = Commands(engine_arg)

        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.owner = Player('ZeroHD', '143072699567177728')
        self.loc = Location('test', 1, 3, self.owner, dimension='Nether')
        self.tunnel = Tunnel(self.owner, 'Green', 105, self.loc)

    def tearDown(self):
        self.session.commit()
        self.session.close()

    def add_shop(self, player):
        shop = self.commands.interface.add_shop(self.session, player, 'test', 1, 3, "nether")
        return shop

    def add_player(self):
        player = self.commands.interface.add_player(self.session, 'ZeroHD', discord_uuid='143072699567177728')
        return player

    def add_loc(self, player):
        loc = self.commands.interface.add_location(self.session, player, 'test', 0, 0)
        return loc

    def test_add_object(self):
        self.commands.interface.database.add_object(self.session, self.loc)
        self.commands.interface.database.add_object(self.session, self.owner)
        self.commands.interface.database.add_object(self.session, self.tunnel)

        uuid = grab_UUID('ZeroHD')
        expr = Player.mc_uuid == uuid
        p = self.commands.interface.database.query_by_filter(self.session, Player, expr)[0]

        expr = Location.owner == p
        loc2 = self.commands.interface.database.query_by_filter(self.session, Location, expr)[0]

        self.assertEqual(self.loc.id, loc2.id)

    def test_query_by_filter(self):
        self.commands.interface.database.add_object(self.session, self.loc)
        self.commands.interface.database.add_object(self.session, self.owner)
        expr = (Location.owner == self.owner)
        loc2 = self.commands.interface.database.query_by_filter(self.session, Location, expr)[0]
        self.assertEqual(loc2.id, self.loc.id)

    def test_delete_entry(self):
        self.commands.interface.database.add_object(self.session, self.loc)
        self.commands.interface.database.add_object(self.session, self.owner)
        self.session.commit()
        id = self.loc.owner_id
        expr = Location.owner == self.owner
        self.commands.interface.database.delete_entry(self.session, Location, expr)

        expr = Player.name == 'ZeroHD'
        player = self.commands.interface.database.query_by_filter(self.session, Player, expr)[0]
        self.assertEqual(player.name, 'ZeroHD')

        expr = Location.owner == player

        loc2 = self.commands.interface.database.query_by_filter(self.session, Location, expr)

        self.assertEqual(len(loc2), 0)

        self.assertRaises(DeleteEntryError, self.commands.interface.database.delete_entry, self.session, Location, expr)

    def test_add_shop(self):
        owner = self.add_player()
        shop = self.add_shop(owner)

        self.assertEqual(type(shop), Shop)

        shop_list = self.commands.interface.find_shop_by_name(self.session, 'test')
        self.assertEqual(shop_list[0].dimension, shop.dimension)

    def test_add_two_shops(self):
        owner = self.add_player()
        shop1 = self.add_shop(owner)
        shop2 = self.commands.interface.add_shop(self.session, owner, 'no u', 1, 3)

        loc_list = self.commands.interface.find_location_by_owner(self.session, owner)

        self.assertEqual(loc_list[1].id, shop2.id)

    def test_add_tunnel(self):
        player = self.add_player()
        tunnel1 = self.commands.interface.add_tunnel(self.session, player, 'green', 155, None)

        tunnel2 = self.commands.interface.find_tunnel_by_owner_name(self.session, 'ZeroHD')[0]
        self.assertEqual(tunnel1, tunnel2)



    def test_add_item(self):
        owner = self.add_player()
        self.add_shop(owner)
        self.commands.interface.add_item(self.session, owner, 'test', 'dirt', 1, 15)

        shops = self.commands.interface.find_shop_selling_item(self.session, 'dirt')
        self.assertGreater(len(shops), 0)

    def test_find_location_by_owner(self):
        owner = self.add_player()
        shop = self.add_shop(owner)

        loc_list = self.commands.interface.find_location_by_owner(self.session, owner)

        self.assertEqual(loc_list[0].id, shop.id)

    def test_find_location_by_name_and_owner(self):
        owner = self.add_player()
        shop = self.add_shop(owner)

        loc_list = self.commands.interface.find_location_by_name_and_owner(self.session, owner, 'test')

        self.assertEqual(loc_list[0].id, shop.id)

    def test_delete_base(self):
        owner = self.add_player()
        self.add_loc(owner)

        self.commands.interface.delete_location(self.session, owner, 'test')

        loc_list = self.commands.interface.find_location_by_name(self.session, 'test')

        self.assertEqual(len(loc_list), 0)

    def test_find_location_around(self):
        owner = self.add_player()
        loc = self.add_loc(owner)

        dim = "o"

        loc_list = self.commands.interface.find_location_around(self.session, 100, 100, 100, dim)

        self.assertGreater(len(loc_list), 0)

        loc_list = self.commands.interface.find_location_around(self.session, 200, 200, 100, dim)

        self.assertEqual(len(loc_list), 0)

        loc_list = self.commands.interface.find_location_around(self.session, -100, -100, 100, dim)

        self.assertGreater(len(loc_list), 0)

        loc_list = self.commands.interface.find_location_around(self.session, 100, -100, 100, dim)

        self.assertGreater(len(loc_list), 0)

        loc_list = self.commands.interface.find_location_around(self.session, -100, 100, 100, dim)

        self.assertGreater(len(loc_list), 0)

        loc_list = self.commands.interface.find_location_around(self.session, 50, -50, 100, dim)

        self.assertGreater(len(loc_list), 0)

    def test_find_location_by_name(self):
        owner = self.add_player()
        loc = self.add_loc(owner)

        loc_list = self.commands.interface.find_location_by_name(self.session, 'test')

        self.assertEqual(loc_list[0].name, loc.name)

    def test_search_all(self):
        owner = self.add_player()
        loc = self.add_loc(owner)

        loc_list = self.commands.interface.search_all_fields(self.session, 'ZeroHD')

        self.assertGreater(len(loc_list), 0)

    def test_wrong_case(self):
        owner = self.add_player()
        loc = self.add_loc(owner)

        loc_list = self.commands.interface.find_location_by_owner_name(self.session, 'zerohd')

        self.assertEqual(loc_list[0].id, loc.id)

        self.commands.interface.add_shop(self.session, owner, 'testshop', 1, 3, 'neThEr')

        self.commands.interface.add_item(self.session, owner, 'testshop', 'dirts', 1, 15)

        shops = self.commands.interface.find_shop_selling_item(self.session, 'diRt')

        self.assertGreater(len(shops), 0)

        loc_list = self.commands.interface.find_location_by_name(self.session, 'TEST')

        self.assertEqual(loc_list[0].name, 'test')

    def test_big_input(self):
        owner = self.add_player()

        self.assertRaises(DatabaseValueError, self.commands.interface.add_location, self.session, owner,
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT', 0, 0,)

    def test_duplicate_name(self):
        owner = self.add_player()
        self.add_loc(owner)

        self.assertRaises(EntryNameNotUniqueError, self.commands.interface.add_location, self.session,
                          owner, 'test', 0, 0, 0)

    def test_delete_parent(self):
        owner = self.add_player()
        loc = self.add_shop(owner)

        self.commands.interface.add_item(self.session, owner, 'test', 'dirt', 1, 15)

        self.commands.interface.delete_location(self.session, owner, 'test')

        shops = self.commands.interface.find_shop_selling_item(self.session, 'dirt')
        self.assertEqual(len(shops), 0)








