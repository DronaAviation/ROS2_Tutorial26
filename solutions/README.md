# Reference solutions for TASKS.md

For instructors. Every solution was run on Humble with turtlesim and Gazebo Fortress; the "tested" lines are the results seen.

| Task | Solution |
| ---- | -------- |
| T1, T2, D1, D3 | the `STEPS` below, pasted into a copy of `turtle_circle.py` / `sim_drone.py` |
| T3 | [turtle_colour_square.py](turtle_colour_square.py) |
| T4 | [turtle_goto_square.py](turtle_goto_square.py) |
| D2 | [drone_square_strafe.py](drone_square_strafe.py) (`diff` it with `2_gazebo/sim_drone.py`) |
| D4 | [drone_hold_height.py](drone_hold_height.py) |

## T1 — square of any size

```python
def square(side, speed=1.0):
    return [
        ('side', side / speed, twist(forward=speed)),
        ('turn', 1.0, twist(turn=math.pi / 2)),
    ] * 4

STEPS = square(1.0) + square(2.0) + square(3.0) + [('stop', 1.0, twist())]
```

Tested: ends about 0.2 m from the start, at (5.71, 5.41). Without the final `stop` the turtle turns an extra 90°, because turtlesim keeps the last command for one second.

## T2 — polygon and star

```python
def polygon(n, side, turn_angle=None, speed=1.0):
    turn_angle = turn_angle or 2 * math.pi / n
    return [
        ('side', side / speed, twist(forward=speed)),
        ('turn', 1.0, twist(turn=turn_angle)),
    ] * n

STEPS = polygon(5, 2.0) + [('stop', 1.0, twist())]                       # pentagon
STEPS = polygon(5, 3.0, turn_angle=4 * math.pi / 5) + [('stop', 1.0, twist())]   # star
```

Tested: the star closes, ending about 0.16 m from the start.

## T3, T4

Tested: T3 draws red, green, blue, yellow sides. T4 reaches every corner within 0.05 m, for example `aimed (8.50, 5.50), reached (8.46, 5.50)`. That is about 4× closer than T1.

## D1 — square by turning

```python
STEPS = [('climb', 3.0, twist(up=0.5))] + [
    ('side', 4.0, twist(forward=0.5)),          # 2 m
    ('hover', 1.0, twist()),
    ('turn', math.pi, twist(turn=0.5)),         # 90° at 0.5 rad/s
    ('hover', 0.5, twist()),
] * 4 + [
    ('descend', 4.0, twist(up=-0.5)),
    ('hover', 1.0, twist()),
]
```

Tested: corners about 2 m apart at 1.53–1.61 m; landed about 0.65 m from the start, at (−0.36, 0.55). Turning at `math.pi / 2` rad/s for 1 s crashed the X3 every time.

## D2 — square without turning

Tested: corners (1.85, 0.01), (1.84, 1.85), (0.07, 1.84), (0.00, 0.00); height 1.46–1.53 m. It lands where it started, because no yaw error rotates the later sides.

## D3 — staircase

```python
STEPS = [('climb', 2.0, twist(up=0.5))] + [
    ('stair', 4.0, twist(forward=0.5, up=0.125)),   # 2 m forward, 0.5 m up
    ('hover', 1.0, twist()),
    ('turn', math.pi, twist(turn=0.5)),
    ('hover', 0.5, twist()),
] * 4 + [
    ('descend', 7.0, twist(up=-0.5)),               # about 3 m down
    ('hover', 1.0, twist()),
]
```

Tested: heights 1.55 → 2.07 → 2.60 → 3.12 m, then landed.

## D4 — hold height

Tested: reached 1.97 m, overshot to 2.05 m, settled at 2.00 m for the 5 s hold, landed.
