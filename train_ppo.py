
import os

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from sumo_ppo_env import SumoTrafficEnv


def main():

    os.makedirs("models", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    print("\n====================================")
    print("   PPO TRAFFIC SIGNAL TRAINING")
    print("   4-Road Traffic Observation")
    print("====================================\n")

    env = SumoTrafficEnv(simulation_time=600)
    env = Monitor(env)

    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=0.0003,
        n_steps=256,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        device="cpu"
    )

    try:

        print("Training started...")

        model.learn(
            total_timesteps=10000,
            progress_bar=False
        )

        model.save("models/ppo_traffic_agent")

        print("\n====================================")
        print("PPO TRAINING COMPLETED!")
        print("Model saved successfully.")
        print("Location: models/ppo_traffic_agent.zip")
        print("====================================")

    finally:

        env.close()


if __name__ == "__main__":
    main()
