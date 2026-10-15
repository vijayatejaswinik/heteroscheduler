import pandas as pd
from scheduler import classify_task_network_aware

df = pd.read_csv("simulated_metrics.csv")

print(f"{'task_id':20s} {'label':22s} {'predicted':22s} {'match':7s}")
print("-" * 75)

match_count = 0
for _, row in df.iterrows():
    predicted = classify_task_network_aware(
        row["ipc"], row["cm_cr"], row["llc_m_llc_l"], row["network_mbps"]
    )
    match = "YES" if predicted == row["classification"] else "NO"
    if match == "YES":
        match_count += 1
    print(f"{row['task_id']:20s} {row['classification']:22s} "
          f"{predicted:22s} {match:7s}")

print()
print(f"Match: {match_count}/{len(df)}")

