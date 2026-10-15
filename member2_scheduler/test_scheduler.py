from scheduler import (
    Server, Task, place_task, calculate_network_cost,
    classify_task_network_aware
)
from monitor import check_contention, check_network_congestion
from baselines import place_all_cpu, place_all_gpu, place_random


def test_compute_task_on_gpu():
    servers = [Server("gpu1", "GPU"), Server("cpu1", "CPU")]
    task = Task("t1", "compute-intensive", 2.3, 2048)
    place_task(task, servers)
    assert task.assigned_server.type == "GPU"


def test_memory_task_on_cpu():
    servers = [Server("gpu1", "GPU"), Server("cpu1", "CPU")]
    task = Task("t2", "memory-intensive", 3.2, 4096)
    place_task(task, servers)
    assert task.assigned_server.type == "CPU"


def test_gpu_overloaded():
    server = Server("gpu1", "GPU")
    server.gpu_util = 85
    assert check_contention(server) is True


def test_cpu_overloaded():
    server = Server("cpu1", "CPU")
    server.llc_miss = 45
    assert check_contention(server) is True


def test_all_cpu_baseline():
    servers = [Server("gpu1", "GPU"), Server("cpu1", "CPU")]
    tasks = [
        Task("t1", "compute-intensive", 2.3, 2048),
        Task("t2", "memory-intensive", 3.2, 4096)
    ]
    place_all_cpu(tasks, servers)
    for task in tasks:
        assert task.assigned_server.type == "CPU"


def test_all_gpu_baseline():
    servers = [Server("gpu1", "GPU"), Server("cpu1", "CPU")]
    tasks = [
        Task("t1", "compute-intensive", 2.3, 2048),
        Task("t2", "memory-intensive", 3.2, 4096)
    ]
    place_all_gpu(tasks, servers)
    for task in tasks:
        assert task.assigned_server.type == "GPU"


def test_random_baseline():
    servers = [Server("gpu1", "GPU"), Server("cpu1", "CPU")]
    tasks = [
        Task("t1", "compute-intensive", 2.3, 2048),
        Task("t2", "memory-intensive", 3.2, 4096)
    ]
    place_random(tasks, servers)
    for task in tasks:
        assert task.assigned_server is not None


def test_network_cost_formula():
    server = Server("gpu1", "GPU", bandwidth_mbps=1000, latency_ms=0.5)
    task = Task("t1", "compute-intensive", 2.3, 100)
    expected = (100 * 8) / 1000 + 0.5 / 1000
    actual = calculate_network_cost(task, server)
    assert abs(actual - expected) < 1e-9


def test_network_intensive_classified():
    result = classify_task_network_aware(0.5, 0.15, 0.30, 120.0)
    assert result == "network-intensive"


def test_network_intensive_avoids_congested_server():
    servers = [
        Server("gpu1", "GPU", bandwidth_mbps=1000),
        Server("gpu2", "GPU", bandwidth_mbps=1000)
    ]
    servers[0].update_network(measured_mbps=200)
    servers[1].update_network(measured_mbps=900)
    task = Task("t1", "network-intensive", 5.0, 512, network_mbps=120.0)
    place_task(task, servers)
    assert task.assigned_server.id == "gpu2"


def test_network_congestion_detected():
    server = Server("gpu1", "GPU", bandwidth_mbps=1000)
    server.update_network(measured_mbps=200)
    assert check_network_congestion(server) is True
