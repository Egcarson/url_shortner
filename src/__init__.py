from fastapi import FastAPI


version = "v1"

app = FastAPI(
    title="URL Shortner API",
    description="An API for URL shortner",
    version=version,
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


@app.get('/')
async def root():
    return {"URL Shortner API"}