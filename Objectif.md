### Mission sentence

> **Our goal is to *quantify* a program’s attack surface *and*, whenever possible, *demonstrate* a concrete exploit, by searching for the best-performing attacker policy with reinforcement-learning/optimisation techniques.**
> This learning-driven approach is meant as a practical alternative to the existing BaxMC Max#SAT method.

---

### Clarifying paragraph

We do **not** have labelled examples of successful exploits, so the task is **not supervised ML**.
Instead, we treat the program as an *environment* and cast the search for the **best agent** as an **optimisation problem** framed by two orthogonal axes:

* **Axis 1 – adversary class / code knowledge**
  *Black-box → Grey-box → White-box*
* **Axis 2 – approximation power of the value function**
  *Tabular → Linear → Deep (CNN/DQN)*

For any point on this grid we seek the policy π that maximises the expected return

$$
J(\pi)\;=\;\mathbb{E}_{\pi}\!\Bigl[\;\sum_{t=0}^{H-1}\gamma^{\,t}\,R(s_t,a_t)\Bigr],
$$

where the reward is shaped to give strong positive feedback for crashes or, better, full control of the vulnerable state.
By maximising $J(\pi)$ we **measure exploitability** (through the maximal value obtained) **and** obtain an explicit input—the action chosen by the best policy—that *proves* the exploitability.
