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
\text{minimize} \quad  & \sum_{s \in S} \sum_{q \in Q_s} f_{sq} \cdot y_{sq} + \sum_{k \in K} \sum_{s \in S} \sum_{t \in T} c_{sk}^{t} \cdot x_{sk}^{t} + \sum_{k \in K} \sum_{t \in T} g_{k}^{t} \cdot w_{k}^{t} \\
& + \sum_{k \in K} \sum_{s \in S} \sum_{t \in T} f^{\text{small}}_{s} \cdot v_{skt}^{\text{small}} \cdot x_{sk}^{t} + 
\sum_{k \in K} \sum_{t \in T} f^{\text{large}} \cdot v_{kt}^{\text{large}} \cdot w_{k}^{t},
\end{align*}
$$

subject to 

$$
\begin{align}
\sum_{q \in Q_s} y_{sq} \ &\leq \ 1,  & \forall s \in S,\\
\sum_{k \in K} v_{skt}^{\text{small}} \cdot x_{sk}^{t} \ & \leq \ \sum_{q \in Q_s} \vartheta_{sq} \cdot y_{sq}, & \forall s \in S, t \in T,\\
w_{k}^{t} + \sum_{s \in S} x_{sk}^{t} \ & = \ 1, & \forall k \in K, t \in T,\\ 
y_{sq} \ & \in \  \{0,1\} , & \forall s \in S, q \in Q_s,\\
x_{ks}^{t} \ & \in \  \{0,1\} , & \forall k \in K, s \in S, t \in T,\\
w_{k}^{t} \ & \in \ \{0,1\}, & \forall k \in K, t \in T,
\end{align}
$$
