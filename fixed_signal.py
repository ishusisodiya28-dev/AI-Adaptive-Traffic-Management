
import traci
import sumolib
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
    "--emission-output", "results/fixed_emissions.xml",
    "--time-to-teleport", "-1"
]

TLS_ID = "B1"

try:
    traci.start(sumo_cmd)

    print("\n================================")
    print(" FIXED-TIME TRAFFIC SIGNAL")
    print(" Green: 42 seconds")
    print(" Yellow: 3 seconds")
    print(" Simulation: 1200 seconds")
    print(" CO2 Emission Monitoring: ON")
    print("================================\n")

    while (
        traci.simulation.getMinExpectedNumber() > 0
        and traci.simulation.getTime() < 1200
    ):
        traci.simulationStep()

    print("\nFixed-Time Simulation Completed!")

finally:
    if traci.isLoaded():
        traci.close()

print("\nFixed-Time Results Generated!")
print("CO2 data saved: results/fixed_emissions.xml")
