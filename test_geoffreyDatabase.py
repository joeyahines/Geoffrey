from unittest import TestCase
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *

class TestGeoffreyDatabase(TestCase):
    def setUp(self):
        self.interface = DiscordDatabaseInterface('sqlite:///:memory:')
        self.owner = Player('ZeroHD', '143072699567177728')
        self.loc = Location('test', 1, 2, 3, self.owner, dimension='Nether')
        self.tunnel = Tunnel(self.owner, 'Green', 105, self.loc)

    def test_add_object(self):
        self.interface.database.add_object(self.loc)
        self.interface.database.add_object(self.owner)
        self.interface.database.add_object(self.tunnel)

        uuid = grab_UUID('ZeroHD')
        expr = Player.mc_uuid == uuid
        p = self.interface.database.query_by_filter(Player, expr)[0]

        expr = Location.owner == p
        loc2 = self.interface.database.query_by_filter(Location, expr)[0]

        self.assertEqual(self.loc.id, loc2.id)

    def test_query_by_filter(self):
        self.interface.database.add_object(self.loc)
        self.interface.database.add_object(self.owner)
        expr = (Location.owner == self.owner)
        loc2 = self.interface.database.query_by_filter(Location, expr)[0]
        self.assertEqual(loc2.id, self.loc.id)

    def test_delete_entry(self):
        self.interface.database.add_object(self.loc)
        self.interface.database.add_object(self.owner)

        expr = Location.owner == self.owner
        self.interface.database.delete_entry(Location, expr)

        loc2 = self.interface.database.query_by_filter(Location, expr)

        self.assertEqual(len(loc2), 0)

        self.assertRaises(DeleteEntryError, self.interface.database.delete_entry, Location, expr)

    def test_add_shop(self):
        owner = self.add_player()
        shop = self.add_shop()

        self.assertEqual(type(shop), Shop)

        shop_list = self.interface.find_shop_by_name('test')
        self.assertEqual(shop_list[0].dimension, shop.dimension)

    def add_shop(self):
        return self.interface.add_shop('143072699567177728', 'test', 1, 2, 3, "nether")

    def add_player(self):
        return self.interface.add_player('ZeroHD', '143072699567177728')

    def add_loc(self):
        return self.interface.add_location('143072699567177728', 'test', 0, 0, 0)

    def test_add_two_shops(self):
        owner = self.add_player()
        shop1 = self.add_shop()
        shop2 = self.interface.add_shop('143072699567177728', 'no u', 1, 2, 3)

        loc_list = self.interface.find_location_by_owner_uuid('143072699567177728')

        self.assertEqual(loc_list[1].id, shop2.id)

    def test_add_tunnel(self):
        self.add_player()
        args=[]
        tunnel1 = self.interface.add_tunnel('143072699567177728', 'green', 155, None)

        tunnel2 = self.interface.find_tunnel_by_owner_name('ZeroHD')[0]
        self.assertEqual(tunnel1, tunnel2)

    def test_add_item(self):
        owner = self.add_player()
        self.add_shop()
        self.interface.add_item('143072699567177728', 'test', 'dirt', 1, 15)

        shops = self.interface.find_shop_selling_item('dirt')
        self.assertEqual(shops[0].name, 'test')

    def test_find_location_by_owner(self):
        owner = self.add_player()
        shop = self.add_shop()

        loc_list = self.interface.find_location_by_owner(owner)

        self.assertEqual(loc_list[0].id, shop.id)

    def test_find_location_by_name_and_owner(self):
        owner = self.add_player()
        shop = self.add_shop()

        loc_list = self.interface.find_location_by_name_and_owner_uuid('143072699567177728', 'test')

        self.assertEqual(loc_list[0].id, shop.id)

    def test_delete_base(self):
        owner = self.add_player()
        self.add_loc()

        self.interface.delete_location('143072699567177728', 'test')

        loc_list = self.interface.find_location_by_name_and_owner_uuid('143072699567177728', 'test')

        self.assertEqual(len(loc_list), 0)

    def test_find_location_around(self):
        owner = self.add_player()
        loc = self.add_loc()

        dim = "o"

        loc_list = self.interface.find_location_around(100, 100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(200, 200, 100, dim)

        self.assertEqual(len(loc_list), 0)

        loc_list = self.interface.find_location_around(-100, -100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(100, -100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(-100, 100, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.interface.find_location_around(50, -50, 100, dim)

        self.assertEqual(loc_list[0].name, loc.name)

    def test_find_location_by_name(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.find_location_by_name('test')

        self.assertEqual(loc_list[0].name, loc.name)

    def test_search_all(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.search_all_fields('ZeroHD')

        self.assertEqual(type(loc_list), str)

    def test_wrong_case(self):
        owner = self.add_player()
        loc = self.add_loc()

        loc_list = self.interface.find_location_by_owner_name('zerohd')

        self.assertEqual(loc_list[0].id, loc.id)

        self.interface.add_shop('143072699567177728', 'testshop', 1, 2, 3, 'neThEr')

        self.interface.add_item('143072699567177728', 'testshop', 'dirts', 1, 15)

        shops = self.interface.find_shop_selling_item('Dirt')

        self.assertEqual(shops[0].name, 'testshop')

        #shops = self.database.find_shop_selling_item('sDirt')

        #self.assertEqual(shops[0].name, 'testshop')

        loc_list = self.interface.find_location_by_name('TEST')

        self.assertEqual(loc_list[0].name, 'test')

    def test_big_input(self):
        owner = self.add_player()
        loc = self.interface.add_location('143072699567177728',
                                         'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT', 0, 0, 0)

        loc_list = self.interface.find_location_by_owner(owner)

        self.assertEqual(loc_list[0].id, loc.id)

    def test_duplicate_name(self):
        self.add_player()
        self.add_loc()

        self.assertRaises(EntryNameNotUniqueError, self.interface.add_location,
                          '143072699567177728', 'test', 0, 0, 0)






