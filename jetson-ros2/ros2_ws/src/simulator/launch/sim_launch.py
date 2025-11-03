from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

import os

def generate_launch_description():
    pkg = 'simulator'
    # inside container you mounted /root/ws → /root/ws/src/...
    default_map = '/root/ws/src/simulator/maps/global_cone_maps/fsg24.yaml'

    map_yaml = LaunchConfiguration('map_yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'map_yaml',
            default_value=default_map,
            description='Global cone map (FSG YAML)'
        ),

        # 0) static world -> map
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='world_to_map',
            arguments=['0', '0', '0', '0', '0', '0', 'world', 'map'],
            output='screen',
        ),

        # 1) vehicle dynamics: /control_action -> /vehicle_pose (frame=map)
        Node(
            package=pkg,
            executable='vehicle_dynamics',
            name='vehicle_dynamics',
            output='screen',
            parameters=[{
                # tune here if you want
                'dt': 0.01,
            }]
        ),

        # 2) turn /vehicle_pose -> TF (map -> base_link)
        Node(
            package=pkg,
            executable='pose_to_tf',
            name='pose_to_tf',
            output='screen',
            parameters=[{
                'pose_topic': '/vehicle_pose',
                'map_frame': 'map',
                'base_frame': 'base_link',
            }]
        ),

        # 3) publish global map as MarkerArray
        Node(
            package=pkg,
            executable='publish_cone_map',
            name='global_cone_markers',
            output='screen',
            parameters=[{
                'map_yaml': map_yaml,
                'world_frame': 'map',
                'cone_scale': 0.4,
            }]
        ),

        # 4) fake perception in base_link (10 Hz)
        Node(
            package=pkg,
            executable='mimic_perception',
            name='mimic_perception',
            output='screen',
        ),
    ])
