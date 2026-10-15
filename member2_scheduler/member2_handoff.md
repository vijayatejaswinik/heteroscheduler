# Member 2 Handoff Document

## Files
- `scheduler.py` — Server, Task, place_task, classify_task_network_aware
- `monitor.py` — check_contention, check_network_congestion, log_contention
- `baselines.py` — place_all_cpu, place_all_gpu, place_random
- `test_scheduler.py` — 11 tests
- `contention_log.json` — logged events

## Classes
Server fields: id, type, gpu_util, gpu_mem, cpu_util, mem_bw, llc_miss, tasks, overloaded, bandwidth_mbps, current_bandwidth_mbps, latency_ms, network_congested
Server method: update_network(measured_mbps, measured_latency_ms=None)

Task fields: id, classification, runtime_sec, memory_mb, state_size_mb, network_mbps, assigned_server

## Functions
- place_task(task, servers)
- calculate_network_cost(task, server)
- classify_task_network_aware(ipc, cm_cr, llc_m_llc_l, network_mbps)

## Contention Thresholds
- GPU: gpu_util > 80 OR gpu_mem > 80
- CPU: mem_bw > 80 OR llc_miss > 40 OR cpu_util > 80
- Network: current_bandwidth < 30% nominal

## Output Format
{"timestamp":1234567890,"server":"gpu1","metric":"gpu_util","value":85,"status":"overloaded","task_id":"task_3"}

## Import for main.py
from scheduler import Server, Task, place_task
from monitor import check_contention, log_contention
from baselines import place_all_cpu, place_all_gpu, place_random
