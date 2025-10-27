#!/usr/bin/env python3
"""
Skeleton Perception Node

Subscribes to /perception/lidar_data and publishes cone detections to /perception/local_cones.
This will be replaced with the full perception pipeline implementation.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
from interfaces.msg import Cone, ConeArray
import numpy as np


class PerceptionNode(Node):
    """Skeleton node that converts LiDAR data to cone detections."""
    
    def __init__(self):
        super().__init__('perception')
        
        # Subscribe to LiDAR data
        self.subscription = self.create_subscription(
            PointCloud2,
            '/perception/lidar_data',
            self.lidar_callback,
            10
        )
        
        # Publish cone detections
        self.publisher_ = self.create_publisher(
            ConeArray,
            '/perception/local_cones',
            10
        )
        
        self.get_logger().info('Perception (skeleton) started')
        self.get_logger().info('  Subscribing to: /perception/lidar_data')
        self.get_logger().info('  Publishing to: /perception/local_cones')
    
    def lidar_callback(self, msg: PointCloud2):
        """Process LiDAR data and extract cone positions."""
        t_start = self.get_clock().now()
        
        # Parse PointCloud2 message
        try:
            points_list = []
            for point in point_cloud2.read_points(
                msg, 
                field_names=('x', 'y', 'z', 'intensity'), 
                skip_nans=True
            ):
                points_list.append([point[0], point[1], point[2], point[3]])
            
            if len(points_list) == 0:
                self.get_logger().warning('Received empty PointCloud2')
                return
            
            points = np.array(points_list, dtype=np.float32)
            
        except Exception as e:
            self.get_logger().error(f'Failed to parse PointCloud2: {e}')
            return
        
        # Dummy processing: Simple clustering by finding high points
        # In reality, this will be the full perception pipeline
        cones = self.dummy_cone_detection(points)
        
        # Publish cone detections
        cone_array = ConeArray()
        cone_array.header = Header()
        cone_array.header.stamp = self.get_clock().now().to_msg()
        cone_array.header.frame_id = 'base_link'
        cone_array.cones = cones
        
        self.publisher_.publish(cone_array)
        
        t_end = self.get_clock().now()
        processing_time = (t_end - t_start).nanoseconds / 1e6  # Convert to ms
        
        self.get_logger().info(
            f'Processed {len(points)} points -> {len(cones)} cones '
            f'({processing_time:.1f}ms)'
        )
    
    def dummy_cone_detection(self, points: np.ndarray) -> list:
        """
        Dummy cone detection for skeleton testing.
        
        This will be replaced with the full perception pipeline:
        - Preprocessing (bounds filtering)
        - Ground filtering
        - Clustering (DBSCAN)
        - Cone classification
        """
        cones = []
        
        # Simple approach: Find points with z > 0.2 (above ground)
        # and cluster them by proximity
        elevated = points[points[:, 2] > 0.2]
        
        if len(elevated) == 0:
            return cones
        
        # Very naive clustering: group by x position
        x_positions = np.unique(np.round(elevated[:, 0]))
        
        for x in x_positions:
            # Find points near this x
            mask = np.abs(elevated[:, 0] - x) < 1.0
            cluster = elevated[mask]
            
            if len(cluster) > 0:
                # Use centroid
                cx = float(np.mean(cluster[:, 0]))
                cy = float(np.mean(cluster[:, 1]))
                cz = float(np.mean(cluster[:, 2]))
                
                # Simple tall/short classification
                z_range = np.max(cluster[:, 2]) - np.min(cluster[:, 2])
                is_tall = bool(z_range > 0.35)  # Convert to Python bool
                
                cone = Cone()
                cone.x = cx
                cone.y = cy
                cone.is_tall = is_tall
                cones.append(cone)
        
        return cones


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down perception node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

