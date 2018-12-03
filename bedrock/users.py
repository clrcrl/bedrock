from bedrock import context


Q_CREATE_USER = 'CREATE USER "{}" WITH PASSWORD \'{}\';'
Q_ALTER_USER = 'ALTER USER "{}" WITH {}; -- Previous value {}'
Q_ALTER_PASSWORD = 'ALTER USER "{}" WITH PASSWORD \'{}\';'

DEFAULT_ATTRIBUTES = {
    'connection_limit': None,
    'can_create_dbs': False,
    'is_superuser': False,
    'valid_until': None,
    'password': 'Te5tPa55word'
}

# to-do: handle date comparison

def get_alter_user_query_option(attribute, value):
    """
    Translate the spec key/value into a query option.
    """
    if attribute == 'is_superuser':
        return '{}CREATEUSER'.format('' if value else 'NO')
    elif attribute == 'can_create_dbs':
        return '{}CREATEDB'.format('' if value else 'NO')
    elif attribute == 'connection_limit':
        return 'CONNECTION LIMIT {}'.format(value or 'UNLIMITED')
    elif attribute == 'valid_until':
        return 'VALID UNTIL {}'.format('\'' + value + '\'' if value else 'INFINITY')


def get_alter_user_queries(user, spec_attributes, current_attributes):
    """
    Get a list of querues to be run to alter a user to match their attributes
    """
    sql_to_run = []
    desired_attributes = get_desired_attributes(
        spec_attributes, DEFAULT_ATTRIBUTES)
    for attribute, spec_value in desired_attributes.items():
        current_value = current_attributes.get(attribute)
        if attribute == 'password':
            sql_to_run.append('-- '
                              + Q_ALTER_PASSWORD.format(
                                  user,
                                  '******'))
        else:
            if spec_value != current_value:
                sql_to_run.append(
                    Q_ALTER_USER.format(
                        user,
                        get_alter_user_query_option(attribute, spec_value),
                        get_alter_user_query_option(attribute, current_value)))
    return sql_to_run


def get_password_sql(user, spec_attributes):
    """
    Handle password sql separately so that passwords are not logged
    """
    # to do
    return []


def get_create_user_queries(user, spec_attributes):
    """
    Create the user with a generic password (required by Redshift).
    Then alter the user so that they meet the spec.
    """
    sql_to_run = []
    sql_to_run.append(Q_CREATE_USER.format(user, 'Te5tPa55word'))
    sql_to_run.extend(get_alter_user_queries(
        user, spec_attributes, DEFAULT_ATTRIBUTES))
    return sql_to_run


def get_desired_attributes(spec_attributes, default_attributes):
    """
    Since the spec may be partial for a user, assume the unlisted objects are
    the default values. Add the defaults to the spec so they are updated if they
    differ from the current state.
    """
    # to do
    return spec_attributes


def get_users_sql(spec, cursor):
    """
    Get all the sql to bring user and their attributes into line with the spec.
    Return password sql separately so that it can be handled separately.
    """
    sql_to_run = []
    all_password_sql_to_run = []

    spec_users = spec.get('users')
    current_users = context.get_all_user_attributes(cursor)

    for user, spec in spec_users.items():
        spec_attributes = spec.get('attributes')
        if user not in current_users:
            sql_to_run.extend(get_create_user_queries(user, spec_attributes))
        else:
            current_attributes = current_users.get(user)
            sql_to_run.extend(get_alter_user_queries(
                user, spec_attributes, current_attributes))
            all_password_sql_to_run.extend(
                get_password_sql(user, spec_attributes))

    return sql_to_run, all_password_sql_to_run
