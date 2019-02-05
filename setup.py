from setuptools import setup

setup(
    name="bedrock",
    packages=["bedrock"],
    entry_points={"console_scripts": ["bedrock = bedrock.main:main"]},
    install_requires=[
        'click',
        'psycopg2-binary',
        'jinja2',
        'cerberus',
        'pyyaml',
        'argparse',
    ]
)
