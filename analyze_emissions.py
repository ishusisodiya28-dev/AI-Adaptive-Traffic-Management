
import os
import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

files = {
    "Fixed-Time": "fixed_emissions.xml",
    "Adaptive V2": "adaptive_emissions.xml",
    "PPO": "ppo_emissions.xml"
}


def calculate_co2(file_path):

    total_co2_mg = 0.0
    vehicle_ids = set()
    previous_time = None
    step_lengths = []

    for event, element in ET.iterparse(file_path, events=("end",)):

        if element.tag == "timestep":

            current_time = float(element.get("time", 0))

            if previous_time is not None:
                step_lengths.append(current_time - previous_time)

            previous_time = current_time

            for vehicle in element.findall("vehicle"):

                co2 = float(vehicle.get("CO2", 0))

                total_co2_mg += co2
                vehicle_ids.add(vehicle.get("id"))

            element.clear()

    if not step_lengths:
        raise ValueError("Could not determine simulation time step.")

    step_length = sum(step_lengths) / len(step_lengths)

    # SUMO CO2 rate is mg/second.
    # Convert integrated emission into kilograms.
    total_co2_kg = (
        total_co2_mg * step_length / 1_000_000
    )

    return total_co2_kg, len(vehicle_ids), step_length


results = {}

print("\n====================================")
print("     CO2 EMISSION ANALYSIS")
print("====================================\n")

for system, filename in files.items():

    file_path = os.path.join(RESULTS_DIR, filename)

    if not os.path.exists(file_path):
        print("Missing file:", file_path)
        continue

    co2, vehicles, step = calculate_co2(file_path)

    results[system] = {
        "CO2_kg": co2,
        "Vehicles": vehicles,
        "Step_Length": step
    }

    print(f"{system}:")
    print(f"  Total CO2: {co2:.3f} kg")
    print(f"  Vehicles: {vehicles}")
    print(f"  Step Length: {step:.2f} seconds")
    print()


if len(results) == 3:

    baseline = results["Fixed-Time"]["CO2_kg"]

    for system in ["Adaptive V2", "PPO"]:

        co2 = results[system]["CO2_kg"]

        if baseline > 0:
            reduction = (
                (baseline - co2) / baseline
            ) * 100
        else:
            reduction = 0

        results[system]["Reduction_Percent"] = reduction

        print(
            f"{system} CO2 change vs Fixed-Time: "
            f"{reduction:.2f}%"
        )

    # Save CSV report
    with open(
        os.path.join(RESULTS_DIR, "co2_comparison.csv"),
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "System",
            "Total_CO2_kg",
            "Vehicles",
            "Reduction_vs_Fixed_Percent"
        ])

        writer.writerow([
            "Fixed-Time",
            results["Fixed-Time"]["CO2_kg"],
            results["Fixed-Time"]["Vehicles"],
            0
        ])

        for system in ["Adaptive V2", "PPO"]:

            writer.writerow([
                system,
                results[system]["CO2_kg"],
                results[system]["Vehicles"],
                results[system]["Reduction_Percent"]
            ])

    # Generate CO2 comparison graph
    systems = list(results.keys())

    values = [
        results[system]["CO2_kg"]
        for system in systems
    ]

    plt.figure(figsize=(9, 5))

    bars = plt.bar(systems, values)

    plt.title("CO2 Emission Comparison")
    plt.xlabel("Traffic Signal System")
    plt.ylabel("Estimated CO2 Emission (kg)")

    plt.bar_label(bars, fmt="%.3f", padding=4)

    plt.tight_layout()

    plt.savefig(
        os.path.join(RESULTS_DIR, "co2_comparison.png"),
        dpi=300
    )

    plt.close()

    print("\nCO2 analysis completed successfully!")
    print("Saved: results/co2_comparison.csv")
    print("Saved: results/co2_comparison.png")

else:
    print("\nAll three emission files are required for comparison.")
