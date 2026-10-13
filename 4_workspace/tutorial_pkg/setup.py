import os
from glob import glob
from setuptools import setup

package_name = 'tutorial_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files so `ros2 launch tutorial_pkg ...` can find them
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Drona Aviation',
    maintainer_email='commongpt@dronaaviation.com',
    description='Tutorial package: a talker, a listener, and a launch file that starts both.',
    license='MIT',
    tests_require=['pytest'],
    # Each line here becomes a `ros2 run tutorial_pkg <name>` command
    entry_points={
        'console_scripts': [
            'talker = tutorial_pkg.talker:main',
            'listener = tutorial_pkg.listener:main',
            'turtle_square = tutorial_pkg.turtle_square:main',
        ],
    },
)
