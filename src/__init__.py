from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.api import auth, user, shortner
from src.app.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting ..................")
    await init_db()
    yield
    print("Server is shutting down...........")
    print("Server has been stopped")

version = "v1"

app = FastAPI(
    title="URL Shortner API",
    description="An API for URL shortner",
    version=version,
    lifespan=lifespan,
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/mit"
    },
    contact={
        "name": "Godprevail Eseh",
        "email": "esehgodprevail@gmail.com",
        "url": "https://github.com/Egcarson?tab=repositories"
    },
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    openapi_url=f"/api/{version}/openai.json"
)


app.include_router(auth.auth_router, prefix=f"/api/{version}/auth")
app.include_router(user.user_router, prefix=f"/api/{version}")
app.include_router(shortner.url_router, prefix=f"/api/{version}")




@app.get('/')
async def root():
    return {"URL Shortner API"}