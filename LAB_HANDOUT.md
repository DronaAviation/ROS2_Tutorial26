# ROS 2 Lab Handout

Ubuntu 22.04 · ROS 2 Humble. Do the steps in order. Each step names the terminal to type in.

---

## Before the first lab

### Get the files and install

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/DronaAviation/ROS2_Tutorial26.git ~/ROS2_Tutorial
```

```bash
bash ~/ROS2_Tutorial/install.sh
```

Takes 15–40 minutes.

### Check the laptop

```bash
bash ~/ROS2_Tutorial/check_setup.sh
```

Expected: `All checks passed. This laptop is ready.` Fix every `FAIL` before Lab 1.

### Open VS Code with four terminals

```bash
cd ~/ROS2_Tutorial
code .
```

1. Open `LAB_HANDOUT.md`, press **Ctrl+Shift+V**, drag the tab to the left half.
2. **Ctrl+`** opens a terminal. Click the split icon three times. Rename them `T1`, `T2`, `T3`, `T4`.

```
+---------------------------+---------------------------+
|                           |  T1          |  T2        |
|   LAB_HANDOUT.md          |--------------+------------|
|                           |  T3          |  T4        |
+---------------------------+---------------------------+
```

### The setup line — every terminal, every time

```bash
source ~/ROS2_Tutorial/env.sh
```

Expected: `ROS 2 humble ready (this laptop only). Tutorial folder: ...`

**Terminal keys:** copy / paste = **Ctrl+Shift+C** / **Ctrl+Shift+V**. **Ctrl+C** stops the program.

---

## Lab 1: Turtlesim

Setup line in **T1, T2, T3, T4**.

### Experiment 1A — Drive the turtle with the keyboard

**1.1 — T1**

```bash
ros2 run turtlesim turtlesim_node
```

Expected: a blue window with a turtle. Don't type in T1 again.

**1.2 — T2**

```bash
ros2 run turtlesim turtle_teleop_key
```

Click inside **T2**, press the arrow keys.

✅ **Checkpoint:** ↑ in T2 moves the turtle.

### Experiment 1B — See the topic that connects them

**1.3 — T3**

```bash
rqt_graph
```

Expected: `/teleop_turtle` → `/turtle1/cmd_vel` → `/turtlesim`. Close the window.

**1.4 — T3** (one at a time)

```bash
ros2 node list
```

```bash
ros2 topic list
```

```bash
ros2 topic info /turtle1/cmd_vel
```

```bash
ros2 interface show geometry_msgs/msg/Twist
```

**1.5 — T3**

```bash
ros2 topic echo /turtle1/cmd_vel
```

Click **T2**, press ↑, ←, ↓, →. Watch T3. Then **Ctrl+C** in T3.

### Experiment 1C — Drive the turtle yourself

**1.6 — T3**

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```

Expected: the turtle drives in circles. **Ctrl+C** to stop.
Try: bigger `z` · negative `z` · `x: 0.0`.

**1.7 — T3**

```bash
ros2 service call /reset std_srvs/srv/Empty
```

```bash
python3 1_turtlesim/turtle_circle.py
```

Expected: one full circle, then the script exits.

✅ **Checkpoint:** your script drew the circle.

### Experiment 1D — Read the turtle's position

**1.8 — T4**

```bash
python3 1_turtlesim/turtle_pose.py
```

Expected: `x=…  y=…  heading=…` twice a second. Drive with T2 and watch it change.

✅ **Checkpoint:** T4's numbers move when the turtle moves.

### Experiment 1E — Change the plan (exercise)

Edit **only** `STEPS` in `1_turtlesim/turtle_circle.py`:

```python
STEPS = [
    ('side', 2.0, twist(forward=1.0)),
    ('turn', 1.0, twist(turn=math.pi / 2)),
] * 4
```

**T3:**

```bash
ros2 service call /reset std_srvs/srv/Empty
```

```bash
python3 1_turtlesim/turtle_circle.py
```

Then try: a triangle · a bigger circle · two laps. Reset before each run.

More: tasks T1–T4 in [TASKS.md](TASKS.md).

### Tidy up

```bash
ros2 service call /reset std_srvs/srv/Empty
```

**Ctrl+C** in T4, T3, T1. **q** in T2. Then:

```bash
ros2 node list
```

Expected: no output. Close all four terminals.

---

## Lab 2: Gazebo simulated drone

Four new terminals. Setup line in each.

### Experiment 2A — Start the simulated drone and the bridge

**2.1 — T1**

```bash
ign gazebo -r multicopter_velocity_control.sdf
```

Expected: Gazebo opens with two drones. Ours is **X3**. The first start can take minutes.

**2.2 — T2**

```bash
ros2 run ros_gz_bridge parameter_bridge "/X3/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist"
```

Expected: `Creating ROS->GZ Bridge`. Leave it running.

**2.3 — T3**

```bash
ros2 node list
```

```bash
ros2 topic list
```

```bash
ign topic -l
```

### Experiment 2B — Take off and hover from the terminal

**2.4 — T3**

```bash
ros2 topic pub --once /X3/gazebo/command/twist geometry_msgs/msg/Twist "{linear: {z: 0.5}}"
```

After 2–3 seconds:

```bash
ros2 topic pub --once /X3/gazebo/command/twist geometry_msgs/msg/Twist "{}"
```

✅ **Checkpoint:** the drone hovers.

### Experiment 2C — Fly with our publisher

**2.5 — T4**

```bash
ros2 topic echo /X3/gazebo/command/twist
```

**2.6 — T3**

```bash
python3 2_gazebo/sim_drone.py
```

Expected: climb → circle → hover → descend → hover.

**2.7 — T3**

```bash
diff 1_turtlesim/turtle_circle.py 2_gazebo/sim_drone.py
```

Write down which lines are different.

### Experiment 2D — Fly your own plan (exercise)

Edit `STEPS` in `2_gazebo/sim_drone.py`. Try: climb higher · two circles · a square.
To put the drone back on the ground: **Ctrl+C** in T1, run 2.1 again.

### Experiment 2E — Fly the drone with the keyboard

Drone on the ground first (**Ctrl+C** in T1, run 2.1 again). Keep T2 and T4 running.

**2.8 — T3**

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/X3/gazebo/command/twist
```

