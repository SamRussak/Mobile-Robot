#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import ButtonEvent

pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size=10)
currentCommand = Twist()
currentCommand.linear.x = 0.0
currentCommand.angular.z = 0.0
flag = True

def updateCommand(data):
    global currentCommand
    currentCommand = data

def bumperCallback(data):
    global flag
    if ((data.button == 0 or data.button == 1 or data.button == 2) and data.state != 0):
        flag = False

def cleanUp():
    global currentCommand
    currentCommand.linear.x = 0.0
    currentCommand.angular.z = 0.0
    pub.publish(currentCommand)
    rospy.sleep(1)

def velSmoother():
    global pub, targetCommand, currentCommand, flag
    rospy.init_node("velocitySmoother", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.Subscriber('/mobile_base/events/button', ButtonEvent, bumperCallback)
   
    while pub.get_num_connections() == 0:
        pass

    while not rospy.is_shutdown() and flag:
        global currentCommand
        pub.publish(currentCommand)
        rospy.sleep(0.01)
    rospy.on_shutdown(cleanUp)


if __name__ == '__main__':
    velSmoother()

