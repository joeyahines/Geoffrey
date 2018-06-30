from unittest import TestCase
from MinecraftAccountInfoGrabber import *


class TestMinecraftInfoGrabber(TestCase):

    def test_handle_data(self):
        self.assertEqual(grab_UUID('ZeroHD'), 'fe7e84132570458892032b69ff188bc3')

    def test_grab_playername(self):
        self.assertEqual(grab_playername('fe7e84132570458892032b69ff188bc3'), 'ZeroHD')

    def test_grab_playername_wrong_case(self):
        self.assertEqual(grab_UUID('zerohd'), 'fe7e84132570458892032b69ff188bc3')
