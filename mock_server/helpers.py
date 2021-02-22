"""The helper class where all functions are done."""
import json
import secrets

from common import utils
from dotty_dict import dotty
from fastapi import HTTPException
from starlette.responses import Response

from mock_server import crud

indexed_urls = []


def UserAuth(credentials, db):
    """Used for User Authentication. Uses HTTPBasicAuth.

    Keyword Arguments:
        credentials {HTTPBasicCredentials} -- HTTPBasicAuth Token
        db {Session} -- gets current db
    """
    cur_username = credentials.username
    cur_password = credentials.password
    hashed_pass = utils.hash_generate(cur_password)
    db_user = crud.UserExist(db=db, username=cur_username, password=cur_password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User Not Authenticated")
    correct_username = secrets.compare_digest(cur_username, db_user.name)
    correct_password = secrets.compare_digest(hashed_pass, db_user.password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401, detail="Incorrect email or password",
        )
    return db_user


def UserCreate(user, db):
    """Function to create a user.

    Keyword Arguments:
        user {[schema]} -- User details to be added.
        db {[Session]} -- The current session.
    """
    user = crud.CreateUser(db=db, user=user)
    if user is None:
        raise HTTPException(status_code=400, detail="User Already Exists")
    return user


def UrlCreate(url, db, user):
    """Function to create or mock a url.

    Keyword Arguments:
        url {schemas.UrlCreate} -- JSON Body that contains url data.
    """
    existing_url = crud.GetUrlDetails(
        db=db, url=url.url, status_code=url.status_code, request_type=url.request_type,
    )
    if existing_url.first():
        raise HTTPException(status_code=400, detail="Url Exists")
    create_url = crud.CreateUrl(db=db, url=url, user_id=user.id)
    return create_url


async def UrlCollectionCreate(url, db, user):
    """Function to create or mock a url.

    Keyword Arguments:
        url {schemas.UrlCreate} -- JSON Body that contains url data.
    """
    existing_url = crud.GetCollectionDetails(
        db=db, url=url.url, request_type=url.request_type,
    )
    if existing_url.first():
        raise HTTPException(status_code=400, detail="Url Collection Exists")
    create_url = crud.CreateCollection(db=db, url=url, user_id=user.id)
    return create_url


def UrlUpdate(url, db, user):
    """Function to update details of any mocked URL.

    Keyword Arguments:
        url {schemas.UrlUpdate} -- Json Body that contains url
        and the value to be changed
    """
    url_dict = dict(url)
    keys_to_be_updated = []
    dict_to_be_updated = {}
    for i in url_dict.keys():
        if url_dict[i]:
            keys_to_be_updated.append(i)
    for j in keys_to_be_updated:
        dict_to_be_updated[j] = url_dict[j]
    updated_url = crud.UpdateUrl(
        db=db, update_details=dict_to_be_updated, user_id=user.id
    )
    if not updated_url:
        raise HTTPException(status_code=500, detail="Incorrect Url provided")
    return updated_url


def UrlDelete(url, db, user):
    """Endpoint to remove any mocked url.

    Keyword Arguments:
        user {str} -- The user who is removing it
        Also only the user who created the URL can delete it.
        db {Session} -- Current db Sessiom
        url {str} -- Url to be deleted
    """
    a = crud.UrlDelete(db=db, url=url)
    if not a:
        raise HTTPException(status_code=500, detail="Incorrect Old Url provided")
    return {"url removed": url.url}


def UrlToggle(url, db, user):
    """Endpoint to toggle url - 200 or 400.

    Keyword Arguments:
        db {Session} -- Current db Session
        url {str} -- The url to be toggled
    """
    toggle_url = crud.UrlToggle(db=db, toggle_details=url)
    if not toggle_url:
        raise HTTPException(status_code=500, detail="Incorrect Url provided")
    return toggle_url


def UrlMocked(user, db):
    """Endpoint for getting all mocked urls.

    Keyword Arguments:
        user {schemas.UserCreate} -- JSON Body with user details to create

    Keyword Arguments:
        db {Session} -- Current db connection
    """
    return crud.UserMockedUrls(db=db, user_id=user.id)


def GetAllUrl(identifier, db, tag):
    """Used to get all urls of a particular identifier.

    Arguments:
        identifier {[str]} -- The identifier
        db {[Session]} -- Session Object

    Returns:
        list_urls[dict] -- The list of urls to add to route table.
    """
    global indexed_urls
    indexed_urls = crud.GetAllUrls(db, identifier, tag)
    list_urls = []
    for url in indexed_urls:
        list_urls.append((url.url, url.request_type))
    return dict(list_urls)


async def aiohttpResponse(
    url, request, db, x_modify_body,
):
    """The main endpoint for every mocked request collection.

    Arguments:
        url {str} -- The url endpoint for which response is mocked
        request {Request} -- The complete curl request
        db {Session} -- Current db Session
        request_type {str} -- GET, POST, PUT

    Returns:
        Response[Any] -- The final response after modifying data,
        converting and validating it.
    """
    global indexed_urls
    db_url = None
    for i in range(len(indexed_urls)):
        if (
            indexed_urls[i].url == url
            and indexed_urls[i].request_type == request.method
        ):
            db_url = indexed_urls[i]
    if not db_url:
        raise HTTPException(status_code=404, detail="Url Not Found")
    db_header = db_url.request_headers
    req_body = db_url.request_body
    if "Content-Type" not in db_header:
        db_header["Content-Type"] = "application/json"
    if x_modify_body:
        x_modify_body = eval(x_modify_body)
        body = json.loads(db_url.request_body)
        dot_dict_resp = dotty(body)
        for i in x_modify_body.keys():
            dot_dict_resp[i] = x_modify_body[i]
        req_body = json.dumps(body)
    final_request = {
        "url": db_url.request_url,
        "body": req_body,
        "headers": db_header,
        "resp_key": db_url.response_key,
    }
    return final_request


def UrlResponse(
    url, query_param, request, db, modify_response, x_masquerader_code, request_type,
):
    """The main endpoint for every mocked request.

    Arguments:
        url {str} -- The url endpoint for which response is mocked
        request {Request} -- The complete curl request
        db {Session} -- Current db Session
        request_type {str} -- GET, POST, PUT

    Returns:
        Response[Any] -- The final response after modifying data,
        converting and validating it.
    """
    global indexed_urls
    db_url = None
    for i in range(len(indexed_urls)):
        if (
            indexed_urls[i].url == url
            and indexed_urls[i].request_type == request_type
            and indexed_urls[i].payload == query_param
        ):
            db_url = indexed_urls[i]
    if not db_url:
        raise HTTPException(status_code=404, detail="Url Not Found")
    if not db_url.is_active:
        return Response(
            status_code=db_url.inactive_status_code, content=db_url.inactive_response,
        )
    db_header = db_url.headers
    resp = db_url.response
    if "Content-Type" not in db_header:
        db_header["Content-Type"] = "application/json"
    if modify_response is not None and db_header["Content-Type"] == "application/json":
        modify_response = eval(modify_response)
        resp = json.loads(db_url.response)
        dot_dict_resp = dotty(resp)
        for i in modify_response.keys():
            dot_dict_resp[i] = modify_response[i]
        resp = json.dumps(resp)
    response = {
        "status_code": db_url.status_code,
        "content": resp,
        "headers": db_header,
        "latency": db_url.latency,
        "payload": db_url.payload,
    }
    return response
