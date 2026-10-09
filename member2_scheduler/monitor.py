import json
import time


def check_contention(server):
    if server.type == "GPU":
        if server.gpu_util > 80 or server.gpu_mem > 80:
            server.overloaded = True
            return True
    else:
        if server.mem_bw > 80 or server.llc_miss > 40 or server.cpu_util > 80:
            server.overloaded = True
            return True
    server.overloaded = False
    return False


def log_contention(server, task_id, log_file="contention_log.json"):
    if server.type == "GPU":
        if server.gpu_util > 80:
            metric, value = "gpu_util", server.gpu_util
        else:
            metric, value = "gpu_mem", server.gpu_mem
    else:
        if server.mem_bw > 80:
            metric, value = "mem_bw", server.mem_bw
        elif server.llc_miss > 40:
            metric, value = "llc_miss", server.llc_miss
        else:
            metric, value = "cpu_util", server.cpu_util

    event = {
        "timestamp": int(time.time()),
        "server": server.id,
        "metric": metric,
        "value": value,
        "status": "overloaded",
        "task_id": task_id
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event