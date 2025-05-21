# Formalizing the Problem in Reinforcement Learning (RL)

## 1. Introduction

We aim to formalize the attack on a vulnerable program as a **Reinforcement Learning (RL) problem**, modeling the attacker as an **agent** interacting with an environment (the target program) to maximize exploitation chances. The key shift from previous approaches is **moving away from random search** and towards an adaptive learning process that refines attack strategies over time.

Additionally, following the professor’s recommendations, we will **separate the attacker from the target program**, treating the latter as a black box abstraction. This allows for modular testing of different vulnerabilities and attack strategies.

## 2. Comparing with Previous Approaches

Previously, our method involved:

- **Random search benchmark**: Generating `(x, y)` inputs randomly and computing attack success probability.
- **Biased sampling**: Increasing the likelihood of selecting promising inputs (`x=42`) to accelerate successful attacks.
- **Static evaluation**: No adaptation to past results, purely probability-driven.

### Shift with RL:

- **Stateful approach**: The attacker learns from previous interactions.
- **Target program as an abstract environment**: Inputs yield outputs without internal knowledge.
- **Graph representation of execution flow**: The program state evolves over time, requiring sequential decision-making.

## 3. Modeling the Problem as a Markov Decision Process (MDP)

To apply RL, we define the problem as an **MDP (Markov Decision Process)** with the following components:

- **S (States):** The set of **possible states** of the program, represented as `(σ, l)`, where:
  - `σ` represents the **internal state** (variable values, memory, registers, execution history, etc.).
  - `l` represents **progress in execution** (current instruction, control flow position).
- **A (Actions):** The attacker’s **possible actions**, such as:
  - Providing new input values `(x, y)`.
  - Modifying a controllable variable.
  - Attempting to bypass a check.
  - Continuing or halting the attack.
- **P (Transition Probability):** The probability of transitioning from state `s` to `s'` after action `a`.
- **R (Reward Function):** Assigns a score to actions based on their impact on exploitation chances.
- **γ (Discount Factor):** Controls the importance of future rewards versus immediate ones.

## 4. Defining the State Representation `(σ, l)`

The attacker's **knowledge of the program state** is crucial.

- `σ` (State Variables) may include:
  - Known variables (`x`, `y`, etc.).
  - Memory/register states.
  - Execution history (previous states, branches taken).
- `l` (Execution Progress) may be represented as:
  - The current instruction.
  - A high-level abstraction (e.g., entry validation, loop execution, reaching a control point).
  - **Graph representation**: Instead of a flat execution trace, `l` could be a path through a control-flow graph.

## 5. Reward Function `R(s, a, s')`

To guide learning, we define a **reward system** that encourages successful exploits:

- `+1` for actions that bring the attacker closer to vulnerability.
- `-1` for irrelevant or failed actions.
- `+10` if the exploit succeeds.

The professor mentioned that **determining how close an attacker is to success is as hard as solving the problem itself**, meaning reward shaping must be carefully designed.

## 6. Handling Randomized Values (`y = y_r + y_c`)

A key challenge is dealing with randomness in the target program. The professor highlighted:

- **`y_r` (Fixed Random Part):** Remains the same within a single execution but changes across runs.
- **`y_c` (Dynamic Random Part):** Changes on every execution.

This distinction impacts RL strategy:

- The agent must **learn stable patterns** in `y_r`.
- The agent must **generalize across variations** in `y_c`.

## 7. Managing Loops and Execution Flow

The professor raised a critical question:

- Should we **account for loops** in the program execution?
- Or should we **abstract them out** to simplify the attack model?

Including loops would make state tracking more complex but may be necessary if they influence exploitability.

## 8. Choosing the RL Model

### 8.1. **Q-Learning (Q-Table Approach)**

- Simple but inefficient for large state spaces.
- Requires discretization of states and actions.

### 8.2. **Deep Q-Network (DQN)**

- Uses a **neural network** to approximate Q-values.
- Efficient for complex state-action spaces.

### 8.3. **Monte Carlo Tree Search (MCTS)**

- Better suited for **sequential attack strategies**.
- Simulates multiple attack paths to find optimal choices.

## 9. Next Steps

Now, we need to:

1. **Define a minimal RL environment** where the target program is separate from the attacker.
2. **Implement a simple RL agent (Q-Learning, DQN, or MCTS) to interact with it**.
3. **Analyze initial results and refine the attack strategy accordingly**.
