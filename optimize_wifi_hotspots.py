import math
from docplex.mp.model import Model
from scipy.spatial import distance_matrix
import numpy as np
import cplex
import matplotlib.pyplot as plt

def read_coords_file(coords_file_path):
    with open(coords_file_path, 'r') as file:
        lines = file.readlines()
        metadata = lines[0].split()
        nb_clients = int(metadata[0])

        coordinates = []
        for coord in lines[1:]:
            x, y = map(int, coord.strip().split())
            coordinates.append((x, y))

        return nb_clients, coordinates

def read_demands_file(demands_file_path):
    with open(demands_file_path, 'r') as file:
        lines = file.readlines()
        demands = [int(line.strip().split()[0]) for line in lines]
        return demands

def log_input_data(nb_clients, clients, demands, output_log_file):
    with open(output_log_file, 'w') as log_file:
        log_file.write(f"Number of clients: {nb_clients}\n")
        log_file.write(f"Clients coordinates: {clients}\n")
        log_file.write(f"Demands: {demands}\n")

def log_solution_details(solution, x, y, clients, demands, nb_clients, output_log_file):
    selected_points = []
    with open(output_log_file, 'a') as log_file:
        log_file.write(f"Solution status: {solution.solve_status}\n")
        log_file.write(f"Objective value: {solution.objective_value}\n")
        covered_clients = 0
        for j in range(nb_clients):
            if solution.get_value(y[j]) > 0.5:
                covered_clients += 1
        nb_facilities = 0
        for j in range(nb_clients):
            if solution.get_value(x[j]) > 0.5:
                nb_facilities += 1
        log_file.write(f"Total facilities placed: {nb_facilities}\n")
        log_file.write(f"Total clients covered: {covered_clients}/{nb_clients}\n")
        log_file.write(f"Total demand covered: {solution.objective_value}/{sum(demands)}\n")
        log_file.write(f"Solution status: {solution.solve_status}\n")
        log_file.write("=====================================\n")
        for j in range(nb_clients):
            if solution.get_value(x[j]) > 0.5:
                selected_points.append((j + 1, clients[j], demands[j]))  

    return selected_points

def write_selected_nodes(output_file_path, selected_points):
    with open(output_file_path, 'w') as output_file:
        output_file.write("NAME : .\n")
        output_file.write("COMMENT: .\n")
        output_file.write("TYPE : CVRP\n")
        output_file.write(f"DIMENSION : {len(selected_points)}\n")
        output_file.write("EDGE_WEIGHT_TYPE : EUC_2D\n")
        output_file.write("CAPACITY : uncapacitated\n")
        output_file.write("NODE_COORD_SECTION\n")
        for idx, coord, demand in selected_points:
            output_file.write(f"{idx} {coord[0]} {coord[1]}\n")
        output_file.write("DEMAND_SECTION\n")
        for idx, coord, demand in selected_points:
            output_file.write(f"{idx} {demand}\n")
        output_file.write("DEPOT_SECTION\nEOF\n")

def compute_N(clients, S):
    coords_array = np.array(clients)
    dist_matrix = distance_matrix(coords_array, coords_array)
    nb_clients = len(clients)
    N = []
    for i in range(nb_clients):
        N.append([j for j in range(nb_clients) if dist_matrix[i][j] <= S])

    print(len(N))
    return N


def visualize_coverage(clients, demands, solution, x, y, N):

    facilities = [i for i in range(len(x)) if solution.get_value(x[i]) > 0.5]
    covered_clients = [i for i in range(len(y)) if solution.get_value(y[i]) > 0.5]

    plt.figure(figsize=(12, 10))
    ax = plt.gca()

    for i, (x_coord, y_coord) in enumerate(clients):
        if i in covered_clients:
            plt.scatter(x_coord, y_coord, color='blue', s=50, label='Covered Clients' if i == covered_clients[0] else "", alpha=0.7)
        else:
            plt.scatter(x_coord, y_coord, color='gray', s=50, label='Uncovered Clients' if i == 0 else "", alpha=0.5)
        plt.text(x_coord + 0.5, y_coord + 0.5, f"{demands[i]}", fontsize=8, color='black')


    for f in facilities:
        plt.scatter(clients[f][0], clients[f][1], color='red', s=120, marker='^', label='Selected Facilities' if f == facilities[0] else "")
    
    plt.title('Facility Coverage Visualization', fontsize=14)
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Y Coordinate', fontsize=12)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(alpha=0.3)
    ax.set_aspect('equal', adjustable='datalim')
    plt.show()





