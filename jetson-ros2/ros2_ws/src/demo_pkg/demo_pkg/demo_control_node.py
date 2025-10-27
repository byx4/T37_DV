#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self.get_logger().info('Control node started - sending commands to actuators')
        self.timer = self.create_timer(0.5, self.timer_callback)
        
    def timer_callback(self):
        self.get_logger().info('Control: Publishing steering/throttle commands...')

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
