import json
import logging
import operator
import random
import time

import classes.pairs as pairs
import modules.config as config
import modules.data as data
from pathlib import Path

from classes import candidatesplit


def solve_default_sort():
    class Comparator(tuple):
        def __lt__(self, other):
            return candidates_pairs["".join(self)]["".join(other)].rel

    logging.info("Sorting using Tim sort (python default) ...")

    solution = sorted(data.final_candidates, key=Comparator)
    logging.info("Sorted list:")
    logging.info(solution)
    check_cost_for_solution(solution)


def solve_insertion_sort():
    logging.info("Sorting using insertion sort ...")

    logging.info("Unsorted List:")
    logging.info(data.final_candidates)

    solution = insertion_sort(data.final_candidates)
    logging.info("Sorted list:")
    logging.info(solution)
    check_cost_for_solution(solution)


def solve_merge_sort():
    logging.info("Sorting using merge sort ...")

    solution = data.final_candidates
    merge_sort(solution)
    logging.info("Sorted list:")
    logging.info(solution)
    check_cost_for_solution(solution)


def solve_quick_sort():
    logging.info("Sorting using quick sort ...")

    solution = quick_sort(data.final_candidates)
    logging.info("Sorted list:")
    logging.info(solution)
    check_cost_for_solution(solution)


def solve_borda():
    logging.info("Sorting using the Borda method ...")
    borda_values = {}
    cost_sum = 0

    for candidate1 in candidates_pairs:
        for candidate2 in candidates_pairs[candidate1]:
            cost_sum = cost_sum + candidates_pairs[candidate1][candidate2].cost / len(candidates_pairs)
        borda_values[candidate1] = cost_sum
        cost_sum = 0

    class Comparator(tuple):
        def __lt__(self, other):
            return borda_values["".join(self)] < borda_values["".join(other)]

    solution = sorted(borda_values, key=Comparator)
    logging.info("Sorted list:")
    logging.info(solution)
    check_cost_for_solution(solution)


def solve_local():
    changes_made = True
    permutation = list(range(len(data.final_candidates)))
    while changes_made:
        changes_made = False
        logging.debug("Running local solve iteration ...")
        random_positions = list(range(len(data.final_candidates)))
        random.shuffle(random_positions)
        positional_costs = {}
        for index_to_swap in random_positions:
            for p2 in permutation:
                permutation[index_to_swap], permutation[p2] = permutation[p2], permutation[index_to_swap]
                positional_costs[p2] = get_costs_for_solution(list(map(lambda x: data.final_candidates[x], permutation)))
                permutation[index_to_swap], permutation[p2] = permutation[p2], permutation[index_to_swap]

            min_cost_position = min(positional_costs, key=positional_costs.get)
            if index_to_swap != min_cost_position:
                cost1 = get_costs_for_solution(list(map(lambda x: data.final_candidates[x], permutation)))
                permutation[index_to_swap], permutation[min_cost_position] = permutation[min_cost_position], \
                                                                             permutation[index_to_swap]
                cost2 = get_costs_for_solution(list(map(lambda x: data.final_candidates[x], permutation)))
                if cost2 < cost1:
                    changes_made = True
                else:
                    permutation[index_to_swap], permutation[min_cost_position] = permutation[min_cost_position], \
                                                                                 permutation[index_to_swap]

    return list(map(lambda x: data.final_candidates[x], permutation))


def generate_solution():
    logging.info("Generating solution via approximation...")
    start = time.time()
    generate_pairs()

    if config.solver == "approx-insertion-sort":
        solve_insertion_sort()
    elif config.solver == "approx-default-sort":
        solve_default_sort()
    elif config.solver == "approx-merge-sort":
        solve_merge_sort()
    elif config.solver == "approx-quick-sort":
        solve_quick_sort()
    elif config.solver == "approx-borda":
        solve_borda()
    elif config.solver == "approx-local":
        logging.info("Sorting using local search ...")
        solution = solve_local()
        logging.info("Sorted list:")
        logging.info(solution)
        check_cost_for_solution(solution)
    elif config.solver == "diverse-local":
        generate_diverse_solutions()
    else:
        raise RuntimeError(f'Solver type {config.solver} not recognized.')
    fin = time.time()
    if config.quiet:
        print(f'Time: {fin - start}')
    else:
        logging.info(f'Solve Time: {fin - start}')


