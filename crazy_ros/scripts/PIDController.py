#!/usr/bin/env python

import rospy
import os
import sys
from time import sleep
import numpy as np
from std_msgs.msg import String, Float64
from crazy_ros.msg import NumpyArrayFloat64 # Can handle messages of type np.array, list and tuple
from geometry_msgs.msg import Point
import signal
from math import sin, pi, sqrt
from json import dumps, load

class PIDcontroller(object):

    def __init__(self):
        # Sets up publishers and subscribers
        self.status_sub = rospy.Subscriber('/system/status_controller', String, self.handle_status)
        self.kinect_sub = rospy.Subscriber('/kinect/position', Point, self.handle_kinect_position)
        self.control_pub = rospy.Publisher('/system/control_signal', NumpyArrayFloat64, queue_size = 10)
 
        self.status = False
        self.kinect_position = None
        params = None

        # Loads configuration parameters
        for filename in rospy.myargv(argv=sys.argv):
            if os.path.basename(filename) == 'configparam.cnf':
                with open(filename) as configfile:
                    param = load(configfile)
                configfile.close()
        if param != None:
            # Sets configuration parameters
            self.timestep = param['global']['timestep']
            self.param = param
        else:
            print 'ERROR. Could not load configuration parameters in %s' % (str(self))

    def handle_status(self, msg):
        # Callback for commands from master which generates a trajectory
        # if MPC is broadcasted, but turns of the controller if anything
        # else is broadcasted and sets all conttrol signals to 0 if "q"
        # is broadcasted
        if msg.data == 'PID':
            self.status = True
        else:
            self.status = False
            if msg.data == 'q':
                self.control_pub.publish(np.zeros((4,1)))

    def handle_kinect_position(self, point):
        self.kinect_position = point

    def __str__(self):
        return 'PID controller node'

def signal_handler(signal, frame):
    print 'Shutting down PID node nicely!'
    sys.exit(0)

def main():
    rospy.init_node('PIDcontroller')
    PID = PIDcontroller()
    signal.signal(signal.SIGINT, signal_handler)

    # Have the while loop outside of the node in order to allow
    # interruptions from the handle_status callback
    while True:
        if PID.status:
            PID.control_pub.publish(200*np.ones((4,1)))
            sleep(PID.timestep)
            # TODO compute PID control signal

if __name__ == '__main__':
    main()
