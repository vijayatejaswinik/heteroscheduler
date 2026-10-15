import math
import pandas as pd
from scheduler import Server, Task, place_task


def is_nan(v):
    try:
        return math.isnan(v)
    except (TypeError, ValueError):
        return False


df = pd.read_csv("simulated_metrics.csv")

print("CSV columns:", df.columns.tolist())
print("Rows:", len(df))

servers = [
    Server("gpu1", "GPU", bandwidth_mbps=940, latency_ms=0.6),
    Server("gpu2", "GPU", bandwidth_mbps=920, latency_ms=0.7),
    Server("cpu1", "CPU", bandwidth_mbps=480, latency_ms=1.1),
    Server("cpu2", "CPU", bandwidth_mbps=460, latency_ms=1.2),
]

tasks = []
for _, row in df.iterrows():
    memory_mb = 0.0 if is_nan(row.get("memory_mb")) else float(row["memory_mb"])
    network_mbps = 0.0 if is_nan(row.get("network_mbps")) else float(row["network_mbps"])

    task = Task(
        task_id=row["task_id"],
        classification=row["classification"],
        runtime_sec=float(row["runtime_sec"]),
        memory_mb=memory_mb,
        network_mbps=network_mbps,
    )
    tasks.append(task)

print("\n=== Placement ===")
for task in tasks:
    place_task(task, servers)
    print(f"{task.id:20s} ({task.classification:22s}) -> {task.assigned_server.id}")
