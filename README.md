# Satellite Alert Simulator

This project simulates and triggers realistic satellite alerts based on various operational circumstances. It is designed to help understand how different satellite health conditions, orbital parameters, and failure modes can lead to critical alerts in a LEO constellation.

## Project Goal

The main objective of this project is to model **satellite alert triggering logic** based on real-world operational conditions. Instead of hardcoding alerts, the system evaluates multiple parameters (altitude, propulsion health, attitude control, safehold duration, maneuver success rate, etc.) to determine when specific alerts should be raised.

This allows for:
- Better understanding of satellite anomaly detection
- Simulation of collision avoidance and deorbit decision-making
- Testing of operational scenarios without using real satellite data
- Educational and engineering analysis of satellite health monitoring

## New File Added

- **`simulate_alerts.py`**  
  Core simulation script that evaluates satellite state and determines which alerts should be triggered.  
  Currently includes logic for:
  - `DEORBIT_AUTHORIZED_ALERT`
  - Safehold-related alerts (`satfc1 long_duration_safehold`)
  - Attitude control alerts (`satfc1 uncontrollable_alarm`, `satfc1 momentum_saturated_alarm`)
  - Propulsion and power degradation alerts

- **`Collision_avoidance.py`**
  Collision Avoidance Strategies Simulator
  This script simulates different methods a satellite can use to avoid collisions
  with other objects (satellites or debris) in Low Earth Orbit.
  Each avoidance alternative is implemented as a separate, detailed function.

## Supported Alerts

The simulator currently models the following alerts and the conditions that trigger them:

| Alert Name                          | Category              | Triggered When |
|-------------------------------------|-----------------------|----------------|
| `deorbit_authorized`                | Deorbit / Disposal    | Satellite is intentionally removed or becomes unrecoverable |
| `satfc1 long_duration_safehold`     | Flight Computer       | Satellite remains in Safehold for an extended period |
| `satfc1 uncontrollable_alarm`       | Attitude Control      | Loss of reliable attitude control |
| `satfc1 momentum_saturated_alarm`   | Attitude Control      | Reaction wheels reach maximum momentum |
| `prop1_degraded_p_tank_sensor`      | Propulsion            | Propellant tank sensor is unreliable |
| `lswitch1_failed`                   | Propulsion            | Critical latch switch failure |
| `sada1_failed`                      | Power                 | Solar array drive failure |
| `force_orbit_transfer_onstation`    | Maneuver Command      | Aggressive orbit change is commanded |
| `limit_max_burn_duration_to_10min`  | Propulsion Limit      | Burn duration is restricted due to system constraints |

## How Alerts Are Triggered

Alerts are not triggered by a single value. Instead, the simulator evaluates a combination of factors, including:

- Current altitude and altitude trend
- Propellant remaining
- Propulsion system health
- Attitude control status
- Time spent in Safehold
- Number of failed maneuvers
- Ground commands
- End-of-life status

The logic aims to reflect how real satellite operations teams assess whether a satellite should be deorbited or placed into a degraded operational state.

## Usage

Run the simulation script with different satellite states:

```bash
python simulate_alerts.py