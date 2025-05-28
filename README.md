# 🚛 Border Truck Simulation

This project simulates the movement and behavior of trucks in a queue at a border checkpoint. The simulation includes both dynamic and static trucks, visual state transitions, countdown logic, and rules for movement and crossing.

## 📦 Features

- Real-time queue simulation of trucks at a border
- Trucks with dynamic or static behavior
- Countdown mechanism to "unstick" static trucks
- Randomized logic to start movement based on empty spaces ahead
- Color-coded truck states for visualization

---

## 🧠 Core Logic

### Truck States

Each truck in the simulation can have the following properties:

- `position`: Integer representing its current spot in the queue (0 = at the border)
- `is_static`: Whether the truck is currently stuck
- `countdown_active`: If true, the static truck has started its countdown to move
- `static_remaining`: Countdown ticks left before the truck can move
- `color`: Indicates the truck's state visually (`green`, `orange`, `red`)

### Truck Colors

- 🟢 **Green** — Moving normally
- 🔴 **Red** — Static and stuck
- 🟠 **Orange** — Just became unstuck, will move in the next update

---

## 🔁 Update Logic (Per Tick)

### Step 1: Activate Static Countdown

If a truck is static and doesn't already have an active countdown, it checks **how many empty spaces are ahead** of it. If there are between **2 and 5 consecutive empty positions**, it activates a countdown to become unstuck.
required_spaces = random.randint(2, 5)
------------------------------------
### Step 2: Countdown Timer
Static trucks with an active countdown tick down their static_remaining value until it reaches 0. When this happens:

The truck is marked as dynamic (is_static = False)

Its color changes to orange (ready to move)
---
### Step 3: Movement Blocking
Movement is blocked for trucks that are behind the first static truck whose countdown is still active, preventing pileups.
---

### Step 4: Movement Logic
Dynamic trucks move forward to the nearest available empty spot ahead of them, unless they're blocked. If they reach position == 0 (the border), they are removed from the queue.
