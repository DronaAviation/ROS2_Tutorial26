#!/usr/bin/env python3
"""Lab 3 subscriber: shows the drone's camera.

The drone publishes images on /plutocamera/image_raw (via plutocam_publisher);
this script subscribes and shows them in a window called "Pluto camera".
Same direction as turtle_pose.py: the robot talks, we listen.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

TOPIC = '/plutocamera/image_raw'
NODE_NAME = 'pluto_camera'
WINDOW = 'Pluto camera'


class CameraViewer(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, TOPIC, self.on_image, 10)
        self.get_logger().info(f'Waiting for images on {TOPIC}...')

    def on_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow(WINDOW, frame)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = CameraViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
