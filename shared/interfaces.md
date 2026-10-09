# Interfaces Between Members

## Interface 1: Task Metrics (Member 1 -> Member 2, 4)

File: task_metrics.csv
Columns: task_id,classification,device,runtime_sec,gpu_util,memory_mb,ipc,cm_cr,llc_m_llc_l

## Interface 2: Network Data (Member 1 -> Member 2, 3)

File: network_measurements.csv
Columns: source,target,bandwidth_mbps,latency_ms

## Interface 3: Contention Event (Member 2 -> Member 3, 4)

File: contention_log.json
Format: {"timestamp":1234567890,"server":"gpu_server_1","metric":"gpu_util","value":85,"status":"overloaded","task_id":"task_3"}

## Interface 4: Migration Event (Member 3 -> Member 4)

File: migration_log.json
Format: {"task_id":"task_3","source":"gpu_server_1","target":"gpu_server_2","checkpoint_time":12.5,"network_time":8.3,"restore_time":4.2,"total_time":25.0,"success":true}
