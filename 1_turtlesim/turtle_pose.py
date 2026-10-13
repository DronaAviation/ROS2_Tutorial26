#!/usr/bin/env python3
"""Lab 1 subscriber: prints where the turtle is.

Subscribes to turtlesim/Pose on /turtle1/pose. Turtlesim publishes about
62 messages a second; we print at most two a second.
"""
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

TOPIC = '/turtle1/pose'
NODE_NAME = 'turtle_pose'


class PosePrinter(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        # Ask ROS to call on_pose for every message on TOPIC.
        self.sub = self.create_subscription(Pose, TOPIC, self.on_pose, 10)

    def on_pose(self, msg):
        self.get_logger().info(
            f'x={msg.x:.2f}  y={msg.y:.2f}  heading={msg.theta:.2f} rad',
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
