
import traci
import sumolib

# ---------------- CONFIGURATION ----------------

NETWORK = "traffic_signal.net.xml"
ROUTES = "traffic.rou.xml"
TLS_ID = "B1"

END_TIME = 600
STEP_LENGTH = 1.0
SEED = 42

PHASE_ROADS = {
    0: ["B2B1"],
    2: ["C1B1"]
}

ALL_ROADS = ["B2B1", "C1B1", "A1B1", "B0B1"]


# ---------------- ADAPTIVE CONTROL ----------------

def calculate_green(queue):
    return min(60, max(15, 15 + 2 * queue))


# ---------------- SIMULATION ----------------

def run_test(method):

    binary = sumolib.checkBinary("sumo")

    command = [
        binary,
        "-n", NETWORK,
        "-r", ROUTES,
        "--seed", str(SEED),
        "--end", str(END_TIME),
        "--step-length", str(STEP_LENGTH),
        "--no-step-log", "true"
    ]

    print(f"\nStarting {method} simulation...")

    traci.start(command)

    waiting = 0.0
    time_loss = 0.0
    co2 = 0.0

    speed_sum = 0.0
    speed_samples = 0

    arrived_count = 0
    departed_count = 0

    previous_loss = {}
    previous_phase = -1

    try:

        while traci.simulation.getMinExpectedNumber() > 0:

            traci.simulationStep()

            # Cumulative vehicle counts
            arrived_count += traci.simulation.getArrivedNumber()
            departed_count += traci.simulation.getDepartedNumber()

            vehicles = traci.vehicle.getIDList()
            phase = traci.trafficlight.getPhase(TLS_ID)

            # Queue on all incoming roads
            total_queue = sum(
                traci.edge.getLastStepHaltingNumber(road)
                for road in ALL_ROADS
            )

            # Adaptive signal control
            if method == "Adaptive" and phase != previous_phase:

                if phase in PHASE_ROADS:

                    active_queue = sum(
                        traci.edge.getLastStepHaltingNumber(road)
                        for road in PHASE_ROADS[phase]
                    )

                    green_time = calculate_green(active_queue)

                    traci.trafficlight.setPhaseDuration(
                        TLS_ID, green_time
                    )

                previous_phase = phase

            # Waiting time: vehicle-seconds
            waiting += total_queue * STEP_LENGTH

            # Time loss: increase in cumulative time loss
            current_loss = {}

            for vehicle in vehicles:

                loss = traci.vehicle.getTimeLoss(vehicle)

                old_loss = previous_loss.get(vehicle, loss)

                time_loss += max(0.0, loss - old_loss)

                current_loss[vehicle] = loss

                speed_sum += traci.vehicle.getSpeed(vehicle)
                speed_samples += 1

            previous_loss = current_loss

            # CO2: SUMO emission rate in mg/s
            emission_mg = sum(
                traci.edge.getCO2Emission(edge)
                for edge in traci.edge.getIDList()
            )

            co2 += (
                emission_mg * STEP_LENGTH / 1_000_000
            )

            # Progress
            sim_time = traci.simulation.getTime()

            if int(sim_time) % 100 == 0:
                print(
                    f"{method}: {sim_time:.0f}s | "
                    f"Departed: {departed_count} | "
                    f"Arrived: {arrived_count} | "
                    f"Active: {len(vehicles)}"
                )

        result = {
            "method": method,
            "departed": departed_count,
            "arrived": arrived_count,
            "waiting": waiting,
            "time_loss": time_loss,
            "speed": (
                speed_sum / speed_samples
                if speed_samples else 0
            ),
            "co2": co2
        }

        return result

    finally:
        traci.close()


# ---------------- COMPARISON ----------------

def show_results(fixed, adaptive):

    print("\n" + "=" * 55)
    print("       TRAFFIC PERFORMANCE COMPARISON")
    print("=" * 55)

    for result in [fixed, adaptive]:

        print(f"\n{result['method']}")

        print("Departed Vehicles:", result["departed"])
        print("Arrived Vehicles:", result["arrived"])

        print(
            "Average Speed:",
            round(result["speed"], 2), "m/s"
        )

        print(
            "Waiting Time:",
            round(result["waiting"], 2), "vehicle-seconds"
        )

        print(
            "Time Loss:",
            round(result["time_loss"], 2), "seconds"
        )

        print(
            "CO2 Emissions:",
            round(result["co2"], 4), "kg"
        )

    # Percentage changes
    print("\n" + "=" * 55)
    print("              PERFORMANCE CHANGE")
    print("=" * 55)

    def improvement(old, new):
        if old == 0:
            return None
        return ((old - new) / old) * 100

    wait_change = improvement(
        fixed["waiting"], adaptive["waiting"]
    )

    loss_change = improvement(
        fixed["time_loss"], adaptive["time_loss"]
    )

    co2_change = improvement(
        fixed["co2"], adaptive["co2"]
    )

    if wait_change is not None:
        print(f"Waiting Time Improvement: {wait_change:.2f}%")

    if loss_change is not None:
        print(f"Time Loss Improvement: {loss_change:.2f}%")

    if co2_change is not None:
        print(f"CO2 Reduction: {co2_change:.2f}%")

    print("=" * 55)


# ---------------- MAIN ----------------

if __name__ == "__main__":

    fixed_result = run_test("Fixed-Time")

    adaptive_result = run_test("Adaptive")

    show_results(fixed_result, adaptive_result)
