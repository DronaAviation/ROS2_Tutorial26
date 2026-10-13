#!/usr/bin/env bash
# Checks this laptop is ready for the tutorial. Run:   bash ~/ROS2_Tutorial/check_setup.sh
# Prints one PASS/FAIL line per check. Each FAIL prints its own fix underneath.

FAILS=0
pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; echo "      fix: $2"; FAILS=$((FAILS+1)); }
warn() { echo "WARN  $1 (optional)"; echo "      fix: $2"; }

echo "== All labs =="
if grep -q 'VERSION_ID="22.04"' /etc/os-release 2>/dev/null; then
    pass "Ubuntu 22.04"
else
    fail "Ubuntu 22.04 (found: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2))" "Use Ubuntu 22.04"
fi

if [ -f /opt/ros/humble/setup.bash ]; then
    pass "ROS 2 Humble installed"
    source /opt/ros/humble/setup.bash
else
    fail "ROS 2 Humble installed" "Run: bash ~/ROS2_Tutorial/install.sh   (or follow README.md, section 2.1)"
    echo; echo "Cannot continue without ROS 2."; exit 1
fi

if [ -f "$HOME/ROS2_Tutorial/env.sh" ]; then
    pass "Tutorial folder at ~/ROS2_Tutorial"
    source "$HOME/ROS2_Tutorial/env.sh" >/dev/null
else
    fail "Tutorial folder at ~/ROS2_Tutorial" "git clone https://github.com/DronaAviation/ROS2_Tutorial26.git ~/ROS2_Tutorial"
fi

have_pkg() { ros2 pkg prefix "$1" >/dev/null 2>&1; }
have_py()  { python3 -c "import $1" >/dev/null 2>&1; }

echo "== Lab 1: Turtlesim =="
have_pkg turtlesim   && pass "turtlesim package"  || fail "turtlesim package"  "sudo apt install ros-humble-desktop"
command -v rqt_graph >/dev/null && pass "rqt_graph" || fail "rqt_graph" "sudo apt install ros-humble-desktop"
have_py rclpy        && pass "rclpy (Python)"     || fail "rclpy (Python)"     "Run the setup line; type 'deactivate' if a virtual environment is active"

echo "== Lab 2: Gazebo =="
command -v ign >/dev/null        && pass "Gazebo (ign)"      || fail "Gazebo (ign)"      "sudo apt install ros-humble-ros-gz"
have_pkg ros_gz_bridge           && pass "ros_gz_bridge"     || fail "ros_gz_bridge"     "sudo apt install ros-humble-ros-gz"
have_pkg teleop_twist_keyboard   && pass "teleop_twist_keyboard" || fail "teleop_twist_keyboard" "sudo apt install ros-humble-teleop-twist-keyboard"
if [ -d "$HOME/.ignition/fuel" ] && find "$HOME/.ignition/fuel" -iname '*x3*' -print -quit 2>/dev/null | grep -q .; then
    pass "X3 drone model cached"
else
    fail "X3 drone model cached (best-effort check)" "Open Gazebo once with internet: ign gazebo -r multicopter_velocity_control.sdf"
fi

echo "== Lab 3: Pluto =="
for p in custom_msgs plutodrone plutoserver; do
    have_pkg "$p" && pass "$p package" || fail "$p package" "Follow README.md section 2.3 (or run install.sh), then open a new terminal"
done
have_py pynput               && pass "pynput"  || fail "pynput"  "pip3 install pynput"

echo "== Section 10: your own package (optional) =="
command -v colcon >/dev/null && pass "colcon" || warn "colcon" "sudo apt install python3-colcon-common-extensions"

echo
if [ "$FAILS" -eq 0 ]; then
    echo "All checks passed. This laptop is ready."
else
    echo "$FAILS check(s) failed. Apply the fixes above, then run this again."
    exit 1
fi
