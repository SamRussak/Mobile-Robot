#!/usr/bin/env python

import rospy
import math
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from kobuki_msgs.msg import BumperEvent

def resetter():
    pub = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty, queue_size = 10)
    while pub.get_num_connections() == 0:
        pass
    pub.publish(Empty())



pub = rospy.Publisher("kobuki_command", Twist, queue_size=10)
command = Twist()
maxSpeed = 0.7
distance = 1.0
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

def cleanUp():
    global pub, command
    command.linear.x = 0.0
    command.angular.z = 0.0
    pub.publish(command)
    rospy.sleep(1)

def bumperCallback(data):
    global pub, command, bumper
    str = ""
    if data.bumper == 0:
        str = str + "*** Left bumper is "
    elif data.bumper == 1:
        str = str + "*** Center bumper is "
    else:
        str = str + "*** Right bumper is "

    if data.state != 0:
        bumper = False
        str = str + "pressed ***"
        print(str)
        command.linear.x = 0
        command.angular.z = 0
        pub.publish(command)
        rospy.sleep(1)
    bumper = True

def remoteController():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag
    rospy.init_node("selfController", anonymous=True)
    rospy.Subscriber('/odom', Odometry, odomCallback)
    rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)
    flag = True
    flag2 = True
    rospy.on_shutdown(cleanUp)
    while pub.get_num_connections() == 0:
        pass
    game()
def reset():
    try:
        resetter()
    except rospy.ROSInterruptException:
         pass

def game():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, tempDistance
    bumper = True
    while bumper:
        try:
            resetter()
        except rospy.ROSInterruptException:
            pass
        mode = input("Select Mode (1 for single and 2 for double)")
        if mode == 1:
            print("Enter a command and press enter")
	    modelString = raw_input()
	    action, maxSpeed, tempDistance = modelString.split()
	    maxSpeed = float(maxSpeed)
            tempDistance = float(tempDistance)
            if (action == "R"):
		if (tempDistance > 170):
		    rotateRightOver()
		    rospy.sleep(1)
		else:
                    target = tempDistance
	            rotate()
            elif (action == "F"):
                distance = tempDistance
	        forward()
            elif (action == "B"):
	        distance = -1*tempDistance
                backward()
	    elif (action == "L"):
                if (tempDistance > 170):
                    rotateLeftOver()
                    rospy.sleep(1)
		else:
                    target = -1*tempDistance
                    rotateleft()
		    reset()
		    rospy.sleep(0.5)
            flag = True
        elif mode == 2:
	    print("Enter multiple commands and press enter")
	    my_input=raw_input()
            new_input = my_input.split(",")
            for i in range(0, len(new_input)):
                flag = True
                try: 
                    resetter()
                except rospy.ROSInterruptException:
                    pass
	        action, maxSpeed, tempDistance = new_input[i].split()
                tempDistance = float(tempDistance)
                maxSpeed = float(maxSpeed)

                if (action == "R"):
                    if (tempDistance > 170):
                        rotateRightOver()
			rospy.sleep(1)
                    else:
                        target = tempDistance
                        rotate()
			reset()
			rospy.sleep(1)

                elif (action == "F"):
                    distance = tempDistance
		    forward()
		    rospy.sleep(1)
                elif (action == "B"):
                    distance = -1*tempDistance
		    backward()
		    rospy.sleep(1)
	        elif (action == "L"):
                    if (tempDistance > 170):
                        rotateLeftOver()
			rospy.sleep(1)
                    else:
                        target = -1*tempDistance
                        rotateleft()
			reset()
			print(degree)
			rospy.sleep(0.5)
            bumper = True            
    command.linear.x = 0
    command.angular.z = 0
    pub.publish(command)
    rospy.sleep(1)

def rotateRightOver():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper, tempDistance
    number10 = 0
    number10complete = 0
    counter = 0
    remainder = 0
    totalDegree = 0
    target = tempDistance/3
    dec = 0
    if(maxSpeed >= .8 and tempDistance < 200):
        dec = maxSpeed/290
    elif(maxSpeed >= .8 and tempDistance >= 200):
        dec = maxSpeed/360
	if (tempDistance >= 270):
	    dec = maxSpeed/540
    elif((maxSpeed == .6 or maxSpeed == .5) and tempDistance < 200):
        dec = maxSpeed/320
    elif((maxSpeed == .6 or maxSpeed == .5) and tempDistance >= 200):
        dec = maxSpeed/500
        if (tempDistance >= 270):
            dec = maxSpeed/750
    elif(tempDistance <= 200):
        dec = maxSpeed/540
    else:
        dec = maxSpeed/1000
    while not rospy.is_shutdown() and flag and action == "R" and bumper:
        if (counter == 3):
            flag = False
            command.linear.x = 0
            command.angular.z = 0
	elif(degree >= target*.98):
	    print(degree)
	    counter = counter + 1
	    reset()
	    rospy.sleep(.25)
        elif (command.angular.z < maxSpeed and counter == 0):
            command.angular.z = command.angular.z + dec
        elif (counter == 1):
            pass
        elif (command.angular.z > 0 and counter == 2):
            command.angular.z = command.angular.z - dec
            if (command.angular.z <= 0):
                break
        pub.publish(command)
        rospy.sleep(0.01)
    flag = True
    reset()
    bumper = True


