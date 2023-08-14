# -------------------------------------------------------------------------------
# Name:        glider Module
# Purpose:     Functions for glider calculations
#
# Author:      Peter
#
# Created:     02/02/2023
# Copyright:   (c) Peter 2023
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import glob
import statistics
from scipy.interpolate import interp1d
import numpy as np


def read_altitude_from_igc(file_path):
    altitudes = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('B'):
                altitude = int(line[30:35])
                altitudes.append(altitude)
    return altitudes


def calculate_optimal_thermal_height():
    highest_altitudes = []

    # Iterate through all .igc files in the current directory
    for file_path in glob.glob('*.igc'):
        altitudes = read_altitude_from_igc(file_path)
        sorted_altitudes = sorted(altitudes, reverse=True)
        top_10_percent = sorted_altitudes[:len(sorted_altitudes)//10]
        highest_altitudes.extend(top_10_percent)

    # Calculate the mean and standard deviation of the highest altitudes
    average_highest_altitude = statistics.mean(highest_altitudes)
    standard_deviation_highest_altitude = statistics.stdev(highest_altitudes)

    return average_highest_altitude, standard_deviation_highest_altitude


def calculate_current_ceiling(best_altitude, finish_height, distance_flown, task_length):
    adjusted_altitude = best_altitude - finish_height
    ceiling = adjusted_altitude * (1 - distance_flown / task_length) + finish_height
    return max(ceiling, finish_height)


def calculate_altitude_speed_relation(file_path="FLIGHT_RECORDS.txt"):
    altitude_data = []
    speed_data = []

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("File not found.")
        return None, None

    date_time_line = None
    altitude_line = None
    speed_line = None

    for i, line in enumerate(lines):
        line = line.strip()
        if "Date and Time:" in line:
            date_time_line = line
        elif "Maximum Altitude:" in line:
            altitude_line = line
        elif "Speed:" in line:
            speed_line = line
        if date_time_line and altitude_line and speed_line:
            try:
                altitude = float(altitude_line.split(":")[1].strip().split()[0])
                speed = float(speed_line.split(":")[1].strip().split()[0])
                altitude_data.append(altitude)
                speed_data.append(speed)
            except (ValueError, IndexError):
                print("Error processing data at line:", i + 1)
            date_time_line = None
            altitude_line = None
            speed_line = None

    if not altitude_data or not speed_data:
        print("No valid data found in the file.")
        return None, None

    fit_curve = np.polyfit(altitude_data, speed_data, 2)
    fit_function = np.poly1d(fit_curve)

    # Find the maximum point of the fitted curve
    max_altitude = -fit_curve[1] / (2 * fit_curve[0])
    mid_factor = fit_function(max_altitude)

    return mid_factor, max_altitude


def takes_speed_returns_sink_rate(speed, speeds, sink_rates):
    # Clamping the speed between 132 and 250
    speed = max(132, min(250, speed))
    coefficients = np.polyfit(speeds, sink_rates, 2)
    return np.polyval(coefficients, speed)


def sink_rate(speed, speeds, sink_rates):
    coefficients = np.polyfit(speeds, sink_rates, 2)
    return np.polyval(coefficients, speed)


def get_glider_data(selected_glider):
    glider_polar_data = {
        "EB29R": (147, 192, 245, -0.69, -1.19, -2.24),
        "Diana2": (144, 191, 228, -0.84, -1.48, -2.32),
        "Genesis2": (126, 176, 227, -0.83, -1.61, -3.15),
        "Antares18S": (146, 190, 239, -0.84, -1.45, -2.69),
        "JS3-15": (144, 191, 251, -0.81, -1.40, -2.82),
        "ASG29-18": (144, 190, 250, -0.82, -1.39, -2.79),
        "ASG29Es-18": (144, 190, 250, -0.82, -1.39, -2.79),
        "JS1-18": (144, 190, 250, -0.82, -1.39, -2.79),
        "Ventus3-15": (132, 190, 248, -0.73, -1.45, -2.85),
        "LS8neo": (123, 168, 213, -0.80, -1.26, -2.32),
        "LS4a": (122, 168, 214, -0.85, -1.40, -2.63),
    }

    if selected_glider in glider_polar_data:
        speeds = glider_polar_data[selected_glider][:3]
        sink_rates = glider_polar_data[selected_glider][3:]
        return speeds, sink_rates
    else:
        return None


def get_best_speed(sink_rate, speeds, sink_rates):
    sink_rate = abs(sink_rate)
    sink_rate = sink_rate * -1  # make sink rate negative

    # Clamp the sink_rate to the range of -0.73 to -2.85
    sink_rate = max(-2.85, min(sink_rate, -0.73))

    # Create a linear interpolation function based on the given speeds and sink rates
    interpolate_speed = interp1d(
        sink_rates, speeds, kind="linear", fill_value="extrapolate"
    )

    # Use the interpolation function to get the speed for the given sink rate
    best_speed = interpolate_speed(sink_rate)
    return best_speed


def recalculate_parameters(desired_average_speed, TASK_DISTANCE, speeds, sink_rates):
    global climb_rate, max_altitude
    START_ALTITUDE = 1200
    sink = sink_rate(desired_average_speed, speeds, sink_rates)
    climb_rate = abs(sink)

    desired_time = TASK_DISTANCE / desired_average_speed * 60
    total_time_decimal_minutes = desired_time
    total_time_in_seconds = total_time_decimal_minutes * 60
    max_altitude = abs(sink) * (total_time_in_seconds / 2) + START_ALTITUDE

    return climb_rate, max_altitude


def projected_speed(task_climb_achieved, speeds, sink_rates):
    START_ALTITUDE = 1200
    FINISH_ALTITUDE = 580
    TASK_DISTANCE = 151.7

    selected_glider = "Ventus3-15"
    # Assuming get_glider_data(selected_glider) returns valid data for speeds and sink_rates
    glider_name, speeds, sink_rates = get_glider_data(selected_glider)

    # Find the nearest matching speed for the provided climb rate
    best_speed = None
    min_difference = float("inf")

    for speed_kph in np.clip(np.arange(min(speeds), max(speeds) + 1, 1), 120, 250):
        coefficients = np.polyfit(speeds, sink_rates, 2)
        sink_rate = np.polyval(coefficients, speed_kph)
        climb_rate = -sink_rate

        difference = abs(climb_rate - task_climb_achieved)

        if difference < min_difference:
            min_difference = difference
            best_speed = speed_kph

    return best_speed


def return_climb_achieved(
    TASK_SPEED_KPH, START_ALTITUDE, FINISH_ALTITUDE, speeds, sink_rates
):
    # Clamp TASK_SPEED_KPH to the range [144, 250]
    TASK_SPEED_KPH = max(144, min(TASK_SPEED_KPH, 250))

    TASK_DISTANCE = 151.7
    TASK_TIME_SECONDS = TASK_DISTANCE / TASK_SPEED_KPH * 3600

    SINK_RATE = sink_rate(TASK_SPEED_KPH, speeds, sink_rates)
    CLIMB_RATE = -SINK_RATE

    return CLIMB_RATE


def calculate_efficiency_altitude(halfway_altitude, distance_to_complete_task):
    distance_to_complete_task = 152.1
    START_ALTITUDE = 1200
    FINISH_ALTITUDE = 580
    TASK_SPEED_KPH = 188

    TASK_TIME_SECONDS = distance_to_complete_task / TASK_SPEED_KPH * 3600

    # get the glider data and calculate sink rate and climb rate
    selected_glider = "Ventus3-15"
    glider_name, speeds, sink_rates = get_glider_data(selected_glider)
    SINK_RATE = sink_rate(TASK_SPEED_KPH, speeds, sink_rates)

    efficiency = halfway_altitude / TASK_SPEED_KPH

    return efficiency


def efficiency_at_speed(target_speed):
    """
    Calculate the efficiency of a glider at a given speed.

    Parameters:
    target_speed (float): The target speed in kph.

    Returns:
    float: The calculated efficiency of the glider at the target speed.
    """
    speeds = [
        120,
        125,
        130,
        135,
        140,
        145,
        150,
        155,
        160,
        165,
        170,
        175,
        180,
        185,
        190,
        195,
        200,
        205,
        210,
        215,
        220,
        225,
        230,
        235,
        240,
        245,
        250,
    ]
    sink_rates = [
        -0.66,
        -0.68,
        -0.71,
        -0.75,
        -0.79,
        -0.83,
        -0.88,
        -0.93,
        -0.99,
        -1.05,
        -1.12,
        -1.20,
        -1.28,
        -1.36,
        -1.45,
        -1.54,
        -1.64,
        -1.75,
        -1.86,
        -1.97,
        -2.09,
        -2.21,
        -2.34,
        -2.48,
        -2.62,
        -2.76,
        -2.91,
    ]
    lift_thermals = 1.70

    # Clamp target speed to the nearest bound if outside the speeds range
    target_speed = max(min(target_speed, speeds[-1]), speeds[0])

    efficiencies = [
        (lift_thermals - sink_rate) / (speed * 1000 / 3600)
        for sink_rate, speed in zip(sink_rates, speeds)
    ]
    f = interpolate.interp1d(speeds, efficiencies, kind="cubic")

    return f(target_speed)


def condor_to_lat_lon(x, y):
    """
    Convert Condor coordinates to latitude and longitude.

    Parameters:
    x, y (float): The Condor coordinates.

    Returns:
    tuple: A tuple containing the latitude and longitude.
    """
    # Reference points and scaling factors
    ref_lat_timmersdorf = 47.37897542739968
    ref_lon_timmersdorf = 14.971524067507714
    ref_lat_zell_am_see = 47.30245447811891
    ref_lon_zell_am_see = 12.793082637667112
    condor_x_timmersdorf = 109713.3671875
    condor_y_timmersdorf = 478069.25
    condor_x_zell_am_see = 273274.8125
    condor_y_zell_am_see = 457956.96875

    scale_lat = (ref_lat_timmersdorf - ref_lat_zell_am_see) / (
        condor_y_timmersdorf - condor_y_zell_am_see
    )
    scale_lon = (ref_lon_timmersdorf - ref_lon_zell_am_see) / (
        condor_x_timmersdorf - condor_x_zell_am_see
    )

    # Calculate latitude and longitude
    lat = ref_lat_timmersdorf + (y - condor_y_timmersdorf) * scale_lat
    lon = ref_lon_timmersdorf + (x - condor_x_timmersdorf) * scale_lon

    return lat, lon


def true_speed(speed, sink, thermal_strength):
    """
    Calculate the true speed of a glider given its speed, sink rate, and thermal strength.

    Parameters:
    speed (float): The speed of the glider in kph.
    sink (float): The sink rate of the glider in m/s.
    thermal_strength (float): The strength of the thermals.

    Returns:
    int: The true speed of the glider in kph.
    """
    # Calculate the distance traveled in 1 second at the current airspeed
    distance = speed * 1000 / 3600

    # Calculate the time taken to recover the altitude lost in the thermal
    time_to_recover_altitude = abs(sink / thermal_strength)

    # Calculate the true speed in kph
    true_speed_kph = int(round(distance / (1 + time_to_recover_altitude) * 3.6))

    return true_speed_kph


def task_calculator(TASK_DISTANCE, TASK_SPEED_KPH, FINISH_ALTITUDE, START_ALTITUDE):
    """
    Calculate the maximum altitude and speed of a glider during a task.

    Parameters:
    TASK_DISTANCE (float): The distance of the task in kilometers.
    TASK_SPEED_KPH (float): The speed of the glider in kph.
    Interception_alt (float): The altitude at the finish in meters.
    START_ALTITUDE (float): The starting altitude in meters.

    Returns:
    tuple: A tuple containing the maximum altitude and task speed.
    """
    TASK_TIME_SECONDS = TASK_DISTANCE / TASK_SPEED_KPH * 3600
    SINK_RATE = sink_rate(TASK_SPEED_KPH)
    CLIMB_RATE = -SINK_RATE
    print(TASK_TIME_SECONDS / 60, "Full task minutes")
    print(SINK_RATE, "sink rate")
    print(CLIMB_RATE, "climb rate")

    # create a list of times in seconds
    time = np.arange(0, TASK_TIME_SECONDS + 1, 1)
    time = time[:-1]

    # create a list of altitudes in meters
    altitude = [START_ALTITUDE]
    for i in time[:-1]:
        # first half of the task is climbing, so it's the climb rate.
        if i < TASK_TIME_SECONDS / 2:
            altitude.append(altitude[-1] + CLIMB_RATE)
        # second half of the task is descending to halfway point, then level off to finish altitude.
        else:
            time_remaining = TASK_TIME_SECONDS - i
            if altitude[-1] > FINISH_ALTITUDE:
                altitude.append(altitude[-1] + SINK_RATE)
            else:
                altitude.append(FINISH_ALTITUDE)

    # plot the change in altitude of the glider over the task distance
    # the y-axis should be the altitude in meters. The x-axis should be time in minutes.
    TASK_SPEED_MPS = TASK_SPEED_KPH * 1000 / 3600
    MAX_ALTITUDE = max(altitude)
    print("Maximum altitude:", MAX_ALTITUDE, "m")

    return MAX_ALTITUDE, TASK_SPEED_KPH
