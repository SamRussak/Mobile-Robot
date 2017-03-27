#!/usr/bin/env python
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
oneBlob = Blob()
oneBlob.x = -10
oneBlob2 = Blob()
oneBlob2.x = -10
alpha1 = 0
beta1 = 0
alpha2 = 0
beta2 = 0
colorImage = Image()
isColorImageReady = False
blobsInfo = Blobs()
isBlobsInfoReady = False
areaBall = 0
areaGoal = 0

degree = 0
x = 0
y = 0

def resetter():
    pub = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty, queue_size = 10)
    degree = 0
    x = 0
    while pub.get_num_connections() == 0:
        pass
    pub.publish(Empty())

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

def rotateRight(count, deg, prelim):
    print deg
    global blobsInfo, alpha1, alpha2, beta1, beta2, areaBall, areaGoal, degree 
    while True:
        command.angular.z = -.3
        pub.publish(command)
        blobsCopy = copy.deepcopy(blobsInfo)
        if len(blobsCopy.blobs) > 0:
	    tempDeg = degree
            oneBlob = mergeBlob(blobsCopy.blobs)
            if oneBlob.x > 310 and oneBlob.x < 330 and oneBlob.area > areaBall and prelim != 0:
		print "ballR"
                if prelim == 1:
	            alpha1 = abs(tempDeg)
		    if count == 2:
		        alpha1 = alpha1 + 90
		if prelim == 2:
		    alpha2 = abs(tempDeg)
		    if count == 2:
		        alpha2 = alpha2 + 90
		areaBall = oneBlob.area
	    oneBlob2 = mergeBlobs(blobsCopy.blobs)
            if oneBlob2.x > 310 and oneBlob2.x < 330 and oneBlob2.area > areaGoal and prelim != 0:
		print "goalR"
                if prelim == 1:
                    beta1 = abs(tempDeg)
		    if count == 2:
		        beta1 = beta1 + 90
                if prelim == 2:
                    beta2 = abs(tempDeg)
		    if count == 2:
		        beta2 = beta2 + 90
		areaGoal = oneBlob2.area
       # if count == 2 and prelim != 0:
	#    if prelim == 1 and alpha1 < 80 and oneBlob.area > areaBall and flag1:
	 #       alpha1 = alpha1 + 90
	 #   if prelim == 1 and beta1 < 80 and oneBlob2.area > areaGoal and flag3:
	#	beta1 = beta1 + 90
	#    if prelim == 2 and alpha2 < 80 and oneBlob.area > areaBall and flag2:
	#	alpha2 = alpha2 + 90
	#    if prelim == 2 and beta2 < 80 and oneBlob2.area > areaGoal and flag4:
	#	beta2 = beta2 + 90 
        if(abs(degree) >= deg):
            command.angular.z = 0
            pub.publish(command)
	    resetter()
	    rospy.sleep(1)
            break

def rotateLeft(count, deg, prelim):
    print deg
    global blobsInfo, alpha1, alpha2, beta1, beta2, areaBall, areaGoal, degree
    while True:
        command.angular.z = .3
        pub.publish(command)
        blobsCopy = copy.deepcopy(blobsInfo)
        if len(blobsCopy.blobs) > 0:
	    tempDeg = degree
            oneBlob = mergeBlob(blobsCopy.blobs)
            if oneBlob.x > 310 and oneBlob.x < 330 and oneBlob.area > areaBall and prelim != 0:
                print "ballL"
	        if prelim == 1:
                    alpha1 = abs(tempDeg)
		    print alpha1
		    if count == 2:
		        alpha1 = alpha1 + 90
                if prelim == 2:
                    alpha2 = abs(tempDeg)
		    print alpha2
		    if count == 2:
		        alpha2 = alpha2 + 90
                areaBall = oneBlob.area
	    oneBlob2 = mergeBlobs(blobsCopy.blobs)
            if oneBlob2.x > 310 and oneBlob2.x < 330 and oneBlob2.area > areaGoal and prelim != 0:
		print "goalL"
                if prelim == 1:
                    beta1 = abs(tempDeg)
		    print beta1
		    if count == 2:
		        beta1 = beta1 + 90
                if prelim == 2:
                    beta2 = abs(tempDeg)
		    print beta2
		    if count == 2:
		        beta2 = beta2 + 90
                areaGoal = oneBlob2.area
       # if count == 2 and prelim != 0:
	#    print flag3
         #   if prelim == 1 and alpha1 < 80 and oneBlob.area > areaBall and flag1:
         #       alpha1 = alpha1 + 90
         #   if prelim == 1 and beta1 < 80 and oneBlob2.area > areaGoal and flag3:
         #       beta1 = beta1 + 90
         #   if prelim == 2 and alpha2 < 80 and oneBlob.area > areaBall and flag2:
         #       alpha2 = alpha2 + 90
         #   if prelim == 2 and beta2 < 80 and oneBlob2.area > areaGoal and flag4:
         #       beta2 = beta2 + 90
 #	flag1 = False
 #	flag2 = False
 #	flag3 = False
 #	flag4 = False
        if(abs(degree) >= deg):
            command.angular.z = 0
            pub.publish(command)
            resetter()
	    rospy.sleep(1)
            break
