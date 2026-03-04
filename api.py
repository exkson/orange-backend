from datetime import datetime
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

app = Starlette(debug=True)

chunk_size = 1024 * 1024


@app.route("/logs", methods=["POST"])
async def logs(request: Request):
    received_at = datetime.now().isoformat().replace("T", "").rstrip("Z")
    location = Path(__file__).parent.joinpath("static", "logs", f"{received_at}.log")
    async with request.form(max_files=1) as form:
        with location.open("a") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk.decode())
    return JSONResponse({"saved_at": location.as_posix()})


@app.route("/db", methods=["POST"])
async def db(request: Request):
    received_at = datetime.now().isoformat().replace("T", "").rstrip("Z")
    location = Path(__file__).parent.joinpath("static", "db", f"{received_at}.db")

    async with request.form(max_files=1) as form:
        with location.open("wb") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk)
    return JSONResponse({"saved_at": location.as_posix()})
