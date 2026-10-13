#!/usr/bin/env python3
"""Lab 3 publisher: take off, hover, land, disarm — on a real Pluto drone.

The same StepPublisher as Labs 1 and 2, with a different topic, message
and plan. One difference that matters: Ctrl+C LANDS the drone, then disarms,
instead of just stopping.

SAFETY: run this the first time with the propellers removed, watching
`ros2 topic echo /drone_command` in T4. Never run it while the keyboard
control (drone_comb.launch.py) is running.
"""
import time

import rclpy
from rclpy.node import Node
from custom_msgs.msg import PlutoMsg

TOPIC = '/drone_command'
NODE_NAME = 'pluto_flight'
RATE_HZ = 10

# Stick values: 1000..2000, 1500 = centre.  rc_aux4: 1500 = armed, 1200 = disarmed.
# command_type: 0 = none, 1 = take off, 2 = land.  Never set trim_roll / trim_pitch.
ARMED, DISARMED = 1500, 1200
CMD_NONE, CMD_TAKEOFF, CMD_LAND = 0, 1, 2


def pluto(throttle=1500, aux4=ARMED, command=CMD_NONE):
    """Build one PlutoMsg with every rc_ field given (a missing field is sent as 0)."""
    msg = PlutoMsg()
    msg.rc_roll = 1500
    msg.rc_pitch = 1500
    msg.rc_yaw = 1500
    msg.rc_throttle = int(throttle)
    msg.rc_aux1 = 1500
    msg.rc_aux2 = 1500
    msg.rc_aux3 = 1500
    msg.rc_aux4 = int(aux4)
    msg.command_type = int(command)
    return msg


LAND_SECONDS = 4.0   # make this longer if the drone disarms before it touches down

# The plan.
STEPS = [
    ('idle', 1.0, pluto(aux4=DISARMED)),
    ('take off and hover', 5.0, pluto(aux4=ARMED, command=CMD_TAKEOFF)),
    ('land', LAND_SECONDS, pluto(aux4=ARMED, command=CMD_LAND)),
    ('disarm', 1.0, pluto(throttle=1300, aux4=DISARMED)),
]


class StepPublisher(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.pub = self.create_publisher(PlutoMsg, TOPIC, 10)

    def wait_for_subscriber(self):
        if self.pub.get_subscription_count() == 0:
            self.get_logger().info(f'Waiting for a subscriber on {TOPIC}...')
            while rclpy.ok() and self.pub.get_subscription_count() == 0:
                rclpy.spin_once(self, timeout_sec=0.5)

    def send(self, msg, seconds):
        """Publish msg RATE_HZ times a second for `seconds`.

        A one-off command (command_type 1 or 2) is sent in the FIRST message
        only; the rest of the step repeats the same sticks with command_type 0.
        plutonode forwards each non-zero command_type it receives to the drone,
        so repeating it 10 times a second would re-send take-off or land."""
        period = 1.0 / RATE_HZ
        ticks = max(1, int(round(seconds * RATE_HZ)))
        self.pub.publish(msg)
        time.sleep(period)
        if msg.command_type != CMD_NONE:
            rest = PlutoMsg()
            for f in msg.get_fields_and_field_types():
                setattr(rest, f, getattr(msg, f))
            rest.command_type = CMD_NONE
            msg = rest
        for _ in range(ticks - 1):
            self.pub.publish(msg)
            time.sleep(period)

    def run(self):
        self.wait_for_subscriber()
        for name, seconds, msg in STEPS:
            self.get_logger().info(f'{name} ({seconds:.1f} s)')
            self.send(msg, seconds)

    def landing(self):
        """What Ctrl+C does: land, wait for it, then disarm."""
        self.get_logger().info('Ctrl+C: landing')
        self.send(pluto(aux4=ARMED, command=CMD_LAND), LAND_SECONDS)
        self.get_logger().info('disarm')
        self.send(pluto(throttle=1300, aux4=DISARMED), 1.0)


def main():
    rclpy.init()
    node = StepPublisher()
    try:
        node.run()
    except KeyboardInterrupt:
        node.landing()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
