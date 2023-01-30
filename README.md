# README.md

# Strategic redesign of Urban Distribution Network

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
\text{minimize} \quad  & \sum_{s \in S} \sum_{q \in Q_s} f_{sq}^{\text{fixed}} \cdot y_{sq} + \sum_{t \in T} \sum_{s \in S} \sum_{q \in Q_{s}} f_{sqt}^{\text{\tiny oper}} \cdot z_{sq}^{t} + \sum_{t \in T} \sum_{s \in S} \sum_{k \in K}  c_{sk}^{t} \cdot x_{sk}^{t} + \sum_{t \in T} \sum_{k \in K} g_{k}^{t} \cdot w_{k}^{t} 
\end{align*}
$$

subject to 

$$
\begin{align}
\sum_{q \in Q_s} y_{sq} \ &\leq \ 1,  & \forall s \in S,\\
z_{sq}^{t} \ & \leq \ y_{sq}, & \forall t \in T, s \in S, q \in Q_{s},\\
x_{sk}^{t} \ & \leq \ \sum_{q \in Q_{s}} z_{sq}^{t}, & \forall t \in T, s \in S, k \in K,\\
\sum_{k \in K} \nu_{sk}^{t} \cdot x_{sk}^{t} \ & \leq \ \sum_{q \in Q_s} \vartheta_{sq} \cdot y_{sq}, & \forall t \in T, s \in S,\\
w_{k}^{t} + \sum_{s \in S} x_{sk}^{t} \ & = \ 1, & \forall  t \in T, k \in K,\\ 
y_{sq} \ & \in \  \{0,1\} , & \forall s \in S, q \in Q_s,\\
x_{sk}^{t} \ & \in \  \{0,1\} , & \forall t \in T,  s \in S, k \in K,\\
w_{k}^{t} \ & \in \ \{0,1\}, & \forall  t \in T, k \in K,
\end{align}
$$

where $c_{sk}^{t}$ and $g_{k}^{t}$ are calculated by:

$$
\begin{equation}
    c_{sk}^{t} \ = \ c^{\text{first}}_{s} \cdot d_{k}^{t} + c^{\text{shipping}}_{sk} \cdot d_{k}^{t} + c^{\text{fixed}}_{s} \cdot \nu_{sk}^{t} 
\end{equation}
$$

$$
\begin{equation}
g_{k}^{t} \ = \ c^{\text{shipping}}_{k} \cdot d_{k}^{t} + c^{\text{fixed}} \cdot \nu_{k}^{t}  
\end{equation}
$$
