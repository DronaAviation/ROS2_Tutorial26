"""A minimal subscriber: prints whatever arrives on /chatter."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.sub = self.create_subscription(String, '/chatter', self.on_msg, 10)

    def on_msg(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main():
    rclpy.init()
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
