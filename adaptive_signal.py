
import traci
import sumolib
import csv
import os

sumo_binary = sumolib.checkBinary("sumo")

os.makedirs("results", exist_ok=True)

sumo_cmd = [
    sumo_binary,
    "-n", "traffic_signal.net.xml",
    "-r", "traffic.rou.xml",
    "--end", "1200",
    "--no-step-log", "true",
    "--duration-log.statistics", "true",
    "--emission-output", "results/adaptive_emissions.xml",
    "--time-to-teleport", "-1"
]

TLS_ID = "B1"

phase_roads = {
    0: ["B2B1", "B0B1"],
    2: ["C1B1", "A1B1"]
}


def get_traffic_data(roads):

    total_queue = 0
    waiting_times = []

    for road in roads:

        queue = traci.edge.getLastStepHaltingNumber(road)
        total_queue += queue

        vehicle_ids = traci.edge.getLastStepVehicleIDs(road)

        for vehicle_id in vehicle_ids:

            waiting = traci.vehicle.getWaitingTime(vehicle_id)
            waiting_times.append(waiting)

    if waiting_times:
        avg_waiting = sum(waiting_times) / len(waiting_times)
    else:
        avg_waiting = 0

    return total_queue, avg_waiting


def calculate_green(queue, avg_waiting):

    green_time = 20 + (1.5 * queue) + (0.15 * avg_waiting)

    green_time = max(20, min(60, green_time))

    return round(green_time, 2)


csv_file = open(
    "results/adaptive_results.csv",
    "w",
    newline=""
)

writer = csv.writer(csv_file)

writer.writerow([
    "Simulation_Time",
    "Phase",
    "Road",
    "Queue",
    "Average_Waiting_Time",
    "Adaptive_Green_Time"
])

try:

    traci.start(sumo_cmd)

    print("\n======================================")
    print("   ADAPTIVE TRAFFIC SIGNAL SYSTEM V2")
    print("   Queue + Waiting Time Optimization")
    print("   CO2 Emission Monitoring: ON")
    print("   Simulation: 1200 Seconds")
    print("======================================\n")

    previous_phase = -1

    while (
        traci.simulation.getMinExpectedNumber() > 0
        and traci.simulation.getTime() < 1200
    ):

        phase = traci.trafficlight.getPhase(TLS_ID)

        if phase != previous_phase:

            if phase in phase_roads:

                roads = phase_roads[phase]

                queue, avg_waiting = get_traffic_data(roads)

                green_time = calculate_green(
                    queue,
                    avg_waiting
                )

                traci.trafficlight.setPhaseDuration(
                    TLS_ID,
                    green_time
                )

                current_time = traci.simulation.getTime()

                writer.writerow([
                    current_time,
                    phase,
                    ",".join(roads),
                    queue,
                    round(avg_waiting, 2),
                    green_time
                ])

                print(
                    f"Time: {current_time:.0f}s | "
                    f"Phase: {phase} | "
                    f"Queue: {queue} | "
                    f"Avg Waiting: {avg_waiting:.2f}s | "
                    f"Green: {green_time}s"
                )

            previous_phase = phase

        traci.simulationStep()

    print("\nAdaptive Traffic Signal V2 Completed!")

finally:

    if traci.isLoaded():
        traci.close()

    csv_file.close()

print("\nAdaptive Results Generated!")
print("CO2 data saved: results/adaptive_emissions.xml")
