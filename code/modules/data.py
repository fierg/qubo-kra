import itertools
import logging

import modules.config as config

rankings_list = []
candidate_counts = {}
final_candidates = []
data_import_finished = False


# Initialize based on format
def init():
    if config.inputformat == "ranking":
        init_from_rankings(config.inputfile)
    elif config.inputformat == "pwg":
        init_from_pwg(config.inputfile)
    else:
        config.error_message_exit(["Could not determine the inputformat. Exiting.]"])


# Initialize data values from rankings format
def init_from_rankings(filename):
    # Define global variables to prevent shadowing
    global rankings_list
    global final_candidates
    global data_import_finished

    # Read input file line by line, construct rankings_list and count candidates appearences
    with open(filename) as file:
        for line in file:
            vote = []
            new_line = line.split(">")
            for v in new_line:
                vote.append(v.rstrip())
            vote = list(dict.fromkeys(vote))
            rankings_list.append(vote)
            count_candidates(vote)

    # Remove candidates that do not appear in all votes from the rankings list and create final_candidates list
    remove_partial_candidates()
    final_candidates = rankings_list[0].copy()

    # Set variable indicating that the import is finished
    data_import_finished = True


# Remove all candidates from the rankings_list that do not appear in all votes
def remove_partial_candidates():
    # Define global variables to prevent shadowing
    global rankings_list
    global final_candidates

    # Loop over all candidates in all votes and check if the candidate_count for the given candidate is equal to the
    # number of votes. If not, remove it.
    for vote in rankings_list:
        index = 0
        while index < len(vote):
            if candidate_counts[vote[index]] != len(rankings_list):
                vote.remove(vote[index])
            else:
                index += 1


# Increment the counter in candidate_counts by 1 for each occuring candidate in the vote
def count_candidates(vote):
    # Define global variables to prevent shadowing
    global candidate_counts

    # Increment counts
    for candidate in vote:
        candidate_counts[candidate] = candidate_counts.get(candidate, 0) + 1


# FIXME: Mayby as global variable in data? Still needed?
def create_mapping(rankings):
    return dict((v, k) for k, v in {i: rankings[i] for i in range(0, len(rankings))}.items())


# Initialize data values from pwg format
def init_from_pwg(filename):
    # Define global variables to prevent shadowing
    global rankings_list
    global final_candidates
    global data_import_finished

    # Read input file line by line, construct rankings_list and count candidates appearences
    index = 0
    candidates = 0
    map = {}
    with open(filename) as file:
        for line in file:
            if index == 0:
                candidates = int(line)
            if index < candidates:
                final_candidates.append(line.rstrip().split(",")[0])
            if index > candidates + 1:
                new_line = line.rstrip().split(",")
                map[(new_line[1], new_line[2])] = int(new_line[0])
            index += 1

    logging.info(f'Generating instances...')
    if candidates > 16:
        config.error_message_exit([f'Too many candidates ({candidates})! Currently not supported.'])

    for combination in itertools.permutations(final_candidates, candidates):
        min_a = map[combination[0], combination[1]]
        min_b = map[combination[1], combination[2]]
        min_c = map[combination[0], combination[2]]
        min_total = min(min_a, min_b, min_c)
        map[combination[0], combination[1]] -= min_total
        map[combination[1], combination[2]] -= min_total
        map[combination[0], combination[2]] -= min_total

        for i in range(0, min_total):
            rankings_list.append(combination)

    # Set variable indicating that the import is finished
    data_import_finished = True
