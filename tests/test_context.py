from bedrock import context
import unittest


class TestContextMethods(unittest.TestCase):
    def test__get_user_attributes(self):
        pg_user_attribute = {
            "usename": "test_user",
            "usesysid": 100,
            "useconnlimit": "UNLIMITED",
            "usecreatedb": True,
            "passwd": "********",
            "usesuper": True,
            "valuntil": None,
        }

        user_attribute = {
            "can_create_dbs": True,
            "connection_limit": None,
            "is_superuser": True,
            "password": "********",
            "valid_until": None,
        }
        self.assertEqual(get_user_attributes(pg_user_attribute), user_attribute)


if __name__ == "__main__":
    TestContextMethods.test__get_user_attributes()
