from unittest import TestCase
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *


class TestGeoffreyDatabase(TestCase):
    def setUp(self):
        self.database = GeoffreyDatabase('sqlite:///:memory:')
        self.owner = Player('ZeroHD')
        self.loc = Location('test', 1, 2, 3, self.owner, ['Green', 0])
        #self.shop = Location('test', 1, 2, 3, self.owner, ['Green', 0])

    def test_add_object(self):
        self.database.add_object(self.loc)
        self.database.add_object(self.owner)

        uuid = grab_UUID('ZeroHD')
        expr = Player.id == uuid
        p = self.database.query_by_filter(Player, expr)[0]

        expr = Location.owner == p
        loc2 = self.database.query_by_filter(Location, expr)[0]

        self.assertEqual(self.loc.id, loc2.id)

    def test_query_by_filter(self):
        expr = (Location.owner_id == 'fe7e84132570458892032b69ff188bc3') & (Location.x == 0)
        loc2 = self.database.query_by_filter(Location, expr)
        self.assertEqual(len(loc2), 0)

    def test_delete_entry(self):
        self.database.add_object(self.loc)
        self.database.add_object(self.owner)

        expr = (Location.owner_id == 'fe7e84132570458892032b69ff188bc3') & (Location.name == 'test')
        self.database.delete_entry(Location, expr)

        expr = (Location.owner_id == 'fe7e84132570458892032b69ff188bc3') & (Location.x == 0)
        loc2 = self.database.query_by_filter(Location, expr)

        self.assertEqual(len(loc2), 0)

        self.assertRaises(DeleteEntryError, self.database.delete_entry, Location, expr)

    def test_add_shop(self):
        shop = self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])

        self.assertEqual(type(shop), Shop)

    def test_add_two_shops(self):
        shop1 = self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])
        shop2 = self.database.add_shop('ZeroHD', 'no u', 1, 2, 3, ['Green', 0])

        loc_list = self.database.find_location_by_owner('ZeroHD')

        self.assertEqual(loc_list[1].id, shop2.id)

    def test_add_item(self):
        self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])
        self.database.add_item('ZeroHD', 'test', 'dirt', 1)

        shops = self.database.find_shop_selling_item('dirt')
        self.assertEqual(shops[0].name, 'test')

    def test_find_location_by_owner(self):
        shop = self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])

        loc_list = self.database.find_location_by_owner('ZeroHD')

        self.assertEqual(loc_list[0].id, shop.id)

    def test_find_location_by_name_and_owner(self):
        shop = self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])

        loc_list = self.database.find_location_by_name_and_owner('ZeroHD','test')

        self.assertEqual(loc_list[0].id, shop.id)

    def test_delete_base(self):
        self.database.add_location('ZeroHD', 'test', 1, 2, 3, ['Green', 0])

        self.database.delete_base('ZeroHD', 'test')

        loc_list = self.database.find_location_by_name_and_owner('ZeroHD', 'test')

        self.assertEqual(len(loc_list), 0)

    def test_find_location_around(self):
        loc = self.database.add_location('ZeroHD', 'test', 0, 0, 0, ['Green', 0])

        loc_list = self.database.find_location_around(100, 100, 200)

        self.assertEqual(loc_list[0].name, loc.name)

        loc_list = self.database.find_location_around(200, 200, 200)

        self.assertEqual(len(loc_list), 0)

    def test_wrong_case(self):
        loc = self.database.add_location('ZeroHD', 'test', 0, 0, 0, ['Green', 0])

        loc_list = self.database.find_location_by_owner('zerohd')

        self.assertEqual(loc_list[0].id, loc.id)





