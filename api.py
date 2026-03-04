import contextlib
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

chunk_size = 1024 * 1024


@contextlib.asynccontextmanager
async def lifespan(app):
    Devices.loads()
    yield


class Devices:
    _devices = {}

    @classmethod
    def loads(cls):
        with open(Path(__file__).parent.joinpath("credentials")) as f:
            for line in f:
                token, customer_name = line.strip().split(",")
                cls._devices[token] = customer_name


app = Starlette(lifespan=lifespan)


@app.route("/logs", methods=["POST"])
async def logs(request: Request):
    token = request.headers.get("X-Device-Token")
    if token not in Devices._devices:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    location = Path(__file__).parent.joinpath("static", "logs", f"{token}.log")
    async with request.form(max_files=1) as form:
        with location.open("a") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk.decode())
    return JSONResponse({"saved_at": location.as_posix()})


@app.route("/db", methods=["POST"])
async def db(request: Request):
    token = request.headers.get("X-Device-Token")
    if token not in Devices._devices:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    location = Path(__file__).parent.joinpath("static", "db", f"{token}.db")

    async with request.form(max_files=1) as form:
        with location.open("wb") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk)
    return JSONResponse({"saved_at": location.as_posix()})
