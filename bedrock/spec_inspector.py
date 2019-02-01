import os

import yaml
import cerberus
import jinja2

from bedrock import common


VALIDATION_ERR_MSG = "Spec error: {}: {}"
UNDOCUMENTED_OBJECTS_MSG = (
    "Spec error: Undocumented {0} found: {1}.\n"
    "Please add these {0} to the spec file or manually remove "
    "them from your redshift cluster"
)

SPEC_SCHEMA_YAML = """
    users:
        attributes:
            required: True
            type: dict
            schema:
                password:
                    type: string
                    required: True
                can_create_dbs:
                    type: boolean
                is_superuser:
                    type: boolean
                valid_until:
                    nullable: True
                    type: string
                connection_limit:
                    nullable: True
                    type: integer
"""


def unpack_error_messages(error, error_path=None, errors=None):
    """
    Spec error messages are nested within python dictionaries. We want the path
    to the error, and the actual error to be printed.
    """
    if error_path is None:
        error_path = []

    if errors is None:
        errors = []

    if isinstance(error, dict):
        for key, value in error.items():
            unpack_error_messages(value, error_path + [key], errors)
    if isinstance(error, list):
        for item in error:
            unpack_error_messages(item, error_path, errors)
    if isinstance(error, str):
        errors.append((error_path, error))

    return errors


def ensure_valid_schema(spec):
    """ Ensure spec has no schema errors """
    error_messages = []
    schema = yaml.load(SPEC_SCHEMA_YAML)
    for object_type, objects in spec.items():
        object_schema = schema[object_type]
        v = cerberus.Validator(object_schema)

        for object, config in objects.items():
            v.validate(config)

            if v.errors:
                error_dict = {object_type: {object: v.errors}}

                for error_path_list, error in unpack_error_messages(error_dict):
                    error_path = " > ".join(error_path_list)
                    error_messages.append(VALIDATION_ERR_MSG.format(error_path, error))

    return error_messages


def ensure_no_undocumented_objects(spec, current_state):
    """
    Ensure that all objects (at the moment just users) in the database are in the spec
    Dropping these objects can cause too much damage
    """
    error_messages = []

    for object_type, objects in current_state.items():
        current_objects = set(objects)
        spec_objects = set(spec.get(object_type, {}))
        undocumented_objects = current_objects.difference(spec_objects)
        if undocumented_objects:
            undocumented_objects_fmtd = (
                '"' + '", "'.join(sorted(undocumented_objects)) + '"'
            )
            error_messages.append(
                UNDOCUMENTED_OBJECTS_MSG.format(object_type, undocumented_objects_fmtd)
            )

    return error_messages


def render_template(path):
    """ Load a spec. There may be templated password variables, which we render using Jinja. """
    try:
        dir_path, filename = os.path.split(path)
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(dir_path), undefined=jinja2.StrictUndefined
        )
        loaded = environment.get_template(filename)
        rendered = loaded.render(env=os.environ)
    except jinja2.exceptions.TemplateNotFound as err:
        common.fail(FILE_OPEN_ERROR_MSG.format(path, err))
    except jinja2.exceptions.UndefinedError as err:
        common.fail(MISSING_ENVVAR_MSG.format(err))
    else:
        return rendered


def load_spec(spec_path, current_state, cursor):
    """ Validate a spec passes various checks and, if so, return the loaded spec. """
    rendered_template = render_template(spec_path)
    spec = yaml.load(rendered_template)

    # Validate the schema before verifying anything else about the spec. If the spec is invalid
    # then other checks may fail in erratic ways, so it is better to error out here
    error_messages = []
    error_messages += ensure_valid_schema(spec)
    error_messages += ensure_no_undocumented_objects(spec, current_state)
    if error_messages:
        common.fail("\n".join(error_messages))

    return spec
