# ROS 2 Tutorial: turtlesim, Gazebo and the Pluto drone

Hands-on ROS 2 labs by Drona Aviation. You drive a simulated turtle, fly a simulated quadcopter in Gazebo, then fly a real Pluto drone, using the same few lines of Python each time.

> **Ubuntu 22.04 with ROS 2 Humble only.** Other Ubuntu versions and ROS 2 distributions are not supported; the install script refuses to run on anything else.

---

## 1. What's here

| | What you do | Needs |
| --- | --- | --- |
| **Lab 1 — Turtlesim** | Drive a 2D turtle from the keyboard, the terminal and Python: publishers and subscribers | ROS 2 |
| **Lab 2 — Gazebo drone** | Fly a simulated X3 quadcopter through the ROS ↔ Gazebo bridge, by keyboard and by script; read its height | Gazebo Fortress |
| **Lab 3 — Pluto drone** | Fly a real Pluto over Wi-Fi and read its telemetry | A Pluto drone, 2 m of clear floor |
| **Extra A** | Topics, services, actions and parameters on the command line | ROS 2 |
| **Extra B** | Your own ROS 2 package: workspace, `colcon`, launch files | `colcon` |

**How to use it:**

1. Install and verify (sections 2–3 below).
2. Open VS Code with four terminals (section 4).
3. Follow **[LAB_HANDOUT.md](LAB_HANDOUT.md)** for every lab, in order.
4. Finished a lab early? **[TASKS.md](TASKS.md)** has eight coding tasks: squares, polygons, a staircase, holding a height.

---

## 2. Install

First, get the tutorial files into your home folder:

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/DronaAviation/ROS2_Tutorial26.git ~/ROS2_Tutorial
```

*Keep the folder name `~/ROS2_Tutorial`: every command in this tutorial uses that path. To get updates later: `cd ~/ROS2_Tutorial && git pull`.*

Everything else in this section is also in `install.sh`, which runs the same commands:

```bash
bash ~/ROS2_Tutorial/install.sh
```

Takes 15–40 minutes and is safe to re-run. Read on if you want to see each step, or if a step fails.

### 2.1 ROS 2 Humble

These are the official steps from docs.ros.org (Humble → Installation → Ubuntu deb packages).

#### Locale

```bash
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

#### Enable Universe, install curl

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
```

#### Add the ROS 2 apt source

```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

