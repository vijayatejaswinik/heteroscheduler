import pandas as pd
from scheduler import Server, Task, place_task
from monitor import check_contention, log_contention
from baselines import place_all_cpu, place_all_gpu, place_random

mock_data = {
    "task_id": ["matrix_multiply", "matrix_multiply", "array_copy", "array_copy"],
    "classification": ["compute-intensive", "compute-intensive", "memory-intensive", "memory-intensive"],
    "device": ["gpu", "cpu", "cpu", "gpu"],
    "runtime_sec": [2.3, 5.1, 3.2, 3.7],
    "gpu_util": [85, 0, 0, 20],
    "memory_mb": [2048, 2048, 4096, 4096],
    "ipc": [0.85, 0.85, 0.45, 0.45],
    "cm_cr": [0.05, 0.05, 0.25, 0.25],
    "llc_m_llc_l": [0.20, 0.20, 0.45, 0.45]
}
df = pd.DataFrame(mock_data)
df.to_csv("mock_task_metrics.csv", index=False)

servers = [
    Server("gpu1", "GPU", bandwidth_mbps=1000, latency_ms=0.5),
    Server("gpu2", "GPU", bandwidth_mbps=1000, latency_ms=0.5),
    Server("cpu1", "CPU", bandwidth_mbps=500, latency_ms=1.0)
]

tasks = []
for _, row in df.iterrows():
    task = Task(
        row["task_id"],
        row["classification"],
        row["runtime_sec"],
        row["memory_mb"],
        state_size_mb=row["memory_mb"]
    )
    tasks.append(task)

print("=== Initial Placement ===")
for task in tasks:
    place_task(task, servers)
    print(f"{task.id} ({task.classification}) -> {task.assigned_server.id}")

print("\n=== Contention Check ===")
servers[0].gpu_util = 85
for server in servers:
    if check_contention(server):
        log_contention(server, "unknown")
        print(f"{server.id} is overloaded")

print("\n=== All-CPU Baseline ===")
for task in tasks:
    task.assigned_server = None
for s in servers:
    s.tasks = []
place_all_cpu(tasks, servers)
for task in tasks:
    print(f"{task.id} -> {task.assigned_server.id}")

print("\n=== All-GPU Baseline ===")
for task in tasks:
    task.assigned_server = None
for s in servers:
    s.tasks = []
place_all_gpu(tasks, servers)
for task in tasks:
    print(f"{task.id} -> {task.assigned_server.id}")

print("\n=== Random Baseline ===")
for task in tasks:
    task.assigned_server = None
for s in servers:
    s.tasks = []
place_random(tasks, servers)
for task in tasks:
    print(f"{task.id} -> {task.assigned_server.id}")