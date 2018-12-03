import os

from bedrock.core_configure import configure
from bedrock.core_generate import generate

spec_path = os.environ['SPEC_PATH']
host = os.environ['BEDROCK_TEST_HOST']
port = os.environ['BEDROCK_TEST_PORT']
dbname = os.environ['BEDROCK_TEST_DBNAME']
user = os.environ['BEDROCK_TEST_USER']
password = os.environ['BEDROCK_TEST_PASSWORD']
live = True


def main():
    generate(host, port, user, password, dbname)
    configure(spec_path, host, port, user, password, dbname, live)
