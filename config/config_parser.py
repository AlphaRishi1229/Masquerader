"""Parse Configurations From Default.yml File."""
import os
import sys

import configargparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_FORMAT = "{0}/{1}"
YAML_FILE = "default.yaml"

default_config_file = FILE_FORMAT.format(BASE_DIR, YAML_FILE)

parser = configargparse.ArgParser(
    config_file_parser_class=configargparse.YAMLConfigFileParser,
    default_config_files=[default_config_file],
    auto_env_var_prefix="",
)

# Environment
parser.add("--ENV", help="ENV")

# Mode
parser.add("--MODE", help="MODE")

# Uvicorn Server Parameters
parser.add("--DEBUG", help="DEBUG")

# Postgresql Parameters
parser.add("--POSTGRES_MASQUERADER_READ_WRITE", help="POSTGRES_MASQUERADER_READ_WRITE")

# Local Parameters
parser.add("--MASQUERADER_LOCAL", help="MASQUERADER_LOCAL")


parser.add("--POSTGRES_TEST_DSN", help="POSTGRES_TEST_DSN")


parser.add("--POSTGRES_PASS_DSN", help="POSTGRES_PASS_DSN")


parser.add("--POSTGRES_NOPASS_DSN", help="POSTGRES_NOPASS_DSN")


parser.add("--POSTGRES_TEST_GITLAB", help="POSTGRES_TEST_GITLAB")

arguments = sys.argv
argument_options = parser.parse_known_args(arguments)
print(parser.format_values())

docker_args = argument_options[0]
