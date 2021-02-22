"""Main App Server to handle requests."""
import asyncio
import os
import re
from subprocess import call
from urllib.parse import urlparse

from aiohttp_requests import requests
from config import current_config
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from starlette.responses import Response

from mock_server import helpers, schemas
from mock_server.database import Base, engine, get_db_for_x0

Base.metadata.create_all(bind=engine)

current_env = os.environ.get("ENV")

local_env = [None, "development"]


def create_app():
    """This function creates the FastAPI app server.

    Returns:
        app[FastAPI] -- The main app server
    """
    app = FastAPI(
        title="Masquerader - Mock Server",
        description="""This project allows you to mock any system,
        or service that you wish to.\n
        For Postman Collection import this url:
        https://www.getpostman.com/collections/a8cea6af57e17a8fcd93""",
        version="1.0.0",
        docs_url="/watchdocs",
        redoc_url="/watchdocs2",
        openapi_prefix="/masquerader" if current_env not in local_env else "",
        openapi_url="/swagger.json",
    )
    return app


app = create_app()

security = HTTPBasic()

engines = engine


def change_engine(eng):
    """Used for changing connected db.

    Will be used only in testing for creating a mock db.
    """
    global engines
    engines = eng
    Base.metadata.create_all(bind=engines)
    return engines


def drop_engine(eng):
    """To drop tables of a db."""
    return Base.metadata.drop_all(bind=eng)


async def get_db():
    """To Get the current db connection.

    Yields:
        [db] -- [The current connection]
    """
    engine1 = engines
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/_healthz", tags=["System Check"])
async def healthz():
    """Healthz check if server is available.

    Returns:
        {dict} -- returns message as working
    """
    return {"message": "Mock Server Working"}


@app.get("/_readyz", tags=["System Check"])
async def readyz():
    """Readyz check if server is available.

    Returns:
        {dict} -- returns message as working
    """
    return {"message": "Mock Server Ready"}


@app.get("/grafana.json", tags=["System Check"])
async def grafana():
    """Grafana check if server is available.

    Returns:
        {dict} -- returns message as working
    """
    return {"message": "Grafana not added yet"}


@app.post("/set-x0-x1-db/", tags=["Only for x0 configuration"])
async def x0():
    """Creates a temp db on x0 x1.

    Returns:
        response[json] -- Message on creation
    """
    if current_config.ENV == "x0" or current_config.ENV == "x1":
        session = get_db_for_x0()
        try:
            session.connection().connection.set_isolation_level(0)
            session.execute("DROP DATABASE mockdb;")
            drop_engine(engine)
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
        Base.metadata.create_all(bind=engine)
        session.execute("CREATE DATABASE mockdb;")
        session.connection().connection.set_isolation_level(1)
        call(["alembic", "upgrade", "head"])
        return {"success": True, "message": "Migrations done successfully"}
    else:
        return HTTPException(status_code=500, detail="Environment is not X0 or X1")


