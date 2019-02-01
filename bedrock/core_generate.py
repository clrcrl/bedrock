from bedrock import common
import psycopg2.extras
import yaml

from bedrock.context import get_current_state


class FormattedDumper(yaml.Dumper):
    """
    A subclass of yaml's Dumper used to add a new line before each role definition and to ensure
    indentation is 4 spaces.

    Partly built using Jace Browning's example here:
        https://stackoverflow.com/questions/25108581/python-yaml-dump-bad-indentation
    """

    def increase_indent(self, flow=False, indentless=False):
        # Add a new line before each role definition
        if self.indent == 0:
            self.write_line_break()

        # In order to properly indent with 4 spaces in lists we need to override the
        # indentless setting
        return super(FormattedDumper, self).increase_indent(flow, indentless=False)


def create_spec(host, port, user, password, dbname):
    db_connection = common.get_db_connection(host, port, dbname, user, password)
    # We will only be reading, so it is worth being safe here and ensuring that we can't write
    db_connection.set_session(readonly=True)
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    spec = get_current_state(cursor)

    return spec


def sort_sublists(data):
    """
    Ensure that any lists within the provided (possibly nested) structure are sorted. This is
    done because PyYAML will sort the keys in a mapping but preserves the order of lists.

    While it would be possible to ensure everything is sorted upstream, i.e. when it is added to
    each sublist, putting this functionality into a function becomes cleaner for testing and a
    better separation of concerns
    """
    if isinstance(data, dict):
        for key, values in data.items():
            sorted_values = sort_sublists(values)
            data[key] = sorted_values
    elif isinstance(data, (list, set)):
        data = sorted(data)

    return data


def output_spec(spec):
    """ Send the YAML file to stdout after adding some customization to the YAML representation,
    namely:
        * Add a blank line between each role definition
        * Indent all items with 4 spaces
        * Convert None and empty Dicts to ''
    """

    def represent_dict(dumper, data):
        """
        Use '' for empty dicts. Based on Brice M. Dempsey's code here:
            https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
        """
        if data:
            return dumper.represent_dict(data)
        return dumper.represent_scalar("tag:yaml.org,2002:null", "")

    def represent_objname(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.qualified_name)

    FormattedDumper.add_representer(dict, represent_dict)

    print(yaml.dump(spec, Dumper=FormattedDumper, default_flow_style=False, indent=4))


def generate(host, port, user, password, dbname):
    """
    Generate a YAML spec that represents the role attributes, memberships, object ownerships,
    and privileges for all roles in a database.

    Note that roles and memberships are database cluster-wide settings, i.e. they are the same
    across multiple databases within a given Postgres instance. Object ownerships and privileges
    are specific to each individual database within a Postgres instance.

    Inputs:

        host - str; the database server host

        port - str; the database server port

        user - str; the database user name

        password - str; the database user's password

        dbname - str; the database to connect to and configure
    """
    spec = create_spec(host, port, user, password, dbname)
    sorted_spec = sort_sublists(spec)
    output_spec(sorted_spec)
