# Coding tasks: squares and more

Eight tasks that make you write code, four on turtlesim and four on the Gazebo drone. Do them after Lab 1 (T tasks) and Lab 2 (D tasks).

| Level | What you do |
| ----- | ----------- |
| ★ | Build `STEPS` with your own Python function |
| ★★ | Change the publisher itself |
| ★★★ | Write a new node that reads the robot's position and decides what to send |

**Work on a copy, never on the original:**

```bash
cp 1_turtlesim/turtle_circle.py 1_turtlesim/my_square.py
python3 1_turtlesim/my_square.py
```

For each task, keep your script and the output lines that show the **Done when** check passed.

---

## Turtlesim tasks

**Setup:** as in Lab 1. **T1** `ros2 run turtlesim turtlesim_node` · **T3** your script · **T4** `python3 1_turtlesim/turtle_pose.py` to read the position.
Before each run: `ros2 service call /reset std_srvs/srv/Empty`.

### T1 ★ — A square of any size

Experiment 1E gave you one square. Now write a function that makes any square:

```python
def square(side, speed=1.0):
    """Return the STEPS for one square with sides `side` metres long."""
    ...
```

Then draw three nested squares that share one corner:

```python
STEPS = square(1.0) + square(2.0) + square(3.0) + [('stop', 1.0, twist())]
```

*Hints:* time for a side = `side / speed`. A 90° turn = `math.pi / 2` rad, so `turn=math.pi / 2` for 1 s. Keep the final `stop` step: turtlesim keeps obeying the last command for one second, so without it the turtle turns an extra 90°.

**Done when:** three nested squares, and T4 shows the turtle back within about 0.2 m of where it started (5.54, 5.54).

### T2 ★ — Any polygon, and a star

Write `polygon(n, side)`, which returns the steps for a regular shape with `n` sides. Draw a triangle, a pentagon and a hexagon.

Then a five-pointed star. It is a "polygon" whose turn is 144° (`4 * math.pi / 5`) instead of 72°.

*Hint:* a full trip round any closed shape turns the turtle through 360° in total, so each turn is `2 * math.pi / n`.

**Done when:** each shape closes, and the star has five points.

### T3 ★★ — A square in four colours

Make each side of the square a different colour. The pen colour is changed with a **service**, `/turtle1/set_pen`. Try it from a terminal first:

```bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 4, off: 0}"
```

Now do the same from your script, before each side.

*Hints:*
- `from turtlesim.srv import SetPen`
- In `__init__`: `self.pen = self.create_client(SetPen, '/turtle1/set_pen')`
- To call it: `future = self.pen.call_async(SetPen.Request(r=..., g=..., b=..., width=4, off=0))`, then `rclpy.spin_until_future_complete(self, future)` to wait for the answer.
- `off=1` lifts the pen. Use it to move without drawing.

**Done when:** a square with four differently coloured sides.

### T4 ★★★ — An exact square, using the turtle's position

T1 drives blind: it sends speeds for a time and hopes. Write a new node that **looks where the turtle is** and drives to each corner:

```python
CORNERS = [(8.5, 5.5), (8.5, 8.5), (5.5, 8.5), (5.5, 5.5)]
```

Your node subscribes to `/turtle1/pose` and publishes on `/turtle1/cmd_vel` (`turtle_pose.py` + `turtle_circle.py` in one node). Ten times a second (`self.create_timer(0.1, self.on_timer)`):

1. Find the direction to the corner: `math.atan2(dy, dx)`.
2. Heading error = that direction − `pose.theta`, wrapped to −π…π: `math.atan2(math.sin(e), math.cos(e))`.
3. Turn by an amount proportional to the error (try `turn = 4 * error`). Drive forward only once the error is small (below 0.05 rad).
4. Closer than 0.05 m → log where you actually are, and go to the next corner.

**Done when:** every corner is reached within 0.05 m. Compare with T1's 0.2 m: why is this one so much better?

---

## Gazebo drone tasks

**Setup:** as in Lab 2, with the two-topic bridge from step 2.10. **T1** Gazebo · **T2** bridge · **T3** your script · **T4** `python3 2_gazebo/sim_drone_pose.py`.
To put the drone back on the ground between runs: **Ctrl+C** in T1, start Gazebo again.

Copy `2_gazebo/sim_drone.py` to start. Two rules from testing:

- **Turn slowly: at most 0.5 rad/s.** At about 1.6 rad/s the X3 loses height and crashes.
- **Put a short `hover` between moves.** The drone needs time to stop before the next move.

### D1 ★ — A square in the air, by turning

Climb to 1.5 m. Fly a square with 2 m sides, turning 90° at each corner. Land.

*Hints:* 0.5 m/s for 4 s = 2 m. A 90° turn at 0.5 rad/s takes `math.pi` seconds (π/2 ÷ 0.5). Reuse your `square()` idea from T1, with hovers added.

**Done when:** T4 shows four corners about 2 m apart at about 1.5 m height, then a landing. Note where it lands, compared with where it started.

### D2 ★★ — A square without turning

A drone can fly sideways. Fly the same square while always facing the same way: forward, left, back, right.

`twist()` has no sideways argument yet. **Add one:** `left`, which sets `msg.linear.y`.

**Done when:** T4 shows corners near (2, 0), (2, 2), (0, 2), (0, 0), and the drone lands close to where it took off. Why does it end closer to its start than in D1?

### D3 ★ — A spiral staircase

Fly the D1 square, but climb 0.5 m along each side. Then land.

*Hints:* a step can climb and move at once: `twist(forward=0.5, up=0.125)` for 4 s = 2 m forward and 0.5 m up. Work out how long `descend` must be from the final height.

**Done when:** T4 shows the height rise by about 0.5 m per side (about 1.5 → 3.0 m), and the drone lands.

### D4 ★★★ — Hold exactly 2.0 m

`sim_drone.py` aimed for 1.5 m and got 1.3 m (step 2.12). Write a node that reaches **exactly** 2.0 m by reading the height.

Your node subscribes to `/model/x3/odometry` and publishes on `/X3/gazebo/command/twist` (`sim_drone_pose.py` + `sim_drone.py` in one node). Ten times a second:

- **Climb:** `up = gain × (2.0 − height)`, with `gain = 1.0`, limited to ±0.5 m/s. Far away → fast. Close → slow.
- When within 0.03 m: **hold** for 5 s, still using the same formula.
- Then **land**: `up = -0.5` until the height is below 0.10 m, then send 0.

**Done when:** your log shows 2.00 ± 0.05 m for the 5 s hold, then a landing. **Bonus:** fly the D2 square at the held height.

---

*Stuck? Ask your instructor. Reference solutions exist for every task.*
