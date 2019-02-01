import logging
import sys

import psycopg2
import click
import yaml

import traceback

logger = logging.getLogger(__name__)

DATABASE_CONNECTION_ERROR_MSG = "Unable to connect to database. Postgres traceback:\n{}"


FAILED_QUERY_MSG = 'Failed to execute query "{}": {}'


def fail(msg):
    click.secho(msg, fg="red")
    sys.exit(1)


def get_db_connection(host, port, dbname, user, password):
    try:
        db_conn = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
        db_conn.set_session(autocommit=False)
        return db_conn
    except Exception as e:
        fail(DATABASE_CONNECTION_ERROR_MSG.format(e))


def run_query(cursor, query):
    logger.debug("Executing query: {}".format(query))
    try:
        cursor.execute(query)
    except Exception as e:
        click.secho(FAILED_QUERY_MSG.format(query, ""), fg="red")
        # The following is needed to output the traceback as well
        exc_type, exc_value, exc_tb = sys.exc_info()
        formatted_tb = "\n".join(traceback.format_tb(exc_tb))
        click.secho(formatted_tb)
        sys.exit(1)
