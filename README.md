# ROS 2 Tutorial


> **This tutorial works only on Ubuntu 22.04 with ROS 2 Humble.** Other Ubuntu versions and other ROS 2 distributions are not supported; the install script refuses to run on anything else.

---

## 1. What is ROS?

### A robot is many programs, not one

A drone has a camera, a position sensor, a battery monitor, four motors and a radio link. Each one needs code.
Writing all of that as **one big program** is a bad idea: one bug stops everything, two people can't work on it at once, and the camera code has to know how a motor works.

**ROS** (Robot Operating System) is the standard way to split a robot into **many small programs that pass messages to each other.**

```
   camera program  ──►  /camera/image   ──►  vision program
                                                   │
   position sensor ──►  /pose           ──►  flight program  ──►  /cmd_vel  ──►  motor program
```

Each arrow is a **topic**: a named channel. A program **publishes** on a topic or **subscribes** to it. It never needs to know who is on the other end — only the topic name and the shape of the message.

### Why robotics people use it

- **Low level and high level are separate.** Motor drivers, sensor drivers and the flight controller are low-level code, usually **C++** or firmware on a microcontroller, written once by whoever built the hardware. The behaviour — "take off, fly a square, land" — is high-level code, usually **Python**, written by you. ROS is the line between the two: you publish a message, the driver does the rest.
- **It can run across machines.** ROS 2 nodes discover each other over the network, so a robot's onboard computer, a laptop and a ground station can share topics. This tutorial sets `ROS_LOCALHOST_ONLY=1`, which disables that: every node is confined to your own machine, so several laptops on one Wi-Fi do not see each other's nodes. In Lab 3 the laptop still talks to the drone, but through `plutonode`'s own TCP connection, not through ROS discovery.
- **Code moves between robots.** Change the topic name and the message type; the rest of your program stays. In Lab 2 you will `diff` the turtle script and the drone script and see this for yourself.
- **Everything is inspectable.** Four commands tell you which programs are running, which channels exist, and what is being said on them. That is the whole of debugging in ROS.

### ROS 1 vs ROS 2 (we use ROS 2)

|                | ROS 1                            | ROS 2                                           |
| -------------- | -------------------------------- | ----------------------------------------------- |
| Central server | `roscore` must run first       | None; nodes find each other directly            |
| Commands       | `rosrun`, `rostopic`         | `ros2 run`, `ros2 topic`                    |
| Python library | `rospy`                        | `rclpy`                                       |
| Status         | Last release reached end of life | Current. We use **Humble** on Ubuntu 22.04 |

If a tutorial online says `roscore` or `rostopic`, it is ROS 1 and won't work here. Look for `ros2` at the start of the command.

### ROS is not an operating system

Despite the name. It is a set of libraries (`rclpy`), command-line tools (`ros2 …`), standard message types (`Twist`), and thousands of ready-made programs (turtlesim, the Gazebo bridge). It runs on Ubuntu.

### Six words you need

| Word                   | Meaning                                     | Think of it as           | Lab 1 example               |
| ---------------------- | ------------------------------------------- | ------------------------ | --------------------------- |
| **Node**         | One running program                         | An app on a phone        | `turtlesim_node`          |
| **Topic**        | A named channel between nodes               | A group chat with a name | `/turtle1/cmd_vel`        |
| **Message type** | The fixed shape of every message on a topic | A form with fixed boxes  | `geometry_msgs/msg/Twist` |
| **Publisher**    | A node that sends on a topic                | Someone posting          | `turtle_circle.py`        |
| **Subscriber**   | A node that receives from a topic           | Someone reading          | `turtle_pose.py`          |
| **Service**      | One request, one reply (not a stream)       | A phone call             | `/reset`                  |

### Four commands you'll use in every lab

| Command                                    | Question it answers                           |
| ------------------------------------------ | --------------------------------------------- |
| `ros2 node list`                         | Which programs are running?                   |
| `ros2 topic list`                        | Which channels exist?                         |
| `ros2 topic echo <topic>`                | What is being said on this channel right now? |
| `ros2 topic pub <topic> <type> "<data>"` | Let me say something on this channel myself.  |

