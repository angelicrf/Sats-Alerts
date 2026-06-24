from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SatelliteState:
    altitude_km: float
    propellant_percent: float
    attitude_control_ok: bool
    propulsion_ok: bool
    days_in_safehold: int
    reaction_wheel_momentum_percent: float
    failed_maneuvers_last_30_days: int
    time_to_conjunction_minutes: int          # Time until closest approach
    miss_distance_km: float                   # Predicted closest approach distance
    object_is_active_satellite: bool          # True if the other object is a controllable satellite
    can_coordinated_maneuver: bool            # Whether coordination with the other object is possible
    ground_command_available: bool

class AvoidanceThresholds:
    HIGH_RISK_MISS_DISTANCE_KM = 5.0
    MEDIUM_RISK_MISS_DISTANCE_KM = 15.0
    CRITICAL_ALTITUDE_KM = 480
    MIN_PROPELLANT_FOR_CAM = 15
    MAX_SAFEHOLD_DAYS = 5
    MAX_FAILED_MANEUVERS = 2
    MOMENTUM_SATURATION = 90


def evaluate_collision_risk(state: SatelliteState) -> Dict[str, Any]:
    if state.miss_distance_km < AvoidanceThresholds.HIGH_RISK_MISS_DISTANCE_KM:
        risk_level = "High"
        recommended_action = "Immediate maneuver required"
    elif state.miss_distance_km < AvoidanceThresholds.MEDIUM_RISK_MISS_DISTANCE_KM:
        risk_level = "Medium"
        recommended_action = "Monitor closely and prepare maneuver"
    else:
        risk_level = "Low"
        recommended_action = "No action needed at this time"

    return {
        "risk_level": risk_level,
        "miss_distance_km": state.miss_distance_km,
        "time_to_conjunction_min": state.time_to_conjunction_minutes,
        "recommended_action": recommended_action
    }


def can_perform_active_maneuver(state: SatelliteState) -> Dict[str, Any]:
    """Check if the satellite is physically capable of performing a Collision Avoidance Maneuver (CAM)."""
    issues = []

    if not state.propulsion_ok:
        issues.append("Propulsion system is not operational")
    if state.propellant_percent < AvoidanceThresholds.MIN_PROPELLANT_FOR_CAM:
        issues.append(f"Insufficient propellant ({state.propellant_percent}%)")
    if not state.attitude_control_ok:
        issues.append("Attitude control is degraded")
    if state.reaction_wheel_momentum_percent >= AvoidanceThresholds.MOMENTUM_SATURATION:
        issues.append("Reaction wheels are saturated")
    if state.days_in_safehold > AvoidanceThresholds.MAX_SAFEHOLD_DAYS:
        issues.append(f"Stuck in Safehold for {state.days_in_safehold} days")
    if state.failed_maneuvers_last_30_days > AvoidanceThresholds.MAX_FAILED_MANEUVERS:
        issues.append("Recent history of failed maneuvers")

    capable = len(issues) == 0

    return {
        "strategy": "Active Collision Avoidance Maneuver (CAM)",
        "feasible": capable,
        "issues": issues,
        "reason": "Satellite is capable of performing a maneuver" if capable else " | ".join(issues)
    }


def passive_avoidance_option(state: SatelliteState) -> Dict[str, Any]:
    """Evaluate the option of doing nothing and letting the conjunction pass."""
    risk = evaluate_collision_risk(state)

    feasible = risk["risk_level"] == "Low" or (
        risk["risk_level"] == "Medium" and state.time_to_conjunction_minutes > 60
    )

    return {
        "strategy": "Passive Avoidance (Do Nothing)",
        "feasible": feasible,
        "reason": "Risk is low enough to accept" if feasible else "Risk level too high for passive approach",
        "risk_level": risk["risk_level"]
    }


def recommend_maneuver_direction(state: SatelliteState) -> Dict[str, Any]:
    """Decide whether to raise or lower the orbit for collision avoidance."""
    if state.altitude_km < AvoidanceThresholds.CRITICAL_ALTITUDE_KM:
        direction = "Raise Orbit"
        reason = "Altitude is already critically low — lowering would increase re-entry risk"
    else:
        # Prefer raising orbit in most cases (more energy efficient for LEO)
        direction = "Raise Orbit" if state.propellant_percent > 25 else "Lower Orbit"
        reason = "Standard preference is to raise orbit unless propellant is very low"

    return {
        "strategy": "Maneuver Direction Selection",
        "recommended_direction": direction,
        "reason": reason,
        "current_altitude": state.altitude_km
    }


def coordinated_maneuver_option(state: SatelliteState) -> Dict[str, Any]:
    if not state.object_is_active_satellite:
        return {
            "strategy": "Coordinated Maneuver",
            "feasible": False,
            "reason": "Other object is not an active satellite (likely debris)"
        }

    feasible = (
        state.can_coordinated_maneuver and 
        state.object_is_active_satellite and
        state.time_to_conjunction_minutes > 30
    )

    return {
        "strategy": "Coordinated Maneuver with Other Satellite",
        "feasible": feasible,
        "reason": "Coordination possible" if feasible else "Coordination not feasible or not enough time",
        "requires_ground_coordination": True
    }


