"""Lab 1's exercise as a proper package node: drives the turtle in a square.

Same idea as 1_turtlesim/turtle_circle.py, but installed with colcon so it
runs as:  ros2 run tutorial_pkg turtle_square
"""
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist

TOPIC = '/turtle1/cmd_vel'
RATE_HZ = 10


def twist(forward=0.0, turn=0.0):
    msg = Twist()
    msg.linear.x = float(forward)
    msg.angular.z = float(turn)
    return msg


STEPS = [
    ('side', 2.0, twist(forward=1.0)),
    ('turn', 1.0, twist(turn=math.pi / 2)),
] * 4


class TurtleSquare(Node):
    def __init__(self):
        super().__init__('turtle_square')
        self.pub = self.create_publisher(Twist, TOPIC, 10)

    def run(self):
        while rclpy.ok() and self.pub.get_subscription_count() == 0:
            self.get_logger().info(f'Waiting for a subscriber on {TOPIC}...')
            rclpy.spin_once(self, timeout_sec=1.0)
        for name, seconds, msg in STEPS:
            self.get_logger().info(f'{name} ({seconds:.1f} s)')
            for _ in range(int(seconds * RATE_HZ)):
                self.pub.publish(msg)
                time.sleep(1.0 / RATE_HZ)
        self.pub.publish(twist())


def main():
    # Let Ctrl+C reach our except-block with ROS still running, so the
    # stop message below can still be published.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = TurtleSquare()
    try:
        node.run()
    except KeyboardInterrupt:
        node.pub.publish(twist())
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
