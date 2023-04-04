# -------------------------------------------------------------------------------
# Name:        glider Module
# Purpose:     Calculate the sink rate for a glider given its speed
#
# Author:      Peter
#
# Created:     02/02/2023
# Copyright:   (c) Peter 2023
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import numpy as np


def sink_rate(speed):
    """
    Calculate the sink rate for a glider given its speed

    Parameters:
    speed (float): The speed of the glider in kph

    Returns:
    float: The sink rate of the glider in m/s
    """
    speeds = [108, 190, 256]
    sink_rates = [-0.66, -1.45, -3.09]

    coefficients = np.polyfit(speeds, sink_rates, 2)
    return np.polyval(coefficients, speed)


def True_speed(speed, sink, thermal_strength):
    # Calculate the distance traveled in 1 second at the current airspeed
    distance = speed * 1000 / 3600

    # Calculate the time taken to recover the altitude lost in the thermal
    time_to_recover_altitude = abs(sink / thermal_strength)

    # Calculate the true speed in kph
    true_speed_kph = int(round(distance / (1 + time_to_recover_altitude) * 3.6))

    return true_speed_kph


# Ts = True_speed(132, -0.73, 5)
# print(Ts)


if __name__ == '__main__':
    # Example usage of the sink_rate function
    sink_rate = sink_rate(151)
    print(sink_rate)  # Output: -0.89
