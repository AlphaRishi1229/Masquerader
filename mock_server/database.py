"""This file contains the database connection string."""
import os
from urllib import parse

from config import current_config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# sqlalchemy_db_url = "postgresql://fyndlocal:fynd@123@localhost:5432/mockdb"
if os.environ.get("ENV") == "development":
    engine = create_engine(current_config.POSTGRES_MASQUERADER_READ_WRITE)
if os.environ.get("ENV") is None:
    os.environ.__setitem__("POSTGRES_HOST", "localhost")
    engine = create_engine(current_config.MASQUERADER_LOCAL)
if os.environ.get("ENV") == "pre-production":
    os.environ.__setitem__("POSTGRES_USER", "runner")
    os.environ.__setitem__("POSTGRES_PASS", "")
    os.environ.__setitem__("POSTGRES_DB", "defaultdb")
    postgres_host = os.environ.get("POSTGRES_HOST", "postgres")
    postgres_port = os.environ.get("POSTGRES_PORT_5432_TCP_PORT", 5432)
    postgres_db = os.environ.get("POSTGRES_DB", "defaultdb")
    db_dict = {
        "username": "runner",
        "password": "",
        "host": postgres_host,
        "port": postgres_port,
        "db": postgres_db,
    }
    default_db_url = current_config.POSTGRES_NOPASS_DSN.format(**db_dict)
    engine = create_engine(default_db_url)
elif os.environ.get("ENV") is not None:
    dsn = os.environ.get("POSTGRES_MASQUERADER_READ_WRITE")
    engine = create_engine(dsn)


def get_db_for_x0():
    """Gets db for x0 x1 Env.

    Returns:
        [session] -- DB Session for x0 x1 env
    """
    DEFAULT_X0_DB = "defaultdb"
    parsed_db_conn_string = parse.urlparse(current_config.POSTGRES_MASQUERADER_READ_WRITE)
    db_name = parsed_db_conn_string.path
    partial_db_conn = str(current_config.POSTGRES_MASQUERADER_READ_WRITE).split(db_name)[0]
    db_conn_string = partial_db_conn + "/" + DEFAULT_X0_DB
    master_engine = create_engine(
        db_conn_string,
        pool_recycle=3600,
        pool_size=10,
        pool_timeout=1,
        echo=False,
        max_overflow=5,
        convert_unicode=True,
        client_encoding="utf8",
    )
    session = scoped_session(sessionmaker(bind=master_engine))
    return session


Base = declarative_base()
