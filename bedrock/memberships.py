from bedrock import context

Q_ADD_GROUP_MEMBER = 'ALTER GROUP "{}" ADD USER "{}";'
Q_REMOVE_GROUP_MEMBER = 'ALTER GROUP "{}" DROP USER "{}";'


def get_add_group_member_query(membership):
    member, group = membership
    return Q_ADD_GROUP_MEMBER.format(group, member)


def get_remove_group_member_query(membership):
    member, group = membership
    return Q_REMOVE_GROUP_MEMBER.format(group, member)


def get_spec_memberships(spec):
    """ Return a list of tuples, where each tuple is (member, group) """
    # keeping this generic in case we want to switch to `<group>: {members: []}` format
    memberships = []
    spec_users = spec.get("users")

    for user, spec in spec_users.items():
        for group in spec.get("member_of", []):
            memberships.append((user, group))
    return memberships


def get_memberships_sql(spec, cursor):
    """
    Get all the sql to bring memberships into line with the spec.
    """
    sql_to_run = []

    spec_memberships = get_spec_memberships(spec)

    # jank jank jank
    pg_users = context.get_all_pg_users(cursor)
    pg_groups = context.get_all_pg_groups(cursor)

    current_memberships = context.get_all_memberships(pg_users, pg_groups)

    # add missing memberships
    for membership in spec_memberships:
        if membership not in current_memberships:
            sql_to_run.append(get_add_group_member_query(membership))

    # remove non-spec memberships
    for membership in current_memberships:
        if membership not in spec_memberships:
            sql_to_run.append(get_remove_group_member_query(membership))

    return sql_to_run
