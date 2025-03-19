# VERIMAG PROJECT - Formalization

## Definition

Our general objective is to assess the exploitability of a program's vulnerabilities using ML (Machine learning), as an alternative to the already implemented BaxMC, that is based on Max#SAT approaches.

Unlike standard ML, where we typically try to approximate an unknown function y = f^(x), based on an input data pair (x,y), where y represents the outcome we want to predict. In our setting, we only have access to the program (code), and there is no explicit attacker model providing examples of successful exploits, which means, in a more general view, that there is no function f mapping program properties to exploitability, the ML-target function that we would try to approximate.

Since we do not have that target function, our problem is more of an optimization problem than a classical supervised learning one. The goal is to find an attacker strategy (input/sequence of actions) that maximizes the likelihood of a vulnerability.

## Formalization

### Binary classification

Let :

- P be the program whose outputs are Out = (y_0, ... ,y_n), and environment inputs are

  (x_1, ... , x_n) such that for each k,

1. y_k depends on y_0, x_1, ... y\_{k-1}, x\_{k-1} and
2. x_k depends on y_0, x_1, ... x\_{k-1}, y\_{k-1}

- An adaptive adversary for program P is a tuple A = (x_1, ... , x_n) with x_i defined as above
- I be the space of all other inputs to P (that are sampled according to some fixed distributions)
- Let
  - f the exploitabilty function f : {y_n} → {0,1} (0 for fail, 1 for success)
  - P(A) [f(y_n)=1] the probability over random inputs i, associated to adversary A, that f exploits the program successfully .

We basically want to maximize P(A) [f(y_n)=1], i.e find (or approximate)

                               **argmax_A   P(A)[f(y_n)=1]),**

which represents the most effective attack strategy for that program.

### Decision tree representation

Instead àof a simple binary representation (1 or 0 for the exploit success), the attacker follows a structured sequence of choices that influence whether we reach the CP (Control Point) in the program or not. We can represent the sequential decision process as a tree.

The tree can be presented as such :

- Each node represents a decision point
- Each branch represents a possible choice (attacker)
- Leaf nodes can correspond to :
  - A successful attack (exploit triggered)
  - A failure (no exploitation)

In this representation, the goal is to find a path that maximizes the likelihood of reaching a CP (Control Point).

An adversary A = (x_1, ... , x_n) could be represented as a set of n decision trees (T_1, ... , T_n), where for the tree T_k:

- The set of features F is a subset of the set of arithmetical expressions over the set {y_0,...,y\_{k-1}}
- Each node represents a decision point, labelled by predicates φ of the form f § c, where f ∈ F is a feature, § ∈ {<, ≤, =, >, ≥} is a comparison, and c is a numeric constant
- Each branch represents a possible choice
- Leaf nodes can all correspond to either linear models M_l(f ) = ∑_i α_i · f_i or multiplication models M_m(f ) = ∏_i f_i ^ {α_i}, where f_i are features over the set {y_0,...,y\_{k-1}} and α_i are numeric constants

```

                        [φ1]
                       /        \
                 [φ2_1]    [φ2_2]
                 /      \     /      \
                   .........
       [φK_l]
      /       \   .................  /      \
 [M_1]      [M_2]      ........
```

Let's give an example :

Let the program P be :

```
if (x == 42) {
    if (y > 1000) {
        crash();  // Vulnerability trigger
    }
}
```

The attack tree would look like this :

```
     Start
       |
    [Choose x]
      /     \
  x=42    x≠42 (fail)
    |
[Choose y]
    / \
y>1000 y≤1000 (fail)
    |
[Exploit]
```

The CP here is when the program reaches the condition `if (y > 1000)`.

N-B : A Control Point represents a critical branch in the execution that dictates whether the attack is successful. If the CP depends on a random variable, the attacker may habe to guess it, meaning we should consider randomness in our work.

## What might be missing :

### Attacker knowledge

- What info is available to the attacker at each decision point ?
- Is the attacker fully aware of the program's internal state, or do they have limited visibility (or both) ?

  _That leaves room for modelling a partially observable environement, where some execution details are hidden._

### Exploitability score

- Based on our previous declarations, exploitability is binary (0 or 1), we can introduce a degree of exploitability.
- A vulnerability might be harder to exploit than another - a scoring system
- Possible metric : likelihood of success per attack attempt.

### Search strategies

#### Possible ML approaches :

- Monte Carlo Tree Search (MCTS): Apparently suitable for sequential decisions (Attacker), simulates multiple attak attempts, gradually refining paths leading to success.
- Reinforcement Learning (RL) : Attacker is an RL agent, can train an attacker to maximize exploitability based on feedback.
- Bayesian Optimization : For expensive attack evaluation (maybe ? To check)
- Genetic Algorithms : We sample attack strategies over generations to find the best/most successful one.

**We should decide if we focus on binary classification, or a tree-based attack navugation (or both), plus choosing an initial search model adapted to each one.**
