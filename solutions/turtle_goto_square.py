#!/usr/bin/env python3
"""Task T4 solution: an exact square, using the turtle's position.

Subscribes to /turtle1/pose and publishes /turtle1/cmd_vel. For each corner:
turn to face it, then drive to it, correcting the heading on the way.
This is feedback control: the command depends on where the turtle really is.
"""
import math

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

CMD_TOPIC = '/turtle1/cmd_vel'
POSE_TOPIC = '/turtle1/pose'
NODE_NAME = 'turtle_goto_square'
RATE_HZ = 10

CORNERS = [(8.5, 5.5), (8.5, 8.5), (5.5, 8.5), (5.5, 5.5)]   # a 3 m square, from the start point
CLOSE_ENOUGH = 0.05        # m: corner reached
FACING = 0.05              # rad: pointing at the corner, start driving
MAX_FORWARD = 2.0          # m/s
MAX_TURN = 2.0             # rad/s


def clamp(value, limit):
    return max(-limit, min(limit, value))


def wrap(angle):
    """Wrap an angle to -pi..pi, so the turtle turns the short way round."""
    return math.atan2(math.sin(angle), math.cos(angle))


class GoToSquare(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.pub = self.create_publisher(Twist, CMD_TOPIC, 10)
        self.sub = self.create_subscription(Pose, POSE_TOPIC, self.on_pose, 10)
        self.timer = self.create_timer(1.0 / RATE_HZ, self.on_timer)
        self.pose = None
        self.corner = 0
        self.done = False

    def on_pose(self, msg):
        self.pose = msg

    def on_timer(self):
        if self.pose is None or self.done:
            return
        goal_x, goal_y = CORNERS[self.corner]
        dx, dy = goal_x - self.pose.x, goal_y - self.pose.y
        distance = math.hypot(dx, dy)

        if distance < CLOSE_ENOUGH:
            self.get_logger().info(
                f'corner {self.corner + 1}: aimed ({goal_x:.2f}, {goal_y:.2f}), '
                f'reached ({self.pose.x:.2f}, {self.pose.y:.2f})')
            self.corner += 1
            if self.corner == len(CORNERS):
                self.done = True
                self.pub.publish(Twist())
            return

        heading_error = wrap(math.atan2(dy, dx) - self.pose.theta)
        msg = Twist()
        msg.angular.z = clamp(4.0 * heading_error, MAX_TURN)
        if abs(heading_error) < FACING:
            msg.linear.x = clamp(1.5 * distance, MAX_FORWARD)
        self.pub.publish(msg)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = GoToSquare()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.pub.publish(Twist())
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
