import classes.pairs as pair


class candidatesplit(object):

    def __init__(self, candidates, rankings):
        self.clean_candidates = []
        self.dirty_candidates = []
        self.candidate_pairs = {}

        self.candidates = candidates
        self.rankings = []

        self.build_rankings_list(rankings)
        self.generate_pairs()
        self.get_non_dirty_candidates()

    def build_rankings_list(self, rankings):
        for ranking in rankings:
            restricted_rankings_list = []
            for candidate in ranking:
                if candidate in self.candidates:
                    restricted_rankings_list.append(candidate)
            self.rankings.append(restricted_rankings_list)

    def generate_pairs(self):
        for candidate in self.candidates:
            self.candidate_pairs[candidate] = self.candidate_pairs.get(candidate, {})

        for can1 in range(0, len(self.candidates)):
            for can2 in range(0, len(self.candidates)):
                if can1 != can2:
                    new_pair = pair.Pairs(self.candidates[can1], self.candidates[can2], self.rankings)
                    self.candidate_pairs[self.candidates[can1]][self.candidates[can2]] = new_pair

    def get_non_dirty_candidates(self):
        for can in self.candidates:
            for cpair in self.candidate_pairs[can]:
                if self.candidate_pairs[can][cpair].dirty:
                    self.dirty_candidates.append(can)
                    break

            if not (can in self.dirty_candidates):
                if not self.clean_candidates:
                    self.clean_candidates.append(can)
                else:
                    index = 0
                    while index < len(self.clean_candidates) and self.candidate_pairs[self.clean_candidates[index]][
                        can].rel:
                        index += 1
                    self.clean_candidates.insert(index, can)

    def split(self):
        if not self.clean_candidates:
            return [self.candidates]

        instances = []

        generated_set = []

        for can in self.candidates:
            if can != self.clean_candidates[0] and self.candidate_pairs[can][self.clean_candidates[0]].rel:
                generated_set.append(can)

        recurse_split = candidatesplit(generated_set, self.rankings)
        recurse_instances = recurse_split.split()

        for instance in recurse_instances:
            instances.append(instance)

        instances.append([self.clean_candidates[0]])

        for count in range(0, len(self.clean_candidates) - 1):
            generated_set = []

            for can in self.candidates:
                if can != self.clean_candidates[count] and can != self.clean_candidates[count + 1] and \
                        self.candidate_pairs[self.clean_candidates[count]][can].rel and self.candidate_pairs[can][
                    self.clean_candidates[count + 1]].rel:
                    generated_set.append(can)

            recurse_split = candidatesplit(generated_set, self.rankings)
            recurse_instances = recurse_split.split()

            for instance in recurse_instances:
                instances.append(instance)

            instances.append([self.clean_candidates[count + 1]])

        generated_set = []

        for can in self.candidates:
            if can != self.clean_candidates[len(self.clean_candidates) - 1] and \
                    self.candidate_pairs[self.clean_candidates[len(self.clean_candidates) - 1]][can].rel:
                generated_set.append(can)

        recurse_split = candidatesplit(generated_set, self.rankings)
        recurse_instances = recurse_split.split()

        for instance in recurse_instances:
            instances.append(instance)

        return instances
