import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    office_bot_share = get_package_share_directory('office_bot')
    nav2_bringup_share = get_package_share_directory('nav2_bringup')

    default_map = os.path.join(office_bot_share, 'maps', 'my_map.yaml')
    default_params = os.path.join(office_bot_share, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(nav2_bringup_share, 'rviz', 'nav2_default_view.rviz')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to map yaml file to load'
    )

    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Full path to the ROS 2 parameters file to use for all Nav2 nodes'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz2'
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz config file'
    )

    # Launch Nav2 Bringup (localization + navigation stack)
    nav2_bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_share, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': LaunchConfiguration('params_file'),
            'autostart': LaunchConfiguration('autostart'),
            'use_composition': 'True',
            'use_respawn': 'False',
        }.items(),
    )

    # Launch RViz2 with pre-configured Nav2 view (Goal tool, costmaps, paths)
    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_share, 'launch', 'rviz_launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'rviz_config': LaunchConfiguration('rviz_config'),
        }.items(),
    )

    return LaunchDescription([
        map_arg,
        params_arg,
        use_sim_time_arg,
        autostart_arg,
        use_rviz_arg,
        rviz_config_arg,
        nav2_bringup_cmd,
        rviz_cmd,
    ])
