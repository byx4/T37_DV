#!/usr/bin/env python3
"""
Push Test Launch File - Full perception-based pipeline for vehicle testing.

This system-wide launch file boots up the complete real vehicle stack:
  lidar_driver -> perception -> path_planning -> controls

This configuration is used for push testing and validates end-to-end
communication between all hardware components in the autonomous system.

Note: System-wide launch files should only be placed in the orchestrator package.
Individual packages may have their own launch files for smaller-scale testing.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description with all pipeline nodes."""
    
    return LaunchDescription([
        # LiDAR Driver - publishes to /perception/lidar_data
        Node(
            package='lidar_driver',
            executable='lidar_node',
            name='lidar_driver',
            output='screen',
            parameters=[],
        ),
        
        # Perception - subscribes to /perception/lidar_data, publishes to /perception/local_cones
        Node(
            package='perception',
            executable='perception_node',
            name='perception',
            output='screen',
            parameters=[],
        ),
        
        # Path Planning - subscribes to /perception/local_cones, publishes to /planning/trajectory
        Node(
            package='path_planning',
            executable='path_planning_node',
            name='path_planning',
            output='screen',
            parameters=[],
        ),
        
        # Controls - subscribes to /planning/trajectory, publishes to /controls/command
        Node(
            package='controls',
            executable='controls_node',
            name='controls',
            output='screen',
            parameters=[],
        ),
    ])

