class Server:
    def __init__(self, server_id, server_type, bandwidth_mbps=1000, latency_ms=0.5):
        self.id = server_id
        self.type = server_type
        self.gpu_util = 0
        self.gpu_mem = 0
        self.cpu_util = 0
        self.mem_bw = 0
        self.llc_miss = 0
        self.tasks = []
        self.overloaded = False
        self.bandwidth_mbps = bandwidth_mbps
        self.latency_ms = latency_ms


class Task:
    def __init__(self, task_id, classification, runtime_sec, memory_mb, state_size_mb=None):
        self.id = task_id
        self.classification = classification
        self.runtime_sec = runtime_sec
        self.memory_mb = memory_mb
        self.state_size_mb = state_size_mb if state_size_mb is not None else memory_mb
        self.assigned_server = None


def calculate_network_cost(task, server):
    transfer_time_sec = (task.memory_mb * 8) / server.bandwidth_mbps
    latency_sec = server.latency_ms / 1000
    return transfer_time_sec + latency_sec


def place_task(task, servers):
    if task.classification == "compute-intensive":
        preferred_type = "GPU"
    elif task.classification == "memory-intensive":
        preferred_type = "CPU"
    else:
        preferred_type = "CPU"

    candidates = [s for s in servers if s.type == preferred_type]
    if not candidates:
        candidates = servers

    best_server = min(candidates, key=lambda s: calculate_network_cost(task, s))
    task.assigned_server = best_server
    best_server.tasks.append(task)
    return best_server