from bedrock import common

Q_GET_ALL_USER_ATTRIBUTES = """
    SELECT
        usename,
        usesysid,
        useconnlimit,
        usecreatedb,
        passwd,
        usesuper,
        valuntil
    FROM pg_user_info
    WHERE usename != 'rdsdb';
    """

USER_COLUMN_NAME_TO_KEYWORD = {
    "useconnlimit": "connection_limit",
    "usecreatedb": "can_create_dbs",
    "usesuper": "is_superuser",
    "passwd": "password",
    "valuntil": "valid_until",
}

USER_COLUMN_VALUES_TO_KEYWORD = {"connection_limit": {"UNLIMITED": None}}


def get_all_pg_user_attributes(cursor):
    """ Return a dict with key = usename and values = all fields in pg_user_info """
    common.run_query(cursor, Q_GET_ALL_USER_ATTRIBUTES)

    all_pg_user_attributes = {row["usename"]: dict(row) for row in cursor.fetchall()}
    return all_pg_user_attributes


def get_user_attributes(user_attributes):
    """ Convert pg_user_info column names to keywords for user """
    user_attributes = {
        USER_COLUMN_NAME_TO_KEYWORD[column_name]: value
        for column_name, value in user_attributes.items()
        if column_name in USER_COLUMN_NAME_TO_KEYWORD
    }
    user_attributes = {
        column_name: USER_COLUMN_VALUES_TO_KEYWORD.get(column_name, {}).get(
            value, value
        )
        for column_name, value in user_attributes.items()
    }
    return user_attributes


def get_all_user_attributes(cursor):
    """ Return a dict with key = username and values = in  """
    all_pg_user_attributes = get_all_pg_user_attributes(cursor)
    all_user_attributes = {
        user: get_user_attributes(pg_attributes)
        for user, pg_attributes in all_pg_user_attributes.items()
    }
    return all_user_attributes


def get_current_state(cursor):
    current_state = {}

    current_state["users"] = {}
    user_attributes = get_all_user_attributes(cursor)

    # need to nest it under an 'attributes' key
    for user, attributes in user_attributes.items():
        current_state["users"][user] = {}
        current_state["users"][user]["attributes"] = attributes

    return current_state
