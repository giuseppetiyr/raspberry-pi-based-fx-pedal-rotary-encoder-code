from RPi import GPIO
import timeit
import time
import math
from time import sleep
from threading import Thread

from pythonosc.udp_client import SimpleUDPClient

#ip = "192.168.2.8"
ip = "127.0.0.1"
port = 5720

client = SimpleUDPClient(ip, port)  #create client


GPIO.setmode(GPIO.BCM)

# clip
# clips value between outMin and outMax
def clip(inVal, outMin, outMax):
     return min(max(inVal, outMin), outMax) #  clip at minimum and maximum value
     # note: min() takes minimum (the smallest) of its arguments, hence sets the maximum output value
     # note: max() takes the maximum (the largest) of its arguments, hence sets the minimum output value

def explin(inVal, inMin, inMax, outMin, outMax, clipType='minmax'):
    outVal = ( (math.log(clip(inVal, inMin, inMax)/inMin)) / (math.log(inMax/inMin)) ) * (outMax-outMin) + outMin
    return float(outVal)


def r_1():

    clk = 18
    dt = 27
    sw = 22

    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    counter = 0
    swState = 0
    swLastState = False
    clkLastState = GPIO.input(clk)
    clkLastTime = 0
    pedalState = False
    holdState = False
    holdStarted = False #init hold flag
    holdStart = 0 # int hold starting time

    while True:
        swState = 1 - GPIO.input(sw) 
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        now = time.monotonic()        
        holdDur = 2
        pedalMode = 1
    
        if clkState != clkLastState:
            clkPeriod = now-clkLastTime #measure time since last change
            increment = explin(clkPeriod, 0.005, 0.25, 4, 1) #set increment per tick depending on time period between ticks
            clkLastTime = now         
          
            if dtState != clkState:
                counter += increment
            else:
                counter -= increment
             
            counter = min(max(round(counter),0), 127)  #round and clip value
            
            print (f"r_1: {counter}")
            client.send_message("/rotary", counter)   #send float message
            clkLastState = clkState

        if swState != swLastState:
                          
            client.send_message("/raw_sw1", swState) #send RAW data           
            holdStart = now #remember time
            holdStarted = True
                          
            if swState:
                
                #if pedal is off
                if not pedalState and pedalMode == 1:
                    #turn it on
                    pedalState = True
                    print(f"PEDAL STATE {pedalState}")
                    print (f"ON_1 {swState}")
                    client.send_message("/ON_1", swState)   #send float message
             
                #if pedal is on                               
                else:            
                    pedalState = False
                    print(f"PEDAL STATE {pedalState}")
                    print ("OFF_1", 0)
                    client.send_message("/ON_1", 0)  
            
            else:
              
                #abort measuring hold time
                holdStarted = False
                
        if swState == swLastState:
            #if value is 1 (pressed)
            if swState:              
                #if pedal is currently held, but didn't switch mode yet
                if not holdState:
                    if holdStarted:
                        #check if pedal is already held long enough
                        if now >= (holdStart + holdDur):
                            pedalState = not pedalState
                            holdState = True
                            print(f"HOLD_1: {holdState}")                           
                            client.send_message("/HOLD_1", holdState)   #send float message
                            holdStarted = False
                else:
                    if holdStarted:
                        #check if pedal is already held long enough
                        if now >= (holdStart + holdDur):
                            pedalState = not pedalState
                            holdState = False
                            print(f"HOLD_1: {holdState}")
                            
                            client.send_message("/HOLD_1", holdState)   #send float message
                            holdStarted = False
            
        swLastState = swState
        sleep(0.001)
            

