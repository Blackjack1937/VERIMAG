# Detailed formalisation of the “one-integer RL attacker” problem v3


---

## 1  Entities

| Symbol | Meaning                                         | Concretisation (MVP)                                               |
| ------ | ----------------------------------------------- | ------------------------------------------------------------------ |
| **P**  | target **p**rogram (vulnerable C binary)        | executed via `subprocess`, **stdin → stdout/exit-code**            |
| **A**  | **a**gent / attacker                            | Python RL loop                                                     |
| **x**  | 32-bit signed **input integer** chosen by *A*   | action space $A=\{0,\dots,2^{32}-1\}$ → start with **n ≤ 16 bits** |
| **y**  | **o**bservable program output after feeding *x* | raw bytes ∥ exit-status                                            |
| **r**  | scalar **r**eward derived from *y*              | shaping policy in § 7                                              |

---

## 2  Interaction semantics (single step)

1. *A* picks $x_k \in A$.
2. $$
   y_k \leftarrow \mathrm{run}(P,x_k)
   $$

   *(one execution, black-box).*
3. Environment returns $(y_k,r_k)$ with

   $$
   r_k =
   \begin{cases}
   +R_{\text{succ}}   & \text{if exploit fired}\\[4pt]
   +R_{\text{partial}} & \text{if symptom detected}\\[4pt]
   0                  & \text{otherwise}
   \end{cases}
   $$
4. Transcript after *k* steps

   $$
   \tau_k = (y_1,x_1,\dots,y_k,x_k)
   $$

---

## 3  Markov Decision Process definition

We model the loop as a finite-horizon MDP

$$
\mathcal{M} = (S, A, P, R, \gamma, H)
$$

| Component    | MVP choice                                   | Rationale                               |
| ------------ | -------------------------------------------- | --------------------------------------- |
| **S**        | last I/O pair $s_k = (y_k,x_k)$              | satisfies “state = input/output” remark |
| **A**        | integer $x$ (possibly truncated to *n* bits) | “one value, no $(X,Y)$ couple”          |
| **P**        | induced by executing *P* with $x$            | unknown to agent, may be stochastic     |
| **R**        | see § 2                                      | observations kept separate from rewards |
| **$\gamma$** | 0.9 (tunable)                                | —                                       |
| **H**        | episode length cap (e.g. 100)                | —                                       |

**State-abstraction ladder**

* $s = (y_{\text{last}},x_{\text{last}})$ — simplest
* $s = \text{window}_k(\tau)$ — fixed sliding window
* $s = \text{hash}(\tau)$ — learned embedding

---

## 4  Objective

Let $\pi$ be a (stochastic) policy $\pi : S \to \Delta(A)$.
The agent seeks

$$
\max_{\pi}\;
\mathbb{E}\!\Bigl[\,
\sum_{k=1}^{H} \gamma^{\,k-1}\, R(s_k,a_k)
\Bigr]
$$

This approximates the probability of triggering the vulnerability (for binary rewards) or a shaped surrogate, superseding the earlier $(x,y)$-based formulation in **`RL_FORM.md`** and matching the optimisation view in **`PROB_FORM_V2.md`**.

---

## 5  Two orthogonal axes

| **Axis #1 – code visibility**                          | **Axis #2 – value-function representation** |
| ------------------------------------------------------ | ------------------------------------------- |
| **Black-box** (no code)                                | Q-table (*n* small)                         |
| **Grey-box** (trace bits, coverage bonus)              | Linear head on one-hot($x$)                 |
| **White-box** (static CFG, weakest-precondition hints) | 1-D CNN / DQN on 32-bit vector              |

*Horizontal axis* = **black → grey → white**
*Vertical axis* ≈ “power of guidance / approximation depth”.

---

## 6  Learning-algorithm roadmap

1. **Phase 0 — prototype**

   * *n* ≤ 8–16, **tabular Q-learning** (cf. `RL_Attack_env.py`)
2. **Phase 1**

   * switch to **DQN** once $|A|$ explodes
   * input = `bits(x) ‖ embed(y_prev)`
3. **Phase 2**

   * add **grey-box bonus**

     $$
       R' = R + \lambda\,\text{coverage\_increase}
     $$

---

## 7  Reward-shaping contract

| Program event       | Example detector   | Suggested reward |
| ------------------- | ------------------ | ---------------- |
| Crash / `SIGSEGV`   | non-zero exit code | **+10**          |
| Specific log string | regex on stdout    | **+5**           |
| Else                | —                  | 0                |

Shaping must be **cheaper** than computing a symbolic exploit distance.

---

## 8  Formal-guarantee target (long-term)

* **Tabular case:** under ergodicity and decaying $\varepsilon$, Q-learning converges to $Q^\*$.
* **Function-approximation case:** rely on empirical stability of DQN; proofs are out of scope.

---

## 9  Open parameters to freeze with the teacher
* Bit-width **n** for milestone #1
* Exact crash / symptom-detection rule
* Episode horizon **H**
* History-window size (> 1 ?)

---

## 10  Summary

We distilled the handwritten sketch and previous drafts into a **clean MDP with a single 32-bit action**, decoupled observations from rewards, and mapped future work onto a 2-axis grid (code visibility × approximation power).
This specification is ready for interface coding and experimental planning.
