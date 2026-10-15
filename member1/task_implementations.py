
import torch
import time
import requests
import psutil


def compute_task_matrix_multiply(size=2048, device="cuda"):
    """Compute-intensive matrix multiplication task."""
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)

    if device == "cuda":
        torch.cuda.synchronize()

    start = time.perf_counter()

    for _ in range(10):
        c = torch.matmul(a, b)

    if device == "cuda":
        torch.cuda.synchronize()

    return time.perf_counter() - start


def memory_task_array_copy(size=10**7, device="cpu"):
    """Memory-intensive array copying task."""
    a = torch.randn(size, device=device)

    if device == "cuda":
        torch.cuda.synchronize()

    start = time.perf_counter()

    for _ in range(5):
        b = a.clone()

    if device == "cuda":
        torch.cuda.synchronize()

    return time.perf_counter() - start


def network_task_file_transfer(
    url="https://speed.cloudflare.com/__down?bytes=10000000",
    device="cpu"
):
    """Download a file and measure network traffic."""
    net_before = psutil.net_io_counters()
    start = time.perf_counter()

    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=65536):
            pass

    runtime = time.perf_counter() - start
    net_after = psutil.net_io_counters()

    total_bytes = (
        net_after.bytes_recv - net_before.bytes_recv
        + net_after.bytes_sent - net_before.bytes_sent
    )

    network_mbps = (
        total_bytes * 8 / (runtime * 1_000_000)
        if runtime > 0 else 0.0
    )

    return runtime, network_mbps, total_bytes


def network_task_api_stream(
    url="https://httpbin.org/get",
    device="cpu"
):
    """Perform 20 HTTP requests and measure network traffic."""
    net_before = psutil.net_io_counters()
    start = time.perf_counter()

    for _ in range(20):
        with requests.get(url, timeout=15) as response:
            response.raise_for_status()
            _ = response.content

    runtime = time.perf_counter() - start
    net_after = psutil.net_io_counters()

    total_bytes = (
        net_after.bytes_recv - net_before.bytes_recv
        + net_after.bytes_sent - net_before.bytes_sent
    )

    network_mbps = (
        total_bytes * 8 / (runtime * 1_000_000)
        if runtime > 0 else 0.0
    )

    return runtime, network_mbps, total_bytes
