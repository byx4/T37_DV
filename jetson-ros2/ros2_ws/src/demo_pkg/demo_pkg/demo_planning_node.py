#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class PlanningNode(Node):
    def __init__(self):
        super().__init__('planning_node')
        self.get_logger().info('Planning node started - generating trajectories')
        self.timer = self.create_timer(1.5, self.timer_callback)
        
    def timer_callback(self):
        self.get_logger().info('Planning: Computing optimal path...')

def main(args=None):
    rclpy.init(args=args)
    node = PlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
