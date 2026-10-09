import pytest
from scheduler import Server, Task, place_task, calculate_network_cost
from monitor import check_contention
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