import sys
import argparse
import socket
import csv
import pandas as pd
import re
import driver
from os.path import exists
tempo=[]
test=True


if __name__ == '__main__':
    pass

# Configure the argument parser
parser = argparse.ArgumentParser(description = 'Python client to connect to the TORCS SCRC server.')

parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                    help='Host IP address (default: localhost)')
parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001,
                    help='Host port number (default: 3001)')
parser.add_argument('--id', action='store', dest='id', default='SCR',
                    help='Bot ID (default: SCR)')
parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1,
                    help='Maximum number of learning episodes (default: 1)')
parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0,
                    help='Maximum number of steps (default: 0)')
parser.add_argument('--track', action='store', dest='track', default=None,
                    help='Name of the track')
parser.add_argument('--stage', action='store', dest='stage', type=int, default=3,
                    help='Stage (0 - Warm-Up, 1 - Qualifying, 2 - Race, 3 - Unknown)')

arguments = parser.parse_args()

# Print summary
print('Connecting to server host ip:', arguments.host_ip, '@ port:', arguments.host_port)
print('Bot ID:', arguments.id)
print('Maximum episodes:', arguments.max_episodes)
print('Maximum steps:', arguments.max_steps)
print('Track:', arguments.track)
print('Stage:', arguments.stage)
print('*********************************************')

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    print('Could not make a socket.')
    sys.exit(-1)

# one second timeout
sock.settimeout(1.0)

shutdownClient = False
curEpisode = 0

verbose = False

d = driver.Driver(arguments.stage)
if test==True:
    d.buildingtree()

while not shutdownClient:
    while True:
        print('Sending id to server: ', arguments.id)
        buf = arguments.id + d.init()
        print('Sending init string to server:', buf)
        try:
            sock.sendto(buf.encode(), (arguments.host_ip, arguments.host_port))
        except socket.error as msg:
            print("Failed to send data...Exiting...")
            sys.exit(-1)
            
        try:
            buf, addr = sock.recvfrom(1000)
            print('Received data from server:', buf.decode())
            if buf.decode().find("***identified***") >= 0:
                break
        except socket.error as msg:
            print("didn't get response from server...")


    currentStep = 0
    #output=pd.DataFrame()
    while True:
        # wait for an answer from server
        buf = None
        try:
            buf, addr = sock.recvfrom(1000)
        except socket.error as msg:
            print("didn't get response from server...")
        
        if verbose:
            print('Received: ', buf)
        
        if buf != None and buf.decode().find('***shutdown***') >= 0:
            d.onShutDown()
            shutdownClient = True
            print('Client Shutdown')
            if test==False:
                with open("gamedata.csv","a",newline="") as f:
                    writer=csv.writer(f)
                    writer.writerows(tempo)
            break
        
        if buf != None and buf.decode().find('***restart***') >= 0:
            d.onRestart()
            print('Client Restart')
            break
        
        currentStep += 1
        if currentStep != arguments.max_steps:
            if buf != None:
               if test==False:
                   buf=d.drive(buf.decode())
                   dlist=[]
                   dlist.append(d.state.getAngle())
                   dlist.append(d.state.getTrackPos())
                   dlist.append(d.state.getSpeedX())
                   dlist.append(d.state.getTrack()[0])
                   dlist.append(d.state.getTrack()[1])
                   dlist.append(d.state.getTrack()[2])
                   dlist.append(d.control.getAccel())
                   dlist.append(d.control.getSteer())
                   dlist.append(d.control.getGear())
                   tempo.append(dlist)
               else:
                    buf=d.Mydriver(buf.decode())
        else:
            buf = '(meta 1)'
        
        if verbose:
            print('Sending: ', buf)
        
        if buf != None:
            try:
                sock.sendto(buf.encode(), (arguments.host_ip, arguments.host_port))
            except socket.error as msg:
                print("Failed to send data...Exiting...")
                sys.exit(-1)
    
    curEpisode += 1
    
    if curEpisode == arguments.max_episodes:
        shutdownClient = True
        

sock.close()
