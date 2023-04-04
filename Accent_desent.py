import matplotlib.pyplot as plt
import numpy as np

# this is a gliders climb and descends for a total of 60 minutes
# the glider ascends at 1.3 m/s and descends at 1.3 m/s
# the glider starts at 0 m and ends at 0 m

# calculate maximum altitude
max_altitude = 1.3 * 60 * 30 / 2

print(max_altitude)


# calculate the time it takes to reach maximum altitude
time_to_max_altitude = 30

# calculate the time it takes to descend
time_to_descent = 30

# calculate the total time
total_time = time_to_max_altitude + time_to_descent

# show a dotted line at the average altitude


# draw the graph
plt.plot([0, time_to_max_altitude], [0, max_altitude], 'r')
plt.plot([time_to_max_altitude, total_time], [max_altitude, 0], 'r')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')
plt.show()