def remove_duplicates(solutions):
    dup_free = {}
    for x in solutions:
        if tuple(x[1]) not in dup_free.keys():
            dup_free[tuple(x[1])] = 1
        else:
            dup_free[tuple(x[1])] = dup_free[tuple(x[1])] + 1

    return dup_free


def generate_diverse_solutions():
    logging.info("Generating diverse solutions with the local search.")
    solutions = []
    for i in range(50):
        solution = solve_local()
        solutions.append((get_costs_for_solution(solution), solution, 1))
    duplicate_free = remove_duplicates(solutions)
    solution = analyze_diverse_solutions(duplicate_free)
    check_cost_for_solution(solution)


def generate_pairs():
    # Define global variables to prevent shadowing
    global candidates_pairs
    candidates_pairs = {}

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


def check_cost_for_solution(solution):
    try:
        total_costs = get_costs_for_solution(solution)

        logging.info(f'Cost for solution: {total_costs} - {solution}')

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
            if config.quiet:
                print(f'Solution is {relative_cost} % of the optimal cost.')
            else:
                logging.info("Solution is +" + str(relative_cost) + "% of the optimal cost.")

    except KeyError:
        logging.info("No solution to validate found for: " + str(config.inputfile))


def get_costs_for_solution(solution):
    total_costs = 0
    for a in range(0, len(solution)):
        for b in range(a + 1, len(solution)):
            sa = solution[a]
            sb = solution[b]
            total_costs += candidates_pairs[sa][sb].cost
    return total_costs


def insertion_sort(array):
    for i in range(1, len(array)):
        key_item = array[i]

        j = i - 1
        while j >= 0 and candidates_pairs[array[i]][array[j]].rel:
            array[j + 1] = array[j]
            j -= 1

        array[j + 1] = key_item

    return array


def merge_sort(array):
    if len(array) > 1:

        r = len(array) // 2
        L = array[:r]
        M = array[r:]

        merge_sort(L)
        merge_sort(M)

        i = j = k = 0

        while i < len(L) and j < len(M):
            if candidates_pairs[L[i]][M[j]].rel:
                array[k] = L[i]
                i += 1
            else:
                array[k] = M[j]
                j += 1
            k += 1

        while i < len(L):
            array[k] = L[i]
            i += 1
            k += 1

        while j < len(M):
            array[k] = M[j]
            j += 1
            k += 1


def quick_sort(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0]
        for x in array:
            if x == pivot:
                equal.append(x)
            elif candidates_pairs[x][pivot].rel:
                less.append(x)
            else:
                greater.append(x)
        return quick_sort(less) + equal + quick_sort(greater)
    else:
        return array


def analyze_diverse_solutions(diverse_solutions):
    logging.info("Listing diverse solutions:")

    kt_distances = {}
    i_s = 0
    sorted_solutions = sorted(diverse_solutions, key=lambda x: (get_costs_for_solution(x), -diverse_solutions[x]))
    sorted_solutions = sorted_solutions[:10]
    for s in sorted_solutions:
        logging.info(f'Cost: {get_costs_for_solution(s)} Solution: {s}  #{diverse_solutions[s]}')
        s = list(s)
        i_s1 = 0
        for s1 in diverse_solutions:
            s1 = list(s1)
            if s != s1:
                try:
                    ranking_info = candidatesplit.candidatesplit(s, [s, s1])
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
        logging.info(
            f'Minimal KT Distance: {sorted(kt_values)[0]}, Avg: {sum(kt_values) / len(kt_values)}, Sum: {sum(kt_values)}')
    else:
        logging.info("No diverse solutions found.")

    return sorted_solutions[0]