def deorbit_as_last_resort(state: SatelliteState) -> Dict[str, Any]:
    critical_issues = (
        not state.propulsion_ok or
        not state.attitude_control_ok or
        state.days_in_safehold > AvoidanceThresholds.MAX_SAFEHOLD_DAYS or
        state.altitude_km < AvoidanceThresholds.CRITICAL_ALTITUDE_KM
    )

    feasible = critical_issues and state.ground_command_available

    return {
        "strategy": "Deorbit as Last Resort",
        "feasible": feasible,
        "reason": "Satellite is unrecoverable and poses ongoing collision risk" if feasible else "Deorbit not justified at this time",
        "requires_ground_authorization": True
    }


def evaluate_maneuver_cost(state: SatelliteState) -> Dict[str, Any]:
    base_cost = 2.0  # rough percentage of propellant for a small CAM

    if state.altitude_km < 500:
        cost_multiplier = 1.5
    else:
        cost_multiplier = 1.0

    estimated_cost = base_cost * cost_multiplier

    return {
        "strategy": "Maneuver Cost Assessment",
        "estimated_propellant_cost_percent": round(estimated_cost, 2),
        "risk_of_maneuver": "Medium" if state.propellant_percent < 30 else "Low",
        "recommendation": "Avoid maneuver if possible" if estimated_cost > state.propellant_percent * 0.3 else "Maneuver cost acceptable"
    }


def decide_best_avoidance_strategy(state: SatelliteState) -> Dict[str, Any]:
    risk = evaluate_collision_risk(state)
    active_maneuver = can_perform_active_maneuver(state)
    passive = passive_avoidance_option(state)
    coordinated = coordinated_maneuver_option(state)
    deorbit = deorbit_as_last_resort(state)
    maneuver_cost = evaluate_maneuver_cost(state)
    direction = recommend_maneuver_direction(state)

    # Decision logic
    recommended_strategies = []

    if risk["risk_level"] == "Low":
        recommended_strategies.append("Passive Avoidance")

    elif active_maneuver["feasible"]:
        recommended_strategies.append("Active Collision Avoidance Maneuver (CAM)")
        recommended_strategies.append(direction["recommended_direction"])

        if coordinated["feasible"]:
            recommended_strategies.append("Coordinated Maneuver (Preferred if possible)")

    elif coordinated["feasible"]:
        recommended_strategies.append("Coordinated Maneuver")

    elif deorbit["feasible"]:
        recommended_strategies.append("Deorbit as Last Resort")

    else:
        recommended_strategies.append("No viable avoidance strategy available - High risk situation")

    return {
        "collision_risk": risk,
        "available_strategies": {
            "active_maneuver": active_maneuver,
            "passive_avoidance": passive,
            "coordinated_maneuver": coordinated,
            "deorbit_last_resort": deorbit,
            "maneuver_cost": maneuver_cost,
            "maneuver_direction": direction
        },
        "recommended_strategies": recommended_strategies,
        "primary_recommendation": recommended_strategies[0] if recommended_strategies else "No recommendation"
    }

if __name__ == "__main__":
    print("=== Collision Avoidance Strategy Evaluation ===\n")

    # Example 1: Healthy satellite with high-risk conjunction
    sat1 = SatelliteState(
        altitude_km=545,
        propellant_percent=45,
        attitude_control_ok=True,
        propulsion_ok=True,
        days_in_safehold=0,
        reaction_wheel_momentum_percent=35,
        failed_maneuvers_last_30_days=0,
        time_to_conjunction_minutes=45,
        miss_distance_km=3.2,
        object_is_active_satellite=True,
        can_coordinated_maneuver=True,
        ground_command_available=True
    )

    result1 = decide_best_avoidance_strategy(sat1)
    print("Example 1: Healthy Satellite - High Risk Conjunction")
    print(f"Primary Recommendation: {result1['primary_recommendation']}")
    print(f"Risk Level: {result1['collision_risk']['risk_level']}")
    print("Recommended Strategies:", result1['recommended_strategies'])
    print()

    # Example 2: Degraded satellite (propulsion + attitude issues)
    sat2 = SatelliteState(
        altitude_km=492,
        propellant_percent=9,
        attitude_control_ok=False,
        propulsion_ok=False,
        days_in_safehold=9,
        reaction_wheel_momentum_percent=97,
        failed_maneuvers_last_30_days=4,
        time_to_conjunction_minutes=28,
        miss_distance_km=4.1,
        object_is_active_satellite=False,
        can_coordinated_maneuver=False,
        ground_command_available=True
    )

    result2 = decide_best_avoidance_strategy(sat2)
    print("Example 2: Severely Degraded Satellite")
    print(f"Primary Recommendation: {result2['primary_recommendation']}")
    print("Recommended Strategies:", result2['recommended_strategies'])