import modules.config as config


# Create a class for objects containing candidate pair statistics
class Pairs(object):

    # Constructor
    def __init__(self, candidate1, candidate2, rankings, dirty=None):
        # Store the cooresponding candidates
        self.candidates = [candidate1, candidate2]

        self.rankings = rankings

        # Import the s-value from config
        self.s = config.s

        self.cost = 0

        # FIXME: Why do we set rel by default to false? Why dirty as a parameter? Why do we set rel in the check_dirty function and return the dirty status instead of setting it? Why is rel not set accordingly when we have the dirty-parameter in the constructor set?
        self.rel = False
        if dirty is None:
            self.dirty = self.check_dirty()
        else:
            self.dirty = dirty

    # Generate pair statistics
    def check_dirty(self):
        bigger, smaller = 0, 0
        # Count how often the first candidate is ranked better and worse then the second candidate
        for vote in self.rankings:
            if vote.index(self.candidates[0]) < vote.index(self.candidates[1]):
                bigger += 1
            else:
                smaller += 1

        # Set relation
        self.rel = bigger >= smaller
        self.cost = smaller

        # Return dirty status
        return not (bigger / (bigger + smaller) >= self.s or smaller / (bigger + smaller) >= self.s)

    # Format the output when converting pair-objects to strings
    def __str__(self):
        rel_val = "False"
        if self.rel:
            rel_val = "True"

        dirty_val = "False"
        if self.dirty:
            dirty_val = "True"

        return "[" + self.candidates[0] + ", " + self.candidates[1] + "] dirty: " + dirty_val + ", rel: " + rel_val
