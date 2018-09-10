from unittest import TestCase
import os
from Commands import *
from BotConfig import get_config
from MinecraftAccountInfoGrabber import *
from time import sleep


class StressTest(TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.bot_config = get_config('{}/GeoffreyConfig.ini'.format(path))
        self.commands = Commands(self.bot_config, True)

    def clr_db(self):
        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.session.close()

    def test_commands(self):
        self.clr_db()
        self.commands.register('BirbHD', '143072699567177728')

        for i in range(0, 1000):
            self.commands.add_shop(0, 0, shop_name='test shop{}'.format(i), discord_uuid='143072699567177728')

            self.commands.find('BirbHD')

            sleep(0.5)

    def test_mc_query(self):

        for i in range(0, 1000):
            grab_playername('fe7e84132570458892032b69ff188bc3')

            sleep(0.1)
