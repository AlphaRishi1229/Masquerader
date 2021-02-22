"""This file contains all the functions performed on the db.

All the crud operations on db are defined here.
"""
from datetime import datetime
import json
from urllib.parse import urlparse

from common import utils
from sqlalchemy.orm import Session

from . import models, schemas


def CreateUrl(db: Session, url: schemas.UrlCreate, user_id: int):
    """Create or Mock a url in the database.

    Arguments:
        db {Session} -- gets Current db Session
        url {schemas.UrlCreate} -- JSON Body that contains
        url details.
        user_id {int} -- The User who created it

    Returns:
        db_url[dict] -- User created details
    """
    url_to_mock = urlparse(url.url)
    path = url_to_mock.path
    query = url_to_mock.query
    transformed_url = "/" + str(path) if path[0] != "/" else path
    status = url.status_code
    status = 200 if status == 0 else status
    new_response = (
        json.dumps(url.response) if type(url.response) in (dict, list) else url.response
    )
    new_inactive_response = (
        json.dumps(url.inactive_response)
        if type(url.inactive_response) in (dict, list)
        else url.inactive_response
    )
    db_url = models.Urls(
        identifier=url.identifier,
        request_type=url.request_type.upper(),
        url=transformed_url,
        response=new_response,
        payload=query,
        headers=url.headers,
        status_code=status,
        latency=url.latency,
        created_by=user_id,
        is_active=1,
        inactive_response=new_inactive_response,
        inactive_status_code=url.inactive_status_code,
        created_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def CreateCollection(db: Session, url: schemas.UrlCollection, user_id: int):
    """Create or Mock a url in the database.

    Arguments:
        db {Session} -- gets Current db Session
        url {schemas.UrlCreate} -- JSON Body that contains
        url details.
        user_id {int} -- The User who created it

    Returns:
        db_url[dict] -- User created details
    """
    transformed_url = "/" + str(url.url) if url.url[0] != "/" else url.url
    new_request_body = (
        json.dumps(url.request_body)
        if type(url.request_body) in (dict, list)
        else url.request_body
    )
    db_url = models.UrlCollection(
        identifier=url.identifier,
        request_type=url.request_type,
        url=transformed_url,
        request_url=url.request_url,
        request_body=new_request_body,
        request_headers=url.request_headers,
        response_key=url.response_key,
        latency=url.latency,
        is_active=url.is_active,
        created_by=user_id,
        created_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def UpdateUrl(db: Session, update_details: dict, user_id: int):
    """Operation to update url details in db.

    Arguments:
        db {Session} -- gets current db session
        update_details {dict} -- key value pair of data
        that needs to be updated.

    Returns:
        to_update[list] -- list of updated keys
    """
    to_update_dict = {}
    to_update = []
    to_ignore = [
        "url_to_update",
        "status_code_of_old_url",
        "request_type_of_old_url",
    ]
    for i in update_details.keys():
        if i not in to_ignore:
            to_update.append(i)

    db_update = GetUrlDetails(
        db,
        update_details["url_to_update"],
        update_details["status_code_of_old_url"],
        update_details["request_type_of_old_url"],
    )
    if not db_update.first():
        return None

    to_update_dict[models.Urls.updated_on] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    to_update_dict[models.Urls.updated_by] = str(user_id)
    for i in to_update:
        if i == "response" or i == "payload":
            updated_data = (
                json.dumps(update_details[i])
                if type(update_details[i]) in (dict, list)
                else update_details[i]
            )
            to_update_dict[i] = updated_data
        else:
            to_update_dict[i] = update_details[i]
    db_update.update(
        to_update_dict, synchronize_session="evaluate",
    )
    db.commit()
    return to_update


def CreateUser(db: Session, user: schemas.UserCreate):
    """Operation to create a user in the db.

    Arguments:
        db {Session} -- gets current db session
        user {schemas.UserCreate} -- JSON Body that contains
        user details to be created.

    Returns:
        db_user[dict] -- Details of created user.
    """
    hashed_pass = utils.hash_generate(user.password)
    old_user = db.query(models.Users).filter(models.Users.name == user.name).first()
    if old_user is not None:
        return None
    db_user = models.Users(
        name=user.name,
        password=hashed_pass,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def UserExist(db: Session, username: str, password: str):
    """To check if the user is correct and exists in db.

    Arguments:
        db {Session} -- current db Session
        username {str} -- username entered by user
        password {str} -- password entered by user

    Returns:
        db_user[dict] -- If user is correct provide details of user.
    """
    hashedpass = utils.hash_generate(password)
    db_user = (
        db.query(models.Users)
        .filter(
            models.Users.name == username, models.Users.password == str(hashedpass),
        )
        .first()
    )
    return db_user


def GetUrlDetails(db: Session, url: str, status_code, request_type: str):
    """To get url details for particular url.

    Arguments:
        db {Session} -- Current db Session
        url {str} -- The URL for which details is needed
        user_id {int} -- The user who is searching for that url.
        status_code {[type]} -- The status code defined for url/

    Returns:
        dbObject[Object] -- Url details
    """
    url_parsed = urlparse(url)
    path = url_parsed.path
    query_param = url_parsed.query
    transformed_url = "/" + str(path) if path[0] != "/" else path
    return (
        db.query(models.Urls).filter(
            models.Urls.url == transformed_url,
            models.Urls.payload == query_param,
            models.Urls.request_type == request_type,
            models.Urls.status_code == status_code,
            models.Urls.is_deleted == False,  # noqa
        )
        if status_code
        else db.query(models.Urls).filter(
            models.Urls.url == transformed_url,
            models.Urls.payload == query_param,
            models.Urls.request_type == request_type,
            models.Urls.is_deleted == False,
        )
    )


def GetCollectionDetails(db: Session, url: str, request_type: str):
    """To get url details for particular url.

    Arguments:
        db {Session} -- Current db Session
        url {str} -- The URL for which details is needed
        user_id {int} -- The user who is searching for that url.
        status_code {[type]} -- The status code defined for url/

    Returns:
        dbObject[Object] -- Url details
    """
    transformed_url = "/" + str(url) if url[0] != "/" else url
    return db.query(models.UrlCollection).filter(
        models.UrlCollection.url == transformed_url,
        models.UrlCollection.request_type == request_type,
        models.UrlCollection.is_deleted == False,  # noqa
    )


def UrlDelete(db: Session, url: schemas.UrlCreate):
    """To delete any created URL.

    Arguments:
        db {Session} -- Current db Session
        url {str} -- The URL needed to be deleted.

    Returns:
        url[dict] -- Message which URL got deleted.
    """
    db_url = GetUrlDetails(db, url.url, url.status_code, url.request_type)
    if not db_url.first():
        return None
    db_url.update({models.Urls.is_deleted: True}, synchronize_session="evaluate")
    db.commit()
    return db_url


def UrlToggle(
    db: Session, toggle_details: schemas.UrlCreate,
):
    """To toggle a URL on or off.

    Arguments:
        db {Session} -- Current db Sesssion
        url {str} -- The URL to be toggled

    Returns:
        msg[dict] -- The current toggle on URL, (0 or 1)
    """
    to_update = {}
    new_inactive_response = (
        json.dumps(toggle_details.inactive_response)
        if type(toggle_details.inactive_response) in (dict, list)
        else toggle_details.inactive_response
    )
    new_inactive_status_code = (
        400
        if not toggle_details.inactive_status_code
        else toggle_details.inactive_status_code
    )
    db_url = GetUrlDetails(
        db, toggle_details.url, toggle_details.status_code, toggle_details.request_type,
    )
    if not db_url.first():
        return None
    changed_to = False
    to_update[models.Urls.inactive_response] = new_inactive_response
    to_update[models.Urls.inactive_status_code] = new_inactive_status_code
    if not toggle_details.is_active:
        to_update[models.Urls.is_active] = False
    else:
        to_update[models.Urls.is_active] = True
        changed_to = True
    db_url.update(to_update, synchronize_session="evaluate")
    db.commit()
    return {toggle_details.url: changed_to}


def UserMockedUrls(db: Session, user_id: int):
    """To show all mocked urls.

    Arguments:
        db {Session} -- Current db Sesssion
        user_id {int} -- The current user

    Returns:
        msg[dict] -- All available urls.
    """
    all_results = db.query(models.Urls).all()
    user_url_list = []
    all_url_list = []
    for row in all_results:
        if row.created_by == user_id:
            user_url_list.append({row.request_type: row.url})
        else:
            all_url_list.append({row.request_type: row.url})
    urls = {
        "Urls_mocked_by_user": user_url_list,
        "Other_mocked_urls": all_url_list,
    }
    return urls


def GetAllUrls(db: Session, identifier: str, tag: str):
    """Used to get all urls of an identifier.

    Arguments:
        db {Session} -- Session Object
        identifier {str} -- identifier for urls.

    Returns:
        results[Query] -- The urls of that identifier.
    """
    model = models.UrlCollection if tag == "collection" else models.Urls
    if identifier:
        results = (
            db.query(models.UrlCollection)
            .filter(models.UrlCollection.identifier == identifier)
            .all()
            if tag == "collection"
            else db.query(models.Urls)
            .filter(models.Urls.identifier == identifier)
            .all()
        )
    else:
        results = db.query(model).all()
    return results
