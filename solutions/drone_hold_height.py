#!/usr/bin/env python3
"""Task D4 solution: climb to exactly TARGET_HEIGHT, hold it, then land.

Subscribes to nav_msgs/Odometry on /model/x3/odometry and publishes
geometry_msgs/Twist on /X3/gazebo/command/twist. The climb speed depends on
how far the drone still has to go: feedback control.

Needs the two-topic bridge from step 2.10.
"""
import time

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

CMD_TOPIC = '/X3/gazebo/command/twist'
ODOM_TOPIC = '/model/x3/odometry'
NODE_NAME = 'drone_hold_height'
RATE_HZ = 10

TARGET_HEIGHT = 2.0        # m
GAIN = 1.0                 # climb speed (m/s) per metre still to go
MAX_SPEED = 0.5            # m/s
CLOSE_ENOUGH = 0.03        # m: "reached" the target
HOLD_SECONDS = 5.0
GROUND = 0.10              # m: below this we have landed (the drone sits at 0.05)


def up(speed):
    msg = Twist()
    msg.linear.z = max(-MAX_SPEED, min(MAX_SPEED, float(speed)))
    return msg


class HoldHeight(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.pub = self.create_publisher(Twist, CMD_TOPIC, 10)
        self.sub = self.create_subscription(Odometry, ODOM_TOPIC, self.on_odom, 10)
        self.timer = self.create_timer(1.0 / RATE_HZ, self.on_timer)
        self.height = None
        self.phase = 'climb'
        self.hold_until = None

    def on_odom(self, msg):
        self.height = msg.pose.pose.position.z

    def set_phase(self, phase):
        self.phase = phase
        self.get_logger().info(f'{phase} (height {self.height:.2f} m)')

    def on_timer(self):
        if self.height is None:
            return
        error = TARGET_HEIGHT - self.height
        self.get_logger().info(f'height={self.height:.2f} m', throttle_duration_sec=1.0)

        if self.phase == 'climb':
            self.pub.publish(up(GAIN * error))
            if abs(error) < CLOSE_ENOUGH:
                self.set_phase('hold')
                self.hold_until = time.monotonic() + HOLD_SECONDS
        elif self.phase == 'hold':
            self.pub.publish(up(GAIN * error))        # keep correcting, so it stays at the target
            if time.monotonic() > self.hold_until:
                self.set_phase('land')
        elif self.phase == 'land':
            self.pub.publish(up(-MAX_SPEED))
            if self.height < GROUND:
                self.pub.publish(up(0.0))
                self.set_phase('done')


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = HoldHeight()
    try:
        while rclpy.ok() and node.phase != 'done':
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.pub.publish(up(0.0))                     # hover, as in sim_drone.py
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
