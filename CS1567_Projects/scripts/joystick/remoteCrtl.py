#!/usr/bin/env python

import rospy
import math
from sensor_msgs.msg import Joy
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

pub = rospy.Publisher("kobuki_command", Twist, queue_size=10)
command = Twist()

a = 0
b = 0
axes = 0
rt = 1
lt = 1


degree = 0
action = ""
target = 90.0
flag = True
x = 0
y = 0
bumper = True
tempDistance = ""
def odomCallback(data):
    # Convert quaternion to degree
    global degree, x, y
    q = [data.pose.pose.orientation.x,
         data.pose.pose.orientation.y,
         data.pose.pose.orientation.z,
         data.pose.pose.orientation.w]
    roll, pitch, yaw = euler_from_quaternion(q)
    # roll, pitch, and yaw are in radian
    degree = yaw * 180 / math.pi
    x = data.pose.pose.position.x
    y = data.pose.pose.position.y
    current = data.pose.pose.position.x
    print current


def joystickCallback(data):
    global pub, command, a, axes, rt, lt, b
    b = data.buttons[1]
    a = data.buttons[0]
    axes = data.axes[0]
    rt = data.axes[5]
    lt = data.axes[2]
    if a == 0:
        command.linear.x = -0.4*rt + 0.4
    else:
        command.linear.x = 0.4*rt - 0.4
    if lt <= 0:
        command.linear.x = 0
    if b == 1:
        command.linear.x = 2
      
    
    command.angular.z = axes
    pub.publish(command)

def cleanUp():
    global pub, command
    command.linear.x = 0.0
    command.angular.z = 0.0
    pub.publish(command)
    rospy.sleep(1)

def remoteController():
    rospy.init_node("remoteControl", anonymous=True)
    rospy.Subscriber("joy", Joy, joystickCallback)
    rospy.Subscriber('/odom', Odometry, odomCallback)

    rospy.on_shutdown(cleanUp)

    #while pub.get_num_connections() == 0:
    #    pass

    rospy.spin()

if __name__ == '__main__':
    remoteController()
