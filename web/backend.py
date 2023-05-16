import watchdog

from pathlib import Path
from loguru import logger
from threading import Thread
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, jsonify, redirect, render_template, request

logs_dir = "../logs"
max_lines = 50  # Lenght of history for the frontend
p = Path("../exploits")
exploitsfiles = list(p.glob("**/[!_]*.py"))


logger.add(
    sink=f"{logs_dir}/backend.log",
    format="{time:HH:mm:ss.SS} [{level:^8}] : {message}",
    enqueue=True,
    level="INFO",
)
app = Flask(__name__)
socketio = SocketIO(app)
channels = list(Path(logs_dir).glob("**/*.log"))
host = "0.0.0.0"
port = 5000
debug = True

CORS(origins="*")


@app.route("/ping")
def ping():
    return jsonify("pong")


@app.route("/logs")
def logs():
    return render_template("logs.html", channels=channels)


@app.route("/configs")
def configs():
    return render_template("configs.html")


@app.route("/exploits", methods=["GET", "POST"])
def exploits():
    if request.method == "POST":
        filename = request.files["exploit_file"].filename
        if filename:
            file = request.files["exploit_file"]
            file.save(f"../exploits/{filename}")
    return render_template("exploits.html", exploits=[e.name for e in exploitsfiles])


@app.route("/", methods=["GET"])
def index():
    return redirect("/logs")


@socketio.on("connected")
def handle_connect(data):
    for channel in channels:
        l = getLogs(channel)
        socketio.emit(str(channel), l)


def getLogs(filename):
    with open(filename, "r") as f:
        l = f.readlines()[-max_lines:]
        return "".join(l)


class logsHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        if not event.is_directory:
            socketio.emit(event.src_path, getLogs(event.src_path))


class newfileHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        global exploitsfiles
        exploitsfiles = list(p.glob("**/[!_]*.py"))


def runObserver():
    obs = watchdog.observers.Observer()
    obs.schedule(logsHandler(), path=logs_dir, recursive=True)
    obs.schedule(newfileHandler(), path=p, recursive=True)
    obs.start()


def main():
    logger.info("Starting Observer Thread")
    t = Thread(target=runObserver)
    t.start()
    logger.info(f"Starting webserver on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
    t.join()


if __name__ == "__main__":
    main()
