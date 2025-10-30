from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    map_yaml = LaunchConfiguration('map_yaml')
    world = LaunchConfiguration('world_frame')
    mapf = LaunchConfiguration('map_frame')
    base = LaunchConfiguration('base_frame')
    cone_scale = LaunchConfiguration('cone_scale')

    return LaunchDescription([
        DeclareLaunchArgument('map_yaml', description='Path to FSG map YAML'),
        DeclareLaunchArgument('world_frame', default_value='world'),
        DeclareLaunchArgument('map_frame', default_value='map'),
        DeclareLaunchArgument('base_frame', default_value='base_link'),
        DeclareLaunchArgument('cone_scale', default_value='0.4'),

        # 1) publish global cones as MarkerArray
        Node(
            package='sim_core',
            executable='publish_cone_map',
            name='global_cone_markers',
            parameters=[{
                'map_yaml': map_yaml,
                'cone_scale': cone_scale,
                'world_frame': world,
            }],
            output='screen'
        ),

        # 2) keep map->base_link in sync using /vehicle_pose
        Node(
            package='sim_core',
            executable='pose_to_tf',
            name='pose_to_tf',
            parameters=[{
                'pose_topic': '/vehicle_pose',
                'map_frame': mapf,
                'base_frame': base,
            }],
            output='screen'
        ),
    ])
