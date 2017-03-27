#!/usr/bin/env python

import rospy
from std_msgs.msg import Float32

def controller():
    pub = rospy.Publisher("command", Float32, queue_size=10)
    rospy.init_node("controller", anonymous=True)
    while not rospy.is_shutdown():
        floating = input("Please enter a floating-point number: ")
        pub.publish(floating)

if __name__ == '__main__':
    controller()
