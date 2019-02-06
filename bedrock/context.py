from bedrock import common

Q_GET_ALL_USERS = """
    SELECT
        usename as user_name,
        usesysid as user_id,
        NULLIF(useconnlimit, 'UNLIMITED') as connection_limit,
        usecreatedb as can_create_dbs,
        passwd as can_create_dbs,
        usesuper as is_superuser,
        valuntil as valid_until
    FROM pg_user_info
    WHERE usename != 'rdsdb';
    """

Q_GET_ALL_GROUPS = """
    SELECT
        groname as group_name,
        grosysid as group_id,
        grolist as member_list
    FROM pg_group;
    """


def get_all_pg_users(cursor):
    """ Return a dict with key = usename and values = all other fields in pg_user
    e.g.
    {'test_user': {
        'user_name': 'test_user',
        'user_id': 100,
        'connection_limit': 'UNLIMITED',
        'can_create_dbs': True,
        'can_create_dbs': '********',
        'is_superuser': True,
        'valid_until': None
    }
    """
    common.run_query(cursor, Q_GET_ALL_USERS)

    all_pg_users = {row["user_name"]: dict(row) for row in cursor.fetchall()}
    return all_pg_users


def get_all_pg_groups(cursor):
    """ Return a dict with key = groupname and values = all other fields in pg_group"""
    common.run_query(cursor, Q_GET_ALL_GROUPS)

    all_pg_groups = {row["group_name"]: dict(row) for row in cursor.fetchall()}
    return all_pg_groups


def get_memberships(pg_users, pg_groups):
    """ Return a list of tuples, where each tuple is (member, group) """
    groups = {
        group: attributes["member_list"] for group, attributes in pg_groups.items()
    }

    """ Now get the user ids"""
    user_ids = {attributes["user_id"]: user for user, attributes in pg_users.items()}

    """ Transform into a list of tuples, where each tuple is (membername, groupname) """
    all_memberships = []
    for group, member_ids in groups.items():
        if not member_ids:
            continue
        for member_id in member_ids:
            user_name = user_ids.get(member_id)
            all_memberships.append((user_name, group))

    user_memberships = {}
    for user, group in all_memberships:
        if user not in user_memberships:
            user_memberships[user] = []
        user_memberships[user].append(group)
    return user_memberships


def get_all_group_attributes(cursor):
    """ Return a dict with key = groupname and values dictionary of attributes"""
    all_pg_group_attributes = get_all_pg_group_attributes(cursor)
    all_group_attributes = {
        group: get_group_attributes(pg_attributes)
        for user, pg_attributes in all_pg_group_attributes.items()
    }
    return all_group_attributes


def get_current_state(cursor):
    current_state = {}

    pg_users = get_all_pg_users(cursor)
    pg_groups = get_all_pg_groups(cursor)

    # add the users to the spec
    current_state["users"] = {user: {} for user in pg_users}

    # add the attributes for each user
    for user in current_state["users"]:
        current_state["users"][user] = {}
        current_state["users"][user]["attributes"] = pg_users[user]

    # add the groups
    current_state["groups"] = {group: {} for group in pg_groups}

    # now get memberships / add them
    user_memberships = get_memberships(pg_users, pg_groups)

    for user, memberships in user_memberships.items():
        current_state["users"][user]["member_of"] = memberships

    return current_state
