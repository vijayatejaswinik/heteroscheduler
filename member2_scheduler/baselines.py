import random


def place_all_cpu(tasks, servers):
    cpu_servers = [s for s in servers if s.type == "CPU"]
    if not cpu_servers:
        cpu_servers = servers
    for task in tasks:
        task.assigned_server = cpu_servers[0]
        cpu_servers[0].tasks.append(task)


def place_all_gpu(tasks, servers):
    gpu_servers = [s for s in servers if s.type == "GPU"]
    if not gpu_servers:
        gpu_servers = servers
    for task in tasks:
        task.assigned_server = gpu_servers[0]
        gpu_servers[0].tasks.append(task)


def place_random(tasks, servers):
    for task in tasks:
        server = random.choice(servers)
        task.assigned_server = server
        server.tasks.append(task)