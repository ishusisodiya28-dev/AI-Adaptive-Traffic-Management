import traci
import sumolib

sumo_binary = sumolib.checkBinary("sumo-gui")

sumo_cmd = [
    sumo_binary,
    "-n", "traffic.net.xml",
    "-r", "traffic.rou.xml",
    "--start",
    "--quit-on-end"
]

traci.start(sumo_cmd)

print("Connected to SUMO!")

for step in range(100):
    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    print(
        "Step:", step,
        "| Vehicles:", len(vehicles)
    )

traci.close()
print("SUMO connection closed!")