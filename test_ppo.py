
import csv
import os

from stable_baselines3 import PPO
from sumo_ppo_env import SumoTrafficEnv


def main():

    model = PPO.load("models/ppo_traffic_agent.zip")

    env = SumoTrafficEnv(simulation_time=1200)

    records = []

    try:

        obs, info = env.reset()

        total_reward = 0
        decisions = 0

        while True:

            action, _ = model.predict(
                obs,
                deterministic=True
            )

            obs, reward, terminated, truncated, info = env.step(action)

            total_reward += reward
            decisions += 1

            records.append({

                "Decision": decisions,
                "Green_Time": info["green_time"],
                "Average_Queue": info["average_queue"],
                "Average_Waiting": info["average_waiting"],
                "Reward": round(reward, 2)

            })

            print(
                f"Decision: {decisions} | "
                f"Green: {info['green_time']} sec | "
                f"Queue: {info['average_queue']} | "
                f"Waiting: {info['average_waiting']}"
            )

            if terminated or truncated:
                break

        os.makedirs("results", exist_ok=True)

        with open(
            "results/ppo_results.csv",
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=records[0].keys()
            )

            writer.writeheader()
            writer.writerows(records)

        avg_queue = sum(
            r["Average_Queue"] for r in records
        ) / len(records)

        avg_waiting = sum(
            r["Average_Waiting"] for r in records
        ) / len(records)

        print("\n========== PPO SUMMARY ==========")

        print("Total decisions:", decisions)

        print("Total reward:", round(total_reward, 2))

        print("Average queue:", round(avg_queue, 2))

        print("Average waiting:", round(avg_waiting, 2))

        print("Saved: results/ppo_results.csv")

    finally:

        env.close()


if __name__ == "__main__":
    main()
