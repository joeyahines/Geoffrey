from unittest import TestCase
from DatabaseModels import GeoffreyDatabase
from DatabaseModels import Location
from BotErrors import *


class TestGeoffreyDatabase(TestCase):
    def setUp(self):
        self.database = GeoffreyDatabase('sqlite:///:memory:')
        self.loc = Location('test', 1, 2, 3, 'owner', ['Green', 0])

    def test_add_object(self):
        self.database.add_object(self.loc)

        loc2 = self.database.query_by_filter(Location, Location.owner == 'owner')[0]

        self.assertEqual(self.loc.id, loc2.id)

    def test_query_by_filter(self):
        expr = (Location.owner == 'owner') & (Location.x == 0)
        loc2 = self.database.query_by_filter(Location, expr)
        self.assertEqual(len(loc2), 0)

    def test_delete_entry(self):
        self.database.add_object(self.loc)
        expr = (Location.owner == 'owner') & (Location.name == 'test')
        self.database.delete_entry(Location, expr)

        expr = (Location.owner == 'owner') & (Location.x == 0)
        loc2 = self.database.query_by_filter(Location, expr)

        self.assertEqual(len(loc2), 0)

        self.assertRaises(DeleteEntryError, self.database.delete_entry, Location, expr)






