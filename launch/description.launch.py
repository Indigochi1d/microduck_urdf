"""Publish the Microduck robot_description and TF tree via robot_state_publisher."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    collision = LaunchConfiguration('collision')
    xacro_file = PathJoinSubstitution(
        [FindPackageShare('microduck_urdf'), 'urdf', 'microduck.urdf.xacro'])
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' collision:=', collision]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('collision', default_value='true',
                              description='Include collision meshes in the URDF'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
    ])
