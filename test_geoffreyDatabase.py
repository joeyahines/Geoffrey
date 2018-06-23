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

    def test_add_shop(self):
        shop = self.database.add_shop('ZeroHD', 'test', 1, 2, 3, ['Green', 0])

        self.assertEqual(type(shop), Shop)

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





