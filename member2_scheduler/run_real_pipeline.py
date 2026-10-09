import pandas as pd
from scheduler import Server, Task, place_task
from monitor import check_contention, log_contention

df = pd.read_csv("task_metrics.csv")

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