def rotateLeftOver():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper, tempDistance
    number10 = 0
    number10complete = 0
    counter = 0
    remainder = 0
    totalDegree = 0
    target = -1*tempDistance/3
    dec = 0
    if(maxSpeed >= .8 and tempDistance < 200):
        dec = maxSpeed/290
    elif(maxSpeed >= .8 and tempDistance >= 200):
        dec = maxSpeed/360
        if (tempDistance >= 270):
            dec = maxSpeed/540

    elif((maxSpeed == .6 or maxSpeed == .5) and tempDistance < 200):
        dec = maxSpeed/320
    elif((maxSpeed == .6 or maxSpeed == .5) and tempDistance >= 200):
        dec = maxSpeed/500
        if (tempDistance >= 270):
            dec = maxSpeed/750
    elif(tempDistance <= 200):
        dec = maxSpeed/540
    else:
        dec = maxSpeed/1000
    while not rospy.is_shutdown() and flag and action == "L" and bumper:
        if (counter == 3):
            flag = False
            command.linear.x = 0
            command.angular.z = 0
        elif(degree <= target*.98):
            print(degree)
            counter = counter + 1
            reset()
            rospy.sleep(.25)
        elif (command.angular.z > -(maxSpeed) and counter == 0):
            command.angular.z = command.angular.z - dec         
        elif (counter == 1):
            pass
        elif (command.angular.z < 0 and counter == 2):
            command.angular.z = command.angular.z + dec           
	    if (command.angular.z >= 0):
	        break
        pub.publish(command)
        rospy.sleep(0.01)
    flag = True
    reset()
    bumper = True

    


def forward():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper
    while not rospy.is_shutdown() and flag and action == "F" and bumper:
	if (x >= distance*.98):
            flag = False
            command.linear.x = 0
            command.angular.z = 0
        elif (x == 0.0 or (x < distance/3 and command.linear.x < maxSpeed)):
            command.linear.x = command.linear.x + 0.015
        elif (x > distance/3 and x < 2*distance/3):
	    pass
        elif (x > 2*distance/3 and x < distance):
            command.linear.x = command.linear.x - 0.015
        pub.publish(command)
	rospy.sleep(0.1)
    flag = True
    reset()
    bumper = True
def rotate():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper
    dec = 0
    if(maxSpeed >= .8):
        dec = maxSpeed/240
    else:
        dec = maxSpeed/480
    while not rospy.is_shutdown() and flag and action == "R" and bumper:
        if (degree >= target*.98):
            flag = False
            command.linear.x = 0
            command.angular.z = 0
        elif (degree <= 0.01 or (degree < target/3 and command.angular.z < maxSpeed)):
            command.angular.z = command.angular.z + maxSpeed/160
        elif (degree > target/3 and degree < 2*target/3):
            pass
        elif (degree > 2*target/3 and degree < target and command.angular.z > 0):
            command.angular.z = command.angular.z - (dec)
        pub.publish(command)
        rospy.sleep(0.01)
    flag = True
    reset()
    bumper = True
def rotateleft():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper
    while not rospy.is_shutdown() and flag and action == "L" and bumper:
        dec = 0
        if(maxSpeed >= .8):
            dec = maxSpeed/240
        else:
            dec = maxSpeed/480
        if (degree <= target*.98):
            flag = False
            print(degree)
            command.linear.x = 0
            command.angular.z = 0
        elif (degree >= 0.01 or (degree > target/3 and command.angular.z > -(maxSpeed))):
            command.angular.z = command.angular.z - dec
        elif (degree < target/3 and degree > 2*target/3):
            pass
        elif (degree < 2*target/3 and degree > target):
            command.angular.z = command.angular.z + dec
        pub.publish(command)
	rospy.sleep(0.01)
    reset()
    bumper = True
def backward():
    global distance, degree, x, y, pub, command, maxSpeed, target, action, flag, bumper
    while not rospy.is_shutdown() and flag and action == "B" and bumper:
        if (x <= distance*.98):
            flag = False
            command.linear.x = 0
            command.angular.z = 0
	    print("Q")	
        elif (x > distance/3 and command.linear.x > -(maxSpeed)):
            command.linear.x = command.linear.x - 0.015
        elif (x < distance/3 and x > 2*distance/3):
            pass
        elif (x < 2*distance/3 and x > distance):
            command.linear.x = command.linear.x + 0.015
        pub.publish(command)
        rospy.sleep(0.1)
    reset()
    bumper = True

if __name__ == '__main__':
    remoteController()

