import pytest

from Database import Notification, DatabaseConnection
from configuration import Configuration


class TestNotification:
    @pytest.fixture(scope="class", autouse=True)
    def notification(self):
        yield Notification(1)

    @pytest.fixture(scope="class", autouse=True)
    def notification_id(self, notification):
        notification_id = notification._write_notification("Supervisor", "Supervisor level message unique")
        yield notification_id
        notification.__delete_notification__(notification_id)

    @pytest.fixture(scope="class")
    def configure_exclude(self, notification, notification_id):
        notification.config.writeNotificationExclusions(notification.employee_id, str(notification_id))
        yield 0
        notification.config.deleteNotificationExclusions(notification.employee_id)

    def test_singleton(self):
        obj1 = Notification(2)
        obj2 = Notification(1)
        assert obj1 is obj2
        assert obj1.role == obj2.role

    def test_constructor(self, notification):
        assert notification.role == "Administrator"
        assert notification.db_connection is DatabaseConnection()
        assert notification.config is Configuration()

    def test_get_notification(self, notification, configure_exclude):
        print(notification.config.getNotificationExclusions(notification.employee_id))
        assert "Supervisor level message unique" not in [value[2] for value in notification.get_notifications()]

    def test_read_notification(self, notification):
        assert "Supervisor level message unique" in [value[2] for value in notification.__read_notifications__()]
        assert "Supervisor level message unique" in [value[2] for value in Notification(2).__read_notifications__()]
        assert "Supervisor level message unique" not in [value[2] for value in Notification(3).__read_notifications__()]
        Notification(1)

    def test_delete_notification(self, notification, notification_id):
        notification.__delete_notification__(notification_id)
        assert "Supervisor level message unique" not in [value[2] for value in notification.__read_notifications__()]
