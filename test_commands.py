from unittest import TestCase
from BotConfig import *
from Commands import *
from BotErrors import *


class TestCommands(TestCase):
    def setUp(self):
        config = read_config()

        engine_arg = config['SQL']['test_args']

        self.commands = Commands(engine_arg)
        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.session.close()

    def test_get_player(self):
        session = self.commands.interface.database.Session()
        self.commands.interface.add_player(session, 'ZeroHD', discord_uuid='143072699567177728')

        player = self.commands.get_player(session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'ZeroHD')
        self.session.close()

    def test_register(self):
        self.commands.register('ZeroHD', '143072699567177728')

        player = self.commands.get_player(self.session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'ZeroHD')

    def test_addbase(self):
        player_name = self.commands.register('ZeroHD', '143072699567177728')
        base = self.commands.add_base(0, 0, discord_uuid='143072699567177728')

        if player_name not in base:
            self.fail()
        else:
            pass

    def test_addshop(self):
        player_name = self.commands.register('ZeroHD', '143072699567177728')
        shop = self.commands.add_shop(0, 0, discord_uuid='143072699567177728')

        if player_name not in shop:
            self.fail()
        else:
            pass

    def test_addtunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        tunnel2 = self.commands.add_tunnel('Green', 50, location_name='test_shop', discord_uuid='143072699567177728')

        if 'Green' not in tunnel2:
            self.fail()

        self.assertRaises(LocationHasTunnelError, self.commands.add_tunnel, 'Blue', 50, location_name='test_shop',
                          discord_uuid='143072699567177728')

    def test_find(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')
        self.commands.add_base(0, 0, 'heck', discord_uuid='143072699567177728')

        result = self.commands.find('zerohd')

        if ('frick' in result) & ('heck' in result):
            pass
        else:
            self.fail()

    def test_delete(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.delete('frick', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.find, 'zerohd')

    def test_findaround(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.find_around(0, 0)

        if 'frick' in result:
            pass
        else:
            self.fail()

    def test_additem(self):
        self.commands.register('ZeroHD', '143072699567177728')
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
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_item('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.selling('cool')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_info(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_tunnel('Green', 50, location_name='frick', discord_uuid='143072699567177728')

        result = self.commands.info('frick')

        if 'Green' in result:
            pass
        else:
            self.fail()

    def test_tunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        tunnel = self.commands.add_tunnel('green', 50, None, discord_uuid='143072699567177728')

        result = self.commands.tunnel('ZeroHD')

        if 'Green' in result:
            pass
        else:
            self.fail()

    def test_edit_name(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_name('cool shop', 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('cool shop')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_edit_pos(self):
        self.commands.register('ZeroHD', '143072699567177728')
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

        self.assertRaises(LocationLookUpError, self.commands.edit_pos, 5, 5, None,
                          discord_uuid='143072699567177728')

    def test_edit_tunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_tunnel('green', 500, 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('test shop')

        if 'Green' in result:
            pass
        else:
            self.fail()

    def test_delete_item(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.add_item('dirt', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')
        self.commands.add_item('wood', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')

        result = self.commands.delete_item('dirt', None, discord_uuid='143072699567177728')

        if ('dirt' not in result) & ('wood' in result):
            pass
        else:
            self.fail()

        self.commands.add_shop(0, 0, shop_name='test shop2', discord_uuid='143072699567177728')
        self.assertRaises(EntryNameNotUniqueError, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')

        self.commands.delete('test shop', discord_uuid='143072699567177728')
        self.commands.delete('test shop2', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')


