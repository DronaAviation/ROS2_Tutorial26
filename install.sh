#!/usr/bin/env bash
# One-shot installer for the ROS 2 Tutorial on Ubuntu 22.04.
# Run:   bash ~/ROS2_Tutorial/install.sh
# Safe to re-run: every step is idempotent. Takes 15–40 minutes depending on the connection.
# What it does is written out step by step in README.md, section 2; this script just runs those commands.
set -e

step() { echo; echo "==================== $1"; }

if ! grep -q 'VERSION_ID="22.04"' /etc/os-release; then
    echo "This installer is for Ubuntu 22.04. Found: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
    exit 1
fi

step "1/8  Locale (UTF-8)"
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

step "2/8  Enable the Universe repository and install curl"
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe
sudo apt update && sudo apt install -y curl

step "3/8  Add the ROS 2 apt source (ros2-apt-source package)"
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

step "4/8  Upgrade the system, then install ROS 2 Humble desktop + dev tools"
sudo apt update
sudo apt upgrade -y            # required on 22.04 before ROS 2: see the warning in README.md, section 2.1
sudo apt install -y ros-humble-desktop ros-dev-tools

step "5/8  Lab 2: Gazebo (Fortress) and the ROS <-> Gazebo bridge"
sudo apt install -y ros-humble-ros-gz ros-humble-teleop-twist-keyboard

step "6/8  Lab 3 + your-own-package (section 10) dependencies"
sudo apt install -y python3-colcon-common-extensions python3-pip
pip3 install --user pynput

step "7/8  Lab 3: build the Pluto workspace in ~/pluto_ws"
source /opt/ros/humble/setup.bash
mkdir -p ~/pluto_ws/src
cd ~/pluto_ws/src
[ -d pluto_ros2_package ] || git clone https://github.com/DronaAviation/pluto_ros2_package.git
cd ~/pluto_ws
colcon build --symlink-install

step "8/8  Lab 2: download the drone models so the first Gazebo start is fast"
ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/X3 UAV" || echo "(model download failed; Gazebo will download it on first start instead)"
ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/X4 UAV Config 1" || true

echo
echo "Done. Now run:   bash ~/ROS2_Tutorial/check_setup.sh"
echo "If every check passes, open a new terminal and start with README.md."
