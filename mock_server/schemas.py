"""The schema file is different from models file.

This file contains the validation part for every request
or response that we get/process.
Also this file validates the response we are sending.
"""
from typing import Any, Dict, List, Union

from pydantic import BaseModel


class UrlBase(BaseModel):
    """The base validation for reuqest Body.

    This is the BaseModel so will be the Base for
    all validations.
    """

    identifier: str
    request_type: str
    url: str
    response: Union[str, Dict, List]
    payload: Any
    headers: Dict
    status_code: int
    latency: int
    is_active: bool
    inactive_response: Any
    inactive_status_code: Any


class UrlCreate(UrlBase):
    """Basic Input Validation while creating url.

    It implements UrlBase so will have those properties too.
    """

    pass


class UrlUpdate(BaseModel):
    """Basic Input Validation while updating url."""

    url_to_update: str
    status_code_of_old_url: int
    request_type_of_old_url: str
    url: Any
    request_type: Any
    response: Any
    payload: Any
    headers: Any
    status_code: Any
    latency: Any
    is_active: Any
    inactive_response: Any


class Url(UrlBase):
    """Basic Input Validation while displaying url details."""

    created_by: int

    class Config:
        """This orm_mode allows ORM to work."""

        orm_mode = True


class UrlCollection(BaseModel):
    """Base Model for UrlCollection.

    Args:
        BaseModel ([type]): [description]
    """
    identifier: str
    request_type: str
    url: str
    request_url: str
    request_body: Dict
    request_headers: Dict
    response_key: str
    latency: int
    is_active: bool


class UrlDelete(BaseModel):
    """Schema for deleting a url."""

    url: str
    status_code: int
    request_type: str

    class Config:
        """This orm_mode allows ORM to work."""

        orm_mode = True


class UrlToggle(BaseModel):
    """Basic Validation while updating a response."""

    url: str
    status_code: int
    request_type: str
    inactive_response: Any
    inactive_status_code: Any
    is_active: bool

    class Config:
        """orm_mode allows ORM to work."""

        orm_mode = True


class UserBase(BaseModel):
    """Basic Input Validation while displaying user details."""

    name: str
    is_active: bool
    is_admin: bool


class UserCreate(UserBase):
    """Basic Input Validation while creating user.

    Implements UserBase so will have above properties as well.
    """

    password: str


class User(UserBase):
    """Basic Input Validation while showing user details."""

    id: int  # noqa
    urls: List[Url] = []

    class Config:
        """orm_mode allows ORM to work."""

        orm_mode = True
