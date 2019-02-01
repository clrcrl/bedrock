import users


class TestUserMethods(unittest.TestCase):
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

    def test__get_alter_user_query_option(self):
        self.assertEqual(
            get_alter_user_query_option("is_superuser", False), "NOCREATEUSER"
        )
        self.assertEqual(
            get_alter_user_query_option("is_superuser", True), "CREATEUSER"
        )
        self.assertEqual(
            get_alter_user_query_option("can_create_dbs", False), "NOCREATEDB"
        )
        self.assertEqual(
            get_alter_user_query_option("can_create_dbs", True), "CREATEDB"
        )
        self.assertEqual(
            get_alter_user_query_option("connection_limit", 5), "CONNECTION LIMIT 5"
        )
        self.assertEqual(
            get_alter_user_query_option("connection_limit", None),
            "CONNECTION LIMIT UNLIMITED",
        )
        self.assertEqual(
            get_alter_user_query_option("valid_until", "2018-01-01"),
            "VALID UNTIL '2018-01-01'",
        )
        self.assertEqual(
            get_alter_user_query_option("valid_until", None), "VALID UNTIL INFINITY"
        )
        self.assertEqual(
            get_alter_user_query_option("password", "hello_world"),
            "PASSWORD 'hello_world'",
        )

    def test__get_alter_user_queries(self):
        self.assertEqual(
            get_alter_user_queries(
                "claire", {"is_superuser": True}, {"is_superuser": True}
            ),
            [],
        )
        # which of the following two is the more correct test?
        self.assertEqual(
            get_alter_user_queries(
                "claire", {"is_superuser": True}, {"is_superuser": False}
            ),
            [Q_ALTER_USER.format("claire", "CREATEUSER", "NOCREATEUSER")],
        )
        self.assertEqual(
            get_alter_user_queries(
                "claire", {"is_superuser": True}, {"is_superuser": False}
            ),
            ['ALTER USER "claire" WITH CREATEUSER; -- Previous value NOCREATEUSER'],
        )

        self.assertEqual(
            get_alter_user_queries(
                "claire", {"is_superuser": False}, {"is_superuser": True}
            ),
            [Q_ALTER_USER.format("claire", "NOCREATEUSER", "CREATEUSER")],
        )

    def test__get_create_user_queries(self):
        # should this just put all the options in one statement? or run them as separate queries?
        self.assertEqual(
            get_create_user_queries("claire", {"is_superuser": True}),
            [
                Q_CREATE_USER.format("claire", "Te5tPa55word"),
                Q_ALTER_USER.format("claire", "CREATEUSER", "NOCREATEUSER"),
            ],
        )
