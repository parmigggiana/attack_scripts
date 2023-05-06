from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Thread
import watchdog
from pathlib import Path
from loguru import logger

logs_dir = "../logs"
max_lines = 50  # Lenght of history for the frontend

logger.add(
    sink=f"{logs_dir}/backend.log",
    format="{time:HH:mm:ss.SS} [{level:^8}] : {message}",
    enqueue=True,
    level="INFO",
)
app = Flask(__name__)
socketio = SocketIO(app)
async_mode = socketio.async_mode
channels = list(Path(logs_dir).glob("**/*.log"))
host = "0.0.0.0"
port = 5000
debug = True

CORS(origins="*")


@app.route("/ping")
def ping():
    return jsonify("pong")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", channels=channels)


@socketio.on("connected")
def handle_connect(data):
    for channel in channels:
        l = getLogs(channel)
        socketio.emit(str(channel), l)


def getLogs(filename):
    # print(f"{filename = }")
    # print(filename)
    with open(filename, "r") as f:
        l = f.readlines()[-max_lines:]
        return "".join(l)


class eventHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        if not event.is_directory:
            socketio.emit(event.src_path, getLogs(event.src_path))


def runObeserver():
    obs = watchdog.observers.Observer()
    obs.schedule(eventHandler(), path=logs_dir, recursive=True)
    obs.start()


def main():
    logger.info("Starting Observer Thread")
    t = Thread(target=runObeserver)
    t.start()
    logger.info(f"Starting webserver on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
    t.join()


if __name__ == "__main__":
    main()
