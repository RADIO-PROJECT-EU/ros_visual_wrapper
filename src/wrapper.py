#!/usr/bin/env python
import os
import roslib, rospy
from std_msgs.msg import String
from datetime import datetime
import rospkg
import subprocess, shlex

ros_visual_topic = ''
logs_path = ''
robot_id = 0
sitting = False
last_sitting_time = 0
first_standing_time = 0

def init():
    global robot_id, logs_path, ros_visual_topic
    dt = datetime.now()
    start_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
    rospy.init_node('ros_visual_wrapper')
    ros_visual_topic = rospy.get_param("~ros_visual_topic", "/classifier/result")
    robot_id = rospy.get_param("~robot_id", 0)
    rospy.Subscriber(ros_visual_topic, String, eventCallback)
    rospack = rospkg.RosPack()
    logs_path = rospack.get_path('ros_visual_wrapper')+'/logs/'
    while not rospy.is_shutdown():
        rospy.spin()

def eventCallback(msg):
    global logs_path, robot_id, last_sitting_time, first_standing_time, sitting
    dt = datetime.now()

    first_time = False
    if not os.path.isfile(logs_path+'official_log_chair_'+datetime.today().strftime("%d-%m-%Y")+'.csv'):
        first_time = True
    if msg.data == 'sit':
        sitting = True
        last_sitting_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
    elif msg.data == 'stand' and sitting:
        sitting = False
        first_standing_time = dt.minute*60000000 + dt.second*1000000 + dt.microsecond
        with open(logs_path+'official_log_chair_'+datetime.today().strftime("%d-%m-%Y")+'.csv','ab+') as f:
            if first_time:
                f.write("Sitting-Standing time\n")
            f.write(str((first_standing_time - last_sitting_time) / 1E6)+"\n")
            #f.write('## Robot ID ##\n')
            #f.write(str(robot_id)+'\n')
            #f.write('## Sit-Stand ##\n')
            #f.write(str(datetime.now().strftime("[%d-%m-%Y %H:%M:%S] ")) + str(msg.time_needed) + ' seconds\n')
            #f.write('---\n')
        
        # Uncomment the following line if we need to log only 1 sit-stand event
        #suicide()
    else:
        sitting = False
    #else:
    #    suicide()

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