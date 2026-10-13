"""Starts turtlesim AND the square driver in one command:  ros2 launch tutorial_pkg turtle_square.launch.py"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim', output='screen'),
        Node(package='tutorial_pkg', executable='turtle_square', name='turtle_square', output='screen'),
    ])
