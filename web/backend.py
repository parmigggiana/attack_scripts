import os
import watchdog

from status_scraper import scrape_status, conf

from time import sleep
from pathlib import Path
from loguru import logger
from threading import Thread
from ansi2html import Ansi2HTMLConverter
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, jsonify, redirect, render_template, request

logs_dir = "../logs"
max_lines = 150  # Lenght of history for the frontend
p = Path("../exploits")
conv = Ansi2HTMLConverter(inline=True, scheme="osx")
status_dict = {}

logger.add(
    sink=f"{logs_dir}/backend.log",
    format="<d>{time:HH:mm:ss.SS}</d> | <level>{level:^8}</level> | {message}",
    enqueue=True,
    level="DEBUG",
    colorize=True,
)
app = Flask(__name__)
socketio = SocketIO(app)
channels = list(
    Path(logs_dir).glob("**/*.log")
)  # **/*.log for all subdirectories as well
host = "0.0.0.0"
port = 7070
debug = False

CORS(origins="*")


@app.route("/ping")
def ping():
    return jsonify("pong")


@app.route("/logs")
def logs():
    return render_template("logs.html", channels=list(Path(logs_dir).glob("*.log")))


@app.route("/configs", methods=["GET", "POST"])
def configs():
    if request.method == "POST":
        filestr = request.data.decode()
        with open("../configs/config.json", "w") as f:
            f.write(filestr)
    with open("../configs/config.json", "r") as f:
        configsfilestring = f.read()
    return render_template("configs.html", filestring=configsfilestring)


@app.route("/exploits", methods=["GET", "POST"])
def exploits():
    if request.method == "POST":
        filename = request.files["exploit_file"].filename
        if filename:
            file = request.files["exploit_file"]
            file.save(f"../exploits/{filename}")
            os.chmod(f"../exploits/{filename}", 0o777)

    exploitsfiles = list(p.glob("**/[!_]*.py"))
    files = {}
    for expf in exploitsfiles:
        with open(expf, "r") as f:
            files[expf.name] = f.read().replace("\\", "\\\\")
    return render_template(
        "exploits.html", filenames=[e.name for e in exploitsfiles], files=files
    )


@app.route("/exploits/<string:filename>", methods=["POST"])
def exploits_edit(filename):
    filename = filename
    body = request.data
    logger.debug(f"{filename = }, {body = }")
    try:
        with open(f"../exploits/{filename}", "bw+") as f:
            f.write(body)
        os.chmod(f"../exploits/{filename}", 0o777)
    except Exception as e:
        logger.info(f"{e}")
        return 500
    return "ok", 200


@app.route("/exploits/delete", methods=["GET"])
def exploit_delete():
    try:
        filename = request.args.get("filename")
    except ValueError:
        return "bad argument", 500
    os.remove(f"../exploits/{filename}")
    return "ok", 200


@app.route("/", methods=["GET"])
def index():
    return redirect("/exploits")


@app.route("/clear_logs", methods=["GET"])
def clear_logs():
    for file in Path(logs_dir).iterdir():
        os.remove(file)
    return "ok", 200


@socketio.on("connected")
def handle_connect(data):
    for channel in channels:
        l = getLogs(channel)
        socketio.emit(str(channel), l)


@socketio.on("statusconnected")
def handle_status(data):
    status_html = ""
    for servicename, statuses in status_dict.items():
        logger.debug(f"service: {servicename} status: {statuses}")
        try:
            status_sla = "verde" if statuses["CHECK_SLA"] == 101 else "rosso"
        except KeyError:
            status_sla = "rosso"
        try:
            status_get = "verde" if statuses["GET_FLAG"] == 101 else "rosso"
        except KeyError:
            status_get = "rosso"
        try:
            status_put = "verde" if statuses["PUT_FLAG"] == 101 else "rosso"
        except KeyError:
            status_put = "rosso"
        status_html += f"""
    <div class="flex items-center gap-3 p-2 bg-scuro">
        <p>{servicename}</p>
        <div class="flex items-center gap-2">
        <div class="rounded-full p-2 bg-{status_sla}"></div>
        <div class="rounded-full p-2 bg-{status_put}"></div>
        <div class="rounded-full p-2 bg-{status_get}"></div>
        </div>
    </div>
    """
    logger.debug("Updating status")
    socketio.emit("status", status_html)


def getLogs(filename):
    with open(filename, "r") as f:
        l = f.readlines()[-max_lines:]
        html_lines = [conv.convert(line, full=False) for line in l]
        return "".join(html_lines)


class logsHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        if not event.is_directory:
            socketio.emit(event.src_path, getLogs(event.src_path))


def runObserver():
    obs1 = watchdog.observers.Observer()
    obs1.schedule(logsHandler(), path=logs_dir, recursive=True)
    obs1.start()


def runStatusChecker():
    d = conf["status_check_delay"]
    global status_dict
    while True:
        try:
            status_dict = scrape_status(logger)
            socketio.emit("status", status_dict)
        except Exception as e:
            logger.error(f"{e}")
        sleep(d)


def main():
    logger.info("Starting Observer Thread")
    t = Thread(target=runObserver)
    t = Thread(target=runStatusChecker)
    t.start()
    logger.info(f"Starting webserver on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
    t.join()


if __name__ == "__main__":
    main()
