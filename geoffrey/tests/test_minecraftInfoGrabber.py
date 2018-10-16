from unittest import TestCase

from geoffrey.MinecraftAccountInfoGrabber import *


class TestMinecraftInfoGrabber(TestCase):

    def test_handle_data(self):
        self.assertEqual(grab_UUID('YMCA'), '5c084bd60c6a417ba084e2c5a382d0e1')

    def test_grab_playername(self):
        self.assertEqual(grab_playername('5c084bd60c6a417ba084e2c5a382d0e1'), 'YMCA')

    def test_grab_playername_wrong_case(self):
        self.assertEqual(grab_UUID('ymca'), '5c084bd60c6a417ba084e2c5a382d0e1')

    def test_grab_invalid_player(self):
        self.assertRaises(UsernameLookupFailed, grab_UUID, 'lsdlkjsljglfjgldkj')
