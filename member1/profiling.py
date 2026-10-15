
import time
import subprocess
import threading
import statistics
import psutil
import torch


def get_gpu_info():
    """Get current NVIDIA GPU utilization and memory usage."""
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used",
                "--format=csv,noheader,nounits"
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2
        )

        values = result.strip().splitlines()[0].split(",")

        return (
            float(values[0].strip()),
            float(values[1].strip())
        )

    except Exception:
        return None, None


def profile_task(task_fn, device="cpu", **kwargs):
    """Measure runtime, GPU utilization and memory usage."""

    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is not available.")

    process = psutil.Process()
    gpu_samples = []
    stop_sampling = threading.Event()
    sampler = None

    def sample_gpu():
        while not stop_sampling.is_set():
            utilization, _ = get_gpu_info()

            if utilization is not None:
                gpu_samples.append(utilization)

            stop_sampling.wait(0.1)

    if device == "cuda":
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

        sampler = threading.Thread(
            target=sample_gpu,
            daemon=True
        )
        sampler.start()

    try:
        start = time.perf_counter()
        runtime = task_fn(device=device, **kwargs)

        if device == "cuda":
            torch.cuda.synchronize()

    finally:
        elapsed = time.perf_counter() - start

        if device == "cuda":
            stop_sampling.set()
            sampler.join(timeout=3)

    if device == "cuda":
        gpu_util = (
            statistics.mean(gpu_samples)
            if gpu_samples else None
        )

        memory_mb = (
            torch.cuda.max_memory_allocated() / (1024 ** 2)
        )
    else:
        gpu_util = 0
        memory_mb = (
            process.memory_info().rss / (1024 ** 2)
        )

    return {
        "runtime_sec": float(runtime),
        "wall_time_sec": float(elapsed),
        "device": device,
        "gpu_util": gpu_util,
        "memory_mb": memory_mb
    }


def profile_network_task(task_fn, url=None):
    """Measure runtime and network throughput for a network task."""

    if url is None:
        runtime, network_mbps, total_bytes = task_fn()
    else:
        runtime, network_mbps, total_bytes = task_fn(url=url)

    return {
        "runtime_sec": float(runtime),
        "device": "cpu",
        "gpu_util": 0,
        "memory_mb": None,
        "network_mbps": float(network_mbps),
        "total_bytes": int(total_bytes)
    }


def check_hardware_counters():
    """Check whether Linux perf hardware counters are accessible."""
    try:
        result = subprocess.run(
            [
                "perf", "stat",
                "-e", "cycles,instructions,cache-misses",
                "true"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return (
                "perf counters are accessible; "
                "validate measurements before using them"
            )

        return "Hardware counters restricted or unavailable: " + (
            result.stderr.strip()[-250:]
        )

    except Exception as exc:
        return "Hardware counters unavailable: " + str(exc)