**2.9 — T3** (click inside T3 first)

`t` climb · `b` descend · `i` / `,` forward / back · `j` / `l` turn · `k` hover

✅ **Checkpoint:** take off, fly forward, turn, land. Then **Ctrl+C** in T3.

### Experiment 2F — Read the drone's height: a Python subscriber

**2.10 — T2** (**Ctrl+C** first)

```bash
ros2 run ros_gz_bridge parameter_bridge "/X3/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist" "/model/x3/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry"
```

Expected: `Creating ROS->GZ Bridge` and `Creating GZ->ROS Bridge`.

**2.11 — T4** (**Ctrl+C** first)

```bash
python3 2_gazebo/sim_drone_pose.py
```

Expected: `x=0.00  y=-0.00  height=0.05 m  climb rate=+0.00 m/s`, twice a second.

**2.12 — T3**

```bash
python3 2_gazebo/sim_drone.py
```

✅ **Checkpoint:** T4 shows the height rise to about 1.3 m, sag in the circle, and come back to 0.05 m.

More: tasks D1–D4 in [TASKS.md](TASKS.md).

### Tidy up

**Ctrl+C** in T4, T2, T1. Close the Gazebo window if it stays open.

---

## Lab 3: Real Pluto drone

### ⚠️ Safety — read before every flight

1. **Open floor.** 2 m clear, people behind the line, fresh battery.
2. **Keyboard control reads the whole laptop. Space arms/disarms.** Start other terminals *before* it. Stop it (**Ctrl+C**) *before* typing anywhere else.
3. **Never run `pluto_flight.py` or `ros2 topic pub` while keyboard control runs.**
4. **Emergency stop:** keyboard flight → **space**. Script flight → **Ctrl+C**.
5. **Stop `plutonode` only when landed and disarmed.** Close its terminal or press **Ctrl+\\**.

### Pre-flight

- [ ] Battery charged and fitted; propellers OK
- [ ] Drone on flat floor, nothing within 2 m
- [ ] Laptop on Wi-Fi `Pluto_XXXX`, password `dronaaviation`
- [ ] Four terminals, setup line run in each

### Experiment 3A — Connect to the drone and read telemetry

**3.1 — T1**

```bash
ros2 run plutodrone plutonode
```

Expected: `Pluto Connected`.

**3.2 — T2**

```bash
ros2 run plutoserver plutoserver
```

Expected: Roll/Pitch/Yaw, Altitude, Battery. Tilt the drone by hand. Write down the battery voltage.

**3.3 — T4**

```bash
ros2 node list
ros2 interface show custom_msgs/msg/PlutoMsg
ros2 topic echo /drone_command custom_msgs/msg/PlutoMsg
```

> **From here until 3.5, do not type in any terminal.**

### Experiment 3B — Fly with the keyboard

**3.4 — T3**

```bash
ros2 launch plutoserver drone_comb.launch.py
```

| Key   | Action       | Key   | Action            |
| ----- | ------------ | ----- | ----------------- |
| space | Arm / disarm | ↑ ↓   | Forward / back    |
| q     | Take off     | ← →   | Left / right      |
| e     | Land         | a / d | Turn left / right |
| w / s | Up / down    | r     | Sticks to centre  |

**Do not press `t`.**

Sequence: **space** → **q** → gentle moves → **e** → **space**. Watch T4.

