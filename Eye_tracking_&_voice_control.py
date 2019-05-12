# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 18:00:16 2019

@author: varun,david,juan

Full integration of eye/voice tracking
""" 
import tkinter as tk
import tkinter.messagebox as mg
import cv2
import numpy as np
import time 
from picamera import PiCamera
from picamera.array import PiRGBArray
import sounddevice as sd
import soundfile as sf
from fftfunction import fftfunction


# Function creation
def getCentroid(arg):
    (x,y,w,h) = cv2.boundingRect(arg)
    cx = float((x+x+w)/2) #Scaling factor also set based on distance, can be changed
    cy = float((y+y+h)/2) #centroid computation for eyes
    return [cx,cy]

    
def Voice_Mode(): #Called when Voice mode is activated, v = 1
    print("Voice mode")
    print(v.get())
    
    fs=44100#Recording frequency for long recording
    fs1=44100#Recording frequency for short recording
    noise=0.04#After seeing the graphs of the words recorded with the microphone,
            #the noise amplitude is always smaller than 0.04

    x=fftfunction('right.wav')#Fast Fourier Trasform of a prerecorded 'R' sound
    y=fftfunction('left.wav')#Fast Fourier Transform of a prerecorded 'L' sound
    z=fftfunction('go.wav')#Fast Fourirer Transform of a prerecorded 'P' sound
    duration2 = 0.1 #Duration of short recording every 0.1 seconds to detect if 
                    #the wheelchair user wants to say something
    duration = 3 #Duration of long recording that records what the wheelchair user says
    j=0
    a3=[]#a3 vector will store the word said by the wheelchair user after filtering
        #the noise
    data1=[]#Vector to accumulate 'R' sound Error
    data2=[]#Vector to accumulate 'L' sound Error
    data3=[]#Vector to accumulate 'P' sound Error
    
    while v.get()==1 and exit_command == 0:
        
        GUI.update()
        if v.get()!= 1 or exit_command ==1:
            break
        
        point=0
        #a1 and a2 vectors will be used to filter the noise ofwhat the wheelchair user says
        a1=[]
        a2=[]
        #This while loop is used to detect if someone is speaking through the microphone
        #If nothing is said the while loop will print 'Hearing' 
        while j<4:
            #myrecording1 is the short recording explained above, channels=1 because 
            #only one microphone is used
            myrecording1 = sd.rec(int(duration2*fs1), samplerate=fs1,
                                  channels=1,dtype='float64')#initiates recording
            if j==0:
                print ("Hearing")
            sd.wait()#stops recording after 0.1 seconds         
            for w in myrecording1:
                a3.append(w)#all values of the short recording are stored in a3
                #from j=0 to j=3
                if w>noise:# checks if what is recorded is only noise, if it is 
                            #not noise point = 1
                    point=1
            j=j+1#in vector a3 values of myrecording1 for 4 loops are stored in order to 
            #not lose any important information of what the wheelchair user is going to say
        if point==1:#point=1 means the wheeelchair user is saying something
            #myrecording is the long recording explained above
            myrecording = sd.rec(duration * fs, samplerate=fs, channels=1,dtype='float64')
            print ("Recording Audio")
            sd.wait()#stops recording after 3 seconds
            e=1;
            #In accordance with NoiseFigure(Annex), the first for is used to take
            #out the left noise of the word recorded and store it in a1 vector
            for w in myrecording:
                if w>noise and e==1:
                    e=e-1;
                    a1.append(w)
                if e==0:
                    a1.append(w)
            #In accordance with NoiseFigure(Annex), the second for is used to take 
            #out the right noise of the word recorded and store in a2 vector, but a2 vector
            #is the word reversed.For this reason, we need a third for to reverse the final word  
            for w in reversed(a1):
                if w>noise or e!=0:
                    e=e-1;
                    a2.append(w)
            #In accordance with NoiseFigure(Annex), the third for is used to store the
            #final word without noise in a3 vector           
            for w in reversed(a2):
                a3.append(w);
            
            if len(a2)<8000:#From the data obtained, if the word recorded has less than 8000
                #values is one of the directions recorded ('R' sound, 'L' sound or 'P' sound) 
                sf.write('word.wav',a3,int(0.93*fs))
                w2=fftfunction('word.wav')#Fast Fourier Trasform of the final word 
                                          #recorded without noise(('R' sound, 'L' sound or 'P' sound))
                    
                #Difference between normalized Fast Fourier of the final word without noise and 
                #Fast Fourier Trasform of a prerecorded sound
                ccr1=abs((w2/max(w2))-(x/max(x))); #'R' sound
                ccr2=abs((w2/max(w2))-(y/max(y)));#'L' sound
                ccr3=abs((w2/max(w2))-(z/max(z)));#'P' sound
                    
                xerr1=np.square(np.mean(ccr1));#'R' sound error
                xerr2=np.square(np.mean(ccr2));#'L' sound error
                xerr3=np.square(np.mean(ccr3));#'P' sound error
                      
                if min(xerr1,xerr2,xerr3)==xerr1:
                    print("RIGHT");
                    DrawCanvas('right')
                if min(xerr1,xerr2,xerr3)==xerr2:
                    print("LEFT");
                    DrawCanvas('left')
                if min(xerr1,xerr2,xerr3)==xerr3:
                    print("GO/STOP");
                    DrawCanvas('straight')
                print(" ")
                print("Right error:")
                print(xerr1)
                print("Left error:")
                print(xerr2)
                print("Go/stop error:")
                print(xerr3)
                #sound errors are stored in data1 vector while the program is running
                data1.append(xerr1)#All 'R' 
                data2.append(xerr2)#All 'L' 
                data3.append(xerr3)#All 'P'
            else:#If the word recorded has more than 8000 values is not one of the directions recorded
                print("You didn't say any direction")
        j=0
        a3=[]
        
        
def Vision_Mode(): #Called when Vision mode is activated. v = 0
    print("Vision mode")
    print(v.get())
    centX_arr = []
    centY_arr = []
    time_arr = []
    
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    time.sleep(0.1)
    calibrate = 1 
    
    ts1 = time.time()
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        if v.get()==1 or exit_command == 1:
            print('loop break')
            break
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rawCapture.truncate(0)
        eyes = eye_cascade.detectMultiScale(gray)
        eyes = np.asarray(eyes,np.uint8)
        if eyes.any():
            edges = cv2.Canny(eyes, 0, 50)
            eyes = np.asarray(edges,np.uint8)
            if calibrate == 1: #Runs only on the calibration run
                
                label_calibrate.config(bg = "red", text = "CALIBRATING")
                
                print('Please look straight for calibration')
                time.sleep(0.5) #To give the patient some time to adjust
                reference = getCentroid(eyes)
                print(reference)
                calibrate = 0  
                
                label_calibrate.config(bg = "#ECECEC", text = "")
                                       
            (s,contours,heirarchy) = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #To find the contours in the eye
            if len(contours):
                try:
                    cnt = np.asarray(contours,np.uint8)
                except ValueError:
                    cnt = contours[0]
                (centX, centY) = getCentroid(cnt)
                centX_arr.append(centX)
                centY_arr.append(centY)
                print(round(centX/reference[0],2))
                if round(centX/reference[0],2) > 1.5: #Done for a fixed distance during calibration.
                    DrawCanvas('right')
                elif round(centX/reference[0],2) < 0.5 and round(centX/reference[0],2)>0:
                    DrawCanvas('left')
                elif round(centX/reference[0],2) == 0:
                    print('Wait for camera to focus')
                else:
                    DrawCanvas('straight')
                ts2 = time.time()
                tStamp = ts2 - ts1
                time_arr.append(tStamp)
            else:
                print('Please wait for camera to focus')
                continue
        else:
            print('No eyes detected')
        GUI.update()
        
    print('Please wait for the datalog')
    with open("DataLog_left.txt", "w") as f:
        f.writelines(map("{},{},{}\n".format, time_arr, centX_arr, centY_arr))
    
def DrawCanvas(order): #Makes changes in canvas, when an order is registered
    
    Can.delete("all")
    label_2.config(text = order) #Prints the order in label under canvas
    if order == 'straight':
        Can.create_polygon(straight, fill = "black") #Draws order in the canvas
       
    elif order == 'right':
        Can.create_polygon(right, fill = "black") #Draws order in the canvas
        
    elif order == 'left':
        Can.create_polygon(left, fill = "black") #Draws order in the canvas
        
    elif order == 'stop':
        Can.create_image(canvas_size/2,canvas_size/2, image=stop) #Draws order in the canvas
    
def ExitYN(): #Makes sure the user wants to exit the program
    global exit_command
    exit_command = 1
    if mg.askyesno('Verify', 'Do you want to exit?'):
        GUI.destroy()
        
        
    else:
        mg.showinfo('No', 'Exit cancelled')
        exit_command = 0

def Normalize(l): #Normalizes the coordinates of the polygons for any canvas size

    l = [x * canvas_size for x in l] #multiplies every coordinate of the polygon by the canvas size

    l = [x + canvas_size/2 for x in l] #changes the origin from the polygon center to the origin of the canvas
    return l
#%% GUI Variables    
GUI = tk.Tk() #create GUI
GUI.title("Eye tracking/Voice control")
v = tk.IntVar()
exit_command = 0

button_width = 15 
canvas_size = 100 
straight = Normalize([0, -0.5,0.4,0,0.1,0,0.1,0.5,-0.1,0.5,-0.1,0,-0.4,0]) #coordinates for straight arrow
right = Normalize([0.5,0,0,0.4,0,0.1,-0.5,0.1,-0.5,-0.1,0,-0.1,0,-0.4]) #coordinates for right arrow
left = Normalize([-0.5,0,0,0.4,0,0.1,0.5,0.1,0.5,-0.1,0,-0.1,0,-0.4]) #coordinates for left arrow
stop = tk.PhotoImage(file="stop.gif")





#%%GUI component creation
label_1 = tk.Label(GUI, text = "Select mode").grid(row = 0, column = 1)
label_2 = tk.Label(GUI, fg="brown")
label_2.grid(row = 6, column = 1)

label_calibrate = tk.Label(GUI, fg = "white", bg = "#ECECEC")
label_calibrate.grid(row = 3, column=1)

button_exit = tk.Button(GUI, text = 'EXIT', width = button_width, 
                        command = ExitYN).grid(row = 8, column=1)
#mode selection buttons
tk.Radiobutton(GUI, text='Vision', indicatoron = 0, width = button_width, padx=10, variable = v,
               command = lambda: Vision_Mode(), value = 0).grid(row = 1, column=0)
tk.Radiobutton(GUI, text='Voice', indicatoron = 0, width = button_width, padx = 10, variable = v,
               command = lambda: Voice_Mode(), value = 1).grid(row = 1, column=2)

#Canvas
Can = tk.Canvas(GUI, width = canvas_size, height = canvas_size, bg = "white")
Can.grid(row = 5, column=1)

#%% Final execution



GUI.mainloop()


