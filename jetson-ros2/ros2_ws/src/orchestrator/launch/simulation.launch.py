#!/usr/bin/env python3
"""
Simulation Launch File - Simulator-based autonomous system demonstration.

This system-wide launch file boots up the simulated vehicle stack:
  simulator -> path_planning -> controls

This configuration is used for development and testing without hardware,
providing a physics-based vehicle model with cone simulation.

Note: System-wide launch files should only be placed in the orchestrator package.
Individual packages may have their own launch files for smaller-scale testing.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for simulation stack."""
    
    return LaunchDescription([
        # Simulator - provides vehicle physics and cone environment
        Node(
            package='simulator',
            executable='simulator_node',
            name='simulator',
            output='screen',
        ),
        
        # Path Planning - processes cone data and generates trajectory
        Node(
            package='path_planning',
            executable='path_planning_node',
            name='path_planning',
            output='screen',
        ),
        
        # Controls - follows trajectory with pure pursuit controller
        Node(
            package='controls',
            executable='controls_node',
            name='controls',
            output='screen',
        ),
    ])