def r_2():
                    
    clk_2 = 23
    dt_2 = 24
    sw_2 = 10

    
    GPIO.setup(clk_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(sw_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    counter_2 = 0
    sw_2State = 0
    sw_2LastState = False
    clk_2LastState = GPIO.input(clk_2)
    clk_2LastTime = 0 
    pedal_2State = False
    hold_2State = False
    hold_2Started = False #init hold flag
    hold_2Start = 0 #int hold starting time

    while True:
        sw_2State = 1 - GPIO.input(sw_2) 
        clk_2State = GPIO.input(clk_2)
        dt_2State = GPIO.input(dt_2)
        
        now_2 = time.monotonic()
        
        hold_2Dur = 2
        pedal_2Mode = 1
    
        if clk_2State != clk_2LastState:
            clk_2Period = now_2 - clk_2LastTime #measure time since last change
            increment_2 = explin(clk_2Period, 0.005, 0.25, 4, 1) #set increment per tick depending on time period between ticks
            clk_2LastTime = now_2           
          
            if dt_2State != clk_2State:
                counter_2 += increment_2
            else:
                counter_2 -= increment_2                
    
            counter_2 = min(max(round(counter_2),0), 127)  #round and clip value
                
            print (f"r_2: {counter_2}")
            client.send_message("/rotary_2", counter_2)   #send float message
            clk_2LastState = clk_2State
                
        if sw_2State != sw_2LastState:
            
            client.send_message("/raw_sw2", sw_2State) #send RAW data            
            hold_2Start = now_2 #remember time
            hold_2Started = True            
            
            if sw_2State:
                
                #if pedal is off 
                if not pedal_2State and pedal_2Mode == 1:
                    #turn it on
                    pedal_2State = True
                    print(f"PEDAL_2 STATE {pedal_2State}")
                    print (f"ON_2 {sw_2State}")
                    client.send_message("/ON_2", sw_2State)   #send float message
                
                #if pedal is on                                
                else:            
                    pedal_2State = False
                    print(f"PEDAL_2 STATE {pedal_2State}")
                    print ("OFF_2", 0)
                    client.send_message("/ON_2", 0)  

        if sw_2State == sw_2LastState:
            #if value is 1 (pressed)
            if sw_2State:
                #if pedal is currently held, but didn't switch mode yet
                if not hold_2State:
                    if hold_2Started:
                        #check if pedal is already held long enough
                        if now_2 >= (hold_2Start + hold_2Dur):
                            pedal_2State = not pedal_2State
                            hold_2State = True
                            print(f"HOLD_2: {hold_2State}")                            
                            client.send_message("/HOLD_2", hold_2State)   #send float message
                            hold_2Started = False
                            
                else:
                    if hold_2Started:
                        #check if pedal is already held long enough
                        if now_2 >= (hold_2Start + hold_2Dur):
                            pedal_2State = not pedal_2State
                            hold_2State = False
                            print(f"HOLD_2: {hold_2State}")
                            
                            client.send_message("/HOLD_2", hold_2State)   #send float message
                            hold_2Started = False
            
        sw_2LastState = sw_2State
        sleep(0.001)
        
def r_3():
    clk_3 = 9
    dt_3 = 25
    sw_3 = 11

    GPIO.setup(clk_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(sw_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    counter_3 = 0
    sw_3State = 0
    sw_3LastState = False
    clk_3LastState = GPIO.input(clk_3)
    clk_3LastTime = 0
    
    pedal_3State = False
    hold_3State = False
    hold_3Started = False #init hold flag
    hold_3Start = 0 #int hold starting time


    while True:
            sw_3State = 1 - GPIO.input(sw_3) 
            clk_3State = GPIO.input(clk_3)
            dt_3State = GPIO.input(dt_3)
            
            now_3 = time.monotonic()
            
            hold_3Dur = 2
            pedal_3Mode = 1
        
            if clk_3State != clk_3LastState:
                clk_3Period = now_3 - clk_3LastTime #measure time since last change
                increment_3 = explin(clk_3Period, 0.005, 0.25, 4, 1) #set increment per tick depending on time period between ticks
                clk_3LastTime = now_3
                
              
                if dt_3State != clk_3State:
                    counter_3 += increment_3
                else:
                    counter_3 -= increment_3
                    
                counter_3 = min(max(round(counter_3),0), 127)  #round and clip value
                    
                print (f"r_3: {counter_3}")
                client.send_message("/rotary_3", counter_3)   #send float message
                clk_3LastState = clk_3State
                    
            if sw_3State != sw_3LastState:
                 
                 
                client.send_message("/raw_sw3", sw_3State)
                
                hold_3Start = now_3 #remember time
                hold_3Started = True #set hold flag
                
                if sw_3State:
                    
                    #if pedal is off and mode=1
                    if not pedal_3State and pedal_3Mode == 1:
                        #turn it on
                        pedal_3State = True
                        print(f"PEDAL_3 STATE {pedal_3State}")
                        print (f"ON_3 {sw_3State}")
                        client.send_message("/ON_3", sw_3State)   #send float message
                    
                    #if pedal is on                                  
                    else:            
                        pedal_3State = False
                        print(f"PEDAL_3 STATE {pedal_3State}")
                        print ("OFF_3", 0)
                        client.send_message("/ON_3", 0)  

                else:                    
                    #abort measuring hold time
                    hold_3Started = False
           
            if sw_3State == sw_3LastState:
                #if value is 1 (pressed)
                if sw_3State:
                    
                    #if pedal is currently held, but didn't switch mode yet
                    if not hold_3State:
                        if hold_3Started:
                            #check if pedal is already held long enough
                            if now_3 >= (hold_3Start + hold_3Dur):
                                pedal_3State = not pedal_3State
                                hold_3State = True
                                print(f"HOLD_3: {hold_3State}")                                
                                client.send_message("/HOLD_3", hold_3State)   #send float message
                                hold_3Started = False
                    else:
                        if hold_3Started:
                            #check if pedal is already held long enough
                            if now_3 >= (hold_3Start + hold_3Dur):
                                pedal_3State = not pedal_3State
                                hold_3State = False
                                print(f"HOLD_3: {hold_3State}")
                                
                                client.send_message("/HOLD_3", hold_3State)   #send float message
                                hold_3Started = False
                
            sw_3LastState = sw_3State
            sleep(0.001)
            
            
r1 = Thread(target = r_1)
r2 = Thread(target = r_2)
r3 = Thread(target = r_3)

r1.start()
r2.start()
r3.start()
