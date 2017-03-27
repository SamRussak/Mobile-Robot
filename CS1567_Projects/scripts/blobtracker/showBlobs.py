#!/usr/bin/env python
import os
import roslib
import rospy
import cv2
import copy
import math
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from cmvision.msg import Blobs, Blob
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from kobuki_msgs.msg import BumperEvent

pub = rospy.Publisher("kobuki_command", Twist, queue_size=10)
command = Twist()

colorImage = Image()
isColorImageReady = False
blobsInfo = Blobs()
isBlobsInfoReady = False
tempBlobs3 = []
degree = 0
x = 0
y = 0

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


def updateColorImage(data):
    global colorImage, isColorImageReady
    colorImage = data
    isColorImageReady = True

def updateBlobsInfo(data):
    global blobsInfo, isBlobsInfoReady
    blobsInfo = data
    isBlobsInfoReady = True

def mergeBlobs(blobs):
    global tempBlobs3
    x = 0;
    y = 0;
    left = 0;
    right = 0;
    top = 0;
    bottom = 0;
    area = 0;
    bigBlob = Blob()
    result = Blob()   
    tempBlobs = copy.deepcopy(blobs)
    tempBlobs = [x for x in tempBlobs if x.name == "Green"]
    temp2Blobs = copy.deepcopy(tempBlobs)
    tempBlobs3 = copy.deepcopy(tempBlobs)
    endBlobs = []
    xDistance = 0
    yDistance = 0
    maxXDistance = 0
    maxYDistance = 0
    while len(tempBlobs) > 0:
        for b in tempBlobs:
            if b.area > area:
                area = b.area
                bigBlob = copy.deepcopy(b)
        area = 0
        
        size = len(tempBlobs)
        counter = 0
        while counter < size:
            counter = 0
            size = len(tempBlobs)
            for c in tempBlobs:
                xDistance = abs(((bigBlob.right - bigBlob.left)/2 + bigBlob.left) - ((c.right - c.left)/2 + c.left))              
                yDistance = abs(((bigBlob.bottom - bigBlob.top)/2 + bigBlob.top) - ((c.bottom - c.top)/2 + c.top))
                maxXDistance = abs(abs((bigBlob.right - bigBlob.left)/2) + abs((c.right - c.left)/2))
                maxYDistance = abs(abs((bigBlob.bottom - bigBlob.top)/2) + abs((c.bottom - c.top)/2))
                if (maxXDistance >= xDistance and maxYDistance >= yDistance) and bigBlob.left > c.left:
                    bigBlob.left = c.left
                if (maxXDistance >= xDistance and maxYDistance >= yDistance) and bigBlob.right < c.right:
                    bigBlob.right = c.right
                if (maxXDistance >= xDistance and maxYDistance >= yDistance) and bigBlob.top > c.top:
                    bigBlob.top = c.top
                if (maxXDistance >= xDistance and maxYDistance >= yDistance) and bigBlob.bottom < c.bottom:
                    bigBlob.bottom = c.bottom
                if (maxXDistance >= xDistance and maxYDistance >= yDistance):
                    temp2Blobs.remove(c)
                else: 
                    counter = counter + 1
                bigBlob.area = abs((bigBlob.right - bigBlob.left)*(bigBlob.top - bigBlob.bottom))
                bigBlob.x = (bigBlob.right - bigBlob.left)/2 + bigBlob.left
                bigBlob.y = (bigBlob.bottom - bigBlob.top)/2 + bigBlob.top
            tempBlobs = copy.deepcopy(temp2Blobs)
        endBlobs.append(copy.deepcopy(bigBlob))
    area = 0
    for d in endBlobs:
        if d.area > area:
            area = d.area
            result = copy.deepcopy(d)
    return result

def main():
    global colorImage, isColorImageReady, blobsInfo, isBlobsInfoReady, pub, degree, x, y, tempBlobs3
    rospy.init_node('showBlobs', anonymous=True)
    rospy.Subscriber("/blobs", Blobs, updateBlobsInfo)
    rospy.Subscriber('/odom', Odometry, odomCallback)
    rospy.Subscriber("/v4l/camera/image_raw", Image, updateColorImage)
    bridge = CvBridge()
    cv2.namedWindow("Blob Location")
    flagit = False
    oneBlob = Blob()
    oneBlob.x = -10
    zeroCounter = 0
    angArray = []
    angArray.append(0)
    angArray.append(0)
    angIndex = 2
    voice = True
    while not rospy.is_shutdown() and (not isBlobsInfoReady or not isColorImageReady):
        pass
    flag = 0
    while not rospy.is_shutdown():
        try:
            color_image = bridge.imgmsg_to_cv2(colorImage, "bgr8")
        except CvBridgeError, e:
            print e
            print "colorImage"

        blobsCopy = copy.deepcopy(blobsInfo)
	tempBlobs3 = [x for blob in blobsCopy.blobs if blob.name == "Green"]
        if len(blobsCopy.blobs) > 0:
            oneBlob = mergeBlobs(blobsCopy.blobs)
            cv2.rectangle(color_image, (oneBlob.left, oneBlob.top), (oneBlob.right, oneBlob.bottom), (0,255,0), 2)
	    flagit = True
	cv2.imshow("Color Image", color_image)
        cv2.waitKey(1)
        while (len(tempBlobs3) > 0):
            if len(tempBlobs3) > 0:
                command.linear.x = .3
                pub.publish(command)
                if oneBlob.x <= 320 and oneBlob.x >= 0:
                    command.angular.z = (320 - oneBlob.x) * .0075 + (angArray[angIndex - 1] - angArray[angIndex - 2])*.001
                if oneBlob.x > 320 and oneBlob.x <= 640:
                    command.angular.z = (oneBlob.x - 320) * -.0075 - (angArray[angIndex - 1] - angArray[angIndex - 2])*.001
                angArray.append(command.angular.z)
                angIndex = angIndex + 1
	        pub.publish(command)
                blobsCopy = copy.deepcopy(blobsInfo)
                oneBlob = mergeBlobs(blobsCopy.blobs)
               # cv2.rectangle(color_image, (oneBlob.left, oneBlob.top), (oneBlob.right, oneBlob.bottom), (0,255,0), 2)
            else:
                command.linear.x = command.linear.x*.9
	if command.linear.x > .05:
	    command.linear.x = command.linear.x - .005
	    if command.linear.x <= .05:
	        flag = 1
        if flag == 1:
	    command.linear.x = 0
            pub.publish(command)
            os.system('spd-say \"show me the ball\"')
	    print("f")
	    flag = 0
        command.angular.z = 0        
           # cv2.imshow("Color Image", color_image)
           # cv2.waitKey(1)
        pub.publish(command)
        flagit = True
        zeroCounter = 0

    cv2.destroyAllWindows()
 
if __name__ == '__main__':
    main()

