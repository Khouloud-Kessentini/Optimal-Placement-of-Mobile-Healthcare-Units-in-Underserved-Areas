# Optimal Placement of Mobile Healthcare Units in Underserved Areas

In many rural and underserved areas, healthcare access remains a significant challenge due to geographic isolation and limited infrastructure. The aim of this model is to optimize the placement of clinics or mobile health units to maximize patient coverage and minimize the distance between healthcare facilities and the populations they serve. In this project, we formulate this optimization problem as a Maximal Covering LOcation Problem.

In the Maximal Covering Location Problem, the objective is to cover the maximum population within a desired service distance $\mathcal{S}$ by optimally locating a fixed number of facilities.

More formally, let $p\in\mathbb{N}$ denote the number of facilities to be placed. Let $I$ denote the finite set of demand nodes $$I = \{ 1, 2, \ldots, {|I|} \}$$ each defined in a 2-dimensional space. Each demand point $i \in I$ is associated to a demand $a_i \in \mathbb{R}$. Let $J$ denote the set of potential facility locations $$J = \{ 1, 2, \ldots, {|J|} \}$$ with $$j = (x_j, y_j) \in \mathbb{R}^{2} \forall j \in J$$. Let $$\mathcal{S}$$ denote the distance beyond which a demand point is considered ``uncovered" and  $$d_{ij}$$ denote the distance from node $${i} \in I$$ to node $$j \in J$$. The objective is to select $$p$$ facility locations from $$F$$ such that the number of covered demand nodes is maximized with respect to the maximal distance $$\mathcal{S}$$. Let $$y_i \in \{0, 1\}$$ be a binary variable denoting that takes value 1 if demand node $$i \in I$$ is covered, and 0 otherwise. Let $$x_{j} \in \{0, 1\}$$ be a binary variable that takes value 1 if if facility $$i$$ is allocated to node $$j$$ and 0 otherwise.

$$
Maximize \sum_{i \in I} a_i y_i
$$

subject to  

$$\sum_{j \in N_i} x_j \geq y_i \quad \forall i \in I$$

limited number of access points 

$$\sum_{j \in J} x_{j} = p$$

binary restrictions

$$x_j \in \{0, 1\} \quad \forall j \in J$$
$$y_i \in \{0, 1\} \quad \forall i \in I$$