def move(distance, speed):
    global x
    command.linear.x = speed
    pub.publish(command)
    while True:
        if (abs(x) >= distance):
            command.linear.x = 0.0
	    pub.publish(command)
	    resetter()
	    rospy.sleep(1)
            break


def mergeBlob(blobs):
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
    tempBlobs = [x for x in tempBlobs if x.name == "Ball"]
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



def mergeBlobs(blobs):
    x = 0;
    y = 0;
    left = 0;
    right = 0;
    top = 0;
    bottom = 0;
    area = 0;
    bigBlob = Blob()
    result = Blob()
    blobCopy = copy.deepcopy(blobs)
    tempBlobs = [x for x in blobCopy if x.name == "Out"]
    temp2Blobs = copy.deepcopy(tempBlobs)
    tempBlobs2 = [x for x in blobCopy if x.name == "In"]
    temp2Blobs2 = copy.deepcopy(tempBlobs2)
    endBlobs = []
    endBlobs2 = []
    endBlobs3 = []
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
    while len(tempBlobs2) > 0:
        for b in tempBlobs2:
            if b.area > area:
                area = b.area
                bigBlob = copy.deepcopy(b)
        area = 0
        
        size = len(tempBlobs2)
        counter = 0
        while counter < size:
            counter = 0
            size = len(tempBlobs2)
            for c in tempBlobs2:
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
                    temp2Blobs2.remove(c)
                else: 
                    counter = counter + 1
                bigBlob.area = abs((bigBlob.right - bigBlob.left)*(bigBlob.top - bigBlob.bottom))
                bigBlob.x = (bigBlob.right - bigBlob.left)/2 + bigBlob.left
                bigBlob.y = (bigBlob.bottom - bigBlob.top)/2 + bigBlob.top
            tempBlobs2 = copy.deepcopy(temp2Blobs2)
        endBlobs2.append(copy.deepcopy(bigBlob))
    area = 0
    for d in endBlobs:
        for e in endBlobs2:
            if (d.left < e.left and d.right > e.right and d.top < e.top and d.bottom > e.bottom):
                endBlobs3.append(d)
    area = 0
    for f in endBlobs3:
        if f.area > area:
            area = f.area
            result = copy.deepcopy(f)
    return result
    
