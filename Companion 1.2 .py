import subprocess
import datetime
import tkinter as tk
import serial
import pynmea2
import threading
import winsound
import os
import sys
from datetime import datetime, timedelta
import time

global START_HEIGHT, END_HEIGHT, CLIMB_RATE, DESCENT_RATE, ABLE_TO_PASS, altitude_data, alt
START_HEIGHT = 1700
END_HEIGHT = 1981
CLIMB_RATE = 1.2 * 0.978
DESCENT_RATE = 1.2 * 0.978
ABLE_TO_PASS = 2729
alt = 2601
Start_Flag = False
Current_Altitude = alt
desired_time = 68  # minutes

speed_label = None


def read_serial(ser):
    global Start_Flag, Current_Altitude, Time_zero, current_time_utc, play_start_sound
    while True:
        try:
            line = ser.readline().decode('utf-8')
            if line.startswith('$GPGGA'):
                msg = pynmea2.parse(line)
                Current_Altitude = msg.altitude
                current_time_utc = msg.timestamp
                if Current_Altitude < START_HEIGHT and not Start_Flag:
                    Start_Flag = True
                    Time_zero = datetime.combine(datetime.now().date(), current_time_utc)
                    play_start_sound = True
        except Exception as e:
            pass


def update_window():
    global Start_Flag, Current_Altitude, Time_zero, current_time_utc, Start_Altitude, beep_flag, play_start_sound
    if Start_Flag:
        if play_start_sound:
            winsound.PlaySound('Start_Task.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
            play_start_sound = False
    if Start_Flag:
        current_datetime = datetime.combine(datetime.now().date(), current_time_utc)
        elapsed_time = (current_datetime - Time_zero).total_seconds()
        elapsed_seconds = int(elapsed_time)
        altitudes = []
        alt = START_HEIGHT
        for i in range(int(desired_time/2 * 60)):
            altitudes.append(alt)
            alt += CLIMB_RATE
        for i in range(int((desired_time/2) * 60)):
            altitudes.append(alt)
            alt -= DESCENT_RATE
        if elapsed_seconds < len(altitudes):
            print(elapsed_seconds)
            desired_altitude = altitudes[elapsed_seconds]
            altitude_difference = Current_Altitude - desired_altitude
            minutes, seconds = divmod(elapsed_seconds, 60)
            average_lift = (Current_Altitude - Start_Altitude) / elapsed_time if elapsed_time > 0 else 0
            speed_label.config(text="Time: {:02d}:{:02d} | Avg Lift: {:.1f} | Altitude: {:d} | desired altitude: {:d} |  {:.1f}".format(
                minutes, seconds, average_lift, int(Current_Altitude), int(desired_altitude), Current_Altitude - desired_altitude))
            if altitude_difference > 0:
                window.config(bg="light green")
                speed_label.config(bg="light green")
            else:
                window.config(bg="red")
                speed_label.config(bg="red")
        else:
            speed_label.config(text="Data unavailable for the current time.")
        if minutes > desired_time/2 and not beep_flag:
            window.config(bg="green")
            speed_label.config(bg="green")
            winsound.PlaySound('Final_Glide_Achieved.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
            beep_flag = True
    else:
        Start_Altitude = Current_Altitude
        speed_label.config(text="Waiting for task to begin : {:.0f}".format(Current_Altitude))
    with open('current_altitudes.txt', 'a') as f:
        f.write("{:.2f}\n".format(Current_Altitude))
    window.after(100, update_window)


def on_close():
    ser.close()
    window.destroy()


def restart():
    window.destroy()
    subprocess.call([sys.executable, __file__])


def main():
    global window, speed_label, ser
    global Start_Flag, Current_Altitude, beep_flag, serial_thread
    ser = serial.Serial('COM5', 9600, timeout=0.1)
    serial_thread = threading.Thread(target=read_serial, args=(ser,))
    window = tk.Tk()
    window.title("Companion 1.1 31/03/2023 2.6 ")
    window.wm_attributes("-topmost", True)
    window.geometry("800x50+600+0")
    window.protocol("WM_DELETE_WINDOW", on_close)
    window.config(bg="light green")
    speed_label = tk.Label(window, text="is this text even used? ", font=("Arial", 18), fg="black", bg="light green")
    speed_label.pack()
    restart_button = tk.Button(window, text="Restart", command=restart)
    restart_button.pack()
    Start_Flag = False
    Current_Altitude = alt
    beep_flag = False
    serial_thread.daemon = True
    serial_thread.start()
    update_window()
    window.mainloop()


if __name__ == "__main__":
    main()
