#!/usr/bin/env python3
"""Lab 3 exercise: your own telemetry server.

The Pluto's sensor data does NOT arrive on a topic. plutonode is a service
CLIENT: it puts roll, pitch, yaw, altitude, battery (and more) into a
custom_msgs/srv/PlutoPilot request and calls /pluto_service many times a
second. Whoever runs the /pluto_service SERVER receives the data.

plutoserver is such a server (it prints everything). This script is a
smaller one: it prints only battery and altitude, twice a second.

Run it INSTEAD of plutoserver (stop T2 first): only one server per service name.
"""
import rclpy
from rclpy.node import Node
from custom_msgs.srv import PlutoPilot

SERVICE = 'pluto_service'
NODE_NAME = 'pluto_telemetry'


class Telemetry(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.srv = self.create_service(PlutoPilot, SERVICE, self.on_request)
        self.get_logger().info(f'Serving {SERVICE}; waiting for plutonode to call it...')

    def on_request(self, request, response):
        self.get_logger().info(
            f'battery={request.battery:.2f} V  altitude={request.alt:.2f}  '
            f'roll={request.roll}  pitch={request.pitch}  yaw={request.yaw}',
            throttle_duration_sec=0.5)
        # The response fields are RC values; plutonode ignores the reply. Leave them 0.
        return response


def main():
    rclpy.init()
    node = Telemetry()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