def mclp_cplex(coords_file_path, demands_file_path, p, S, output_file_path, output_log_file):
    nb_clients, clients = read_coords_file(coords_file_path)
    demands = read_demands_file(demands_file_path)

    log_input_data(nb_clients, clients, demands, output_log_file)

    N = compute_N(clients, S)

    model = Model(name="mclp-docplex")

    y = [model.binary_var(name=f"y_{i}") for i in range(nb_clients)]
    x = [model.binary_var(name=f"x_{j}") for j in range(nb_clients)]

    objective = model.sum(demands[i] * y[i] for i in range(nb_clients))
    model.maximize(objective)

    model.add_constraint(model.sum(x[j] for j in range(nb_clients)) == p)

    for i in range(nb_clients):
        model.add_constraint(model.sum(x[j] for j in N[i]) >= y[i])
        model.add_constraint(y[i] <= model.sum(x[j] for j in N[i]))


    model.parameters.simplex.tolerances.feasibility.set(1e-9) #1e-9 est le threshold
    model.parameters.mip.tolerances.absmipgap.set(0)
    model.parameters.mip.tolerances.mipgap.set(0)
    model.parameters.mip.tolerances.integrality = 1e-9
    model.context.solver.log_output = True
    model.parameters.mip.tolerances.uppercutoff.set(cplex.infinity)
    model.parameters.mip.tolerances.lowercutoff.set(-cplex.infinity)

    print("CPLEX Parameters Set:")
    print("Feasibility Tolerance:", model.parameters.simplex.tolerances.feasibility)
    print("MIP Gap Tolerance:", model.parameters.mip.tolerances.mipgap)
    print("Integrality Tolerance:", model.parameters.mip.tolerances.integrality)

    solution = model.solve(log_output=True)
    if solution:
        selected_points = log_solution_details(solution, x, y, clients, demands, nb_clients, output_log_file)
        relative_gap = solution.solve_details.mip_relative_gap
        print(f"Relative gap: {relative_gap:.16f}")
        write_selected_nodes(output_file_path, selected_points)
        visualize_coverage(clients, demands, solution, x, y, N)
    else:
        print("No solution was found.")
    
    with open(output_log_file, 'a') as log_file:
        log_file.write("Finished running the MCLP model.\n")


SJC818_hashTable = {150: [80, 90, 100, 120, 140, 160, 200, 273], 200: [80, 90, 100, 120, 140, 150, 160, 170, 180, 190, 200, 273]}  
SJC500_hashTable = {150: [40, 50, 60, 70, 80, 100, 130, 167], 200: [40, 50, 60, 70, 80, 100, 130, 167]} 
SJC324_hashTable = {150: [20, 30, 40, 50, 60, 80, 108], 200: [20, 30, 40, 50, 60, 80, 108]}  

instance = "SJC818_hashTable"
instance_data = SJC818_hashTable
print("aaaa", 'input/{instance[:6]}.dat')


for S in instance_data:
    for p in instance_data[S]:
        print("S =", S)
        print("p =", p)
        mclp_cplex(f'input/{instance[:6]}.dat', f'input/demand-{instance[:6]}.dat', p, S, f'output/mclp-selected-points/mclp-{instance[:6]}-p{p}-S{S}', f'output/mclp-log-files/mclp-{instance[:6]}-p{p}-S{S}')

