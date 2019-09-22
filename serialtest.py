import serial
import numpy as np
from multiprocessing import Process, Value
import tkinter as tk
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt

"""
    Written by Baris SOYKÖK
    17/09/2019
"""

#Read values from serial port. Device is connected to COM5 and uses 19200 Baud.s
def ReadSerial(pitch, yaw, roll, tmp):
    global RunFlag
    while (RunFlag):
        ser = serial.Serial()
        ser.baudrate = 19200
        ser.port = 'COM5'
        ser.open()
        #print(ser.isOpen())
        x=ser.read (16) #Bytes to read
        #print(x)
        pitch_int = np.array([x[0], x[1], x[2], x[3]], dtype=np.uint8)
        pitch_float = pitch_int.view(dtype=np.float32)  #Combine 4 bytes to float
        #print('Pitch: ' + str(pitch_float))
        pitch.value = pitch_float
        yaw_int = np.array([x[4], x[5], x[6], x[7]], dtype=np.uint8)
        yaw_float = yaw_int.view(dtype=np.float32)
        #print('Yaw: ' + str(yaw_float))
        yaw.value = yaw_float
        roll_int = np.array([x[8], x[9], x[10], x[11]], dtype=np.uint8)
        roll_float = roll_int.view(dtype=np.float32)
        #print('Roll: ' + str(roll_float))
        roll.value = roll_float
        Temp_int = np.array([x[12], x[13], x[14], x[15]], dtype=np.uint8)
        Temp_float = Temp_int.view(dtype=np.float32)
        #print('Temperature: ' + str(Temp_float))
        tmp.value = Temp_float
        ser.close()
        sleep(1)    #Decrease this is serial is faster
    #print('Process Terminated')
    return

#Update measurements on gui
def UpdateLabels(Temp_l, Pitch_l, Yaw_l, Roll_l, tmp, pitch, yaw, roll):
    def Update():
        Temp_l.config(text='Temperature: ' + str(tmp.value))
        Temp_l.after(1000, Update)
        Pitch_l.config(text='Pitch: ' + str(pitch.value))
        Yaw_l.config(text='Yaw: ' + str(yaw.value))
        Roll_l.config(text='Roll: ' + str(roll.value))
    Update()

#Terminate treads. They keep running otherwise    
def quit():
    global RunFlag
    RunFlag = False
    root.destroy()

# This function is called periodically from FuncAnimation
#It is used to plot measurements realtime.
def animate(i, xs, ys, tmp):
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(tmp.value)

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    #plt.subplots_adjust(bottom=0.30)
    fig.autofmt_xdate()
    plt.title('TMP100 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

#same as above, but for gyro measurements
def animate2(i, xs2, yp, yy, yr, pitch, yaw, roll):
    xs2.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    yp.append(pitch.value)
    yy.append(yaw.value)
    yr.append(roll.value)

    xs2 = xs2[-20:]
    yp = yp[-20:]
    yy = yy[-20:]
    yr = yr[-20:]

    ax2.clear()
    ax2.plot(xs2, yp, color = 'red')
    ax2.plot(xs2, yy, color = 'green')
    ax2.plot(xs2, yr, color = 'blue')
    fig2.autofmt_xdate()
    plt.subplots_adjust(bottom=0.30)
    plt.title('MPU6050 Angle over Time')
    plt.ylabel('Angle(degrees)')

    
#Golobal variables:    
RunFlag = True  #Quit Detection
root = tk.Tk()  #GUI

fig2 = plt.figure() #Plot
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax2 = fig2.add_subplot(1, 1, 1)
xs = []
xs2 = []
ys = []
yr = []
yp = []
yy = []
    
if __name__ == "__main__":
    pitch = Value('f', 0.0) #Variables for multiprocessing
    yaw = Value('f', 0.0)
    roll = Value('f', 0.0)
    tmp = Value('f', 0.0)
    #Setup Tkinter GUI
    root.title = ("Serial Reader")
    label_T = tk.Label(root, text="Test...")
    label_T.pack()
    label_Pitch = tk.Label(root, text="Test...")
    label_Pitch.pack()
    label_Yaw = tk.Label(root, text="Test...")
    label_Yaw.pack()
    label_Roll = tk.Label(root, text="Test...")
    label_Roll.pack()
    #Quit button MUST be used to terminate process.
    #Otherwise use task manager to kill python processes
    B_exit = tk.Button(root, text="Quit", command=quit)
    B_exit.pack()
    p=Process(target = ReadSerial, args = (pitch, yaw, roll, tmp))
    p.start()   #Start multiprocess
    #print('Temperature: ' + str(tmp.value))
    UpdateLabels(label_T, label_Pitch, label_Yaw, label_Roll, tmp, pitch, yaw, roll)    
    #Plot updates:
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, tmp), interval=1000)
    ani2 = animation.FuncAnimation(fig2, animate2, fargs=(xs2, yp, yy, yr, pitch, yaw, roll), interval=1000)
    plt.show()
    #Mainloop blocks the process:
    root.mainloop()
    while(RunFlag):
        sleep(0.05)
        print('Waiting')    #If you see this printing, program didn't quit properly.
    print ('Quitting...')
    p.terminate()
    print('Done')
    
    