#### Upgrade, then install

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop ros-dev-tools
```

> **Do not skip `apt upgrade` on a fresh 22.04.** The ROS 2 docs warn that installing ROS 2 before `systemd`/`udev` are updated can remove critical system packages.

`ros-humble-desktop` includes the `ros2` tools, `rclpy`, `turtlesim`, `rqt_graph` and RViz. `ros-dev-tools` includes `colcon` and `rosdep`.

#### Check

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

Expected: a window with a turtle. Ctrl+C to stop. (You do not need to add anything to `~/.bashrc` — `env.sh` sources ROS 2 for you.)

---

### 2.2 Gazebo and the bridge (Lab 2)

ROS 2 Humble pairs with Gazebo **Fortress** (the `ign` commands).

```bash
sudo apt install ros-humble-ros-gz ros-humble-teleop-twist-keyboard
```

This installs Gazebo Fortress, `ros_gz_bridge`, and the keyboard controller used in Experiment 2E. Then download the drone models once, so the first start of Lab 2 does not spend minutes downloading:

```bash
ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/X3 UAV"
ign fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/X4 UAV Config 1"
```

Check:

```bash
ign gazebo -r multicopter_velocity_control.sdf
```

Expected: Gazebo opens with two drones on the ground. Close it.

---

### 2.3 Pluto drone packages (Lab 3) and build tools

#### System packages

```bash
sudo apt install python3-colcon-common-extensions python3-pip
pip3 install --user pynput
```

| Package                                      | Used by                                              |
| -------------------------------------------- | ---------------------------------------------------- |
| `python3-colcon-common-extensions`         | `colcon build` (Pluto workspace; Extra B in the handout)       |
| `python3-pip`                              | installing `pynput`                                  |
| `pynput`                                   | the keyboard control node (`drone_comb.launch.py`) |

#### Build the Pluto workspace

The Pluto ROS 2 packages come from Drona Aviation's `pluto_ros2_package` repository. They are built into their own workspace, `~/pluto_ws`, which `env.sh` sources automatically.

```bash
source /opt/ros/humble/setup.bash
mkdir -p ~/pluto_ws/src
cd ~/pluto_ws/src
git clone https://github.com/DronaAviation/pluto_ros2_package.git
cd ~/pluto_ws
colcon build --symlink-install
```

Expected: `Summary: 3 packages finished` (`custom_msgs`, `plutodrone`, `plutoserver`). Warnings about `setup.py` / `easy_install` deprecation are normal.

If you keep the workspace somewhere else, set `PLUTO_WS` at the top of `env.sh`.

#### Check

```bash
source ~/pluto_ws/install/setup.bash
ros2 interface show custom_msgs/msg/PlutoMsg
```

Expected: the message fields (`int64 rc_roll` … `bool is_auto_pilot_on`).

---

### Install problems

| What you see                                       | Fix                                                                                                                                                                                    |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `E: Unable to locate package ros-humble-desktop` | The "Add the ROS 2 apt source" step did not complete, or you are not on 22.04. Run `apt policy ros-humble-desktop`; if it shows no candidate, redo that step and `sudo apt update`. |
| `dpkg: error … ros2-apt-source`                 | `ROS_APT_SOURCE_VERSION` came back empty (no network to api.github.com). Re-run the `export` line and check it prints a version with `echo $ROS_APT_SOURCE_VERSION`.             |
| `colcon: command not found`                      | `sudo apt install python3-colcon-common-extensions`, then open a new terminal.                                                                                                       |
| `colcon build` fails in `custom_msgs`          | `sudo apt install ros-humble-rosidl-default-generators`, then `rm -rf ~/pluto_ws/build ~/pluto_ws/install` and build again.                                                        |
| `ModuleNotFoundError: No module named 'pynput'`  | `pip3 install --user pynput`, in the same Python ROS uses (`which python3` → `/usr/bin/python3`).                                                                               |
| `ign: command not found` after 2.2               | Open a new terminal; if still missing, `sudo apt install ignition-fortress`.                                                                                                          |

---

## 3. Verify

```bash
bash ~/ROS2_Tutorial/check_setup.sh
```

Expected: one `PASS` line per check, ending `All checks passed. This laptop is ready.`
Each `FAIL` prints the command that fixes it underneath. Resolve every failure before Lab 1; the labs assume a passing check.

---

## 4. VS Code, the four terminals and the setup line

1. Install **VS Code** (`sudo snap install code --classic`, or the .deb from code.visualstudio.com).
2. In a terminal:

   ```bash
   cd ~/ROS2_Tutorial
   code .
   ```
3. Open `LAB_HANDOUT.md`, press **Ctrl+Shift+V** to see it rendered, and drag that tab to the **left** half.
4. Open a terminal with **Ctrl+`** (the backtick key). Click the **split** icon in the terminal panel three times, so you have **four** terminals. Right-click each → **Rename** → `T1`, `T2`, `T3`, `T4`.

You should see:

```
+---------------------------+---------------------------+
|                           |  T1          |  T2        |
|   LAB_HANDOUT.md          |--------------+------------|
|                           |  T3          |  T4        |
+---------------------------+---------------------------+
```

*Small screen? **Ctrl+B** hides the file list and gives the handout more room.*

What each terminal is for, in every lab:

| Terminal     | Job                         | Lab 1                              | Lab 2                     | Lab 3                                  |
| ------------ | --------------------------- | ---------------------------------- | ------------------------- | -------------------------------------- |
| **T1** | The robot                   | `turtlesim_node`                 | Gazebo                    | `plutonode`                          |
| **T2** | A helper that keeps running | keyboard control                   | bridge                    | `plutoserver`                        |
| **T3** | Your commands and scripts   | commands, `turtle_circle.py`      | commands, keyboard, `sim_drone.py` | keyboard, commands, `pluto_flight.py` |
| **T4** | Watching messages           | `turtle_pose.py`, `topic echo` | `topic echo`, `sim_drone_pose.py` | `topic echo`                         |

### The setup line

Run this in **every** terminal, first, every time you open a new one:

