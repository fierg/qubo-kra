import json

import modules.config as config
import modules.data as data
import classes.subkernel as subkernel
import classes.candidatesplit as candidatesplit
from classes import pairs
from classes.graph import *
from pathlib import Path
import logging


initialized = False
candidates_pairs = {}
dirty_candidates = []
clean_candidates = []
instances = []
subkernels = []


# Build the kernels and generate the solution
def generate_solution():
    # Make sure, nothing is initialized
    reset_kernel()

    # Build the kernel
    logging.info("Generating the kernel instances ...")
    build_kernel()

    # Solve the kernel
    logging.info("Solving the kernel ...")
    solution = solve_kernel(config.inputfile)

    # print solution
    logging.info("The solution is:")
    logging.info(solution)

    if config.quality:
        check_cost_for_solution(solution)


def check_cost_for_solution(solution):
    try:
        total_costs = 0

        for a in range(0, len(solution[0])):
            for b in range(a + 1, len(solution[0])):
                sa = solution[0][a]
                sb = solution[0][b]
                total_costs += candidates_pairs[str(sa)][str(sb)].cost

        logging.info("Cost for solution: " + str(total_costs))

        if Path('../data/solutions/generated-costs.json').is_file():
            with open('../data/solutions/generated-costs.json', 'r') as f:
                solutions = json.load(f)
        else:
            if Path('data/solutions/generated-costs.json').is_file():
                with open('data/solutions/generated-costs.json', 'r') as f:
                    solutions = json.load(f)
            else:
                raise KeyError

        file = Path(config.inputfile)
        if file.parts[len(file.parts) - 2] == 'original':
            expected = int(solutions[f'data/original/{file.name}'])
        elif file.parts[len(file.parts) - 3] == "generated":
            expected = int(solutions[f'data/generated/{file.parts[len(file.parts) - 2]}/{file.name}'])
        elif str(file.parts[len(file.parts) - 2]).startswith("missing"):
            expected = int(solutions[f'data/original/{file.name}'])
        else:
            raise KeyError
        logging.info("Cost for Optimal solution: " + str(expected))

        relative_cost = ((total_costs / expected) - 1) * 100
        if total_costs < expected:
            logging.info("############ ????")
        else:
            logging.info("Solution is +" + str(relative_cost) + "% of the optimal cost.")

    except KeyError:
        logging.info("No solution to validate found for: " + str(config.inputfile))


# Reset all kernel variables
def reset_kernel():
    # Define global variables to prevent shadowing
    global initialized
    global candidates_pairs
    global dirty_candidates
    global clean_candidates
    global instances
    global subkernels

    initialized = False
    candidates_pairs = {}
    dirty_candidates = []
    clean_candidates = []
    instances = []
    subkernels = []


# Generate the subinstances
def build_kernel():
    # Define global variables to prevent shadowing
    global initialized
    global instances
    global subkernels

    # Generate statistics
    generate_pairs()
    get_non_dirty_candidates()

    # Switch split mode
    if config.splitmode == "candidates":
        split_instances_with_candidates()

    elif config.splitmode == "condorcet":
        split_instances_with_majority()

    elif config.splitmode == "none":
        instances.append(data.final_candidates)

    # Remove empty instances
    new_instances = []
    for instance in instances:
        if instance != []:
            new_instances.append(instance)
    instances = new_instances

    # logging.info debug output
    logging.debug(["The kernel contains the following instances:", instances])

    # Generate subkernels
    for instance in instances:
        subkernels.append(subkernel.Subkernel(instance, data.rankings_list))

    # Set the kernal variable indicating that it is initialized
    initialized = True

def generate_pairs():
    # Define global variables to prevent shadowing
    global candidates_pairs

    # Initialize empty dict for every candidate
    for candidate in data.final_candidates:
        candidates_pairs[candidate] = candidates_pairs.get(candidate, {})

    # Loop over all candidate combinations, generate a new pair and add it to the corresponding list
    for i in range(0, len(data.final_candidates)):
        for j in range(0, len(data.final_candidates)):
            # Do not create a pair if both candidates are equal
            if i != j:
                new_pair = pairs.Pairs(data.final_candidates[i], data.final_candidates[j], data.rankings_list)
                candidates_pairs[data.final_candidates[i]][data.final_candidates[j]] = new_pair



# Initialize the lists of dirty_candidates and clean_candidates. The list of clean_candidates is ordered.
def get_non_dirty_candidates():
    # Define global variables to prevent shadowing
    global dirty_candidates
    global clean_candidates
    global candidates_pairs

    # Loop over all final candidates
    for candidate in data.final_candidates:
        # If the candidate has one dirty pair append him to the dirty candidates list
        for current_pair in candidates_pairs[candidate]:
            if candidates_pairs[candidate][current_pair].dirty:
                dirty_candidates.append(candidate)
                break

        # If the candidate was not appended to the dirty candidates list, he has to be clean
        if not (candidate in dirty_candidates):
            # If the list of clean candidates is empty, just append the candidate
            if not clean_candidates:
                clean_candidates.append(candidate)
            # Otherwise loop over the list until the corresponding spot is found and insert the candidate there
            # (keeps the list sorted)
            else:
                index = 0
                while index < len(clean_candidates) and candidates_pairs[clean_candidates[index]][candidate].rel:
                    index += 1
                clean_candidates.insert(index, candidate)


