#!/usr/bin/env python
import roslib, rospy
from decision_making.msg import Event
from datetime import datetime
import rospkg
import subprocess, shlex

ros_visual_topic = ''
logs_path = ''
robot_id = 0

def init():
    global robot_id, logs_path, ros_visual_topic
    dt = datetime.now()
    start_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
    print "start_time = ", start_time
    rospy.init_node('ros_visual_wrapper')
    ros_visual_topic = rospy.get_param("~ros_visual_topic", "/decision_making/events")
    robot_id = rospy.get_param("~robot_id", 0)
    rospy.Subscriber(ros_visual_topic, Event, eventCallback)
    rospack = rospkg.RosPack()
    logs_path = rospack.get_path('ros_visual_wrapper')+'/logs/'
    while not rospy.is_shutdown():
        rospy.spin()

def eventCallback(msg):
    global logs_path, robot_id
    if msg.event == 3:
        with open(logs_path+'official_log_'+datetime.today().strftime("%d-%m-%Y")+'.log','ab+') as f:
            f.write('## Robot ID ##\n')
            f.write(str(robot_id)+'\n')
            f.write('## Sit-Stand ##\n')
            f.write(str(datetime.now().strftime("[%d-%m-%Y %H:%M:%S] ")) + str(msg.time_needed) + ' seconds\n')
            f.write('---\n')
    else:
        suicide()

def suicide():
    print 'Killing ros_visual'
    command = "rosnode kill decision_making"
    command = shlex.split(command)
    subprocess.Popen(command)
    command = "rosnode kill fusion"
    command = shlex.split(command)
    subprocess.Popen(command)
    command = "rosnode kill chroma"
    command = shlex.split(command)
    subprocess.Popen(command)
    command = "rosnode kill depth"
    command = shlex.split(command)
    subprocess.Popen(command)
    print 'Killing myself'
    rospy.signal_shutdown("This is the end.")

if __name__ == '__main__':
    init()