from unittest import TestCase
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from BotConfig import *

class TestGeoffreyDatabase(TestCase):
    def setUp(self):
        config = read_config()

        engine_arg = config['SQL']['test_args']
        self.interface = DiscordDatabaseInterface(engine_arg)
        self.session = self.interface.database.Session()
        self.owner = Player('ZeroHD', '143072699567177728')
        self.loc = Location('test', 1, 3, self.owner, dimension='Nether')
        self.tunnel = Tunnel(self.owner, 'Green', 105, self.loc)

    def tearDown(self):
        self.interface.database.clear_all(self.session)
        self.session.close()

    def test_add_object(self):
        self.interface.database.add_object(self.session, self.loc)
        self.interface.database.add_object(self.session, self.owner)
        self.interface.database.add_object(self.session, self.tunnel)

        uuid = grab_UUID('ZeroHD')
        expr = Player.mc_uuid == uuid
        p = self.interface.database.query_by_filter(self.session, Player, expr)[0]

        expr = Location.owner == p
        loc2 = self.interface.database.query_by_filter(self.session, Location, expr)[0]

        self.assertEqual(self.loc.id, loc2.id)

    def test_query_by_filter(self):
        self.interface.database.add_object(self.session, self.loc)
        self.interface.database.add_object(self.session, self.owner)
        expr = (Location.owner == self.owner)
        loc2 = self.interface.database.query_by_filter(self.session, Location, expr)[0]
        self.assertEqual(loc2.id, self.loc.id)

    def test_delete_entry(self):
        self.interface.database.add_object(self.session, self.loc)
        self.interface.database.add_object(self.session, self.owner)

        expr = Location.owner == self.owner
        self.interface.database.delete_entry(self.session, Location, expr)

        loc2 = self.interface.database.query_by_filter(self.session, Location, expr)

        self.assertEqual(len(loc2), 0)

        self.assertRaises(DeleteEntryError, self.interface.database.delete_entry, self.session, Location, expr)

    def test_add_shop(self):
        owner = self.add_player()
        shop = self.add_shop()

        self.assertEqual(type(shop), Shop)

        shop_list = self.interface.find_shop_by_name(self.session, 'test')
        self.assertEqual(shop_list[0].dimension, shop.dimension)

    def add_shop(self):
        return self.interface.add_shop(self.session, '143072699567177728', 'test', 1, 3, "nether")

    def add_player(self):
        return self.interface.add_player(self.session, 'ZeroHD', '143072699567177728')

    def add_loc(self):
        return self.interface.add_location(self.session, '143072699567177728', 'test', 0, 0)

    def test_add_two_shops(self):
        owner = self.add_player()
        shop1 = self.add_shop()
        shop2 = self.interface.add_shop(self.session, '143072699567177728', 'no u', 1, 3)

        loc_list = self.interface.find_location_by_owner_uuid(self.session, '143072699567177728')

        self.assertEqual(loc_list[1].id, shop2.id)

    def test_add_tunnel(self):
        self.add_player()
        tunnel1 = self.interface.add_tunnel(self.session, '143072699567177728', 'green', 155, None)

        tunnel2 = self.interface.find_tunnel_by_owner_name(self.session, 'ZeroHD')[0]
        self.assertEqual(tunnel1, tunnel2)

    def test_add_item(self):
        owner = self.add_player()
        self.add_shop()
        self.interface.add_item(self.session, '143072699567177728', 'test', 'dirt', 1, 15)

        shops = self.interface.find_shop_selling_item(self.session, 'dirt')
        self.assertGreater(len(shops), 0)

    def test_find_location_by_owner(self):
        owner = self.add_player()
        shop = self.add_shop()

        loc_list = self.interface.find_location_by_owner(self.session, owner)

        self.assertEqual(loc_list[0].id, shop.id)

    def test_find_location_by_name_and_owner(self):
        owner = self.add_player()
        shop = self.add_shop()

        loc_list = self.interface.find_location_by_name_and_owner_uuid(self.session, '143072699567177728', 'test')

        self.assertEqual(loc_list[0].id, shop.id)

    def test_delete_base(self):
        owner = self.add_player()
        self.add_loc()

        self.interface.delete_location(self.session, '143072699567177728', 'test')

        loc_list = self.interface.find_location_by_name_and_owner_uuid(self.session, '143072699567177728', 'test')

        self.assertEqual(len(loc_list), 0)

    def test_find_location_around(self):
        owner = self.add_player()
        loc = self.add_loc()

        dim = "o"

        loc_list = self.interface.find_location_around(self.session, 100, 100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(self.session, 200, 200, 100, dim)

        self.assertEqual(len(loc_list), 0)

        loc_list = self.interface.find_location_around(self.session, -100, -100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(self.session, 100, -100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(self.session, -100, 100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(self.session, 50, -50, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

    def test_find_location_by_name(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.find_location_by_name(self.session, 'test')

        self.assertEqual(loc_list[0].name, loc.name)

    def test_search_all(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.search_all_fields(self.session, 'ZeroHD')

        self.assertEqual(type(loc_list), str)

    def test_wrong_case(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.find_location_by_owner_name(self.session, 'zerohd')

        self.assertEqual(loc_list[0].id, loc.id)

        self.interface.add_shop(self.session, '143072699567177728', 'testshop', 1, 3, 'neThEr')

        self.interface.add_item(self.session, '143072699567177728', 'testshop', 'dirts', 1, 15)

        shops = self.interface.find_shop_selling_item(self.session, 'diRt')

        self.assertGreater(len(shops), 0)

        #shops = self.database.find_shop_selling_item('sDirt')

        #self.assertEqual(shops[0].name, 'testshop')

        loc_list = self.interface.find_location_by_name(self.session, 'TEST')

        self.assertEqual(loc_list[0].name, 'test')

    def test_big_input(self):
        owner = self.add_player()

        self.assertRaises(StringTooLong, self.interface.add_location, self.session,'143072699567177728',
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT', 0, 0,)

    def test_duplicate_name(self):
        self.add_player()
        self.add_loc()

        self.assertRaises(EntryNameNotUniqueError, self.interface.add_location, self.session,
                          '143072699567177728', 'test', 0, 0, 0)

    def test_delete_parent(self):
        owner = self.add_player()
        loc = self.add_shop()

        self.interface.add_item(self.session, '143072699567177728', 'test', 'dirt', 1, 15)

        self.interface.delete_location(self.session, '143072699567177728', 'test')

        shops = self.interface.find_shop_selling_item(self.session, 'dirt')
        self.assertEqual(len(shops), 0)