**3.5 — T3:** **Ctrl+C**. Typing is safe again.

### Experiment 3C — Fly from the terminal

**3.6 — T3** (one at a time, wait between)

Take off:

```bash
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1500, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1500, command_type: 1}"
```

Land:

```bash
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1500, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1500, command_type: 2}"
```

Disarm:

```bash
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1300, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1200, command_type: 0}"
```

Copy the commands exactly. Do not leave out any `rc_` field.

### Experiment 3D — Fly with our script

**3.7 — T3** (first run **with the propellers removed**)

```bash
python3 3_pluto/pluto_flight.py
```

Expected: idle → take off and hover → land → disarm. Watch T4. Then fit the propellers and run it again.

### Experiment 3E — Your own telemetry server (exercise)

**T2:** **Ctrl+C** to stop `plutoserver`, then:

```bash
python3 3_pluto/pluto_telemetry.py
```

Expected: `battery=… V  altitude=…  roll=…  pitch=…  yaw=…`. Tilt the drone.

### Tidy up

Land and disarm. **Ctrl+C** in T3, T4. Close the T1 and T2 terminals. Power off, unplug the battery.

---

## Extra A: Topics, services, actions, parameters

Setup line in **T1, T2, T3**.

**T1:**

```bash
ros2 run turtlesim turtlesim_node
```

**T2:**

```bash
ros2 run turtlesim turtle_teleop_key
```

Everything below in **T3**, one at a time.

**Nodes**

```bash
ros2 node list
```

```bash
ros2 node info /turtlesim
```

**Topics**

```bash
ros2 topic list -t
```

```bash
ros2 topic info /turtle1/cmd_vel
```

```bash
ros2 topic echo /turtle1/pose
```

```bash
ros2 topic hz /turtle1/pose
```

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 1.0}}"
```

**Message types**

```bash
ros2 interface show geometry_msgs/msg/Twist
```

```bash
ros2 interface show turtlesim/msg/Pose
```

**Services**

```bash
ros2 service list -t
```

```bash
ros2 interface show turtlesim/srv/Spawn
```

```bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```

```bash
ros2 topic list
```

```bash
ros2 service call /clear std_srvs/srv/Empty
```

```bash
ros2 service call /reset std_srvs/srv/Empty
```

**Actions**

```bash
ros2 action list -t
```

```bash
ros2 interface show turtlesim/action/RotateAbsolute
```

```bash
ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

**Parameters**

```bash
ros2 param list
```

```bash
ros2 param get /turtlesim background_b
```

```bash
ros2 param set /turtlesim background_r 255
```

```bash
ros2 service call /clear std_srvs/srv/Empty
```

**Tidy up:** **Ctrl+C** in T3 and T1. **q** in T2.

---

## Extra B: Your own package

Setup line in **T1, T2, T3**.

**B.1 — T1: make a workspace**

```bash
mkdir -p ~/ros2_ws/src
```

```bash
cd ~/ros2_ws/src
```

**B.2 — T1: create a package, then copy ours**

```bash
ros2 pkg create --build-type ament_python --license MIT demo_pkg --dependencies rclpy std_msgs
```

```bash
ls demo_pkg
```

```bash
cp -r ~/ROS2_Tutorial/4_workspace/tutorial_pkg ~/ros2_ws/src/
```

Open `package.xml` and `setup.py` in `~/ros2_ws/src/tutorial_pkg`.

**B.3 — T1: build**

```bash
cd ~/ros2_ws
```

```bash
colcon build --symlink-install
```

Expected: `Summary: 2 packages finished`. Then in every terminal:

```bash
source ~/ros2_ws/install/setup.bash
```

**B.4 — publisher and subscriber**

T1:

```bash
ros2 run tutorial_pkg talker
```

T2:

```bash
ros2 run tutorial_pkg listener
```

T3:

```bash
ros2 topic list
```

```bash
ros2 topic echo /chatter
```

**Ctrl+C** in T1, T2, T3.

**B.5 — T1: launch both at once**

```bash
ros2 launch tutorial_pkg talker_listener.launch.py
```

**Ctrl+C** to stop.

**B.6 — T1: turtlesim and the square, one command**

```bash
ros2 launch tutorial_pkg turtle_square.launch.py
```

**Exercise**

1. Copy `talker.py` to `counter.py`; publish an `Int32` on `/count`. Add `'counter = tutorial_pkg.counter:main'` to `entry_points` in `setup.py`.
2. `colcon build --symlink-install`, re-source, `ros2 run tutorial_pkg counter`, `ros2 topic echo /count`.
3. Add it to `talker_listener.launch.py` and launch all three.

---

**Stuck?** Check in this order: is the other program running (`ros2 node list`)? Is the topic name exact (`ros2 topic list`)? Did this terminal run the setup line? Then raise your hand.
