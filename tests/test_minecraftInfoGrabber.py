from unittest import TestCase

from MinecraftAccountInfoGrabber import *


class TestMinecraftInfoGrabber(TestCase):

    def test_handle_data(self):
        self.assertEqual(grab_UUID('ZeroHD'), 'fe7e84132570458892032b69ff188bc3')

    def test_grab_playername(self):
        self.assertEqual(grab_playername('01c29c443f8d4ab490a56919407a5bd2'), 'CoolZero123')

    def test_grab_playername_wrong_case(self):
        self.assertEqual(grab_UUID('zerohd'), 'fe7e84132570458892032b69ff188bc3')

    def test_grab_invalid_player(self):
        self.assertRaises(UsernameLookupFailed, grab_UUID, 'lsdlkjsljglfjgldkj')
