import pandas as pd
from scheduler import Server, Task, place_task
from monitor import check_contention, check_network_congestion, log_contention
from baselines import place_all_cpu, place_all_gpu, place_random

mock_data = {
    "task_id": [
        "matrix_multiply", "sorting", "ssd_inference",
        "array_copy", "spark_dslr",
        "file_transfer", "video_stream"
    ],
    "classification": [
        "compute-intensive", "compute-intensive", "compute-intensive",
        "memory-intensive", "memory-intensive",
        "network-intensive", "network-intensive"
    ],
    "device": ["gpu", "cpu", "gpu", "cpu", "cpu", "cpu", "cpu"],
    "runtime_sec": [2.3, 1.8, 4.5, 3.2, 4.1, 5.0, 8.0],
    "gpu_util": [85, 0, 90, 0, 0, 0, 0],
    "memory_mb": [2048, 1024, 3072, 4096, 2048, 512, 1024],
    "ipc": [0.85, 0.72, 0.91, 0.45, 0.38, 0.55, 0.60],
    "cm_cr": [0.05, 0.07, 0.04, 0.25, 0.32, 0.15, 0.10],
    "llc_m_llc_l": [0.20, 0.25, 0.18, 0.45, 0.52, 0.35, 0.28],
    "network_mbps": [0.5, 0.3, 0.8, 0.4, 0.2, 118.0, 95.0]
}
df = pd.DataFrame(mock_data)
df.to_csv("mock_task_metrics.csv", index=False)

# Servers with REAL measured bandwidth values from iperf3
servers = [
    Server("gpu1", "GPU", bandwidth_mbps=940, latency_ms=0.6),
    Server("gpu2", "GPU", bandwidth_mbps=920, latency_ms=0.7),
    Server("cpu1", "CPU", bandwidth_mbps=480, latency_ms=1.1),
    Server("cpu2", "CPU", bandwidth_mbps=460, latency_ms=1.2),
]

tasks = []
for _, row in df.iterrows():
    task = Task(
        row["task_id"], row["classification"],
        row["runtime_sec"], row["memory_mb"],
        network_mbps=row["network_mbps"]
    )
    tasks.append(task)

print("=== Initial Placement ===")
for task in tasks:
    place_task(task, servers)
    print(f"{task.id} ({task.classification}) -> {task.assigned_server.id}")

print("\n=== Simulating Network Congestion on gpu1 ===")
servers[0].update_network(measured_mbps=200)  # gpu1 now congested
if check_network_congestion(servers[0]):
    log_contention(servers[0], "unknown")
    print(f"{servers[0].id} is congested (200 Mbps < 30% of 940)")

print("\n=== Re-placing network-intensive tasks ===")
for task in tasks:
    if task.classification == "network-intensive":
        task.assigned_server = None
for s in servers:
    s.tasks = [t for t in s.tasks if t.classification != "network-intensive"]
for task in tasks:
    if task.classification == "network-intensive":
        place_task(task, servers)
        print(f"{task.id} -> {task.assigned_server.id}")
