#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from struct import *

pub = rospy.Publisher("kobuki_command", Twist, queue_size=10)
pub2 = rospy.Publisher("robotstop", Twist, queue_size=10)
command = Twist()

depthData = Image()
isDepthReady = False

degree = 0
x = 0
y = 0

def depthCallback(data):
    global depthData, isDepthReady
    depthData = data
    isDepthReady = True

def main():
    global depthData, isDepthReady, command, pub
    rospy.init_node('depth_example', anonymous=True)
    rospy.Subscriber("/camera/depth/image", Image, depthCallback, queue_size=10)
#    command.linear.x = .3
 #   pub.publish(command)
    print 'ha\n'
    forwardSpeed = command.linear.x
    angularSpeed = command.angular.z
    while not isDepthReady:
        pass

    while not rospy.is_shutdown():
        step = depthData.step
        midX = 320
        midY = 240
        min = 20.0
        for x in range(100, 540):
            for y in range(190,240):
                offset = (y*2560) + (x*4)
                (dist,) = unpack('f', depthData.data[offset] + depthData.data[offset+1] + depthData.data[offset+2] + depthData.data[offset+3])
                if dist < min:
                    min = dist 
        if min < 0.6:
            command.linear.x = 1
            pub2.publish(command)
        elif min > 0.6:
            command.linear.x = -1
            pub2.publish(command)
if __name__ == '__main__':
    main()