# Generate the instances using the candidates splitmode
def split_instances_with_candidates():
    # Define global variables to prevent shadowing
    global instances

    splitter = candidatesplit.candidatesplit(data.final_candidates, data.rankings_list)
    instances = splitter.split()


def split_instances_with_majority():
    global candidates_pairs
    global instances

    logging.info("Building the majority graph ...")

    graph = Graph(data.final_candidates)

    for candidate1 in candidates_pairs:
        for candidate2 in candidates_pairs[candidate1]:

            pair = candidates_pairs[candidate1][candidate2]
            logging.debug("Checking: " + str(pair))
            if pair.rel:
                graph.add_edge(pair.candidates[0], pair.candidates[1])

    instances = graph.get_scc()


def cleanup_diverse_kernels(diverse_kernels):
    index = 0
    for subk in diverse_kernels:
        expected_length = subkernels[index].candidate_count
        index += 1
        for result in subk:
            if len(set(result)) < expected_length:
                subk.remove(result)


# Generate the solution by concatenating the solutions of the subkernels.
def solve_kernel(filename):
    global initialized
    global subkernels

    if not initialized:
        logging.error("Kernel not initialized. Exiting.")
        exit(1)

    solution = []
    diverse_kernels = []

    for currentKernel in subkernels:
        result = currentKernel.generate_solution(filename)
        solution += result[0]
        if config.solver == "dwave" or config.solver == "hybrid":
            if len(result) == 4:
                diverse_kernels.append(result[3])
            else:
                diverse_kernels.append(result[2])
        else:
            if len(result) == 3:
                diverse_kernels.append(result[2])
            else:
                diverse_kernels.append([solution])

    for index in range(0,len(diverse_kernels)):
        new_diverse_kernel = []
        for element in diverse_kernels[index]:
            if element not in new_diverse_kernel:
                new_diverse_kernel.append(element)
        diverse_kernels[index] = new_diverse_kernel
        if len(diverse_kernels[index]) > 10:
            diverse_kernels[index] = diverse_kernels[index][:10]

    if config.solver == "dwave" or config.solver == "hybrid" or config.solver == "simulated":
        diverse_solutions = []
        cleanup_diverse_kernels(diverse_kernels)

        if not diverse_kernels:
            logging.error("All kernel samples invalid. No solution found.")
            exit(1)
        diversify(diverse_solutions, diverse_kernels)
        analyze_diverse_solutions(diverse_solutions)

    if config.solver == "dwave" or config.solver == "hybrid":
        return solution, result[1], result[2]
    else:
        return solution, result[1]


def analyze_diverse_solutions(diverse_solutions):
    logging.info("Listing diverse solutions:")

    kt_distances = {}
    i_s = 0
    for s in diverse_solutions:
        if len(s) < len(data.final_candidates):
            diverse_solutions.remove(s)
            continue

        logging.info(s)
        i_s1 = 0
        for s1 in diverse_solutions:
            if s != s1:
                try:
                    ranking_info = candidatesplit.candidatesplit(s[1], [s[1], s1[1]])
                except ValueError:
                    diverse_solutions.remove(s)
                    continue
                kt_pairs = ranking_info.candidate_pairs
                kt_distance = 0
                for a in kt_pairs:
                    for b in kt_pairs:
                        if a != b:
                            if kt_pairs[a][b].cost == 1:
                                kt_distance += kt_pairs[a][b].cost
                kt_distances[(i_s, i_s1)] = kt_distance

            i_s1 += 1
        i_s += 1

    kt_values = kt_distances.values()

    if kt_values:
        logging.debug(f'KT Distances: {kt_values}')
        logging.info(f'Minimal KT Distance: {sorted(kt_values)[0]}, Avg: {sum(kt_values) / len(kt_values)}, Sum: {sum(kt_values)}')
    else:
        logging.info("No diverse solutions found.")


def diversify(diverse_solutions, diverse_kernels, kernel_index=0, subsolution=[]):
    if kernel_index == len(diverse_kernels):
        try:
            cost = get_rank_value(subsolution)
        except KeyError:
            return

        if len(diverse_solutions) == 0:
            diverse_solutions.append([cost, subsolution])
            return

        insert_index = 0
        while (len(diverse_solutions) > insert_index) and (diverse_solutions[insert_index][0] < cost):
            insert_index += 1
        diverse_solutions.insert(insert_index, [cost, subsolution])
        max_solutions = 10
        if len(diverse_solutions) > max_solutions:
            diverse_solutions.pop(max_solutions)
        return

    for part in diverse_kernels[kernel_index]:
        new_subsolution = subsolution.copy()
        for item in part:
            new_subsolution.append(item)
        diversify(diverse_solutions, diverse_kernels, kernel_index + 1, new_subsolution)


def get_rank_value(solution):
    total_costs = 0

    for a in range(0, len(solution) - 1):
        for b in range(a + 1, len(solution)):
            sa = solution[a]
            sb = solution[b]
            total_costs += candidates_pairs[str(sa)][str(sb)].cost

    return total_costs
