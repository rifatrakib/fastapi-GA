import os
import subprocess

import uvicorn
from typer import Typer

app = Typer()


@app.command(name="runserver")
def run_api_server(mode: str = "development"):
    os.environ["MODE"] = mode

    if mode == "development":
        subprocess.Popen("wsl redis-server", shell=True)

    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    app()
