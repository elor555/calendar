from app import config
from app.database import engine, models
from app.dependencies import get_db, logger, MEDIA_PATH, STATIC_PATH, templates
from app.internal import daily_quotes, json_data_loader, load_hebrew_view

from app.internal.languages import set_ui_language
from app.internal.security.ouath2 import auth_exception_handler
from app.utils.extending_openapi import custom_openapi
from app.routers.salary import routes as salary
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy.orm import Session


def create_tables(engine, psql_environment):
    if 'sqlite' in str(engine.url) and psql_environment:
        raise models.PSQLEnvironmentError(
            "You're trying to use PSQL features on SQLite env.\n"
            "Please set app.config.PSQL_ENVIRONMENT to False "
            "and run the app again."
        )
    else:
        models.Base.metadata.create_all(bind=engine)


create_tables(engine, config.PSQL_ENVIRONMENT)

app = FastAPI(title="Pylander", docs_url=None)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")
app.logger = logger

app.add_exception_handler(HTTP_401_UNAUTHORIZED, auth_exception_handler)

json_data_loader.load_to_db(next(get_db()))
load_hebrew_view.load_hebrew_view_if_table_empty(next(get_db()))
# This MUST come before the app.routers imports.
set_ui_language()

from app.routers import (  # noqa: E402
    about_us, agenda, calendar, categories, celebrity,
    currency, dayview, email, event, export, four_o_four,
    google_connect, hebrew_date, invitation, login,
    logout, profile, register, search, telegram, user,
    weekview, whatsapp,
)

json_data_loader.load_to_db(next(get_db()))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


routers_to_include = [
    about_us.router,
    agenda.router,
    calendar.router,
    categories.router,
    celebrity.router,
    currency.router,
    dayview.router,
    email.router,
    event.router,
    export.router,
    four_o_four.router,
    hebrew_date.router,
    google_connect.router,
    invitation.router,
    login.router,
    logout.router,
    profile.router,
    register.router,
    salary.router,
    search.router,
    telegram.router,
    user.router,
    weekview.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)


# TODO: I add the quote day to the home page
# until the relevant calendar view will be developed.
@app.get("/", include_in_schema=False)
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "quote": quote,
    })


custom_openapi(app)
