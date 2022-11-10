#!/usr/bin/env python
import rclpy 
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from ackermann_msgs.msg import AckermannDriveStamped

import numpy as np

# TODO: import ROS msg types and libraries

class Safety(Node):
    """
    The class that handles emergency braking.
    """
    def __init__(self):
        """
        One publisher should publish to the /brake topic with a AckermannDriveStamped brake message.

        One publisher should publish to the /brake_bool topic with a Bool message.

        You should also subscribe to the /scan topic to get the LaserScan messages and
        the /odom topic to get the current speed of the vehicle.

        The subscribers should use the provided odom_callback and scan_callback as callback methods

        NOTE that the x component of the linear velocity in odom is the speed
        """
        super().__init__('safety_node')
        self.speed = 0
        self.odom_sub_ = self.create_subscription(Odometry, '/ego_racecar/odom', self.odom_callback, 10)
        self.scan_sub_ = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.drive_pub_ = self.create_publisher(AckermannDriveStamped, '/cmd_vel', 10)

    def odom_callback(self, odom_msg):
        self.speed = odom_msg.twist.twist.linear.x

    def scan_callback(self, scan_msg):
        # TODO: calculate TTC
        angle_min = scan_msg.angle_min
        angle_max = scan_msg.angle_max
        ranges = np.array(scan_msg.ranges)
        cos_theta = np.cos(np.linspace(angle_min, angle_max, num=len(ranges)))
        # print(angle_min,angle_max,ranges,cos_theta)
        for item in cos_theta:
            print(item)
        time_to_collision = np.argmin(np.abs(ranges/(self.speed*cos_theta)))

        if time_to_collision <= 1:
            vel = AckermannDriveStamped()
            vel.drive.speed = 0
            self.drive_pub_.publish(vel)

        # TODO: publish brake message and publish controller bool


def main(args=None):
    rclpy.init(args=args)
    sn = Safety()
    rclpy.spin(sn)
    rclpy.shutdown()
if __name__ == '__main__':
    main()