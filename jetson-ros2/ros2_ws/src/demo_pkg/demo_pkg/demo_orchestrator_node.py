#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class OrchestratorNode(Node):
    def __init__(self):
        super().__init__('orchestrator_node')
        self.get_logger().info('Orchestrator node started - managing system state')
        self.timer = self.create_timer(2.0, self.timer_callback)
        
    def timer_callback(self):
        self.get_logger().info('Orchestrator: System running...')

def main(args=None):
    rclpy.init(args=args)
    node = OrchestratorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()