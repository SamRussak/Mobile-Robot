#!/usr/bin/env python

import rospy
from std_msgs.msg import Float32 
import math

prev = 0
goal = 0

def callback(data):
    global prev 
    global goal
    prev = goal
    goal = data.data    

def smoother():
    rospy.init_node("smoother", anonymous=True)
    rate = rospy.Rate(10)
    global prev
    global goal
    rospy.Subscriber("command", Float32, callback)
    while not rospy.is_shutdown():
        while math.fabs(prev-goal) > .015:
            rate = rospy.Rate(10)
            if(goal - prev > 0):
                prev = prev + .01
            elif(goal - prev < 0):
                prev = prev - .01
            else:
                prev = goal
            print prev
            rate.sleep()
        print prev
    



if  __name__ == '__main__':
    try:
        smoother()
    except rospy.ROSInterruptException:
        pass
