# Import the yaml file as a python dictionary

# Validate that the yaml meets the schema (use jsonschema over cerberus)

# Generate the current spec of the database -- for the managed schemas only?
# schemas
# tables
# users
# groups
# permissions
# memberships
# spec = initialize_spec(dbcontext)
# spec = add_users(spec, dbcontext)
# spec = add_groups(spec, dbcontext)
# spec = add_memberships(spec, dbcontext)
# spec = add_ownerships(spec, dbcontext)
# spec = add_privileges(spec, dbcontext)

# Find the difference between the two dictionaries
# note that this is different to the pgbedrock approach, which I think dives
# into each user and finds the diff for that user

# if something is in the desired spec, but not in the current spec, generate the
# sql to add it

# if something is in the current spec but not in the desired spec:
# - if it's a permission, simply add the permission
# - if it's an object, does anyone own it?

# what happens if there are extra objects?

# ok should I be building the mvp, or should I just adapt bedrock to do what I want it to do?
# hmmmmmmm
import psycopg2.extras

# from bedrock.spec_inspector import load_spec
from bedrock.spec_inspector import load_spec
from bedrock.context import get_current_state
from bedrock import common

from bedrock.users import get_users_sql

import os


import logging


logger = logging.getLogger(__name__)


def create_divider(section):
    """ Within our output, we prepend all SQL statements for a given submodule (e.g. memberships,
    privileges, etc.) with a divider that names the section that we're on """
    edge_line = "--------------------------------"
    center_line = "--- Configuring {} ".format(section)
    padding = 32 - len(center_line)
    divider = "\n".join(["", "", edge_line, center_line + "-" * padding, edge_line, ""])
    return divider


def has_changes(statements):
    """ See if a list of SQL statements has any lines that are not just comments """
    for stmt in statements:
        if not stmt.startswith("--") and not stmt.startswith("\n\n--"):
            return True
    return False


def run_module_sql(module_sql, cursor):
    if module_sql and has_changes(module_sql):
        # Put all SQL into 1 string to reduce network IO of sending many small calls to Postgres
        combined_sql = "\n".join(module_sql)
        common.run_query(cursor, combined_sql)


def run_password_sql(cursor, all_password_sql_to_run):
    """
    Run one or more SQL statements that contains a password. We do this outside of the
    common.run_query() framework for two reasons:
        1) If verbose mode is requested then common.run_query() will show the password in its
        reporting of the queries that are executed
        2) The input to common.run_query() is the module output. This output is faithfully rendered
        as-is to STDOUT upon pgbedrock's completion, so we would leak the password there as well.

    By running password-containing queries outside of the common.run_query() approach we can avoid
    these issues
    """
    query = "\n".join(all_password_sql_to_run)

    try:
        cursor.execute(query)
    except Exception as e:
        common.fail(msg=common.FAILED_QUERY_MSG.format(query, e))


def configure(spec_path, host, port, user, password, dbname, live):
    """
    Configure the role attributes, memberships, object ownerships, and/or privileges of a
    database cluster to match a desired spec.

    Note that attributes and memberships are database cluster-wide settings, i.e. they are the
    same across multiple databases within a given Postgres instance. Ownerships and privileges
    are specific to each individual database within a Postgres instance.

    Inputs:

        spec_path - str; the path for the configuration file

        host - str; the database server host

        port - str; the database server port

        user - str; the database user name

        password - str; the database user's password

        dbname - str; the database to connect to and configure

        live - bool; whether to apply the changes (True) or just show what changes
            would be made without actually appyling them (False)
    """
    db_connection = common.get_db_connection(host, port, dbname, user, password)
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    current_state = get_current_state(cursor)

    spec = load_spec(spec_path, current_state, cursor)

    sql_to_run = []

    # users
    sql_to_run.append(create_divider("users"))
    users_sql, all_password_sql_to_run = get_users_sql(spec, cursor)
    run_module_sql(users_sql, cursor)
    sql_to_run.extend(users_sql)

    changed = has_changes(sql_to_run)

    if changed and live:
        logger.debug("Committing changes")
        db_connection.commit()
    else:
        db_connection.rollback()
