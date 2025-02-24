from flask import jsonify, Blueprint, request, current_app
import sqlite3
import psutil
import time
import os

stats_bp = Blueprint('stats', __name__)


def format_uptime(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, sec = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


@stats_bp.route('/stats', methods=['GET'])
def stats():
    api_key = request.headers.get('X-API-KEY')
    if api_key != current_app.config.get('AUTO_TRAIN_API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
    vm = psutil.virtual_memory()
    memory_info = {
        "total": f"{vm.total / (1024 ** 3):.2f} GB",
        "available": f"{vm.available / (1024 ** 3):.2f} GB",
        "used": f"{vm.used / (1024 ** 3):.2f} GB",
        "percentage": f"{vm.percent} %"
    }

    cpu_usage = psutil.cpu_percent(interval=1)
    uptime_seconds = time.time() - psutil.boot_time()

    return jsonify({
        "memory": memory_info,
        "cpu": f"{cpu_usage} %",
        "uptime": format_uptime(uptime_seconds)
    })
