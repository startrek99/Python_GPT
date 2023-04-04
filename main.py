# program to show how high in a thermal you can go before you have to leave the thermal to get the fastest task
# completion time

import matplotlib.pyplot as plt
import glider_functions

# constants
liftThermal = 5
Distance_Task = 158
# polar calculation for Ventus3-15 Glider
speed1 = 108  # kph
speed2 = 190  # kph
speed3 = 248  # kph

# sink at previous speeds
sink1 = -0.65  # m/s
sink2 = -1.45  # m/s
sink3 = -3.09  # m/s


lift = 5  # m/s
current_height = 1700  # m
current_speed = 132  # kph
current_time = 0  # s
current_distance = 0  # km

sink = glider_functions.sink_rate(current_speed)
height_needed = sink * (Distance_Task / current_speed) * 3600
height_needed = height_needed - current_height
thermal_time = height_needed / lift
thermal_time = abs(thermal_time / 60)
print("Thermal time is", thermal_time, "minutes")

Minutes_to_complete_task = (Distance_Task / current_speed) * 60 # without thermaling time
print (Minutes_to_complete_task)
Minutes_to_complete_task = Minutes_to_complete_task + thermal_time


print(Minutes_to_complete_task)

print("The Sink rate is ", sink, "m/s")
Seconds_left = (Minutes_to_complete_task - int(Minutes_to_complete_task)) * 60
print("Time to complete the task at the current speed is", int(Minutes_to_complete_task), "minutes and",
      int(Seconds_left), "seconds")
