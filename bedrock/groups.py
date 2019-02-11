from bedrock import context

Q_CREATE_GROUP = 'CREATE GROUP "{}";'


def get_create_group_query(group):
    return Q_CREATE_GROUP.format(group)


def get_groups_sql(spec, cursor):
    sql_to_run = []

    spec_groups = spec.get("groups")
    current_groups = context.get_all_pg_groups(cursor)

    for group, spec in spec_groups.items():
        if group not in current_groups:
            sql_to_run.append(get_create_group_query(group))
    return sql_to_run
