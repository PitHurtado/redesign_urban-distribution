# README.md

# Strategic of an Urban Distribution Network

@authors: P. Hurtado-Cayo, J. Pina-Pardo

## Install dependences:
Run:
```
conda create <name_conda_enviroment> --file requirements.txt
```
Pre-requisite:

- gurobi installed
- license gurobi

**The MILP formulation is presented below:**

$$
\begin{align*}
\text{minimize} \quad  & \sum_{s \in S} \sum_{q \in Q_s} f_{sq}^{\text{fixed}} \cdot y_{sq} + \sum_{t \in T} \sum_{s \in S} \sum_{q \in Q_{s}} z_{sq}^{t} \cdot f_{sq}^{t} + \sum_{t \in T} \sum_{s \in S} \sum_{l \in L} \sum_{k \in K^{l}}  c_{sk}^{t} \cdot x_{sk}^{t} + \sum_{t \in T} \sum_{l\in L} \sum_{k \in K^{l}} g_{k}^{t} \cdot w_{k}^{t} 
\end{align*}
$$

subject to 

$$
\begin{align}
\sum_{q \in Q_s} y_{sq} \ &\leq \ 1,  & \forall s \in S,\\
z_{sq}^{t} \ & \leq \ y_{sq}, & \forall t \in T, s \in S, q \in Q_{s},\\
x_{sk}^{t} \ & \leq \ \sum_{q \in Q_{s}} z_{sq}^{t}, & \forall t \in T, s \in S, k \in K^{l}, l \in L,\\
\sum_{l \in L}\sum_{k \in K^{l}} v_{sk}^{t} \cdot x_{sk}^{t} \ & \leq \ \sum_{q \in Q_s} \vartheta_{sq} \cdot y_{sq}, & \forall t \in T, s \in S, l \in L, \\
w_{k}^{t} + \sum_{s \in S} x_{sk}^{t} \ & = \ 1, & \forall  t \in T, k \in K^{l}, l\in L,\\ 
y_{sq} \ & \in \  \{0,1\} , & \forall s \in S, q \in Q_s, \\
x_{sk}^{t} \ & \in \  \{0,1\} , & \forall t \in T,  s \in S, k \in K^{l}, l \in L,\\
w_{k}^{t} \ & \in \ \{0,1\}, & \forall  t \in T, k \in K^{l}, l \in L,
\end{align}
$$

where $c_{sk}^{t}$ and $g_{k}^{t}$ are calculated by:

$$
c_{sk}^{t} \quad = 
$$

$$
g_{k}^{t} \quad = 
$$
