# 📜 RL-BASED ATTACKER MODEL

## Table of Contents

1. [Adversary Classes](#1-adversary-classes)
2. [Program Representation](#2-program-representation)
3. [State Definition](#3-state-definition)
4. [Action Space](#4-action-space)
5. [Reward Function](#5-reward-function)
6. [Randomness Model](#6-randomness-model)
7. [Features & Observations](#7-features--observations)
8. [Reinforcement Learning Setup](#8-reinforcement-learning-setup)

---

## 1. Adversary Classes

We define exactly **three** classes of adversaries, with no in-between:

1. **Black-Box Non-Adaptive**

   - **Definition**: This attacker picks a finite set of inputs `(x_i, y_i)` in advance, without seeing any output from the program.  
     Formally, the attacker’s strategy is a list `(a₁, a₂, …, a_N)`, chosen offline.
   - **Knowledge**: Zero knowledge of code.
   - **Interaction**: Possibly multiple tries, but always ignoring the program’s outputs.

2. **Black-Box Adaptive**

   - **Definition**: This attacker picks inputs step by step, using prior outputs. For attempt `k`, the chosen `(x_k, y_k)` = gₖ( o₁, …, oₖ₋₁ ), where oᵢ is the output (e.g. EXPLOIT=0/1) from the previous attempt.
   - **Knowledge**: No code knowledge, purely sees success/fail each time.
   - **Interaction**: Potentially unbounded tries, each time can adapt.

3. **Symbolic (White-Box) Attacker**
   - **Definition**: Has partial or total knowledge of the code, can form path constraints and do model-counting or Max#SAT.
   - **Knowledge**: Full or partial.
   - **Interaction**: Possibly one or more tries, but can also do “offline” perfect analysis.

For our RL environment, we **focus** on the **Black-Box Adaptive** case. We do not code anything for the other classes, but we keep them as references.

---

## 2. Program Representation

We use real C programs, each compiled into a separate binary `target.bin`. The environment:

1. Feeds `(x, y)` via stdin in a single line. Example:
   ```bash
   echo "X=42 Y=900" | ./target.bin
   ```
   The target prints `EXPLOIT=1` on success, `EXPLOIT=0` otherwise.

We capture that line and convert `EXPLOIT=1` → reward=+10, `EXPLOIT=0` → reward=-1.

No partial instrumentation, no side-channels measured. We do black-box only.

---

## 3. State Definition

We represent the RL state as:
sₜ = ( last_x, last_y, last_success, step_index )

- `last_x, last_y ∈` integer sets: the action from the previous step.
- `last_success ∈ {0, 1}`: whether the prior attempt triggered an exploit.
- `step_index ∈ {0..MaxAttempts}`: indicates how many tries have been taken in the current episode.

No additional memory or rolling window. Exactly one-step memory. If `t=0`, we set them to `( -1, -1, 0, 0 )` (meaning no prior attempt) at the start of an episode.

---

## 4. Action Space

We fix a discrete action space:

- `Val_x = 0..100` (inclusive), so 101 bins for `x`.
- `Val_y = 0..1000` (inclusive), so 1001 bins for `y`.

Therefore total number of discrete actions = `101 × 1001 = 101,101`.

(We realize that’s large, but that is our final choice. We do not do continuous controls.)

Each RL step, the agent picks `(x,y)` from this set.

---

## 5. Reward Function

Single-snapshot scheme:

```java
If exploit triggered => +10
Else => -1
```

We do not add shaping (like partial +1).

We fix the discount factor γ = 1.0 exactly, meaning we sum rewards over the tries in one episode.

The episode ends early if exploit is triggered, or after MaxAttempts = 50.

---

## 6. Randomness Model

Inside each episode, the target picks:

- `y_r`, a random offset in `[0..100]`, once at the beginning of the episode (the user can do `rand() % 101` in the C code).
- For each run, we do exactly one attempt, so if the code draws further random values `y_c`, it’s overshadowed by the fact that the attempt ends quickly. Essentially, `y_c` can appear, but the RL agent never sees it.

We finalize that `y_r` is constant for the entire episode. Next episode, `y_r` is newly chosen.

Hence the agent must discover that some seeds are “harder” or “easier” but cannot see them. This is final.

---

## 7. Features & Observations

We store only:

```scss
(last_x, last_y, last_success, step_index)
```

No other features, no code knowledge, no path constraints, no partial BFS or partial symbolic execution. This is purely black-box adaptive.

---

## 8. Reinforcement Learning Setup

### 8.1 MDP

- **States**: `( last_x, last_y, last_success, step_index )`.
- **Actions**: `( x, y )` from discrete sets described above.
- **Transition**:
  1. We pass `(x, y)` to the binary `target.bin`.
  2. We read `EXPLOIT=?`.
  3. Next state has `last_x ← x`, `last_y ← y`, `last_success ← (0 or 1)`, `step_index ← step_index + 1`.

### 8.2 Q-Learning

- Q-Table dimension = `|S| × |A|`, with `|S| = 101 × 1001 × 2 × 51` if we consider `step_index` up to 50, etc.
- Large but we proceed anyway.
- If too big, we might switch to neural net approximation, but that’s not in scope right now.

### 8.3 Implementation Outline

We do **not** embed C code in Python. Instead:

1. Compile `target.c → target.bin`.
2. For each RL step:

   ```bash
   echo "X=17 Y=500" | ./target.bin
   ```
