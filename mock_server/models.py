"""This file contains the db model details.

This file contains details regarding the database like
columns, names and relaionship between them.
"""
import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from .database import Base


class Urls(Base):
    """This is the urls table.

    Here you will store the details of URL's that are being mocked.
    """

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    identifier = Column(String, index=True)
    request_type = Column(String)
    url = Column(String)
    response = Column(String)
    payload = Column(String)
    headers = Column(JSON)
    status_code = Column(Integer)
    latency = Column(Integer)
    is_active = Column(Boolean, default=True)
    inactive_status_code = Column(Integer)
    inactive_response = Column(String)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_on = Column(DateTime)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)

    user = relationship("Users", back_populates="url")


Index(
    "url_details_index",
    Urls.url.desc(),
    Urls.payload.desc(),
    Urls.request_type.desc(),
    Urls.status_code.desc(),
    Urls.is_deleted.desc(),
)


class Users(Base):
    """This is the users table.

    This table contains details of the users
    logged into masquerader.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    name = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    url = relationship("Urls", back_populates="user")


class UrlCollection(Base):
    """This is the urls table.

    Here you will store the details of URL's that are being mocked.
    """

    __tablename__ = "url_collection"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    identifier = Column(String, index=True)
    request_type = Column(String)
    url = Column(String)
    request_url = Column(String)
    request_body = Column(String)
    request_headers = Column(JSON)
    response_key = Column(String)
    latency = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_on = Column(DateTime)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)


Index(
    "url_collection_index",
    UrlCollection.url.desc(),
    UrlCollection.request_url.desc(),
    UrlCollection.request_body.desc(),
    UrlCollection.request_type.desc(),
    UrlCollection.is_deleted.desc(),
)
