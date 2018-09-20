import os
from unittest import TestCase

from Commands import *
from BotConfig import get_config


class TestCommands(TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.bot_config = get_config('{}/GeoffreyConfig.ini'.format(path))
        self.commands = Commands(self.bot_config, True)
        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.session.close()

    def test_get_player(self):
        session = self.commands.interface.database.Session()
        self.commands.interface.add_player(session, 'BirbHD', discord_uuid='143072699567177728')

        player = self.commands.get_player(session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'BirbHD')

        self.assertRaises(AttributeError, self.commands.get_player, session)
        session.close()

    def test_get_location(self):
        session = self.commands.interface.database.Session()
        self.commands.interface.add_player(session, 'BirbHD', discord_uuid='143072699567177728')
        session.close()

        session = self.commands.interface.database.Session()

        player = self.commands.get_player(session, discord_uuid='143072699567177728')

        self.assertRaises(NoLocationsInDatabase, self.commands.get_location,
                          session, player, name=None, loc_type=Location)

        session.close()

        self.commands.add_base(0, 0, discord_uuid='143072699567177728')
        session = self.commands.interface.database.Session()

        self.commands.get_location(session, player, name=None, loc_type=Location)

        session.close()

        self.commands.add_base(0, 0, base_name='Birb', discord_uuid='143072699567177728')

        session = self.commands.interface.database.Session()

        self.assertRaises(EntryNameNotUniqueError, self.commands.get_location,
                          session, player, name=None, loc_type=Location)

        self.commands.get_location(session, player, name="Birb", loc_type=Location)

        self.assertRaises(LocationLookUpError, self.commands.get_location,
                          session, player, name="Henlo", loc_type=Location)

        session.close()




    def test_register(self):
        self.commands.register('BirbHD', '143072699567177728')

        player = self.commands.get_player(self.session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'BirbHD')

    def test_addbase(self):
        player_name = self.commands.register('BirbHD', '143072699567177728')
        base = self.commands.add_base(0, 0, discord_uuid='143072699567177728')

        self.assertRaises(EntryNameNotUniqueError, self.commands.add_base, 0, 0, discord_uuid='143072699567177728')

        if player_name not in base:
            self.fail()
        else:
            pass

    def test_addshop(self):
        player_name = self.commands.register('BirbHD', '143072699567177728')
        shop = self.commands.add_shop(0, 0, discord_uuid='143072699567177728')

        self.assertRaises(EntryNameNotUniqueError, self.commands.add_shop, 0, 0, discord_uuid='143072699567177728')

        if player_name not in shop:
            self.fail()
        else:
            pass

    def test_addtunnel(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop2', discord_uuid='143072699567177728')

        tunnel2 = self.commands.add_tunnel("East", 50, location_name='test_shop',
                                           discord_uuid='143072699567177728')

        if "East" not in tunnel2:
            self.fail()

        self.assertRaises(LocationHasTunnelError, self.commands.add_tunnel, "East", 50,
                          location_name='test_shop', discord_uuid='143072699567177728')

        self.assertRaises(EntryNameNotUniqueError, self.commands.add_tunnel, "East", 50,
                          discord_uuid='143072699567177728')

    def test_find(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')
        self.commands.add_base(0, 0, 'heck', discord_uuid='143072699567177728')

        result = self.commands.find('BirbHD')

        if ('frick' in result) & ('heck' in result):
            pass
        else:
            self.fail()

    def test_delete(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.delete('frick', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.find, 'BirbHD')

    def test_findaround(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.find_around(0, 0)

        if 'frick' in result:
            pass
        else:
            self.fail()

    def test_additem(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.assertRaises(NoLocationsInDatabase, self.commands.add_item, 'dirt', 5, 5
                          , discord_uuid='143072699567177728')

        self.commands.add_shop(0, 0, discord_uuid='143072699567177728')

        result = self.commands.add_item('dirt', 5, 5, None, discord_uuid='143072699567177728')

        if 'dirt' in result:
            pass
        else:
            self.fail()

        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.add_item('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_selling(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_item('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.selling('cool')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_info(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_tunnel("West", 50, location_name='frick', discord_uuid='143072699567177728')

        result = self.commands.info('frick')

        if "West" in result:
            pass
        else:
            self.fail()

    def test_add_tunnel(self):
        self.commands.register('BirbHD', '143072699567177728')

        self.assertRaises(NoLocationsInDatabase, self.commands.add_tunnel, "soUTH", 50, None,
                          discord_uuid='143072699567177728')

        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.add_tunnel("soUTH", 50, None, discord_uuid='143072699567177728')

        result = self.commands.tunnel('BirbHD')

        if "South" in result:
            pass
        else:
            self.fail()

    def test_tunnel(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.tunnel, 'BirbHD')

        result = self.commands.add_tunnel("WEST", 50, None, discord_uuid='143072699567177728')

        if "West" in result:
            pass
        else:
            self.fail()



    def test_edit_name(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_name('cool shop', 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('cool shop')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_edit_pos(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_pos(500, 500, 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('test shop')

        if '500' in result:
            pass
        else:
            self.fail()

        self.commands.edit_pos(500, 500, None, discord_uuid='143072699567177728')

        if '500' in result:
            pass
        else:
            self.fail()

        self.commands.delete(name='test shop', discord_uuid='143072699567177728')

        self.assertRaises(NoLocationsInDatabase, self.commands.edit_pos, 5, 5, None,
                          discord_uuid='143072699567177728')

    def test_edit_tunnel(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_tunnel("West", 500, 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('test shop')

        if "West" in result:
            pass
        else:
            self.fail()

    def test_delete_item(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.add_item('dirt', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')
        self.commands.add_item('wood', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.delete_item('dirt', None, discord_uuid='143072699567177728')

        self.assertRaises(ItemNotFound, self.commands.selling, 'dirt')

        self.commands.add_shop(0, 0, shop_name='test shop2', discord_uuid='143072699567177728')
        self.assertRaises(EntryNameNotUniqueError, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')

        self.commands.delete('test shop', discord_uuid='143072699567177728')
        self.commands.delete('test shop2', discord_uuid='143072699567177728')

        self.assertRaises(NoLocationsInDatabase, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')

    def test_me(self):
        self.commands.register('BirbHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        result = self.commands.me(discord_uuid='143072699567177728')

        if 'test shop' in result:
            pass
        else:
            self.fail()

    def test_update_mc_uuid(self):
        self.commands.register('BirbHD', '143072699567177728')

        self.commands.update_mc_uuid('143072699567177728', '0')

        self.assertRaises(PlayerNotFound, self.commands.add_shop, 0, 0, shop_name='test shop',
                          mc_uuid='fe7e84132570458892032b69ff188bc3')

    def test_update_mc_name(self):
        self.commands.register('BirbHD', '143072699567177728')

        self.commands.update_mc_name('143072699567177728')

    def test_update_discord_uuid(self):
        self.commands.register('BirbHD', '143072699567177728')

        self.commands.update_discord_uuid('143072699567177728', '0')

        self.assertRaises(PlayerNotFound, self.commands.add_shop, 0, 0, shop_name='test shop',
                          discord_uuid='143072699567177728')