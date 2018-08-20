from unittest import TestCase
from Commands import *
from BotConfig import *
from MinecraftAccountInfoGrabber import *
from time import sleep


class StressTest(TestCase):
    def setUp(self):
        self.commands = Commands(bot_config.config['SQL']['test_args'])

    def clr_db(self):
        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.session.close()

    def test_commands(self):
        self.clr_db()
        self.commands.register('ZeroHD', '143072699567177728')

        for i in range(0, 1000):
            self.commands.add_shop(0, 0, shop_name='test shop{}'.format(i), discord_uuid='143072699567177728')

            self.commands.find('ZeroHD')

            sleep(0.5)

    def test_mc_query(self):

        for i in range(0, 1000):
            grab_playername('fe7e84132570458892032b69ff188bc3')

            sleep(0.1)
