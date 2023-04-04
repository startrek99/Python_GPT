# calculate the climb and decent trends for a glider task


import math

# define the task
start_altitude = 1700  # m
end_altitude = 1981  # m
difference_altitude = end_altitude - start_altitude

Task_in_kilometers = 158.9
desired_time = 68  # minutes
half_way_time = 34  # minutes

# calculate highest altitude
climb_rate = 1.2  # m/s
descent_rate = 1.2  # m/s
max_altitude = (climb_rate * half_way_time * 60) + difference_altitude  # m
print("max altitude: ", max_altitude, "m")
