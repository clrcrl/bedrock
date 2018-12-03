class TestSpecInspectorMethods(unittest.TestCase):
    def test__ensure_valid_schema(self):
        input = yaml.load(
            """
            users:
                fivetran:
                    attributes:
                        password: foobar
                        valid_until: '2018-09-01'
                        can_create_dbs: True
                        is_superuser: False
                        valid_until: null
                        connection_limit: null
        """
        )

        self.assertEqual(ensure_valid_schema(input), [])

    def test__unpack_error_messages(self):
        input = {
            "users": {
                "fivetran": {
                    "attributes": [
                        {"password": ["required field"]},
                        {"connection_limit": ["wrong type", "something else"]},
                    ]
                }
            }
        }
        output = [
            (["users", "fivetran", "attributes", "password"], "required field"),
            (["users", "fivetran", "attributes", "connection_limit"], "wrong type"),
            (["users", "fivetran", "attributes", "connection_limit"], "something else"),
        ]
        self.assertEqual(unpack_error_messages(input), output)

    def test__ensure_no_undocumented_objects(self):
        spec = {"users": {"foo": {}}}
        current_state = {"users": {"foo": {}, "bar": {}}, "groups": {"baz": {}}}
        self.assertEqual(
            ensure_no_undocumented_objects(spec, current_state),
            [
                UNDOCUMENTED_OBJECTS_MSG.format("users", '"bar"'),
                UNDOCUMENTED_OBJECTS_MSG.format("groups", '"baz"'),
            ],
        )
