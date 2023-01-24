# README.md

# Strategic of an Urban Distribution Network

@author:s P. Hurtado-Cayo, J. Pina-Pardo

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
\text{minimize} \quad  & \sum_{s \in S} \sum_{q \in Q_s} f_{sq} \cdot y_{sq} + \sum_{t \in T} \sum_{s \in S} \sum_{k \in K}  c_{sk}^{t} \cdot x_{sk}^{t} + \sum_{t \in T} \sum_{k \in K} g_{k}^{t} \cdot w_{k}^{t} 
\end{align*}
$$

subject to 

$$
\begin{align}
\sum_{q \in Q_s} y_{sq} \ &\leq \ 1,  & \forall s \in S,\\
\sum_{k \in K} v_{sk}^{t} \cdot x_{sk}^{t} \ & \leq \ \sum_{q \in Q_s} \vartheta_{sq} \cdot y_{sq}, & \forall t \in T, s \in S,\\
w_{k}^{t} + \sum_{s \in S} x_{sk}^{t} \ & = \ 1, & \forall  t \in T, k \in K,\\ 
y_{sq} \ & \in \  \{0,1\} , & \forall s \in S, q \in Q_s,\\
x_{sk}^{t} \ & \in \  \{0,1\} , & \forall t \in T,  s \in S, k \in K,\\
w_{k}^{t} \ & \in \ \{0,1\}, & \forall  t \in T, k \in K,
\end{align}
$$

where $c_{sk}^{t}$ and $g_{k}^{t}$ are calculated by:

$$
c_{sk}^{t} \quad = d_{k}^{t} \cdot f^{\text{fee}}_{s} + d_{k}^{t} \cdot t^{\text{fee}}_{sk} + v_{sk}^{t} \cdot f_{s}
$$

$$
g_{k}^{t} \quad = d_{k}^{t} \cdot t^{\text{fee}}_{k} + v_{k}^{t} \cdot f
$$
