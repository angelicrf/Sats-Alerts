def check_deorbit_authorized(
    altitude_km: float,
    propellant_percent: float,
    attitude_control_ok: bool,
    propulsion_ok: bool,
    days_in_safehold: int,
    failed_maneuvers_last_30_days: int,
    ground_deorbit_command: bool,
    end_of_life_flag: bool
) -> dict:

    reasons = []
    trigger = False
    if ground_deorbit_command:
        trigger = True
        reasons.append("Ground explicitly authorized deorbit")

    # End of life / planned disposal
    if end_of_life_flag:
        trigger = True
        reasons.append("Satellite reached end of life")

    # Unrecoverable state (most common)
    if not attitude_control_ok and not propulsion_ok:
        trigger = True
        reasons.append("Lost both attitude control and propulsion capability")

    # Very low propellant + cannot maintain orbit
    if propellant_percent < 8 and altitude_km < 520:
        trigger = True
        reasons.append("Propellant critically low and altitude decaying")

    # Stuck in Safehold for too long + failed maneuvers
    if days_in_safehold >= 7 and failed_maneuvers_last_30_days >= 3:
        trigger = True
        reasons.append("Long duration in Safehold with repeated failed maneuvers")

    # Severe altitude decay with no recovery capability
    if altitude_km < 480 and not propulsion_ok:
        trigger = True
        reasons.append("Altitude critically low and no propulsion to recover")

    return {
        "deorbit_authorized": trigger,
        "reasons": reasons if reasons else ["No deorbit conditions met"]
    }

result1 = check_deorbit_authorized(
    altitude_km=505,
    propellant_percent=6,
    attitude_control_ok=False,
    propulsion_ok=False,
    days_in_safehold=12,
    failed_maneuvers_last_30_days=4,
    ground_deorbit_command=False,
    end_of_life_flag=False
)

print("Failed satellite:")
print(result1)
print()

result2 = check_deorbit_authorized(
    altitude_km=550,
    propellant_percent=65,
    attitude_control_ok=True,
    propulsion_ok=True,
    days_in_safehold=0,
    failed_maneuvers_last_30_days=0,
    ground_deorbit_command=False,
    end_of_life_flag=False
)

print("Healthy satellite:")
print(result2)
print()

result3 = check_deorbit_authorized(
    altitude_km=545,
    propellant_percent=40,
    attitude_control_ok=True,
    propulsion_ok=True,
    days_in_safehold=0,
    failed_maneuvers_last_30_days=0,
    ground_deorbit_command=True,
    end_of_life_flag=True
)

print("Planned deorbit:")
print(result3)
