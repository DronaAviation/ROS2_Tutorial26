"""Starts the talker and the listener together:  ros2 launch tutorial_pkg talker_listener.launch.py"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='tutorial_pkg', executable='talker', name='talker', output='screen'),
        Node(package='tutorial_pkg', executable='listener', name='listener', output='screen'),
    ])
