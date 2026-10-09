# Member 2 Report Section

## Scheduler Design
- Compute-intensive -> GPU servers
- Memory-intensive -> CPU servers
- Choose server with minimum network cost

## Contention Detection
- GPU overloaded: gpu_util > 80% OR gpu_mem > 80%
- CPU overloaded: mem_bw > 80% OR llc_miss > 40% OR cpu_util > 80%

## Baselines
- All-CPU, All-GPU, Random

## Network Cost Formula
network_cost = (memory_mb * 8) / bandwidth_mbps + latency_ms / 1000

## Tests
All 8 tests pass.

## Viva Topics
- Why compute-intensive on GPU?
- Why memory-intensive on CPU?
- Network cost formula
- Contention thresholds
- Baselines