Services, actions and parameters get their own hands-on tour in [section 8](#8-extra-ros-2-basics-on-the-command-line), using turtlesim and no code. Do it before or after Lab 1.

---

### Check your understanding

<details><summary>1. A camera node and a flight node need to exchange images. What do they have to agree on, and what do they not need to know about each other?</summary>

They agree on the **topic name** and the **message type**. Neither needs to know the other's name, where it runs, or even whether it exists — a publisher sends regardless of who listens.

</details>

<details><summary>2. You see <code>roscore</code> in an online tutorial. Will it work here?</summary>

No. `roscore` is ROS 1. ROS 2 has no central server; look for commands that start with `ros2`.

</details>

<details><summary>3. Which of the four everyday commands answers "what is being said on <code>/turtle1/cmd_vel</code> right now?"</summary>

`ros2 topic echo /turtle1/cmd_vel`

</details>

<details><summary>4. Which word describes "put the turtle back in the centre" — topic or service — and why?</summary>

A **service**: it is one request with one reply, not a stream. Velocity commands are a stream, so they go on a topic.

</details>

---

## 2. Install everything

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
sudo apt install ros-humble-ros-gz
```

This installs Gazebo Fortress and `ros_gz_bridge`. Then download the drone models once, so the first start of Lab 2 does not spend minutes downloading:

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
sudo apt install python3-colcon-common-extensions \
                 ros-humble-cv-bridge ros-humble-image-transport \
                 python3-opencv python3-numpy python3-pip ffmpeg
pip3 install --user pynput
```

| Package                                      | Used by                                              |
| -------------------------------------------- | ---------------------------------------------------- |
| `python3-colcon-common-extensions`         | `colcon build` (Pluto workspace, section 10)       |
| `ros-humble-cv-bridge`, `python3-opencv` | `pluto_camera.py`, the camera publisher            |
| `ffmpeg`                                   | the camera publisher (H.264 decoding)                |
| `pynput`                                   | the keyboard control node (`drone_comb.launch.py`) |

#### Build the Pluto workspace

The Pluto ROS 2 packages come from two Drona Aviation repositories. They are built into their own workspace, `~/pluto_ws`, which `env.sh` sources automatically.

```bash
source /opt/ros/humble/setup.bash
mkdir -p ~/pluto_ws/src
cd ~/pluto_ws/src
git clone https://github.com/DronaAviation/pluto_ros2_package.git
git clone https://github.com/DronaAviation/pluto_cam_ros2.git
cd ~/pluto_ws
colcon build --symlink-install
```

Expected: `Summary: 5 packages finished` (`custom_msgs`, `plutodrone`, `plutoserver`, `pluto_camera_sense`, `pluto_image_sub`). Warnings about `setup.py` / `easy_install` deprecation are normal.

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

## 3. Verify the installation

```bash
bash ~/ROS2_Tutorial/check_setup.sh
```

Expected: one `PASS` line per check, ending `All checks passed. This laptop is ready.`
Each `FAIL` prints the command that fixes it underneath. Resolve every failure before Lab 1; the labs assume a passing check.

---

## 4. Set up VS Code and the four terminals

1. Install **VS Code** (`sudo snap install code --classic`, or the .deb from code.visualstudio.com).
2. In a terminal:

   ```bash
   cd ~/ROS2_Tutorial
   code .
   ```
3. Open `README.md`, press **Ctrl+Shift+V** to see it rendered, and drag that tab to the **left** half.
4. Open a terminal with **Ctrl+`** (the backtick key). Click the **split** icon in the terminal panel three times, so you have **four** terminals. Right-click each → **Rename** → `T1`, `T2`, `T3`, `T4`.

You should see:

```
+---------------------------+---------------------------+
|                           |  T1          |  T2        |
|   README (this file)      |--------------+------------|
|                           |  T3          |  T4        |
+---------------------------+---------------------------+
```

*Small screen? **Ctrl+B** hides the file list and gives the README more room.*

What each terminal is for, in every lab:

| Terminal     | Job                         | Lab 1                              | Lab 2                     | Lab 3                                  |
| ------------ | --------------------------- | ---------------------------------- | ------------------------- | -------------------------------------- |
| **T1** | The robot                   | `turtlesim_node`                 | Gazebo                    | `plutonode`                          |
| **T2** | A helper that keeps running | keyboard control                   | bridge                    | `plutoserver`                        |
| **T3** | Your commands and scripts   | commands, `turtle_circle.py`      | commands, `sim_drone.py` | keyboard, commands, `pluto_flight.py` |
| **T4** | Watching messages           | `turtle_pose.py`, `topic echo` | `topic echo`            | `topic echo`                         |

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
- Copying a command from this README: select it with the mouse and press **Ctrl+C** (in the README, Ctrl+C copies; only in a terminal does it stop the program), then **Ctrl+Shift+V** in the terminal. On GitHub, each code box also has a copy icon at its top-right.

---

## 5. Lab 1: Turtlesim

**The idea:** a robot is driven by messages on a named topic. Anything that publishes the right message on that topic drives the robot — the keyboard, a one-line command, or your own script. The turtle can't tell the difference.

You will drive a turtle with the keyboard, then from the terminal, then with your own Python publisher, and read its position with your own subscriber. About 45 minutes.

**Prerequisite:** `bash ~/ROS2_Tutorial/check_setup.sh` reports `PASS` for the Lab 1 checks (`turtlesim`, `rqt_graph`, `rclpy`).

**Experiments in this lab**

| Experiment | What you do | Steps |
| ---------- | ----------- | ----- |
| **1A** — Drive the turtle with the keyboard | Start turtlesim and the keyboard node | 1.1 – 1.2 |
| **1B** — See the topic that connects them | `rqt_graph`, `ros2 node/topic`, `topic echo` | 1.3 – 1.5 |
| **1C** — Drive the turtle yourself | `ros2 topic pub`, then `turtle_circle.py` | 1.6 – 1.7 |
| **1D** — Read the turtle's position | `turtle_pose.py` | 1.8 |
| **1E** — Change the plan (exercise) | Edit `STEPS`: square, triangle, bigger circle | — |

First, the setup line in **T1, T2, T3 and T4**:

```bash
source ~/ROS2_Tutorial/env.sh
```

---

### Experiment 1A — Drive the turtle with the keyboard

**Goal:** steer a turtle with the arrow keys. · *Terminals: T1, T2*

#### 1.1 — T1: start the robot

```bash
ros2 run turtlesim turtlesim_node
```

Expected: a blue window with a turtle in the middle, and in T1:

```
[INFO] [...] [turtlesim]: Starting turtlesim with node name /turtlesim
```

*T1 belongs to the robot for the rest of the lab. Don't type in it again; don't close the window.*

#### 1.2 — T2: drive with the keyboard

```bash
ros2 run turtlesim turtle_teleop_key
```

**Click inside T2**, then press the arrow keys: ↑ forward, ↓ back, ← → turn.

*The keys only reach the turtle while T2 is the active window. The turtle window itself ignores the keyboard.*

**Checkpoint:** ↑ in T2 moves the turtle.

---

### Experiment 1B — See the topic that connects them

**Goal:** see the one topic that joins the keyboard to the turtle. · *Terminal: T3*

#### 1.3 — T3: see who talks to whom

```bash
rqt_graph
```

Expected: two ovals, `/teleop_turtle` and `/turtlesim`, joined by one arrow labelled `/turtle1/cmd_vel`.
No arrow? Choose **Nodes/Topics (active)** in the top-left drop-down and click refresh. Close the window when done.

*Two programs, one topic. The keyboard node talks on `/turtle1/cmd_vel`; the turtle listens there. Neither knows the other's name.*

#### 1.4 — T3: inspect from the command line (one at a time)

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

Look for: `/turtlesim` in the node list · `/turtle1/cmd_vel` in the topic list · `Publisher count: 1` (the keyboard) and `Subscription count: 1` (the turtle) · a `Twist` = `linear` x y z + `angular` x y z.

*Same picture as `rqt_graph`, as text. These four commands work on a real robot with no screen. The turtle uses only two of the six numbers: `linear.x` = forward speed, `angular.z` = turn rate (rad/s, positive = left).*

#### 1.5 — T3: watch the messages

```bash
ros2 topic echo /turtle1/cmd_vel
```

Click inside **T2** and press ↑ once. T3 shows one message:

```
linear:
  x: 2.0
  ...
angular:
  ...
  z: 0.0
```

Try ← (`angular: z: 2.0`), ↓ (`x: -2.0`), → (`z: -2.0`). Then **Ctrl+C** in T3.

*That is everything the keyboard program says to the turtle. One key, one `Twist`.*

---

### Experiment 1C — Drive the turtle yourself: terminal, then a Python publisher

**Goal:** replace the keyboard — first with one command, then with a Python publisher. · *Terminal: T3*

#### 1.6 — T3: be the keyboard yourself

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```

Expected: the turtle drives in circles. **Ctrl+C** → it stops within a second.

Try: bigger `z` = tighter circle · negative `z` = clockwise · `x: 0.0` = spin on the spot.

*We are now the keyboard program: same topic, same message type, our numbers. The turtle stops 1 s after the last command, which is why this repeats once a second (`--rate 1`) instead of sending once (`--once`). Remember this for Lab 2.*

#### 1.7 — T3: run our publisher

Open `turtle_circle.py` in the editor. Find `TOPIC`, `RATE_HZ`, `twist(...)`, `STEPS` and `StepPublisher`. `STEPS` is the plan: a list of `(name, seconds, message)`.

```bash
ros2 service call /reset std_srvs/srv/Empty
```

```bash
python3 1_turtlesim/turtle_circle.py
```

Expected: one full circle, then the script exits by itself:

```
[INFO] [...] [turtle_circle]: circle (6.3 s)
[INFO] [...] [turtle_circle]: stop (1.0 s)
```

*Step 1.6 in Python. 6.3 s because one lap is 2π radians at 1 rad/s. The same script, with only its topic, node name and plan changed, flies the drone in Lab 2.*
*`Waiting for a subscriber…`? Turtlesim isn't running, or T3 skipped the setup line.*

**Checkpoint:** your script, not the keyboard, drew the circle.

---

### Experiment 1D — Read the turtle's position: a Python subscriber

**Goal:** listen to the turtle — a Python subscriber that prints where it is. · *Terminal: T4*

#### 1.8 — T4: run our subscriber

```bash
python3 1_turtlesim/turtle_pose.py
```

Expected, twice a second:

```
[INFO] [...] [turtle_pose]: x=5.54  y=5.54  heading=0.00 rad
```

Now drive with T2 (click T2 first). The numbers change. `x`, `y` run 0 → ~11 from the bottom-left corner; `heading` is radians (0 = right, 1.57 = up).

*The other direction: the robot talks, our code listens. `create_subscription(...)` says "call my function for every message on `/turtle1/pose`". `rclpy.spin()` waits and keeps taking calls.*

**Checkpoint:** T4's numbers move when the turtle moves and stop when it stops.

---

### Experiment 1E — Change the plan (exercise)

**Goal:** make the turtle draw a new shape by editing data, not code. · *Terminal: T3*

Edit **only** `STEPS` in `turtle_circle.py`. For a square:

```python
STEPS = [
    ('side', 2.0, twist(forward=1.0)),            # drive straight for 2 s
    ('turn', 1.0, twist(turn=math.pi / 2)),       # turn 90 degrees in 1 s
] * 4                                             # four times = a square
```

Then in **T3**:

```bash
ros2 service call /reset std_srvs/srv/Empty
```

```bash
python3 1_turtlesim/turtle_circle.py
```

#### More to try

- **Triangle:** turn `2 * math.pi / 3` (120°) in 1 s, repeated three times.
- **Bigger circle:** `forward=3.0`, keep `turn=1.0`. The radius is forward speed divided by turn rate, so this gives 3 m instead of 1 m.
- **Two laps:** make the circle step `4 * math.pi` seconds long.

Reset the turtle (`ros2 service call /reset std_srvs/srv/Empty`) before each run so the shape starts from the centre.

*You changed the robot's behaviour without touching any ROS code. The plan is data.*

---

### Tidy up

```bash
ros2 service call /reset std_srvs/srv/Empty     # turtle back to the centre, trail cleared
```

**Ctrl+C** in T4, T3 and T1. **q** in T2. Then confirm nothing is left running:

```bash
ros2 node list
```

Expected: no output. Close all four terminals before Lab 2 and open four new ones.

---

### Check your understanding

<details><summary>1. In step 1.6 you drove the turtle with <code>ros2 topic pub</code>. What did the turtle "think" was driving it?</summary>

Nothing in particular. It only sees `Twist` messages on `/turtle1/cmd_vel`; the keyboard node, your command and `turtle_circle.py` are indistinguishable to it.

</details>

<details><summary>2. Why does step 1.6 use <code>--rate 1</code> but <code>turtle_circle.py</code> sends 10 messages a second?</summary>

Turtlesim stops one second after the last command. Once a second is the minimum that keeps it moving; ten a second gives smooth motion and a safety margin.

</details>

<details><summary>3. What would you change in <code>turtle_circle.py</code> to make the turtle drive a triangle? Which lines stay untouched?</summary>

Only `STEPS`: a side step and a `2 * math.pi / 3` turn, repeated three times. `TOPIC`, `RATE_HZ`, `twist()` and `StepPublisher` do not change.

</details>

<details><summary>4. <code>turtle_pose.py</code> prints twice a second but turtlesim publishes about 62 times a second. Where do the other 60 go?</summary>

They are still delivered to `on_pose`; `throttle_duration_sec=0.5` only limits how often the logger prints. The subscriber receives every message.

</details>

<details><summary>5. <code>ros2 node list</code> does not show <code>/turtlesim</code>, and your script says <code>Waiting for a subscriber</code>. What happened?</summary>

Turtlesim is not running (or this terminal skipped the setup line, so it cannot see it). A message published before anyone subscribes is lost, so the script waits instead of sending into nothing.

</details>

### Troubleshooting

| What you see                                             | Likely cause                                                      | Fix                                                                                                           |
| -------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| The arrow keys do nothing                                | `turtle_teleop_key` is not running, or another window is active | Start it in T2 (step 1.2), click inside T2, and press the keys there. The turtle window ignores the keyboard. |
| The keys print in T2 but the turtle never moves; `ros2 topic info /turtle1/cmd_vel` shows `Subscription count: 0` | T1 and T2 have different ROS settings (for example `ROS_LOCALHOST_ONLY=0` in one, `1` in the other), so they can't find each other | Run `printenv ROS_LOCALHOST_ONLY` in T1 and T2: both must print `1`. Stop both programs, run the setup line in each, start them again |
| The keys worked, then stopped                            | You clicked another window, such as the turtle window             | Click back inside T2                                                                                          |
| No turtle window; `could not connect to display`        | Running over SSH, or no desktop session                           | Run it on the machine's own desktop                                                                           |
| `rqt_graph` shows no arrow                             | The view shows nodes only, or has not refreshed                   | Choose **Nodes/Topics (active)** at the top left and click refresh                                       |
| The turtle moves for one second, then stops              | You used `--once`. Turtlesim stops after 1 s without a command   | Use `--rate 1`                                                                                               |
| The turtle is stuck against a wall                       | It reached the edge of the window (0 or about 11)                 | `ros2 service call /reset std_srvs/srv/Empty`                                                               |
| `turtle_pose.py` prints nothing                        | Turtlesim is not running                                          | Start it in T1, then check `ros2 topic hz /turtle1/pose`                                                     |
| A script prints `Waiting for a subscriber on …`        | Turtlesim is not running, or this terminal skipped the setup line | Start turtlesim; run the setup line                                                                           |
| `turtle_circle.py` draws the wrong shape after editing | A typo in `STEPS`, or the turtle did not start in the centre     | Reset the turtle first. Check every step has the shape `('name', seconds, twist(...))`                       |
| `IndentationError` or `SyntaxError` after editing    | Spaces mixed with tabs, or a missing bracket or comma             | Indent with 4 spaces only. Compare your `STEPS` with the example, bracket by bracket                         |

General problems (`command not found`, `rclpy` missing, nodes not seeing each other): [section 9](#9-troubleshooting).

---

## 6. Lab 2: Gazebo simulated drone

**The idea:** ROS code moves between robots. Same message type, almost the same script as the turtle, and a quadcopter flies. About 40 minutes.

**Prerequisite:** Lab 1 completed, and `check_setup.sh` reports `PASS` for the Lab 2 checks (`ign`, `ros_gz_bridge`, the X3 model).

**Experiments in this lab**

| Experiment | What you do | Steps |
| ---------- | ----------- | ----- |
| **2A** — Start the simulated drone and the bridge | Gazebo, `parameter_bridge`, inspect | 2.1 – 2.3 |
| **2B** — Take off and hover from the terminal | `ros2 topic pub --once` | 2.4 |
| **2C** — Fly with our publisher | `sim_drone.py`, then `diff` it with the turtle script | 2.5 – 2.7 |
| **2D** — Fly your own plan (exercise) | Edit `STEPS` in `sim_drone.py` | — |

**Gazebo** is a physics simulator — gravity, collisions, motors, a 3D world. It is **not** a ROS program: it has its own messages and topics, so a **bridge** translates between the two.

Open **four new terminals**. Setup line in each:

```bash
source ~/ROS2_Tutorial/env.sh
```

---

### Experiment 2A — Start the simulated drone and the bridge

**Goal:** a simulated quadcopter that ROS 2 can talk to. · *Terminals: T1, T2, T3*

#### 2.1 — T1: start the simulator

```bash
ign gazebo -r multicopter_velocity_control.sdf
```

Expected: Gazebo opens with two drones on the ground. Ours is **X3**, the quadcopter. The first start can take minutes while the model downloads; later starts are fast.

*`-r` = run. Without it the simulation is paused and the drone ignores every command until you press ▶ at the bottom left.*

#### 2.2 — T2: start the bridge

```bash
ros2 run ros_gz_bridge parameter_bridge "/X3/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist"
```

Expected: a line starting `Creating ROS->GZ Bridge`. Leave T2 running.

*Read the quoted part left to right: the topic name · `@` the ROS message type · `]` one way, ROS → Gazebo · the Gazebo message type.*

#### 2.3 — T3: inspect

```bash
ros2 node list
```

```bash
ros2 topic list
```

```bash
ign topic -l
```

Expected: **one** ROS node, `/ros_gz_bridge`. The topic list includes `/X3/gazebo/command/twist`. `ign topic -l` is Gazebo's own, much longer, list.

*Gazebo isn't in `node list` because it isn't a ROS node. Only the bridge is.*

---

### Experiment 2B — Take off and hover from the terminal

**Goal:** lift off and hover with two one-line commands. · *Terminal: T3*

#### 2.4 — T3: take off, then hover

```bash
ros2 topic pub --once /X3/gazebo/command/twist geometry_msgs/msg/Twist "{linear: {z: 0.5}}"
```

Expected: the X3 lifts off at 0.5 m/s — and keeps climbing. After 2–3 seconds:

```bash
ros2 topic pub --once /X3/gazebo/command/twist geometry_msgs/msg/Twist "{}"
```

Expected: it stops and holds height. `"{}"` is a `Twist` with every value 0.

*This drone keeps obeying the last command it got, so one message (`--once`) is enough. The turtle forgot after one second. Same message, different robot behaviour.*

**Checkpoint:** the drone hovers.

---

### Experiment 2C — Fly with our publisher

**Goal:** fly a circle with the same publisher you wrote for the turtle. · *Terminals: T3, T4*

#### 2.5 — T4: watch the messages

```bash
ros2 topic echo /X3/gazebo/command/twist
```

Prints nothing until something publishes. Leave it running.

#### 2.6 — T3: run our publisher

```bash
python3 2_gazebo/sim_drone.py
```

Expected: climb about 1.5 m → one circle → hover → descend → hover, and in T3:

```
[INFO] [...] [sim_drone]: climb (3.0 s)
[INFO] [...] [sim_drone]: circle (6.3 s)
[INFO] [...] [sim_drone]: hover (2.0 s)
[INFO] [...] [sim_drone]: descend (4.0 s)
[INFO] [...] [sim_drone]: hover (1.0 s)
```

T4 fills with the same `Twist` messages you saw for the turtle, 10 a second.

*`STEPS`: climb 0.5 m/s × 3 s = 1.5 m · circle `forward=1.0, turn=1.0` = one lap, 1 m radius (the real drone comes up a little short on both: it needs time to speed up) · descend a little longer than the climb. Ctrl+C part-way sends hover first — otherwise the drone would keep its last command forever.*

#### 2.7 — T3: see how little the code changed

```bash
diff 1_turtlesim/turtle_circle.py 2_gazebo/sim_drone.py
```

Expected: only the description, `TOPIC`, the node name, `STEPS` and the Ctrl+C comment differ.

*The robot changed and the code barely did. That is the point of ROS.*

---

### Experiment 2D — Fly your own plan (exercise)

**Goal:** design and fly your own flight plan. · *Terminal: T3*

Edit `STEPS` in `2_gazebo/sim_drone.py`. **Climb higher:** climb 6 s, descend 7 s. **Two circles:** `4 * math.pi` seconds. **A square:** the turtle's square steps, with a climb before and a descend after.

Reset the drone to the ground: **Ctrl+C** in T1, run 2.1 again. T2 (the bridge) can keep running.

---

### Tidy up

**Ctrl+C** in T4, T2 and T1. If the Gazebo window stays open, close it with its window button.

---

### Check your understanding

<details><summary>1. Why does <code>ros2 node list</code> show one node in Lab 2, when there are clearly two programs running (Gazebo and the bridge)?</summary>

Gazebo is not a ROS 2 program. It has its own transport and topics (`ign topic -l`). Only the bridge is a ROS 2 node.

</details>

<details><summary>2. In step 2.4 one <code>--once</code> message made the drone climb indefinitely. Why did one message not do that to the turtle in Lab 1?</summary>

The X3's controller holds the last velocity it received; turtlesim forgets a command after one second. Same `Twist`, different robot behaviour — the message type is a contract about shape, not about what the robot does with it.

</details>

<details><summary>3. Read the bridge argument: <code>/X3/gazebo/command/twist@geometry_msgs/msg/Twist]ignition.msgs.Twist</code>. What does each part mean?</summary>

Topic name · `@` the ROS 2 type · `]` one way, ROS 2 → Gazebo · the Gazebo type.

</details>

<details><summary>4. What did <code>diff</code> in step 2.7 show, and what does that tell you about ROS 2?</summary>

Only the description, `TOPIC`, the node name, `STEPS` and a comment differ. The publisher pattern is independent of the robot; changing robots means changing data, not code.

</details>

<details><summary>5. Why does <code>sim_drone.py</code> send hover when you press Ctrl+C?</summary>

Because this drone keeps obeying its last command. Exiting mid-climb without a hover would leave it climbing forever.

</details>

### Troubleshooting

| What you see                                                   | Likely cause                                            | Fix                                                                             |
| -------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `ign: command not found`                                     | Gazebo is not installed                                 | `sudo apt install ros-humble-ros-gz`                                          |
| Gazebo takes minutes to open                                   | It is downloading the drone model                       | Wait once; the model is cached afterwards                                       |
| The Gazebo window is black or very slow                        | A virtual machine, or a missing graphics driver         | `ign gazebo -r --render-engine ogre multicopter_velocity_control.sdf`         |
| The drone ignores every command                                | The simulation is paused, or the bridge is not running  | Press ▶ at the bottom left. Check T2 is still running the bridge               |
| `ros2 node list` does not show `/ros_gz_bridge`            | The bridge stopped, or T2 skipped the setup line        | Restart step 2.2 in T2                                                          |
| The drone keeps climbing or circling after you stop the script | Ctrl+C was pressed twice, which skips the hover command | `ros2 topic pub --once /X3/gazebo/command/twist geometry_msgs/msg/Twist "{}"` |
| The drone has flipped or crashed                               | It hit the ground or flew too fast                      | Ctrl+C in T1, then run step 2.1 again                                           |

General problems: [section 9](#9-troubleshooting).

> **Later, on ROS 2 Jazzy (Ubuntu 24.04):** Gazebo Harmonic replaces Fortress, and `ign` becomes `gz`: `gz sim -r …` in 2.1, `gz.msgs.Twist` in 2.2, `gz topic -l` in 2.3. This tutorial itself supports Humble only.

---

## 7. Lab 3: Real Pluto drone

**The idea:** the pattern survives contact with hardware. A real drone needs a new message type (shaped like a radio controller's sticks), a translator that speaks its Wi-Fi protocol, and real safety rules — but the publisher is the same `StepPublisher` from Labs 1 and 2.

This lab needs a Pluto drone, a charged battery, and 2 m of clear floor. About 40 minutes.

**Prerequisite:** Labs 1 and 2 completed; `check_setup.sh` reports `PASS` for the Lab 3 checks (`custom_msgs`, `plutodrone`, `plutoserver`, `pluto_camera_sense`, `pynput`, OpenCV, `ffmpeg`).

**Experiments in this lab**

| Experiment | What you do | Steps |
| ---------- | ----------- | ----- |
| **3A** — Connect to the drone and read telemetry | `plutonode`, `plutoserver`, inspect | 3.1 – 3.3 |
| **3B** — Fly with the keyboard | `drone_comb.launch.py` | 3.4 – 3.5 |
| **3C** — Fly from the terminal | `ros2 topic pub --once` with `PlutoMsg` | 3.6 |
| **3D** — Fly with our script | `pluto_flight.py` | 3.7 |
| **3E** — Write your own telemetry server (exercise) | `pluto_telemetry.py` | — |
| **3F** — See through the drone's camera | `pluto_camera.py` | 3.8 |

If you are following this lab without a drone of your own (for example, watching one being flown), do steps 3.1 – 3.3 and 3.5 – 3.7 by reading the commands and the expected output; everything the drone does is visible in the `ros2 topic echo` of step 3.3.

---

### Safety — read before every flight

1. **Open floor.** 2 m clear, people behind a line, fresh battery.
2. **Keyboard control listens to the whole laptop. Space arms/disarms.** Start other terminals *before* it. Stop it (**Ctrl+C**) *before* typing anywhere else.
3. **Never run `pluto_flight.py` or `ros2 topic pub` while keyboard control runs.**
4. **Emergency stop:** keyboard flight → **space** disarms. Script flight → **Ctrl+C** lands and disarms.
5. **Stop `plutonode` only when landed and disarmed.** Ctrl+C may not stop it: close its terminal or **Ctrl+\\**.

### Pre-flight

- [ ] Battery charged and fitted; propellers undamaged, on the right motors
- [ ] Drone on flat floor, nothing within 2 m
- [ ] Laptop on the drone's Wi-Fi: `Pluto_XXXX`, password `dronaaviation`
- [ ] Four terminals, setup line run in each:

```bash
source ~/ROS2_Tutorial/env.sh
```

---

### Experiment 3A — Connect to the drone and read telemetry

**Goal:** a live link to the real drone, with its sensor readings on screen. · *Terminals: T1, T2, T4*

#### 3.1 — T1: connect to the drone

```bash
ros2 run plutodrone plutonode
```

Expected: `Pluto Connected`. (`Cannot connect to Pluto` → you're not on the drone's Wi-Fi. `plutonode` opens a TCP connection to `192.168.4.1:23`.)

*`plutonode` is this lab's bridge: ROS messages on one side, the drone's own protocol over Wi-Fi on the other. It resends the latest command every 22 ms.*

#### 3.2 — T2: telemetry

```bash
ros2 run plutoserver plutoserver
```

Expected: `Ready to Provide Pluto Service`, then Roll/Pitch/Yaw, Altitude, Battery (volts). Tilt the drone by hand and watch Roll and Pitch. Note the full-charge voltage.

*This is a **service**, not a topic — and the roles are the opposite of what you'd expect. `plutonode` is the service client: it packs the sensor readings into a request and calls `/pluto_service` many times a second. `plutoserver` is the server: it receives them and prints them. Step 3.3 shows this.*

#### 3.3 — T4: inspect, then watch commands

```bash
ros2 node list
ros2 interface show custom_msgs/msg/PlutoMsg
ros2 topic echo /drone_command custom_msgs/msg/PlutoMsg
```

Expected: `/pluto_node`, `/pluto_service`; the `PlutoMsg` fields; then the echo waits.

`rc_*` sticks: 1000–2000, 1500 = centre · `rc_aux4`: 1500 armed, 1200/1000 disarmed · `command_type`: 1 take off, 2 land · **never set `trim_*`**.

> **From here until 3.5, do not type in any terminal.**

---

### Experiment 3B — Fly with the keyboard

**Goal:** a first flight, by hand. · *Terminal: T3*

#### 3.4 — T3: fly with the keyboard

```bash
ros2 launch plutoserver drone_comb.launch.py
```

| Key   | Action       | Key   | Action            |
| ----- | ------------ | ----- | ----------------- |
| space | Arm / disarm | ↑ ↓ | Forward / back    |
| q     | Take off     | ← → | Left / right      |
| e     | Land         | a / d | Turn left / right |
| w / s | Up / down    | r     | Sticks to centre  |

Any other key = sticks to centre. **Esc** quits the node. **Do not press `t`** — it toggles autopilot mode.

Sequence: **space** → **q** → gentle moves → **e** → **space**. Watch `rc_aux4` and `command_type` in T4.

*Two nodes: `key_command` reads keys (with `pynput`, from the whole laptop) and publishes a number on `/input_key`; `key_handling` turns it into a `PlutoMsg` on `/drone_command`. Check with `ros2 node info /key_handling`.*

#### 3.5 — T3: stop keyboard control

**Ctrl+C** in T3. Typing is safe again.

---

### Experiment 3C — Fly from the terminal

**Goal:** take off, land and disarm with single commands. · *Terminal: T3*

#### 3.6 — T3: fly from the terminal (one command at a time, wait between)

```bash
# take off (also arms)
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1500, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1500, command_type: 1}"

# land
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1500, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1500, command_type: 2}"

# disarm
ros2 topic pub --once /drone_command custom_msgs/msg/PlutoMsg "{rc_roll: 1500, rc_pitch: 1500, rc_yaw: 1500, rc_throttle: 1300, rc_aux1: 1500, rc_aux2: 1500, rc_aux3: 1500, rc_aux4: 1200, command_type: 0}"
```

*Give **every** `rc_` field — a missing field is sent as 0, far outside 1000–2000. `--once` is enough because `plutonode` resends every 22 ms; the turtle needed `--rate 1` because nothing repeated for it.*

---

### Experiment 3D — Fly with our script

**Goal:** a complete flight run by `StepPublisher`. · *Terminal: T3*

#### 3.7 — T3: fly with our script

```bash
python3 3_pluto/pluto_flight.py
```

Expected: idle → take off and hover → land → disarm, and in T3:

```
[INFO] [...] [pluto_flight]: idle (1.0 s)
[INFO] [...] [pluto_flight]: take off and hover (5.0 s)
[INFO] [...] [pluto_flight]: land (4.0 s)
[INFO] [...] [pluto_flight]: disarm (1.0 s)
```

Run it the first time **with the propellers removed** and watch T4: `command_type` should be `1` in exactly one message, then `0`; later `2` once, then `0`; and `rc_aux4` should end at `1200`. Then fit the propellers and run it again.

*Same `StepPublisher` as Labs 1 and 2: different topic, message and plan — and **Ctrl+C lands** instead of just stopping. Disarms before touchdown? Increase `LAND_SECONDS` at the top of the script.*

---

### Experiment 3E — Write your own telemetry server (exercise, T2)

**Goal:** replace `plutoserver` with your own 20-line service server. · *Terminal: T2*

Stop `plutoserver` in T2 (**Ctrl+C**), then:

```bash
python3 3_pluto/pluto_telemetry.py
```

Expected: `battery=… V  altitude=…  roll=…  pitch=…  yaw=…`, twice a second. Tilt the drone and watch.

*20 lines: `create_service(PlutoPilot, 'pluto_service', self.on_request)` and a callback that reads `request.battery`. You wrote the server; the drone side calls you. Compare with `1_turtlesim/turtle_pose.py`: a subscriber gets a message, a server gets a request and must return a response.*

**Idea:** log battery to a file and print a warning below a voltage you choose.

---

### Experiment 3F — See through the drone's camera

**Goal:** live video from the drone in a window on your laptop. · *Terminals: T1, T2, T3*

#### 3.8 — Camera (separate demo)

Land, disarm, stop T1 and T2. Join the **camera module's** Wi-Fi. Then:

```bash
ros2 run pluto_camera_sense plutocam_publisher     # T1
python3 3_pluto/pluto_camera.py                    # T2
ros2 topic hz /plutocamera/image_raw               # T3
```

Expected: `Connected to PlutoCamera at 192.168.0.1`, a **Pluto camera** window, a frame rate in T3. Wave at it.

*The drone publishes, your script subscribes. A laptop joins one Wi-Fi at a time, which is why this can't run alongside flight.*

---

### Tidy up

Land and disarm first. **Ctrl+C** in T3, T4. Close the T1 and T2 terminals (trash-can icon), since `plutonode` ignores Ctrl+C. Power off, unplug the battery.

---

### Check your understanding

<details><summary>1. What does the Pluto publish on ROS 2 topics?</summary>

Nothing. `plutonode` subscribes to `/drone_command` (and `/drone_ap_command`) and is a **service client** of `/pluto_service`. Its sensor data travels inside service requests, which is why `ros2 topic echo` can never show telemetry.

</details>

<details><summary>2. <code>plutoserver</code> and <code>pluto_telemetry.py</code> — which one is the client and which the server?</summary>

Both are **servers** for `/pluto_service`; `plutonode` is the client that calls them. Run only one server at a time.

</details>

<details><summary>3. Why must every <code>rc_</code> field be given in a <code>ros2 topic pub</code> message?</summary>

A field you leave out is sent as 0, which is far below the 1000–2000 stick range. `plutonode` forwards those values to the drone as they are.

</details>

<details><summary>4. Why is <code>--once</code> enough for the Pluto when the turtle needed <code>--rate 1</code>?</summary>

`plutonode` resends the latest values to the drone every 22 ms. The repeating happens on the other side of the translator.

</details>

<details><summary>5. What does Ctrl+C do in <code>pluto_flight.py</code>, and why is it different from Labs 1 and 2?</summary>

It lands and then disarms, instead of just stopping. "Stop" is not a safe thing to do to a real aircraft in the air.

</details>

<details><summary>6. Which two things in this lab are the same idea as the Gazebo bridge?</summary>

`plutonode` (ROS 2 on one side, the drone's own protocol over TCP on the other) and `plutocam_publisher` (the camera's stream in, `sensor_msgs/Image` out). Most hardware needs a translator.

</details>

### Troubleshooting

| What you see                                            | Likely cause                                                        | Fix                                                                                                                     |
| ------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `Cannot connect to Pluto, please try again`           | The laptop is not on the drone's Wi-Fi                              | Join `Pluto_XXXX` (password `dronaaviation`), then run `plutonode` again                                           |
| `ModuleNotFoundError: No module named 'custom_msgs'`  | The Pluto workspace is not built or not sourced                     | Build it (section 2.3); check `PLUTO_WS` in `env.sh`; open a new terminal                                            |
| `ModuleNotFoundError: No module named 'pynput'`       | The keyboard library is missing                                     | `pip3 install pynput`                                                                                                 |
| The keyboard control does nothing                       | Ubuntu is using Wayland, which blocks reading the keyboard globally | Log out, click the gear icon on the login screen, choose **Ubuntu on Xorg**, log in again. Or use step 3.6 instead |
| `plutonode` crashed after a `ros2 topic pub`        | `trim_roll` or `trim_pitch` was set                             | Leave the trim fields out                                                                                               |
| The drone behaves wildly after a `ros2 topic pub`      | An `rc_` field was left out, so it was sent as 0                   | Land with **e** or the land command. Always give all eight `rc_` fields                                          |
| The drone drifts badly                                  | Uneven ground at start-up, or a sensor needs resetting              | Land at once. Put the drone on flat ground and power-cycle it                                                           |
| The drone disarms before it touches down                | The `land` step is too short                                       | Increase `LAND_SECONDS` in `pluto_flight.py`                                                                         |
| `plutonode` will not stop with Ctrl+C                 | Its sending threads keep running                                    | Close its terminal window, or press Ctrl+\\                                                                             |
| `plutoserver` prints nothing                          | `plutonode` is not connected, so nothing calls the service        | Check T1 says `Pluto Connected`                                                                                        |
| `pluto_telemetry.py` and `plutoserver` both running | Two servers on one service name                                     | Stop one. ROS 2 does not prevent two servers with one name, and both receive the calls |
| No camera window                                        | The laptop is on the wrong Wi-Fi                                    | Join the camera module's Wi-Fi, not `Pluto_XXXX`; check `plutocam_publisher` says `Connected`                      |

General problems: [section 9](#9-troubleshooting).

---

## 8. Extra: ROS 2 basics on the command line

The four ways ROS 2 nodes communicate — topics, services, actions, parameters — seen from the terminal, using turtlesim as the robot. No code yet. About 30 minutes.

**Prerequisite:** `check_setup.sh` reports `PASS` for the Lab 1 checks.
Read **[section 1](#1-what-is-ros)** first.

Setup line in **T1, T2, T3**:

```bash
source ~/ROS2_Tutorial/env.sh
```

---

### 8.1 — T1: a robot to talk to

```bash
ros2 run turtlesim turtlesim_node
```

### 8.2 — T2: a second node

```bash
ros2 run turtlesim turtle_teleop_key
```

Everything below goes in **T3**.

---

### Nodes — *which programs are running?*

```bash
ros2 node list
```

```bash
ros2 node info /turtlesim
```

*`node info` lists everything one node publishes, subscribes to, and offers as services and actions. It is the map of the robot.*

---

### Topics — *a stream of messages, many-to-many, no reply*

```bash
ros2 topic list -t
```

```bash
ros2 topic info /turtle1/cmd_vel
```

```bash
ros2 topic echo /turtle1/pose
```

(Drive in T2 and watch. **Ctrl+C** to stop the echo.)

```bash
ros2 topic hz /turtle1/pose
```

*`-t` shows each topic's message type. `hz` shows how fast messages arrive — about 62 a second for the pose. A topic is for things that keep happening: positions, camera frames, velocity commands.*

Say something yourself:

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 1.0}}"
```

---

### Message types — *the shape of a message*

```bash
ros2 interface show geometry_msgs/msg/Twist
```

```bash
ros2 interface show turtlesim/msg/Pose
```

*A `.msg` is a list of named, typed fields. Every message on a topic has exactly this shape. Both sides must agree on it.*

---

### Services — *one request, one reply*

```bash
ros2 service list -t
```

```bash
ros2 interface show turtlesim/srv/Spawn
```

*A `.srv` has two halves separated by `---`: the request fields and the response fields.*

Call one:

```bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```

Expected: a second turtle appears, and the reply `name='turtle2'` prints. Now there are more topics:

```bash
ros2 topic list
```

Two more useful ones:

```bash
ros2 service call /clear std_srvs/srv/Empty
```

```bash
ros2 service call /reset std_srvs/srv/Empty
```

*Use a service for things that happen once and need an answer: spawn, reset, take a photo, save a map. Use a topic for things that stream.*

---

### Actions — *a long task with progress and the option to cancel*

```bash
ros2 action list -t
```

```bash
ros2 interface show turtlesim/action/RotateAbsolute
```

*An `.action` has three parts: goal, result, feedback. Like a service, but it can take seconds or minutes, it reports progress while it runs, and you can cancel it.*

Send a goal and watch the feedback:

```bash
ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

Expected: the turtle rotates to face up; `remaining:` counts down to 0; then `Result: delta: …` and `Goal finished with status: SUCCEEDED`.

*Navigation ("go to the kitchen") and a drone's "take off to 2 m" are actions in real systems: they take time, you want progress, and you may need to abort.*

---

### Parameters — *a node's settings, changeable while it runs*

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

Expected: after `/clear`, the background turns purple.

*Parameters are how you configure a node without editing code: a camera's frame rate, a controller's gain, a topic name.*

---

### The four kinds of communication, side by side

|                     | Pattern                      | Who starts it           | Reply?           | Turtlesim example                       | Real-robot example                 |
| ------------------- | ---------------------------- | ----------------------- | ---------------- | --------------------------------------- | ---------------------------------- |
| **Topic**     | stream                       | publisher, continuously | no               | `/turtle1/cmd_vel`, `/turtle1/pose` | camera frames, velocity commands   |
| **Service**   | request → reply             | the client, once        | yes, one         | `/spawn`, `/reset`                  | "take a photo", "save the map"     |
| **Action**    | goal → feedback… → result | the client, once        | progress + final | `/turtle1/rotate_absolute`            | "navigate to X", "take off to 2 m" |
| **Parameter** | setting                      | whoever sets it         | —               | `background_r`                        | controller gains, frame rate       |

---

### Tidy up

**Ctrl+C** in T3 (if anything is running) and T1. **q** in T2.

---

## 9. Troubleshooting

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

Each lab also ends with its own troubleshooting table.

---

## 10. Extra: your own package — workspace, colcon, launch

Labs 1–3 ran loose Python files with `python3 file.py`. Real ROS 2 code lives in a **package** inside a **workspace**, is built with **colcon**, and runs with `ros2 run` and `ros2 launch`. This section builds one. About 40 minutes.

Needs `colcon`: `sudo apt install python3-colcon-common-extensions` (checked by `check_setup.sh`).

Setup line in **T1, T2, T3**:

```bash
source ~/ROS2_Tutorial/env.sh
```

---

### The shape of things

```
~/ros2_ws/                       the WORKSPACE
├── src/                         your source packages go here
│   └── tutorial_pkg/            a PACKAGE
│       ├── package.xml          name, version, dependencies
│       ├── setup.py             how to install it; which commands it provides
│       ├── setup.cfg
│       ├── resource/tutorial_pkg
│       ├── tutorial_pkg/        the Python module
│       │   ├── __init__.py
│       │   ├── talker.py        a publisher
│       │   ├── listener.py      a subscriber
│       │   └── turtle_square.py Lab 1's exercise, as a node
│       └── launch/
│           ├── talker_listener.launch.py
│           └── turtle_square.launch.py
├── build/                       made by colcon — don't edit
├── install/                     made by colcon — you `source` this
└── log/
```

---

### 10.1 — T1: make a workspace

```bash
mkdir -p ~/ros2_ws/src
```

```bash
cd ~/ros2_ws/src
```

*A workspace is just a folder with a `src/` inside. colcon builds everything it finds under `src/`.*

---

### 10.2 — T1: see how a package is created, then use ours

This is the command that creates an empty package. Run it to see the scaffold:

```bash
ros2 pkg create --build-type ament_python --license MIT demo_pkg --dependencies rclpy std_msgs
```

```bash
ls demo_pkg
```

Expected: `LICENSE  package.xml  setup.py  setup.cfg  resource/  demo_pkg/  test/`.

Now copy the finished package from the tutorial folder next to it:

```bash
cp -r ~/ROS2_Tutorial/4_workspace/tutorial_pkg ~/ros2_ws/src/
```

Open `~/ros2_ws/src/tutorial_pkg` in the editor and read these two files:

| File            | Look for                                                              | Why it matters                                                 |
| --------------- | --------------------------------------------------------------------- | -------------------------------------------------------------- |
| `package.xml` | `<depend>rclpy</depend>`, `<build_type>ament_python</build_type>` | Tells ROS what this package needs and how to build it          |
| `setup.py`    | `entry_points` → `'talker = tutorial_pkg.talker:main'`           | Each line becomes a `ros2 run tutorial_pkg talker` command    |
| `setup.py`    | `data_files` → `launch/*.launch.py`                              | Without this line, `ros2 launch` can't find your launch files |

---

### 10.3 — T1: build it

```bash
cd ~/ros2_ws
```

```bash
colcon build --symlink-install
```

Expected: `Summary: 2 packages finished`.

*`--symlink-install` links your `.py` files instead of copying them, so editing a Python file doesn't need a rebuild. Adding a new node or launch file does.*

Then, in **every terminal that will run this package**:

```bash
source ~/ros2_ws/install/setup.bash
```

*The setup line (`env.sh`) already does this for `~/ros2_ws` if it exists, so new terminals get it automatically.*

---

### 10.4 — T1 and T2: the publisher and the subscriber

**T1:**

```bash
ros2 run tutorial_pkg talker
```

Expected: `Publishing: "Hello 0"`, `"Hello 1"`, … twice a second.

**T2** (setup line, then):

```bash
ros2 run tutorial_pkg listener
```

Expected: `I heard: "Hello 7"`, … matching T1.

**T3:**

```bash
ros2 topic list
```

```bash
ros2 topic echo /chatter
```

*`talker.py`: `create_publisher(String, '/chatter', 10)` + a `create_timer(0.5, …)` that publishes. `listener.py`: `create_subscription(String, '/chatter', self.on_msg, 10)` + `rclpy.spin()`. That is the entire pub/sub pattern; every node you ever write is a variation.*

**Ctrl+C** in T1, T2, T3.

---

### 10.5 — T1: a launch file starts several nodes at once

```bash
ros2 launch tutorial_pkg talker_listener.launch.py
```

Expected: both nodes start in one terminal, with `[talker]` and `[listener]` prefixes. **Ctrl+C** stops both.

Open `launch/talker_listener.launch.py`: a Python function that returns a list of `Node(package=…, executable=…)`.

*Real robots start dozens of nodes. Nobody opens dozens of terminals; they write a launch file. Lab 3's `drone_comb.launch.py` is one — it starts `key_command` and `key_handling` together.*

---

### 10.6 — T1: Lab 1's exercise (Experiment 1E), as a real package

```bash
ros2 launch tutorial_pkg turtle_square.launch.py
```

Expected: turtlesim opens **and** the turtle draws a square, from one command.

*Compare `tutorial_pkg/turtle_square.py` with `1_turtlesim/turtle_circle.py`: same code, but now it has a `ros2 run` name, lives in a package you can share, and can be launched with the simulator.*

---

### Exercise

1. Add a node: copy `talker.py` to `counter.py`, make it publish an `Int32` on `/count` (import from `std_msgs.msg`). Add `'counter = tutorial_pkg.counter:main'` to `entry_points` in `setup.py`.
2. Rebuild (`colcon build --symlink-install`), re-source, `ros2 run tutorial_pkg counter`, then `ros2 topic echo /count`.
3. Add it to `talker_listener.launch.py` and launch all three.

---

### Quick reference

| Command                                              | Does                                                            |
| ---------------------------------------------------- | --------------------------------------------------------------- |
| `ros2 pkg create --build-type ament_python <name>` | New empty Python package                                        |
| `colcon build --symlink-install`                   | Build every package under `src/` (run from the workspace root) |
| `colcon build --packages-select tutorial_pkg`      | Build just one                                                  |
| `source install/setup.bash`                        | Make the built packages visible to this terminal                |
| `ros2 run <pkg> <node>`                            | Run one node                                                    |
| `ros2 launch <pkg> <file>.launch.py`               | Run a set of nodes                                              |
| `ros2 pkg list \| grep tutorial`                    | Is my package visible?                                          |

| You see                              | Fix                                                                        |
| ------------------------------------ | -------------------------------------------------------------------------- |
| `Package 'tutorial_pkg' not found` | `source ~/ros2_ws/install/setup.bash` in this terminal                   |
| `No executable found`              | Entry point missing in `setup.py`, or not rebuilt after adding it         |
| `file 'x.launch.py' was not found` | `data_files` in `setup.py` doesn't include `launch/`, or not rebuilt |
| `colcon: command not found`        | `sudo apt install python3-colcon-common-extensions`                      |

---

## 11. Where things are

```
ROS2_Tutorial/
├── install.sh             section 2 as one script
├── env.sh                 the setup line runs this
├── check_setup.sh         checks the laptop is ready
├── 1_turtlesim/
│   ├── turtle_circle.py   publisher: drives the turtle in one circle
│   └── turtle_pose.py     subscriber: prints where the turtle is
├── 2_gazebo/
│   └── sim_drone.py       publisher: flies the simulated drone
├── 3_pluto/
│   ├── pluto_flight.py    publisher: take off, hover, land, disarm
│   ├── pluto_telemetry.py service server: receives the drone's sensor data
│   └── pluto_camera.py    subscriber: shows the drone's camera
└── 4_workspace/
    └── tutorial_pkg/      a complete ROS 2 Python package to copy into ~/ros2_ws/src
```

Keep learning: [ROS 2 Humble tutorials](https://docs.ros.org/en/humble/Tutorials.html) · [Drona Aviation on GitHub](https://github.com/DronaAviation)
