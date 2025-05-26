# VERIMAG PROJECT - Formalization

## Definition

Our general objective is to assess the exploitability of a program's vulnerabilities using ML (Machine learning), as an alternative to the already implemented BaxMC, that is based on Max#SAT approaches.

Unlike standard ML, where we typically try to approximate an unknown function y = f^(x), based on an input data pair (x,y), where y represents the outcome we want to predict. In our setting, we only have access to the program (code), and there is no explicit attacker model providing examples of successful exploits, which means, in a more general view, that there is no function f mapping program properties to exploitability, the ML-target function that we would try to approximate.

Since we do not have that target function, our problem is more of an optimization problem than a classical supervised learning one. The goal is to find an attacker strategy (input/sequence of actions) that maximizes the likelihood of a vulnerability.

## Formalization

### Binary classification

Let :

- P be the program
- I be the space of all possible inputs to P (Or actions if we consider sequences)
- A be the set of attacker-controlled variables
  - f the exploitabilty function f : I → {0,1} (0 for fail, 1 for success)
  - P[f(i)=1] the probability that a random input i exploits the program successfully.

We basically want to maximize P[f(i)=1], i.e find max_i∈A(P[f(i)=1]), which represents the most effective attack strategy for that program.

### Decision tree representation

Instead of a simple binary representation (1 or 0 for the exploit success), the attacker follows a structured sequence of choices that influence whether we reach the CP (Control Point) in the program or not. We can represent the sequential decision process as a tree.

The tree can be presented as such :

- Each node represents a decision point
- Each branch represents a possible choice (attacker)
- Leaf nodes can correspond to :
  - A successful attack (exploit triggered)
  - A failure (no exploitation)

In this representation, the goal is to find a path that maximizes the likelihood of reaching a CP (Control Point).

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

The CP here is when the program reaches the condition `if (y > 1000)`.

N-B : A Control Point represents a critical branch in the execution that dictates whether the attack is successful. If the CP depends on a random variable, the attacker may habe to guess it, meaning we should consider randomness in our work.
