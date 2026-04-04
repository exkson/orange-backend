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
                token, id, customer_name = line.strip().split(",")
                cls._devices[token] = (id, customer_name)


app = Starlette(lifespan=lifespan)


@app.route("/", methods=["GET"])
async def index(request: Request):
    return JSONResponse({"message": "Hello, World!"})


@app.route("/logs", methods=["POST"])
async def logs(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token not in Devices._devices:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    id, _ = Devices._devices[token]

    async with request.form(max_files=1) as form:
        client_mode = form.get("mode", "auto")
        location = Path(__file__).parent.joinpath(
            "static", client_mode, "logs", f"{id}.log"
        )
        with location.open("a") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk.decode())
        return JSONResponse({"saved_at": location.as_posix()})


@app.route("/db", methods=["POST"])
async def db(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token not in Devices._devices:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    id, _ = Devices._devices[token]

    async with request.form(max_files=1) as form:
        client_mode = form.get("mode", "auto")
        location = Path(__file__).parent.joinpath(
            "static", client_mode, "db", f"{id}.db"
        )
        with location.open("wb") as out:
            while chunk := await form["file"].read(chunk_size):
                out.write(chunk)
        return JSONResponse({"saved_at": location.as_posix()})