```bash
source ~/ROS2_Tutorial/env.sh
```

Expected: `ROS 2 humble ready (this laptop only). Tutorial folder: /home/<you>/ROS2_Tutorial`

It loads ROS 2, loads the Pluto packages, sets `ROS_LOCALHOST_ONLY=1` (restricting ROS 2 discovery to this machine, so nodes on other laptops on the same network are neither seen nor controlled), and changes into the tutorial folder.
Skip it and you get `ros2: command not found`, or two of your programs can't see each other.

Optional: to make it automatic in every new terminal, run once:

```bash
echo "source ~/ROS2_Tutorial/env.sh" >> ~/.bashrc
```

*From then on, every new terminal starts in `~/ROS2_Tutorial` and keeps ROS 2 on this laptop only, including later for other projects. To undo it:*

```bash
sed -i '/ROS2_Tutorial\/env.sh/d' ~/.bashrc
```

---

### Terminal tips

- **Copy / paste** in a terminal: **Ctrl+Shift+C** / **Ctrl+Shift+V**. Plain **Ctrl+C** does not copy: it **stops the program**.
- A terminal that is running a program can't take a new command. Use another one.
- **Ctrl+C** stops the program in that terminal. Each lab ends with a **Tidy up** section that lists which terminals to stop, in which order, so the next lab starts from a clean state.
- Copying a command from the handout: select it with the mouse and press **Ctrl+C** (in the handout, Ctrl+C copies; only in a terminal does it stop the program), then **Ctrl+Shift+V** in the terminal. On GitHub, each code box also has a copy icon at its top-right.

---

## 5. Folder layout

```
ROS2_Tutorial/
├── README.md              this page: install and setup
├── LAB_HANDOUT.md         every lab, step by step
├── TASKS.md               coding tasks for after Labs 1 and 2
├── install.sh             section 2 as one script
├── env.sh                 the setup line runs this
├── check_setup.sh         checks the laptop is ready
├── 1_turtlesim/
│   ├── turtle_circle.py   publisher: drives the turtle in one circle
│   └── turtle_pose.py     subscriber: prints where the turtle is
├── 2_gazebo/
│   ├── sim_drone.py       publisher: flies the simulated drone
│   └── sim_drone_pose.py  subscriber: prints where the simulated drone is
├── 3_pluto/
│   ├── pluto_flight.py    publisher: take off, hover, land, disarm
│   └── pluto_telemetry.py service server: receives the drone's sensor data
└── 4_workspace/
    └── tutorial_pkg/      a complete ROS 2 Python package (Extra B)
```

Update to the latest version at any time:

```bash
cd ~/ROS2_Tutorial && git pull
```

---

## 6. Common problems

Most problems come down to one of four things. Check them in this order:

1. Is the other program running? → `ros2 node list`
2. Is the topic name exactly the same? → `ros2 topic list` (one typo = a new, empty topic)
3. Is the message type the same? → `ros2 topic info <topic>`
4. Did **every** terminal run the setup line? → `printenv | grep ROS` must show `ROS_DISTRO=humble` and `ROS_LOCALHOST_ONLY=1`

| You see                                                     | Fix                                                                                                                                                                     |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ros2: command not found`                                 | Run the setup line in this terminal                                                                                                                                     |
| `ModuleNotFoundError: No module named 'rclpy'`            | Run the setup line. If a Python virtual environment is active, type `deactivate`                                                                                       |
| A script prints `Waiting for a subscriber on …`           | Start the other side (turtlesim, the bridge, `plutonode`)                                                                                                              |
| A robot on another laptop responds to your commands         | A terminal skipped the setup line, so `ROS_LOCALHOST_ONLY` is unset and discovery crossed the network. Run the setup line in every terminal, then restart the programs |
| `yaml` / `Failed to populate field` after `topic pub` | Retype the quotes as plain `"`, keep a space after every colon                                                                                                         |
| Ctrl+C doesn't copy                                         | It stops the program. Use Ctrl+Shift+C                                                                                                                                  |

---

More: [ROS 2 Humble tutorials](https://docs.ros.org/en/humble/Tutorials.html) · [Drona Aviation on GitHub](https://github.com/DronaAviation)
