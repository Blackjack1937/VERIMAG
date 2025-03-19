# Small-scale prototyping

Before jumping into ML models, we will test our attack strategies on a small but well-defined example.

We described an attack tree in the problem formalization for the following :

```
if (x == 42) {
    if (y > 1000) {
        crash();  // Vulnerability trigger
    }
}

```

Let's implement a basic test case where the program accepts (x,y) as inputs. The exploit succeeds if x = 42 abd y > 1000, otherwise it fails. We'll simulate the attack trying different values of x and y, either randomly or using a search model.

My initial idea is to write a pseudo-code, which I will try to adapt into a python script, where inputs are random, and we'll record success and failure each time, to compute the probability of success. (Benchmark to compare against ML search models ?)

## Pseudo-code of a basic attack simulation

```
Initialize:
  success_count = 0
  total_attempts = 0
  num_iterations = N

Loop num_iterations times:
  Generate random x in range [X_min, X_max]
  Generate random y in range [Y_min, Y_max]

  If x == 42 and y > 1000:
    success_count += 1  # Attack successful

  total_attempts += 1  # Track number of total attempts

Compute probability of success:
  success_probability = success_count / total_attempts

Print results:
  - Total attempts made
  - Number of successful attacks
  - Probability of success

```

**_For python script, check prototype_random.py_**

## Analysis of the probability evolution plot

### Initial testing

The plot shows multiple attempts of attack, with the success probability over `10 000` iterations.

Initially, probability fluctuates significantly due to the small sample size, which is expected since we do not have enough data to converge.

As more iterations are performed, the probability smoothly converges to a stable value `(0.0042 to 0..50)`, which indicates that random search constistently finds the attack at the expected rate. The expected theoretical probability `(0.00495`) matches well with the simulated one, affirming the correctness of the random model.

### Testing biased sampling for x = 42

An issue with the random model is that x is selected uniformly across [0,X_MAX], and for `X_MAX =50`, this means :

- The probability of getting `x=42` is only `1/51`
- ... of getting y > 1000 is 1/2
- The expected probability of success is therefore less than `1%`

This leads to too few successful attacks, which makes visualization difficult.

### Biased sampling approach

Instead of picking a random x, we can increase the likelihood of a successful guess. We can do it by **biasing the sampling**.
`x = 42 if np.random.rand() < 0.2 else np.random.randint(X_MIN, X_MAX + 1)`. We can assure that `20%` of the time, `x=42` is selected, and that would result in 10x more successful attacks, making anlysis more reliable.

## Discussion on random model as a baseline

The random model provides a **benchmark** against which we can compare more advanced search models, like the ones already mentionned in the problem formalization. The convergence of random search validates that the exploit condition is correctly defined and we can measure attack success probability.

Nevertheless, random search is inefficient, as it does **not adapt to past results**, and this is where other models will perform better.

### Comparison of random search and structured search

| **Aspect**      | **Random search**                                 | **Structured search**                    |
| --------------- | ------------------------------------------------- | ---------------------------------------- |
| **Exploration** | Blind, uniform sampling                           | Focuses search on promising inputs       |
| **Efficiency**  | Needs a lot of iterations to find rare conditions | Less iterations needed                   |
| **Adaptation**  | Does not learn from previous tries                | Adjusts attack strategy dynamically      |
| **Usefulness**  | Good for probability estimation                   | Necessary for real-world attack modeling |

### Transition to ML-based models

We can evaluate how much better ML-based strategies perform by answering the following :

- Does the model find an exploit faster than random ?
- How many attempts does each model needs to reach the same success probability.

_ML models can generalize the biasing strategy by learning optimal attack paths_

## Conclusion & Next Steps

The random model has provided a strong baseline for evaluating exploitability, showing that while random guessing can eventually succeed, it is **highly inefficient**. Our tests with **biased sampling** have demonstrated that even simple optimizations can significantly improve the attack success rate. However, these adjustments remain **static**, whereas real-world attacks require **adaptive decision-making**.

From our **problem formalization**, we identified two structured search approaches:

1. **Binary classification**: Finding an attacker strategy that maximizes the probability of success.
2. **Tree-based attack navigation**: Sequentially choosing inputs to reach a Control Point (CP).

We will now move beyond random search and test **structured attack strategies**:

- **Monte Carlo Tree Search (MCTS)**: Suitable for **tree-based navigation**, allowing an attacker to explore sequential choices dynamically.
- **Reinforcement Learning (RL)**: Can model both **binary** and **tree-based** strategies by adapting to past attempts.
- **Genetic Algorithms (GA)**: More suited for **binary classification**, evolving attack strategies over multiple iterations.

The next step is to **choose which structured search model to implement first**: **If we start with binary classification**, we will compare **GA and Random Search** to measure efficiency. **If we start with tree-based navigation**, we will first implement **MCTS** and analyze how it improves over naive search.
Our goal is to progressively refine our approach, moving toward a model that best balances **efficiency, adaptability, and real-world exploitability.**

_We should create a tri-ratio score to calculate the balance between those three parameters, and formalize comparison between models._
