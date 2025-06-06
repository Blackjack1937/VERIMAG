# Final Precise Formalisation


## 0 — Scope & Rationale

We want **a learning-driven alternative to BaxMC/Max#SAT** able to

* **measure** the exploitability of a C program (attack-surface score), **and**
* **demonstrate** it by producing at least one concrete input that triggers the vulnerability.

Because we have **no labelled examples of exploits**, the task is framed as a **sequential optimisation / reinforcement-learning problem**, not as supervised ML.

---

## 1 — Symbols & Entities

| Symbol | Meaning                 | MVP concretisation                                                              |
| ------ | ----------------------- | ------------------------------------------------------------------------------- |
| **P**  | Target program (binary) | executed via `subprocess`, stdin → stdout + exit-code                           |
| **A**  | Attacker agent          | RL policy implemented in Python                                                 |
| **x**  | Integer input           | one signed word, default 32 bits (option: reduce to *n* ≤ 16 for tabular proto) |
| **y**  | Observable output       | concatenation of stdout bytes & exit-status                                     |
| **r**  | Scalar reward           | shaped from *y* (see § 3.4)                                                     |

---

## 2 — One-step semantics

1. Agent chooses $x_k \in \{0,\dots,2^{n}-1\}$.
2. Run $y_k \leftarrow \text{exec}(P,x_k)$.
3. Environment returns $(y_k,r_k)$.
4. Transcript after *k* steps:

   $$
     \tau_k = (y_1,x_1,\dots,y_k,x_k).
   $$

---

## 3 — MDP Definition

$$
\mathcal{M}=(S,A,P,R,\gamma,H)
$$

### 3.1  State space $S$

* **Minimal** $s_k = (y_k,x_k)$ (*state = input/output*).
* **State-abstraction ladder** (optional upgrades)

  1. sliding window of $k$ pairs;
  2. learned embedding $h(\tau_k)$.

### 3.2  Action space $A$

$A = \{0,\dots,2^{n}-1\}$ — one integer.S

### 3.3  Transition kernel $P$

Induced by running *P*; can be stochastic (randomised program, ASLR…).

### 3.4  Reward function $R$

Shaped automatic proxy:

| Event in *P*                           | Reward                     |
| -------------------------------------- | -------------------------- |
| Exploit (control EIP / shell)          | $+20$ *(optional, future)* |
| Crash (`SIGSEGV`, abort)               | $+10$                      |
| Partial symptom (assert, specific log) | $+5$                       |
| Otherwise                              | $0$                        |

*Why a crash?* — dense signal, easy to detect; still aligns with the end-goal because any exploit implies (at least) crashing behaviour.

### 3.5  Discount and horizon

* $\gamma = 0.9$ (tunable)
* $H = 100$ steps by default (episode cap)

---

## 4 — Optimisation Objective

$$
\boxed{\;
J(\pi)=\mathbb{E}_{\pi}\Bigl[\,
\sum_{t=0}^{H-1}\gamma^{\,t}\,R(s_t,a_t)
\Bigr]}
$$

*Maximise* $J(\pi)$ → highest crash/exploit probability.
The **value of $J\_{\max}$** gives a *quantitative measure* of exploitability; the action chosen by the optimal policy constitutes the *exploit example*.

---

## 5 — Function approximation & Bellman

### 5.1  True action-value

$$
Q^{*}(s,a)\;=\;
\mathbb{E}\Bigl[
R(s,a)+\gamma\max_{a'}Q^{*}(s',a')
\Bigr]
$$

### 5.2  Approximator

$$
Q_{w}(s,a)\;=\;f_{w}\bigl(X(s),a\bigr)
$$

* $X(s)$ : feature vector (bits of $x$ ‖ embedding of $y$)
* $w$ : weights (table entries, linear coefficients, CNN filters…)

**Temporal-difference loss**

$$
\mathcal{L}(w)\;=\;
\bigl(
R+\gamma\max_{a'}Q_{w}(s',a')-Q_{w}(s,a)
\bigr)^{2}
$$

**Best parameters**

$$
w^{*}\;=\;\arg\min_{w}\;
\mathbb{E}\bigl[\mathcal{L}(w)\bigr]
$$

With $Q_{w^{*}}\!\approx Q^{*}$, greedily selecting
$\displaystyle a=\arg\max_{a}Q_{w^{*}}(s,a)$
provides the best attacker within the chosen approximation family.


## 6 — Two orthogonal design axes

**Axis 1 : knowledge / adversary class**
*Black-box → Grey-box → White-box* (no code → trace hints → full CFG/WP).

**Axis 2 : approximation power**
*Tabular → Linear → Deep (CNN/DQN).*

Every point on this grid defines a *family of agents*; optimisation picks the best within that family.

---

## 7 — Implementation roadmap

| Phase | n-bits | Approximation       | Code hints            |
| ----- | ------ | ------------------- | --------------------- |
| 0     | 8 – 16 | Q-table             | none                  |
| 1     | 32     | DQN (MLP / 1-D CNN) | none                  |
| 2     | 32     | DQN + bonus         | coverage bitmap       |
| 3     | 32     | CNN + heuristics    | static CFG, WP scores |

---

## 8 — Open questions
1. **Bit-width for Phase 0** : 8, 12, 16 ou direct 32 bits ?
2. **Exact success/partial detectors** : code-retour seul, regex, mix ?
3. **Episode horizon $H$** : 100 appels convient-il ?
4. **State abstraction** : une seule paire, fenêtre $k$ (quel $k$ ?), embedding ?

---

## 9 — Relation to BaxMC

* BaxMC counts satisfying assignments of a vulnerability formula via **Max#SAT**.
* Our RL formulation **optimises** over concrete inputs instead of counting, giving

  1. a **scalar exploitability score** $J_{\max}$
  2. an **input witness**.
* Thus it complements (or replaces) BaxMC with a data-driven, *executability-first* approach.

---

## 10 — Summary in one sentence

> *We search, along the (adversary class × approximation power) grid, for the policy that maximises
> $\displaystyle J(\pi)=\mathbb{E}\bigl[\sum\gamma^{t}R\bigr]$; the maximum value quantifies the program’s exploitability and the corresponding action sequence is the concrete exploit.*