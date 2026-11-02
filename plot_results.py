
import os
import csv
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

systems = ["Fixed-Time", "Adaptive V2", "PPO"]

data = {
    "Speed (m/s)": [5.46, 5.89, 6.02],
    "Duration (s)": [129.49, 119.02, 122.40],
    "Waiting Time (s)": [48.16, 42.54, 47.90],
    "Time Loss (s)": [84.41, 73.96, 77.33],
    "Depart Delay (s)": [74.32, 75.90, 72.86]
}

for metric, values in data.items():

    plt.figure(figsize=(9, 5))

    bars = plt.bar(systems, values)

    plt.title(f"{metric} Comparison")
    plt.xlabel("Traffic Signal System")
    plt.ylabel(metric)

    plt.bar_label(bars, fmt="%.2f", padding=4)

    plt.tight_layout()

    filename = (
        metric.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
    )

    plt.savefig(
        f"results/{filename}_comparison.png",
        dpi=300
    )

    plt.close()

with open("results/system_comparison.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow(["Metric"] + systems)

    for metric, values in data.items():
        writer.writerow([metric] + values)

print("\nAll comparison graphs generated successfully!")

print("\nSaved inside results folder:")
print("1. speed_comparison.png")
print("2. duration_comparison.png")
print("3. waiting_time_comparison.png")
print("4. time_loss_comparison.png")
print("5. depart_delay_comparison.png")
print("6. system_comparison.csv")