def main():
    global colorImage, isColorImageReady, blobsInfo, isBlobsInfoReady, pub, degree, x, y, command, oneBlob, oneBlob2, areaBall, areaGoal, alpha1, alpha2, beta1, beta2
    rospy.init_node('showBlobs', anonymous=True)
    rospy.Subscriber("/blobs", Blobs, updateBlobsInfo)
    rospy.Subscriber('/odom', Odometry, odomCallback)
    rospy.Subscriber("/v4l/camera/image_raw", Image, updateColorImage)
    bridge = CvBridge()
    cv2.namedWindow("Blob Location")
    flagit = False
    dflag = False

    while not rospy.is_shutdown() and (not isBlobsInfoReady or not isColorImageReady):
        pass

    while not rospy.is_shutdown():
        try:
            color_image = bridge.imgmsg_to_cv2(colorImage, "bgr8")
        except CvBridgeError, e:
            print e
            print "colorImage"
        rotateRight(1, 89, 3)
	if (areaBall != 0):
	    areaBall = 0
	    areaGoal = 0
	    alpha1 = 0
	    beta1 = 0
            rotateLeft(1, 89, 1)
            rotateLeft(2, 89, 1)
	   # rotateRight(1, 90, 0)
	   # rotateRight(2, 90, 0)
        else:
	    areaBall = 0
	    areaGoal = 0
	    alpha1 = 0
	    beta1 = 0
	    rotateLeft(1, 89, 0)
	    rotateLeft(2, 89, 0)
	    rotateRight(1, 89, 1)
	    rotateRight(2, 89, 1)	
	    dflag = True
       # if(tempBallDegree < 90 and tempBallDegree > 0):
	distance = 1
	move(distance, 0.2)
	areaBall = 0
	areaGoal = 0
       # if(tempBallDegree > 90 and tempBallDegree < 180):
       #     move(1, -0.2)
        if dflag:
	    rotateLeft(1, 89, 0)
	    rotateLeft(1, 89, 0)
            rotateRight(1, 89, 2)
            rotateRight(2, 89, 2)
        if not dflag:
	    rotateRight(1, 89, 0)
	    rotateRight(1, 89, 0)
            rotateLeft(1, 89, 2)
	    rotateLeft(2, 89, 2)
        oppositeknown = 180 - (180 - alpha1) - alpha2
	print "opposite known"
	print oppositeknown
	oppositeknownrad = math.radians(oppositeknown)
        print "alpha1 = "
        print  alpha1
	print "alpha2 = " 
        print  alpha2
	print "beta1 = " 
        print  beta1
	print "beta2 = " 
        print  beta2
        opBall = math.sin(math.radians(alpha2)*distance/(math.sin(oppositeknownrad)))
	print "opBall = " 
        opBall
        spBall = math.sqrt(math.pow(opBall, 2) + math.pow(distance, 2) - 2*distance*opBall*math.cos(math.radians(180 - alpha1)))
	print "spBall = "
	print  spBall
        oppositeknown2 = 180 - (180 - beta1) - beta2
	print "oppositeknown2 = " 
        print  oppositeknown2
        spGoal = math.sin(math.radians(180 - beta1))/((math.sin(math.radians(oppositeknown2))/distance))
	print "spGoal = "
	print spGoal
        goalBall = math.sqrt(math.pow(spBall,2) + math.pow(spGoal,2) - 2*spBall*spGoal*math.cos(math.radians(beta2 - alpha2)))
	print "goalBall ="
	print  goalBall
	spGoalAngle = math.asin(spGoal*math.sin(math.radians(beta2-alpha2))/goalBall)
	print "spGoalAngle = "
	print spGoalAngle
	spGoalAngle = math.degrees(spGoalAngle)
	opUnknown = 180 - (alpha1 - alpha2) - spGoalAngle
	print "opUnknown = "
	print opUnknown
	opOpBall = 180 - alpha1 - opUnknown
	print "opOpBall"
	print opOpBall
	unknown = math.sin(math.radians(opUnknown))*opBall/math.sin(math.radians(opOpBall))
	print "unknown"
	print unknown
	finalBall = math.sin(math.radians(alpha1))*opBall/math.sin(math.radians(opOpBall))
	print "finalBall"
	print finalBall
	move(distance + unknown + .1, -.2)
	rospy.sleep(2)
        if not dflag:
	    rotateRight(1, opOpBall, 0)
        if dflag:
	    rotateLeft(1, opOpBall, 0)
        move(finalBall + goalBall*.5, 1)
	rospy.sleep(2)
	break            
   #     blobsCopy = copy.deepcopy(blobsInfo)

    #    if len(blobsCopy.blobs) > 0:
     #       oneBlob = mergeBlobs(blobsCopy.blobs)
      #      cv2.rectangle(color_image, (oneBlob.left, oneBlob.top), (oneBlob.right, oneBlob.bottom), (0,255,0), 2)
       #     flagit = True
	
       # cv2.imshow("Color Image", color_image)
       # cv2.waitKey(1)
#	while (flagit):
#	    if len(blobsCopy.blobs) > 0:
#		command.linear.x = .3
#		pub.publish(command)
 #           if oneBlob.x <= 320 and oneBlob.x >= 0:
  #              command.angular.z = (320 - oneBlob.x) * .00125
#            if oneBlob.x > 320 and oneBlob.x <= 640:
 #               command.angular.z = (oneBlob.x - 320) * -.00125
#	    pub.publish(command)
 #           blobsCopy = copy.deepcopy(blobsInfo)
#
 #           if len(blobsCopy.blobs) > 0:
  #              oneBlob = mergeBlobs(blobsCopy.blobs)
   #             cv2.rectangle(color_image, (oneBlob.left, oneBlob.top), (oneBlob.right, oneBlob.bottom), (0,255,0), 2)
#	    else:
 #               flagit = False	
  #          cv2.imshow("Color Image", color_image)
   #         cv2.waitKey(1)
    #    command.angular.z = 0
#	command.linear.x = 0
 #       pub.publish(command)
  #      flagit = False

    cv2.destroyAllWindows()
 
if __name__ == '__main__':
    main()

