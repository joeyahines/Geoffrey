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
        base = self.commands.addbase(0, 0, discord_uuid='143072699567177728')

        if player_name not in base:
            self.fail()
        else:
            pass

    def test_addshop(self):
        player_name = self.commands.register('ZeroHD', '143072699567177728')
        shop = self.commands.addshop(0, 0, discord_uuid='143072699567177728')

        if player_name not in shop:
            self.fail()
        else:
            pass

    def test_addtunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='test shop', discord_uuid='143072699567177728')

        tunnel1 = self.commands.addtunnel('green', 50, None, discord_uuid='143072699567177728')

        self.assertGreater(len(tunnel1), 0)

        tunnel2 = self.commands.addtunnel('Green', 50, location_name='test_shop', discord_uuid='143072699567177728')

        if 'Green' not in tunnel2:
            self.fail()
        else:
            pass

    def test_find(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')
        self.commands.addbase(0, 0, 'heck', discord_uuid='143072699567177728')

        result = self.commands.find('zerohd')

        if ('frick' in result) & ('heck' in result):
            pass
        else:
            self.fail()

    def test_delete(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')

        self.commands.delete('frick', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.find, 'zerohd')


    def test_findaround(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')

        result = self.commands.findaround(0, 0)

        if 'frick' in result:
            pass
        else:
            self.fail()

    def test_additem(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, discord_uuid='143072699567177728')

        result = self.commands.additem('dirt', 5, 5, None, discord_uuid='143072699567177728')

        if 'dirt' in result:
            pass
        else:
            self.fail()

        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')

        result = self.commands.additem('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_selling(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')

        self.commands.additem('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.selling('cool')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_info(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='frick', discord_uuid='143072699567177728')

        self.commands.addtunnel('Green', 50, location_name='frick', discord_uuid='143072699567177728')

        result = self.commands.info('frick')

        if 'Green' in result:
            pass
        else:
            self.fail()

    def test_tunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.addshop(0, 0, shop_str='test shop', discord_uuid='143072699567177728')

        tunnel = self.commands.addtunnel('green', 50, None, discord_uuid='143072699567177728')

        result = self.commands.tunnel('ZeroHD')

        if 'Green' in result:
            pass
        else:
            self.fail()
