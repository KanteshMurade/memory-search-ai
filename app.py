from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

# Serve images from photos folder
app.mount(
    "/photos",
    StaticFiles(directory="photos"),
    name="photos"
)

templates = Jinja2Templates(
    directory="templates"
)


@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "results": []
        }
    )


@app.get("/search")
async def search(
    request: Request,
    query: str = ""
):

    try:
        with open(
            "master_data.json",
            "r"
        ) as f:
            data = json.load(f)

    except:
        data = []

    results = []

    for item in data:

        searchable_text = (
            item.get("caption", "")
            + " "
            + " ".join(
                item.get("objects", [])
            )
            + " "
            + " ".join(
                item.get("people", [])
            )
        ).lower()

        if query.lower() in searchable_text:
            results.append(item)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "results": results,
            "query": query
        }
    )