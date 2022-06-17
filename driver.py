import carControl
import keyboard
import carState
import msgParser
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree

regr=DecisionTreeRegressor(random_state=0)
score=0

class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage
        
        self.parser = msgParser.MsgParser()
        
        self.state = carState.CarState()
        
        self.control = carControl.CarControl()
        
        self.steer_lock = 0.785398
        self.max_speed = 200
        self.prev_rpm = None
    
    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]
        
        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15
        
        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5
        
        return self.parser.stringify({'init': self.angles})
    
    def drive(self, msg):
        self.state.setFromMsg(msg)
       # ang=0
       # v=0.3
       # if keyboard.is_pressed('right') == True:
       #     ang=-v
       # if keyboard.is_pressed('left') == True:
       #     ang=v
       # if keyboard.is_pressed('down') == True:
       #     self.speeding(0)
       # elif keyboard.is_pressed(' ') == True:
       #     self.control.setBrake(10)
#
       # else:
       #     if self.control.getBrake()!=0:
       #         self.control.setBrake(0)
#
 
        self.steer()
        self.gear()
    #    if keyboard.is_pressed('up') == True:
  
    #        self.control.setAccel(20)
        

     #   self.steerings(ang)
        
        
        
        self.speed()
        
        return self.control.toMsg()
    
    def steerings(self, ang):
        distance = self.state.trackPos
        if ang==0:
            self.control.setSteer((ang))
        else:
            self.control.setSteer((ang)/self.steer_lock)

    
    def steer(self):
        angle = self.state.angle
        dist = self.state.trackPos
        
        self.control.setSteer((angle - dist*0.5)/self.steer_lock)
    


    def gear(self):
        rpm = self.state.getRpm()
        gear = self.state.getGear()
        
        if self.prev_rpm == None:
            up = True
        else:
            if (self.prev_rpm - rpm) < 0:
                up = True
            else:
                up = False
        
        if up and rpm > 7000:
            gear += 1
        
        if not up and rpm < 3000:
            gear -= 1
        
        self.control.setGear(gear)
    
    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()
        
        if speed < self.max_speed:
            accel += 0.1
            if accel > 1:
                accel = 1.0
        else:
            accel -= 0.1
            if accel < 0:
                accel = 0.0
        
        self.control.setAccel(accel)

    def speeding (self, side):
        speed= self.state.getSpeedX()
        accel = self.control.getAccel()
        if side == 0:
            if accel > 0 and self.control.setGear()!=0:
                accel=0
            self.control.setGear(0)
        accel+=0.4
        self.control.setAccel(accel)

    def buildingtree(self):
        np.set_printoptions(suppress=True)
        df=pd.read_csv('gamedata.csv')


        df.col=['Angle','Trackpos','SpeedX','SpeedY','SpeedZ','s0','s1','s2','s3','s4','s5','accel','Steer','Gear','Brake']

        X=df.iloc[:,:- 4].values
        y=df.iloc[:, 11:15].values

        X_train,X_test,y_train,y_test= train_test_split(X,y,test_size=0.2)

        regr.fit( X_train, y_train)

        text_rep=tree.export_text(regr)
        print("OUTPUT AS REQUIRED BY SIR::",text_rep)
       
    
    def Mydriver(self,msg):
        self.state.setFromMsg(msg)

        val=[[self.state.getAngle(),self.state.getTrackPos(),self.state.getSpeedX(),self.state.getSpeedY(),self.state.getSpeedZ(),self.state.getTrack()[0],self.state.getTrack()[1],self.state.getTrack()[2],self.state.getTrack()[3],self.state.getTrack()[4],self.state.getTrack()[5]]]
        valss=np.reshape(regr.predict(val),(4,1))
        accel=valss[0][0]
        steer=valss[1][0]
        gear=valss[2][0]
        brek=valss[3][0]

        print("Predicted values : \n", accel,", ",steer, ", ",gear,", ",brek,"\n")
        self.control.setAccel(accel)
        self.control.setSteer(steer)
        self.control.setGear(gear)
        self.control.setBrake(brek)

        return self.control.toMsg()




    def onShutDown(self):
        pass
    
    def onRestart(self):
        pass
        