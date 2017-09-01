#!/usr/bin/env python
import os
import rospkg
import roslib, rospy
import subprocess, shlex
from datetime import datetime
from std_msgs.msg import String
from radio_services.srv import InstructionAndStringWithAnswer

first_standing_time = 0
last_sitting_time = 0
ros_visual_topic = ''
sitting = False
running = False
rospack = None
logs_path = ''
robot_id = 0
sub = None

def init():
    global robot_id, logs_path, ros_visual_topic
    global running, sub, rospack
    rospy.init_node('ros_visual_wrapper')
    ros_visual_topic = rospy.get_param("~ros_visual_topic", "/classifier/result")
    robot_id = rospy.get_param("~robot_id", 0)
    rospack = rospkg.RosPack()
    rospy.Service('/ros_visual_wrapper/node_state_service', InstructionAndStringWithAnswer, nodeStateCallback)
    if running:
        sub = rospy.Subscriber(ros_visual_topic, String, eventCallback)
    while not rospy.is_shutdown():
        rospy.spin()

def nodeStateCallback(req):
    global running, sub, logs_path, ros_visual_topic
    if req.command == 0 and running:
        running = False
        sub.unregister()
        print 'Stopped ros visual wrapper!'
    elif req.command == 1 and not running:
        dt = datetime.now()
        current_name = req.name
        filename = 'official_log_chair_'+current_name+'_'+datetime.today().strftime("%d-%m-%Y")+'_'+dt.strftime("%H%M%S")+'.csv'
        logs_path = rospack.get_path('ros_visual_wrapper') + '/logs/' + filename
        sub = rospy.Subscriber(ros_visual_topic, String, eventCallback)
        running = True
        with open(logs_path,'ab+') as f:
            f.write("Sitting-Standing time, Event\n")
        print 'Started ros visual wrapper!'
    return running

def eventCallback(msg):
    global logs_path, robot_id, last_sitting_time, first_standing_time, sitting
    dt = datetime.now()
    if msg.data == 'sit':
        sitting = True
        last_sitting_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
    elif 'stand' in msg.data and sitting:
        sitting = False
        first_standing_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
        with open(logs_path,'ab+') as f:
            f.write(str((first_standing_time - last_sitting_time) / 1E6)+',')
            f.write(msg.data+'\n')
    else:
        sitting = False

if __name__ == '__main__':
    init()
