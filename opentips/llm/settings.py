import os


def get_temperature(facility: str, default: float) -> float:
    env_var_name = f"OPENTIPS_{facility.upper()}_TEMPERATURE"
    temperature = os.environ.get(env_var_name)
    if temperature:
        return float(temperature)

    return default
