#!/usr/bin/env python3
"""Lab 2 subscriber: prints where the simulated X3 drone is.

Subscribes to nav_msgs/Odometry on /model/x3/odometry (bridged from Gazebo).
Gazebo publishes about 50 messages a second; we print at most two a second.
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

TOPIC = '/model/x3/odometry'
NODE_NAME = 'sim_drone_pose'


class PosePrinter(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        # Ask ROS to call on_odom for every message on TOPIC.
        self.sub = self.create_subscription(Odometry, TOPIC, self.on_odom, 10)

    def on_odom(self, msg):
        p = msg.pose.pose.position
        v = msg.twist.twist.linear
        self.get_logger().info(
            f'x={p.x:.2f}  y={p.y:.2f}  height={p.z:.2f} m  climb rate={v.z:+.2f} m/s',
            throttle_duration_sec=0.5)


def main():
    rclpy.init()
    node = PosePrinter()
    try:
        rclpy.spin(node)          # wait here and keep taking calls, until Ctrl+C
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