@app.get("/user/auth/", response_model=schemas.User, tags=["User"])
async def UserAuth(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Used for User Authentication. Uses HTTPBasicAuth.

    Keyword Arguments:
        credentials {HTTPBasicCredentials} -- HTTPBasicAuth Token
        db {Session} -- gets current db

    Raises:
        HTTPException: if user not authenticated

    Returns:
        db_user{dict} -- User Details stored in db
    """
    return helpers.UserAuth(credentials, db)


@app.post("/user/create/", response_model=schemas.User, tags=["User"])
async def UserCreate(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint for creating a user.

    Arguments:
        user {schemas.UserCreate} -- JSON Body with user details to create

    Keyword Arguments:
        db {Session} -- Current db connection

    Raises:
        HTTPException: If user already exists or failed to add user

    Returns:
        user[dict] -- If successful shows the user id and other data
    """
    return helpers.UserCreate(user, db)


@app.post("/url/create/", response_model=schemas.Url, tags=["Url"])
async def UrlCreate(
    url: schemas.UrlCreate, db: Session = Depends(get_db), user=Depends(UserAuth),
):
    """Endpoint to create or mock a url.

    Arguments:
        url {schemas.UrlCreate} -- JSON Body that contains url data.

    Keyword Arguments:
        db {Session} -- To get current db Session
        user {str} -- The User detail who mocked the URL

    Returns:
        MockedURL[dict] -- Details of the mocked URL

    Use this Request Body --
    { "identifier": "string", "request_type": "string",
    "url": "string", "response":{}, "headers": {}, "status_code": 0,
    "latency": 0, "is_active": true }

    If response you are mocking is a json use {},
    if xml then add it as string "".
    """
    return helpers.UrlCreate(url, db, user)


@app.post("/url/update/", tags=["Url"])
async def UrlUpdate(
    url: schemas.UrlUpdate, db: Session = Depends(get_db), user=Depends(UserAuth),
):
    """Endpoint to update details of any mocked URL.

    Arguments:
        url {schemas.UrlUpdate} -- Json Body that contains url
        and the value to be changed

    Keyword Arguments:
        db {Session} -- Current db Session
        user {str} -- The User who modified the Data

    Raises:
        HTTPException: If url not found or failed due to incorrect data

    Returns:
        b[list] -- [List of keys that were updated
    """
    return helpers.UrlUpdate(url, db, user)


@app.post("/url/delete/", tags=["Url"])
async def UrlDelete(
    url: schemas.UrlDelete, db: Session = Depends(get_db), user=Depends(UserAuth),
):
    """Endpoint to remove any mocked url.

    Keyword Arguments:
        user {str} -- The user who is removing it
        Also only the user who created the URL can delete it.
        db {Session} -- Current db Sessiom
        old_url {str} -- Url to be deleted

    Raises:
        HTTPException: If incorrect URL provided

    Returns:
        [dict] -- message that url was removed
    """
    return helpers.UrlDelete(url, db, user)


@app.post("/url/toggle/", tags=["Url"])
async def UrlToggle(
    url: schemas.UrlToggle, db: Session = Depends(get_db), user=Depends(UserAuth),
):
    """Endpoint to toggle url - 200 or 400.

    Keyword Arguments:
        db {Session} -- Current db Session
        url {str} -- The url to be toggled
        status_code {int} -- status code of old url,
        If not mentioned will toggle all similar urls.
        inactive_response {str} -- if required any negative response
        user {str} -- User Details who is toggling it.

    Raises:
        HTTPException: If Incorrect URL details provided

    Returns:
        b[dict] -- Url and current status of URL.
    """
    return helpers.UrlToggle(url, db, user)


@app.get("/url/mocked/", tags=["Url"])
async def UrlMocked(user=Depends(UserAuth), db: Session = Depends(get_db)):
    """Endpoint for getting all mocked urls.

    Keyword Arguments:
        user {schemas.UserCreate} -- JSON Body with user details to create

    Keyword Arguments:
        db {Session} -- Current db connection
    """
    return helpers.UrlMocked(user, db)


@app.post("/url/collection/create/", tags=["Url Collection [NEW]"])
async def UrlCollectionCreate(
    url: schemas.UrlCollection, db: Session = Depends(get_db), user=Depends(UserAuth),
):
    """This creates a collection for url mocking.

    Args:
        url (schemas.UrlCollection): [description]
        db (Session, optional): [description]. Defaults to Depends(get_db).
        user ([type], optional): [description]. Defaults to Depends(UserAuth).

    Returns:
        [type]: [description]
    """
    resp = await helpers.UrlCollectionCreate(url, db, user)
    return resp


@app.get("/collection{path:path}", tags=["Url Collection [NEW]"])
@app.post("/collection{path:path}", tags=["Url Collection [NEW]"])
@app.put("/collection{path:path}", tags=["Url Collection [NEW]"])
async def UrlCollection(
    path: str,
    request: Request,
    x_identifier_id: str = Header(None, convert_underscores=True),
    x_modify_body=Header(None, convert_underscores=True),
    db: Session = Depends(get_db),
):
    """This is the endpoint for every mocked url.

    Arguments:
        request {Request} -- The whole Request details

    Keyword Arguments:
        x_identifier_id {str} -- Identifier required to know which url to use.
        modify_response {[type]} -- If you want to modify the response
        **Works for json data only.**
        x_status_code {int} -- For multiple urls with different status code.
        You can mention in headers which status code you require.
        db {Session} -- Session object

    Raises:
        HTTPException: if URL is not found.

    Returns:
        response[Response] -- The required response.
    """
    await asyncio.Task(UrlLoad(x_identifier_id, request, db, "collection"))
    regex_list = []
    route_id = 0
    for route in range(0, len(app.routes)):
        regex_list.append(app.routes[route].path_regex)
    for regex in regex_list:
        if re.match(regex, path):
            route_id = regex_list.index(regex)
    url_to_search_in_db = app.routes[route_id].path
    requests_new = await helpers.aiohttpResponse(
        url_to_search_in_db, request, db, x_modify_body,
    )
    response_new = requests
    if request.method == "GET":
        response_new = await requests.get(
            requests_new["url"], headers=requests_new["headers"]
        )
    elif request.method == "POST":
        response_new = await requests.post(
            requests_new["url"],
            headers=requests_new["headers"],
            data=requests_new["body"],
        )
    elif request.method == "PUT":
        response_new = await requests.put(
            requests_new["url"],
            headers=requests_new["headers"],
            data=requests_new["body"],
        )
    return Response(content=await response_new.text(), headers=response_new.headers,)


async def UrlLoad(identifier, request: Request, db=None, tag: str = None):
    """This loads the mocked URL's in the app route table.

    Keyword Arguments:
        identifier {[str]} -- To load URL's of a particular identifier.
        request {Request} -- Request object
    """
    if not db:
        engine1 = engines
        try:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
            db = SessionLocal()
        finally:
            db.close()
    urls_dict = helpers.GetAllUrl(identifier, db, tag)
    for url in urls_dict.keys():
        app.add_api_route(url, Url, methods=[urls_dict[url]], tags=["Mocked Urls"])
    print({"urls": "mocked"})


@app.get("{path:path}", tags=["Url Endpoint"])
@app.post("{path:path}", tags=["Url Endpoint"])
@app.put("{path:path}", tags=["Url Endpoint"])
async def Url(
    path: str,
    request: Request,
    x_identifier_id: str = Header(None, convert_underscores=True),
    x_modify_response=Header(None, convert_underscores=True),
    x_status_code: int = Header(None, convert_underscores=True),
    db: Session = Depends(get_db),
):
    """This is the endpoint for every mocked url.

    Arguments:
        request {Request} -- The whole Request details

    Keyword Arguments:
        x_identifier_id {str} -- Identifier required to know which url to use.
        modify_response {[type]} -- If you want to modify the response
        **Works for json data only.**
        x_status_code {int} -- For multiple urls with different status code.
        You can mention in headers which status code you require.
        db {Session} -- Session object

    Raises:
        HTTPException: if URL is not found.

    Returns:
        response[Response] -- The required response.
    """
    await asyncio.Task(UrlLoad(x_identifier_id, request, db, "url"))
    o = urlparse(str(request.url))
    url_path = o.path
    url_query = o.query
    regex_list = []
    route_id = 0
    for route in range(0, len(app.routes)):
        regex_list.append(app.routes[route].path_regex)
    for regex in regex_list:
        if re.match(regex, url_path):
            route_id = regex_list.index(regex)
    url_to_search_in_db = app.routes[route_id].path
    print(request.headers, x_modify_response)
    response = helpers.UrlResponse(
        url_to_search_in_db,
        url_query,
        request,
        db,
        x_modify_response,
        x_status_code,
        request.method,
    )
    if type(response) == Response:
        return response
    if response["payload"] != "" and response["payload"] != url_query:
        raise HTTPException(
            status_code=402, detail=("Incorrect Query Params."),
        )
    await asyncio.sleep(response["latency"])
    return Response(
        status_code=response["status_code"],
        content=response["content"],
        headers=response["headers"],
    )
