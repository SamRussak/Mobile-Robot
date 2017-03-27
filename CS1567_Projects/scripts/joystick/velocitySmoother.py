#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import Twist


pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size=10)
currentCommand = Twist()
currentCommand.linear.x = 0.0
currentCommand.angular.z = 0.0
targetCommand = Twist()
targetCommand.linear.x = 0.0
targetCommand.angular.z = 0.0

def updateCommand(data):
    global targetCommand
    targetCommand = data

def cleanUp():
    global currentCommand
    currentCommand.linear.x = 0.0
    currentCommand.angular.z = 0.0
    pub.publish(currentCommand)
    rospy.sleep(1)

def velSmoother():
    global pub, targetCommand, currentCommand
    rospy.init_node("velocitySmoother", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)

    while pub.get_num_connections() == 0:
        pass

    while not rospy.is_shutdown():
        global targetCommand, currentCommand
        if(targetCommand.linear.x == 2):
            currentCommand.linear.x = 0
            currentCommand.angular.z = 0
        elif(currentCommand.linear.x < targetCommand.linear.x - 0.01):
	    currentCommand.linear.x = currentCommand.linear.x + 0.02
	elif(currentCommand.linear.x > targetCommand.linear.x + 0.01):
            currentCommand.linear.x = currentCommand.linear.x - 0.02
        currentCommand.angular.z = targetCommand.angular.z
        pub.publish(currentCommand)
        rospy.sleep(0.1)


if __name__ == '__main__':
    velSmoother()

