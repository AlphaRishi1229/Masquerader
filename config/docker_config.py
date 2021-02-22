"""Docker Config."""
from config.config_parser import docker_args as args


class DockerConfig(object):
    """The main config part."""
    # Environment
    ENV = args.ENV

    # Mode
    MODE = args.MODE

    # Uvicorn Server Parameters
    DEBUG = args.DEBUG

    # Postgresql Parameters
    POSTGRES_MASQUERADER_READ_WRITE = args.POSTGRES_MASQUERADER_READ_WRITE

    # Local Parameters
    MASQUERADER_LOCAL = args.MASQUERADER_LOCAL

    # TEST URL FOR PYTEST
    POSTGRES_TEST_DSN = args.POSTGRES_TEST_DSN

    # POSTGRES DSN WITH PASSWORD
    POSTGRES_PASS_DSN = args.POSTGRES_PASS_DSN

    # POSTGRES DSN WITHOUT PASSWORD
    POSTGRES_NOPASS_DSN = args.POSTGRES_NOPASS_DSN

    # POSTGRES GITLAB DSN
    POSTGRES_TEST_GITLAB = args.POSTGRES_TEST_GITLAB
