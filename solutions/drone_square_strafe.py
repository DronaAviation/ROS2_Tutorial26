#!/usr/bin/env python3
"""Task D2 solution: a 2 m square without turning — the drone always faces the same way.

The change from sim_drone.py: twist() takes a new `left` argument (linear.y,
sideways in m/s), and STEPS flies forward, left, back and right.
"""
import time

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist

TOPIC = '/X3/gazebo/command/twist'
NODE_NAME = 'drone_square_strafe'
RATE_HZ = 10


def twist(forward=0.0, left=0.0, up=0.0, turn=0.0):
    """Build one Twist message: forward, left and up in m/s, turn in rad/s."""
    msg = Twist()
    msg.linear.x = float(forward)
    msg.linear.y = float(left)
    msg.linear.z = float(up)
    msg.angular.z = float(turn)
    return msg


# The plan: a list of (name, seconds, message) steps, played in order.
STEPS = [
    ('climb', 3.0, twist(up=0.5)),
    ('forward', 4.0, twist(forward=0.5)),     # 0.5 m/s for 4 s = 2 m
    ('hover', 1.0, twist()),                  # let it stop before the corner
    ('left', 4.0, twist(left=0.5)),
    ('hover', 1.0, twist()),
    ('back', 4.0, twist(forward=-0.5)),
    ('hover', 1.0, twist()),
    ('right', 4.0, twist(left=-0.5)),
    ('hover', 1.0, twist()),
    ('descend', 4.0, twist(up=-0.5)),
    ('hover', 1.0, twist()),
]

# What to send if you press Ctrl+C part-way: hover. Without this the drone keeps its last command.
ON_CTRL_C = twist()


class StepPublisher(Node):
    """Waits until something subscribes, then sends each step's message
    RATE_HZ times a second for that step's duration."""

    def __init__(self):
        super().__init__(NODE_NAME)
        self.pub = self.create_publisher(Twist, TOPIC, 10)

    def wait_for_subscriber(self):
        if self.pub.get_subscription_count() == 0:
            self.get_logger().info(f'Waiting for a subscriber on {TOPIC}...')
            while rclpy.ok() and self.pub.get_subscription_count() == 0:
                rclpy.spin_once(self, timeout_sec=0.5)

    def send(self, msg, seconds):
        period = 1.0 / RATE_HZ
        for _ in range(max(1, int(round(seconds * RATE_HZ)))):
            self.pub.publish(msg)
            time.sleep(period)

    def run(self):
        self.wait_for_subscriber()
        for name, seconds, msg in STEPS:
            self.get_logger().info(f'{name} ({seconds:.1f} s)')
            self.send(msg, seconds)

    def on_ctrl_c(self):
        self.send(ON_CTRL_C, 0.5)


def main():
    # Let Ctrl+C reach our except-block with ROS still running, so the
    # stop message below can still be published.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = StepPublisher()
    try:
        node.run()
    except KeyboardInterrupt:
        node.on_ctrl_c()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
