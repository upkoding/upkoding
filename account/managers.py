from django.db import models

USER_SETTING_TYPE_BOOL = 0  # True/False
USER_SETTING_TYPE_INT = 1  # 99
USER_SETTING_TYPE_FLOAT = 2  # 1.5
USER_SETTING_TYPE_STRING = 3  # 'hello'

USER_SETTING_TYPES = (
    (USER_SETTING_TYPE_BOOL, 'bool'),
    (USER_SETTING_TYPE_INT, 'int'),
    (USER_SETTING_TYPE_FLOAT, 'float'),
    (USER_SETTING_TYPE_STRING, 'string'),
)


class UserSettingManager(models.Manager):

    def __get_setting(self, user, key, default):
        try:
            setting = self.get(user=user, key=key)
            if setting.type == USER_SETTING_TYPE_BOOL:
                return setting.value == 'True'
            if setting.type == USER_SETTING_TYPE_INT:
                return int(setting.value)
            if setting.type == USER_SETTING_TYPE_FLOAT:
                return float(setting.value)
            if setting.type == USER_SETTING_TYPE_STRING:
                return setting.value
        except self.model.DoesNotExist:
            return default

    def __set_bool(self, user, key, value: bool):
        self.update_or_create(
            user=user,
            key=key,
            type=USER_SETTING_TYPE_BOOL,
            defaults={'value': value}
        )

    def __set_int(self, user, key, value: int):
        self.update_or_create(
            user=user,
            key=key,
            type=USER_SETTING_TYPE_INT,
            defaults={'value': int(value)}
        )

    def __set_float(self, user, key, value: float):
        self.update_or_create(
            user=user,
            key=key,
            type=USER_SETTING_TYPE_FLOAT,
            defaults={'value': str(value)}
        )

    def __set_string(self, user, key, value: str):
        self.update_or_create(
            user=user,
            key=key,
            type=USER_SETTING_TYPE_STRING,
            defaults={'value': value}
        )

    # any access to user settings need to use one of the methods below
    # this is to enforce data integrity and consistency of setting keys and values
    # IMPORTANT: method name == key for the sake of consistency.

    def email_notify_project_message(self, user, value: bool = None):
        key = 'email_notify_project_message'
        if value is None:
            return self.__get_setting(user, key, True)
        self.__set_bool(user, key, value)

    def email_notify_project_approved(self, user, value: bool = None):
        key = 'email_notify_project_approved'
        if value is None:
            return self.__get_setting(user, key, True)
        self.__set_bool(user, key, value)

    def email_notify_project_disapproved(self, user, value: bool = None):
        key = 'email_notify_project_disapproved'
        if value is None:
            return self.__get_setting(user, key, True)
        self.__set_bool(user, key, value)

    def email_notify_project_review_request(self, user, value: bool = None):
        key = 'email_notify_project_review_request'
        if value is None:
            return self.__get_setting(user, key, True)
        self.__set_bool(user, key, value)
