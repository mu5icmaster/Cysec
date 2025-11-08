import json
import os


class Configuration:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Configuration, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.repo_file_path = f"{os.path.dirname(os.path.abspath(__file__))}"
        self.config_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/config.json"
        self._updatePaths()

    def getGraphicsPath(self) -> str:
        with open(self.config_file_path, "r") as f:
            return json.load(f)["program_files"]["Graphics"]

    def getDatabaseFile(self) -> str:
        with open(self.config_file_path, "r") as f:
            return json.load(f)["program_files"]["Database"]

    def getPreviewFile(self) -> str:
        with open(self.config_file_path, "r") as f:
            return json.load(f)["program_files"]["Preview"]

    def getLogFile(self) -> str:
        with open(self.config_file_path, "r") as f:
            return json.load(f)["program_files"]["Log"]

    def getReportsFile(self) -> str:
        with open(self.config_file_path, "r") as f:
            return json.load(f)["program_files"]["Reports"]

    def getPreferences(self, employee_id: str) -> tuple[str, str]:
        """Returns: (profile_picture, theme_name)"""
        try:
            with open(self.config_file_path, "r") as f:
                data = json.load(f)
                print(data['user_preferences']['user_id'][str(employee_id)])
                # print(json.load(f)["user_preferences"]["user_id"][str(employee_id)])
                preferences = tuple([data["user_preferences"]["user_id"][str(employee_id)]["profile_picture"],
                                    data["user_preferences"]["user_id"][str(employee_id)]["theme_name"]])
                return preferences

        except KeyError:
            self.writePreferences(str(employee_id))
            return self.getPreferences(employee_id)
            pass

    def writePreferences(self, employee_id: str, profile_picture: str = "default", theme_name: str = "default"):
        with open(self.config_file_path, "r") as f:
            data = json.load(f)

        try:
            test = data["user_preferences"]["user_id"][str(employee_id)]["profile_picture"]
            test = data["user_preferences"]["user_id"][str(employee_id)]["theme_name"]
            if profile_picture != "default":
                data["user_preferences"]["user_id"][str(employee_id)]["profile_picture"] = profile_picture
            if theme_name != "default":
                data["user_preferences"]["user_id"][str(employee_id)]["theme_name"] = theme_name

        except KeyError:
            data["user_preferences"]["user_id"][str(employee_id)] = {}
            data["user_preferences"]["user_id"][str(employee_id)]["profile_picture"] = "user_1a"
            data["user_preferences"]["user_id"][str(employee_id)]["theme_name"] = "litera"

        with open(self.config_file_path, "w") as f:
            json.dump(data, f, indent=4)

    def deletePreferences(self, employee_id: str):
        with open(self.config_file_path, "r") as f:
            data = json.load(f)

        try:
            del data["user_preferences"]["user_id"][str(employee_id)]
            with open(self.config_file_path, "w") as f:
                json.dump(data, f, indent=4)

        except KeyError:
            print('key error')
            return

    def getNotificationExclusions(self, employee_id: str) -> list:
        try:
            with open(self.config_file_path, "r") as f:
                data = json.load(f)
            return data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"]

        except KeyError:
            self.writeNotificationExclusions(str(employee_id))
            return self.getNotificationExclusions(str(employee_id))

    def writeNotificationExclusions(self, employee_id: str, notification_id: str = None):
        with open(self.config_file_path, "r") as f:
            data = json.load(f)

        try:
            test = data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"]
            if notification_id in test or notification_id is None:
                pass
            else:
                data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"].append(str(notification_id))

        except KeyError:
            if notification_id is None:
                data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"] = []
            else:
                data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"] = [notification_id]

        with open(self.config_file_path, "w") as f:
            json.dump(data, f, indent=4)

    def deleteNotificationExclusions(self, employee_id: str):
        with open(self.config_file_path, "r") as f:
            data = json.load(f)

        try:
            test = data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"]
            data["user_preferences"]["user_id"][str(employee_id)]["exclude_notifications"] = []

        except KeyError:
            return

        with open(self.config_file_path, "w") as f:
            json.dump(data, f, indent=4)

    def _updatePaths(self) -> None:
        try:
            with open(self.config_file_path, "r") as f:
                data = json.load(f)

            data["program_files"] = {
                "Graphics": f"{self.repo_file_path}/Graphics",
                "Database": f"{self.repo_file_path}/Database/Database.db",
                "Preview": f"{self.repo_file_path}/Frames/ui_preview_text.json",
                "Log": f"{self.repo_file_path}/Database/Database.log",
                "Reports": f"{self.repo_file_path}/Reports"
            }

        except FileNotFoundError:
            data = {
                "program_files": {
                    "Graphics": f"{self.repo_file_path}/Graphics",
                    "Database": f"{self.repo_file_path}/Database/Database.db",
                    "Preview": f"{self.repo_file_path}/Frames/ui_preview_text.json",
                    "Log": f"{self.repo_file_path}/Database/Database.log",
                    "Reports": f"{self.repo_file_path}/Reports"
                },
                "user_preferences": {
                    "user_id": {
                    }
                }
            }

        with open(self.config_file_path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    obj1 = Configuration()
    #obj1.writePreferences('1', "user_3a", theme_name="pulse")
    #print(obj1.getPreferences('1'))
    # obj1.deletePreferences('1')
    # obj1.writeNotificationExclusions('-1', '5')
    print(obj1.getPreferences('1'))
    obj1.writeNotificationExclusions('1', "3")

