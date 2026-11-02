# AI-Based Adaptive Traffic Management System

## Project Overview
This project uses Artificial Intelligence and traffic simulation to analyze traffic congestion and improve traffic signal timing.

It compares three traffic signal control approaches:
- Fixed-Time Traffic Signal Control
- Adaptive V2 Traffic Signal Control
- PPO (Proximal Policy Optimization) Based Traffic Signal Control

The objective is to reduce vehicle waiting time, traffic congestion, and CO₂ emissions while improving traffic flow.

## Key Features
- Vehicle detection using YOLO11.
- Vehicle tracking using ByteTrack.
- Traffic queue analysis using road zones.
- SUMO-based traffic simulation.
- Adaptive traffic signal control.
- PPO-based traffic signal optimization.
- CO₂ emission comparison.
- Streamlit dashboard for result visualization.
- Camera-based traffic analysis using recorded video.

## Technologies Used
- Python
- YOLO11
- ByteTrack
- OpenCV
- SUMO
- TraCI
- Stable-Baselines3 / PPO
- Streamlit
- Pandas
- Matplotlib

## Project Results

Simulation comparison using 450 vehicles:

| Metric | Fixed-Time | Adaptive V2 | PPO |
|---|---:|---:|---:|
| Speed (m/s) | 5.46 | 5.89 | 6.02 |
| Duration (s) | 129.49 | 119.02 | 122.40 |
| Waiting Time (s) | 48.16 | 42.54 | 47.90 |
| Time Loss (s) | 84.41 | 73.96 | 77.33 |
| Depart Delay (s) | 74.32 | 75.90 | 72.86 |

### CO₂ Emission Comparison

| System | CO₂ Emissions (kg) | Reduction vs Fixed-Time |
|---|---:|---:|
| Fixed-Time | 113.32 | 0% |
| Adaptive V2 | 105.92 | 6.53% |
| PPO | 107.81 | 4.86% |

**Observation:** Adaptive V2 achieved the lowest waiting time, duration, time loss, and CO₂ emissions. PPO achieved the highest average speed and lowest departure delay.

## Main Project Files
- `sumo_ppo_env.py` – PPO traffic environment.
- `train_ppo.py` – PPO training script.
- `test_ppo.py` – PPO testing script.
- `traci_test.py` – TraCI testing.
- `traffic.net.xml` – SUMO road network.
- `traffic.rou.xml` – Traffic routes.
- `traffic_signal.net.xml` – Traffic signal network.
- `traffic_tls.net.xml` – Traffic light configuration.
- `yolo11n.pt` – YOLO11 model weights.
- `results/` – Simulation results, CSV files, and graphs.
- `detection/` – Vehicle detection and queue analysis scripts.
- `pages/` – Streamlit dashboard pages.

## How to Run

### 1. Activate the virtual environment
```powershell
.\ppo_env\Scripts\Activate.ps1
```

### 2. Run the dashboard
```powershell
streamlit run dashboard.py --server.port 8502
```

Open in your browser:
`http://localhost:8502`

### 3. Run PPO testing
```powershell
python test_ppo.py
```

### 4. Run camera queue analysis
Open the Camera Queue Analysis page from the Streamlit dashboard.

## Important Note
Camera analysis currently uses a recorded traffic video. SUMO simulation and recorded-video analysis are separate parts of the project.

## Conclusion
The project demonstrates how computer vision, traffic simulation, adaptive signal control, and reinforcement learning can support smarter traffic management and help reduce traffic-related emissions.