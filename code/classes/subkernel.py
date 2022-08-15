import logging
import time
import dimod
import greedy
import neal
from dimod import BinaryQuadraticModel
#logging.getLogger('dwave.cloud.client.base').setLevel(logging.WARNING)
from dwave.system import LeapHybridSampler, DWaveSampler, EmbeddingComposite
import numpy as np
import modules.config as config
import statistics


class Subkernel(object):

    # Constructor.
    def __init__(self, candidates, full_rankings_list):

        logging.debug("Init sub kernel ...")
        self.candidates = candidates
        self.candidates.sort()

        self.candidate_count = len(self.candidates)

        self.X = self.candidate_count * self.candidate_count * len(full_rankings_list)

        self.candidate_map = self.build_candidate_map()

        self.rankings_list = self.build_rankings_list(full_rankings_list)

        self.candidate_pair_penalty = self.calculate_candidate_pair_penalty()

        logging.debug("Init matrix ...")
        self.matrix = self.init_matrix()

        logging.debug("Setting candidate relation values in matrix ...")
        self.set_matrix_candidate_relation_values()

        logging.debug("Setting row column values in matrix ...")
        self.set_matrix_row_column_values()

        # logging.info(self.matrix)

    # Create a hash-map, which gives every candidate an index
    # (values 0,...,len(candidates)-1).
    def build_candidate_map(self):
        candidate_map = {}

        for i in range(0, len(self.candidates)):
            candidate_map[self.candidates[i]] = i

        return candidate_map

    # Build the restricted rankings list for the subkernel from the full rankings list.
    def build_rankings_list(self, full_rankings_list):
        rankings_list = []

        for i in range(0, len(full_rankings_list)):
            rankings_list.append([])

            for candidate in full_rankings_list[i]:
                if candidate in self.candidates:
                    rankings_list[i].append(candidate)

        return rankings_list

    # Calculate a candidate pair penalty matrix, that tells how often candidate
    # j is ranked better then candidate i.
    def calculate_candidate_pair_penalty(self):
        candidate_pair_penalty = []

        for i in range(0, self.candidate_count):
            candidate_pair_penalty.append([])

        for i in range(0, self.candidate_count):
            for j in range(0, self.candidate_count):
                candidate_pair_penalty[i].append(0)

        for vote in self.rankings_list:
            for i in range(0, self.candidate_count - 1):
                c1_index = self.candidate_map[vote[i]]
                for j in range(i + 1, self.candidate_count):
                    c2_index = self.candidate_map[vote[j]]

                    candidate_pair_penalty[c2_index][c1_index] += 1

        return candidate_pair_penalty

    # Build the matrix, that contains the edge weights.
    def init_matrix(self):
        size = self.candidate_count * self.candidate_count

        bitsize = self.X.bit_length()

        if bitsize < 14:
            matrix = np.zeros((size, size), dtype=np.int16)
        elif bitsize < 30:
            matrix = np.zeros((size, size), dtype=np.int32)
        else:
            matrix = np.zeros((size, size), dtype=np.int64)

        return matrix

    # Calculate the matrix index for the node corresponding to the given
    # candidate and position (position values are 0,...,self.candidate_count-1).
    def get_matrix_index(self, candidate, position):
        return self.candidate_map[candidate] * self.candidate_count + position

    # Map row/column pair to index.
    def row_column_to_index(self, row, column):
        return row * self.candidate_count + column

    # Set a value in the matrix.
    def set_matrix_value(self, index1, index2, value):
        if index1 > index2:
            self.matrix[index2][index1] = value
        else:
            self.matrix[index1][index2] = value

    # Add to a value in the matrix.
    def add_to_matrix_value(self, index1, index2, value):
        if index1 > index2:
            self.matrix[index2][index1] += value
        else:
            self.matrix[index1][index2] += value

    # Set all candidate pair related edge values in the matrix.
    def set_matrix_candidate_relation_values(self):
        for candidate1 in self.candidates:
            for candidate2 in self.candidates:
                if candidate1 != candidate2:
                    self.set_candidate_pair_edge_values(candidate1, candidate2)

    # Set ranking related edge values for a given candidate pair.
    def set_candidate_pair_edge_values(self, candidate1, candidate2):
        candidate_id1 = self.candidate_map[candidate1]
        candidate_id2 = self.candidate_map[candidate2]
        value = self.candidate_pair_penalty[candidate_id1][candidate_id2]

        for pos1 in range(0, self.candidate_count - 1):
            matrix_index1 = self.get_matrix_index(candidate1, pos1)
            for pos2 in range(pos1 + 1, self.candidate_count):
                matrix_index2 = self.get_matrix_index(candidate2, pos2)

                self.set_matrix_value(matrix_index1, matrix_index2, value)

    # Set row/column edge values for a given candidate pair.
    def set_matrix_row_column_values(self):
        for row in range(0, self.candidate_count):
            for column in range(0, self.candidate_count):
                index = self.row_column_to_index(row, column)
                self.add_to_matrix_value(index, index, -4 * self.X)
        for row in range(0, self.candidate_count):
            for column1 in range(0, self.candidate_count):
                for column2 in range(0, self.candidate_count):
                    index1 = self.row_column_to_index(row, column1)
                    index2 = self.row_column_to_index(row, column2)
                    self.add_to_matrix_value(index1, index2, self.X)
        for column in range(0, self.candidate_count):
            for row1 in range(0, self.candidate_count):
                for row2 in range(0, self.candidate_count):
                    index1 = self.row_column_to_index(row1, column)
                    index2 = self.row_column_to_index(row2, column)
                    self.add_to_matrix_value(index1, index2, self.X)

    # Generate the solution for the subkernel.
    def generate_solution(self, filename):
        kernelsize = len(self.candidates)
        if kernelsize == 1:
            return [self.candidates, 0.0, [self.candidates]]

        if kernelsize == 0:
            return [self.candidates, 0.0, [self.candidates]]
            # raise ValueError('FIX ME! unknown issue causing the subkernel to be size 0 ... ')

        bqm = BinaryQuadraticModel(self.matrix, 'BINARY')

        logging.info(f'Subkernel size: {str(kernelsize)}, QUBO matrix entries: {self.matrix.size}')
        label = 'QUBO - KRA - [' + str(kernelsize) + '] - ' + filename
        reads = config.num_reads
        if isinstance(reads, type(None)):
            reads = 'default'
        start = time.time()

        if config.solver == "exact":
            logging.info("Solving kernel with local exact solver...")
            sampler = dimod.ExactSolver()
            sample_set = sampler.sample(bqm)
        elif config.solver == "steepest-decent":
            logging.info(f"Solving kernel with greedy steepest decent solver with {reads} downhill runs ...")
            sampler = greedy.SteepestDescentSolver()
            if reads == 'default':
                sample_set = sampler.sample(bqm)
            else:
                sample_set = sampler.sample(bqm, num_reads=config.num_reads)
        elif config.solver == "simulated":
            logging.info(f'Solving kernel with the simulated annealing solver with {reads} reads ...')
            sampler = neal.SimulatedAnnealingSampler()
            if reads == 'default':
                sample_set = sampler.sample(bqm, label=label, num_reads=10, max_answers=10)
            else:
                sample_set = sampler.sample(bqm, label=label, num_reads=config.num_reads, max_answers=10)
            # ,answer_mode='raw')
        elif config.solver == "hybrid":
            logging.info("Solving kernel with the leap hybrid solver...")
            sampler = LeapHybridSampler()
            sample_set = sampler.sample(bqm, label=label)
        elif config.solver == "dwave":
            logging.info(f'Solving kernel with the DWave solver with {reads} reads ...')
            sampler = EmbeddingComposite(DWaveSampler(solver={'topology__type': 'pegasus'}))
            if reads == 'default':
                sample_set = sampler.sample(bqm, label=label, num_reads=10, max_answers=10, answer_mode='histogram')
            else:
                sample_set = sampler.sample(bqm, label=label, num_reads=config.num_reads, max_answers=10, answer_mode='histogram')

        else:
            raise ValueError('Unknown solver: ' + config.solver)

        fin = time.time()
        logging.info("Total sample took " + str(fin - start) + " seconds")
        sample = sample_set.first.sample
        info = sample_set.info

        if info == {}:
            info = fin - start
        else:
            if config.solver == "hybrid":
                info = (float(info['qpu_access_time']) / 1000000) % 60
                q_info = sample_set.info
            if config.solver == "dwave":
                info = (float(info["timing"]['qpu_access_time']) / 1000000) % 60
                q_info = sample_set.info["timing"]

        solution = self.extract_solution(sample)

        if config.solver == "hybrid" or config.solver == "dwave" or config.solver == "simulated":
            samples = sorted(sample_set.record, key=lambda x: x[1])
            energies = list(map(lambda x: x[1], samples))
            logging.info(
                f'Best Energy: {energies[0]}, Avg: {sum(energies) / len(energies)}, Median: {statistics.median(energies)} ')

            diversity = []
            for sample in samples:
                diversity.append(self.extract_solution_from_energies(sample))

        if config.solver == "dwave" or config.solver == "hybrid":
            logging.info(f'QPU timing {info}')
            return solution, info, q_info, diversity
        else:
            if config.solver == "simulated":
                return solution, info, diversity
            else:
                return solution, info,

    def extract_solution(self, sample):
        solution = []
        for position in range(0, len(self.candidates)):
            found = False
            for candidate in range(0, len(self.candidates)):
                if sample[candidate * len(self.candidates) + position] == 1:
                    if found:
                        logging.error(f'Error: invalid solution: {sample}')
                    else:
                        found = True
                        solution.append(self.candidates[candidate])
        return solution

    def extract_solution_from_energies(self, sample):
        solution = []
        for position in range(0, len(self.candidates)):
            found = False
            for candidate in range(0, len(self.candidates)):
                if sample[0][candidate * len(self.candidates) + position] == 1:
                    if found:
                        logging.debug(f'Error: invalid solution: {sample}')
                    else:
                        found = True
                        solution.append(self.candidates[candidate])
        return solution
