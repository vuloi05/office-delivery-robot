import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('office_bot')
    default_map = os.path.join(pkg_share, 'maps', 'my_map.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to map yaml file to load'
    )

    map_yaml_file = LaunchConfiguration('map')

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml_file,
            'use_sim_time': True
        }]
    )

    # AMCL node với cấu hình vị trí ban đầu tự động (tránh lỗi Frame [map] does not exist)
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'base_frame_id': 'base_footprint',
            'odom_frame_id': 'odom',
            'global_frame_id': 'map',
            'set_initial_pose': True,
            'initial_pose': {
                'x': -2.0,
                'y': -0.5,
                'z': 0.0,
                'yaw': 0.0
            }
        }]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        map_arg,
        map_server_node,
        amcl_node,
        lifecycle_manager_node,
        rviz_node
    ])
