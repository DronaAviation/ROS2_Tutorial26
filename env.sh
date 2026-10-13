#!/usr/bin/env bash
# The setup line. Run in EVERY new terminal:   source ~/ROS2_Tutorial/env.sh
#
# 1. Loads ROS 2 Humble
# 2. Loads the Pluto drone packages (Lab 3)
# 3. Sets ROS_LOCALHOST_ONLY=1 so your programs talk only to this laptop
# 4. Moves you into the tutorial folder

# >>> EDIT THIS if your Pluto workspace is somewhere else <<<
PLUTO_WS="${PLUTO_WS:-$HOME/pluto_ws}"

if [ ! -f /opt/ros/humble/setup.bash ]; then
    echo "ROS 2 Humble not found in /opt/ros/humble"
    echo "Install it first: bash ~/ROS2_Tutorial/install.sh  (or follow README.md, section 2)."
    return 1 2>/dev/null || exit 1
fi
source /opt/ros/humble/setup.bash

if [ -f "$PLUTO_WS/install/setup.bash" ]; then
    source "$PLUTO_WS/install/setup.bash"
fi

# Your own workspace from README.md section 10, if you have built it
if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
    source "$HOME/ros2_ws/install/setup.bash"
fi

export ROS_LOCALHOST_ONLY=1
cd "$HOME/ROS2_Tutorial" 2>/dev/null || cd "$(dirname "${BASH_SOURCE[0]}")"

echo "ROS 2 humble ready (this laptop only). Tutorial folder: $(pwd)"
