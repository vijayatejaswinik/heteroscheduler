import math

NETWORK_THRESHOLD_MBPS = 10.0
CONGESTION_THRESHOLD = 0.3


def _is_nan(value):
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False


def _clean_float(value, default=0.0):
    if value is None or _is_nan(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class Server:
    def __init__(self, server_id, server_type,
                 bandwidth_mbps=1000, latency_ms=0.5):
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
        self.current_bandwidth_mbps = bandwidth_mbps
        self.latency_ms = latency_ms
        self.network_congested = False

    def update_network(self, measured_mbps, measured_latency_ms=None):
        self.current_bandwidth_mbps = measured_mbps
        if measured_latency_ms is not None:
            self.latency_ms = measured_latency_ms
        if measured_mbps < CONGESTION_THRESHOLD * self.bandwidth_mbps:
            self.network_congested = True
        else:
            self.network_congested = False


class Task:
    def __init__(self, task_id, classification, runtime_sec, memory_mb,
                 state_size_mb=None, network_mbps=0.0):
        self.id = task_id
        self.classification = classification
        self.runtime_sec = _clean_float(runtime_sec)
        self.memory_mb = _clean_float(memory_mb)
        self.state_size_mb = (
            state_size_mb if state_size_mb is not None else self.memory_mb
        )
        self.network_mbps = _clean_float(network_mbps)
        self.assigned_server = None


def classify_task_network_aware(ipc, cm_cr, llc_m_llc_l, network_mbps):
    if _clean_float(network_mbps) >= NETWORK_THRESHOLD_MBPS:
        return "network-intensive"
    ipc = _clean_float(ipc)
    cm_cr = _clean_float(cm_cr)
    llc_m_llc_l = _clean_float(llc_m_llc_l)
    if ipc >= 0.6 and cm_cr < 0.1:
        return "compute-intensive"
    if cm_cr >= 0.1 and llc_m_llc_l >= 0.3:
        return "memory-intensive"
    return "unclassified"


def calculate_network_cost(task, server):
    bw = server.current_bandwidth_mbps if server.current_bandwidth_mbps > 0 else 1
    transfer_time_sec = (task.memory_mb * 8) / bw
    latency_sec = server.latency_ms / 1000
    return transfer_time_sec + latency_sec


def place_task(task, servers):
    if task.classification == "network-intensive":
        best = max(servers, key=lambda s: s.current_bandwidth_mbps)
        task.assigned_server = best
        best.tasks.append(task)
        return best

    if task.classification == "compute-intensive":
        preferred = "GPU"
    elif task.classification == "memory-intensive":
        preferred = "CPU"
    else:
        preferred = "CPU"

    candidates = [s for s in servers if s.type == preferred]
    if not candidates:
        candidates = servers

    best = min(candidates, key=lambda s: calculate_network_cost(task, s))
    task.assigned_server = best
    best.tasks.append(task)
    return best
