import pytest
import json
from os.path import dirname, abspath

from configuration import Configuration


class TestConfiguration:
    @pytest.fixture(scope="class")
    def configuration(self):
        return Configuration()

    def test_singleton(self):
        obj1 = Configuration()
        obj2 = Configuration()
        assert obj1 is obj2

    def test_constructor(self, configuration):
        assert configuration.repo_file_path == dirname(dirname(abspath(__file__)))
        assert configuration.config_file_path == f"{dirname(dirname(abspath(__file__)))}/config.json"

    def test_get_graphics_path(self, configuration):
        assert configuration.getGraphicsPath() == f"{dirname(dirname(abspath(__file__)))}/Graphics"

    def test_get_database_file(self, configuration):
        assert configuration.getDatabaseFile() == f"{dirname(dirname(abspath(__file__)))}/Database/Database.db"

    def test_get_ui_preview_file(self, configuration):
        assert configuration.getPreviewFile() == f"{dirname(dirname(abspath(__file__)))}/Frames/ui_preview_text.json"

    def test_write_preferences(self, configuration):
        configuration.writePreferences('-1')
        assert configuration.getPreferences('-1') == ('user_1a', 'litera')
        configuration.writePreferences('-1', 'user_3b',)
        assert configuration.getPreferences('-1') == ('user_3b', 'litera')
        configuration.writePreferences('-1', theme_name='flatly')
        assert configuration.getPreferences('-1') == ('user_3b', 'flatly')
        configuration.writePreferences('-1', 'user_2a', 'pulse')
        assert configuration.getPreferences('-1') == ('user_2a', 'pulse')

    def test_delete_preferences(self, configuration):
        configuration.deletePreferences('-1')
        with open(configuration.config_file_path, "r") as f:
            data = json.load(f)
        assert '-1' not in data["user_preferences"]["user_id"]

    def test_write_notification_exclusions(self, configuration):
        configuration.writeNotificationExclusions('-1', '1')
        configuration.writeNotificationExclusions('-1', '3')
        assert configuration.getNotificationExclusions('-1') == ['1', '3']

    def test_delete_notification_exclusions(self, configuration):
        configuration.deleteNotificationExclusions('-1')
        assert configuration.getNotificationExclusions('-1') == []


