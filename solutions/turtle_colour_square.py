#!/usr/bin/env python3
"""Task T3 solution: a square with each side in a different colour.

Publishes geometry_msgs/Twist on /turtle1/cmd_vel to drive, and calls the
/turtle1/set_pen service before each side to change the pen colour.
"""
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen

TOPIC = '/turtle1/cmd_vel'
PEN_SERVICE = '/turtle1/set_pen'
NODE_NAME = 'turtle_colour_square'
RATE_HZ = 10

SIDE_SECONDS = 2.0                                      # at 1 m/s: 2 m sides
COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]   # red, green, blue, yellow


def twist(forward=0.0, turn=0.0):
    """Build one Twist message: forward in m/s, turn in rad/s."""
    msg = Twist()
    msg.linear.x = float(forward)
    msg.angular.z = float(turn)
    return msg


class ColourSquare(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.pub = self.create_publisher(Twist, TOPIC, 10)
        self.pen = self.create_client(SetPen, PEN_SERVICE)

    def wait_until_ready(self):
        self.get_logger().info(f'Waiting for {TOPIC} and {PEN_SERVICE}...')
        while rclpy.ok() and self.pub.get_subscription_count() == 0:
            rclpy.spin_once(self, timeout_sec=0.5)
        self.pen.wait_for_service()

    def set_colour(self, r, g, b):
        request = SetPen.Request(r=r, g=g, b=b, width=4, off=0)
        future = self.pen.call_async(request)
        rclpy.spin_until_future_complete(self, future)   # wait for turtlesim's answer

    def send(self, msg, seconds):
        period = 1.0 / RATE_HZ
        for _ in range(max(1, int(round(seconds * RATE_HZ)))):
            self.pub.publish(msg)
            time.sleep(period)

    def run(self):
        self.wait_until_ready()
        for r, g, b in COLOURS:
            self.get_logger().info(f'side in colour ({r}, {g}, {b})')
            self.set_colour(r, g, b)
            self.send(twist(forward=1.0), SIDE_SECONDS)
            self.send(twist(turn=math.pi / 2), 1.0)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = ColourSquare()
    try:
        node.run()
    except KeyboardInterrupt:
        node.send(twist(), 0.5)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
