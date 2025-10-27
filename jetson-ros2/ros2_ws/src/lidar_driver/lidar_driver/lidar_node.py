#!/usr/bin/env python3
"""
Skeleton LiDAR Driver Node

Publishes dummy PointCloud2 data to /perception/lidar_data for testing.
This will be replaced with the full Ouster LiDAR driver implementation.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import numpy as np
import struct


class LidarDriverNode(Node):
    """Skeleton node that publishes dummy LiDAR data for testing pipeline."""
    
    def __init__(self):
        super().__init__('lidar_driver')
        
        # Publisher to namespaced topic
        self.publisher_ = self.create_publisher(
            PointCloud2, 
            '/perception/lidar_data', 
            10
        )
        
        # Simulate 10Hz LiDAR
        self.timer = self.create_timer(0.1, self.publish_dummy_pointcloud)
        
        self.get_logger().info('LiDAR Driver (skeleton) started - publishing to /perception/lidar_data')
    
    def publish_dummy_pointcloud(self):
        """Publish a dummy point cloud with cone-like pattern."""
        # Create a simple corridor pattern (similar to simulator)
        points = []
        
        # Generate points in a corridor pattern
        for x in np.linspace(2.0, 20.0, 10):
            # Left side cones
            points.append([x, 1.5, 0.3, 100.0])
            # Right side cones
            points.append([x, -1.5, 0.3, 100.0])
            # Some ground points
            for _ in range(5):
                points.append([
                    x + np.random.uniform(-0.5, 0.5),
                    np.random.uniform(-2.0, 2.0),
                    np.random.uniform(-0.1, 0.1),
                    50.0
                ])
        
        points_array = np.array(points, dtype=np.float32)
        
        # Create PointCloud2 message
        msg = PointCloud2()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        
        # Define fields: x, y, z, intensity
        msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        
        msg.height = 1
        msg.width = len(points_array)
        msg.is_bigendian = False
        msg.point_step = 16  # 4 floats * 4 bytes
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = True
        
        # Pack data
        buffer = []
        for point in points_array:
            buffer.append(struct.pack('ffff', point[0], point[1], point[2], point[3]))
        msg.data = b''.join(buffer)
        
        self.publisher_.publish(msg)
        self.get_logger().debug(f'Published PointCloud2 with {len(points_array)} points')


def main(args=None):
    rclpy.init(args=args)
    node = LidarDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down LiDAR driver node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

