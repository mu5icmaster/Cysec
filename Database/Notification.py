# Database/Notification.py
from ttkbootstrap.toast import ToastNotification
from Database import DatabaseConnection
from configuration import Configuration
import json


class Notification:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Notification, cls).__new__(cls)
        return cls._instance

    def __init__(self, employee_id: int):
        self.db_connection = DatabaseConnection()
        self.config = Configuration()
        self.notification_file = f"{self.config.repo_file_path}/Database/Notifications.json"
        self.employee_id = str(employee_id)
        emp = self.db_connection.query_employee(employee_id)
        self.role = emp[1] if emp else "Worker"

    def get_notifications(self):
        """Returns: [NotificationID, TimeStamp, Description] excluding configured exclusions."""
        notifications = self.__read_notifications__()
        try:
            exclusions = self.config.getNotificationExclusions(str(self.employee_id))
        except Exception:
            exclusions = []
        for exclusion in exclusions:
            notifications = [n for n in notifications if str(n[0]) != exclusion]
        return notifications

    def create_notification(self, notification_key: str, placeholder: str = None):
        """Creates a new notification. Placeholder is inserted if necessary."""
        data = self._read_json_key(notification_key)
        if not data:
            return

        message = data.get("Message", "")
        if placeholder is not None:
            try:
                message = message.format(placeholder)
            except Exception:
                pass

        self._write_notification(data.get("Access", "Worker"), message)

        dictionary = {"Worker": 3, "Supervisor": 2, "Administrator": 1}
        try:
            if dictionary.get(self.role, 3) <= dictionary.get(data.get("Access", "Worker"), 3):
                ToastNotification(title=data.get("Title", "Notification"),
                                  message=message, duration=500).show_toast()
        except Exception:
            # Don't crash UI if toast fails
            pass

    def exclude_notification(self, notification_id: str) -> None:
        try:
            self.config.writeNotificationExclusions(self.employee_id, notification_id)
        except Exception:
            pass

    def __read_notifications__(self):
        """Returns: [NotificationID, TimeStamp, Description] without exclusions."""
        try:
            return self.db_connection.query_notification(self.role)
        except Exception:
            return []

    def _write_notification(self, role: str, message: str) -> int:
        """role: Access Level, message: Message -> notificationID: int"""
        try:
            return self.db_connection.add_notification(role, message)
        except Exception:
            return -1

    def __delete_notification__(self, notification_id: int):
        """Reference to delete a notification from the database."""
        try:
            self.db_connection.delete_notification(notification_id)
        except Exception:
            pass

    # ---- helpers ---------------------------------------------------------

    def _read_json_key(self, key: str):
        try:
            with open(self.notification_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(key)
        except Exception:
            return None


if __name__ == '__main__':
    obj = Notification(1)
    obj.create_notification("New Product Added", f"Executive Office Chair")
