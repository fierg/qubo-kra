import numpy as np
import os


# coordinates sample creation
def director(candidates, numberOfSamples, minVotes, maxVotes, sampleName):
    nextSample = 5
    for i in range(numberOfSamples):
        if minVotes == maxVotes:
            numberOfVotes = maxVotes
        else:
            numberOfVotes = np.random.randint(minVotes, maxVotes)
        generator(candidates, numberOfVotes, nextSample, sampleName)
        nextSample = nextSample + 1


# creates a single sample
def generator(candidates, numberOfVotes, sampleNumber, sampleName):
    votes = []

    for i in range(numberOfVotes):
        np.random.shuffle(candidates)
        x = candidates.copy()
        votes.append(x)

    filename = "../data/generated/" + str(numberOfVotes) + "/" + sampleName + str(sampleNumber) + ".election"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w+")

    for i in range(numberOfVotes):
        for j in range(len(candidates)):
            f.write(votes[i][j])
            if j < len(candidates) - 1:
                f.write(">")
        f.write("\n")


def generate():
    print(os.getcwd())
    candidates = []
    nrCandidates = 100
    for i in range(0, nrCandidates):
        candidates.append(str(i))

    director(candidates, 5, nrCandidates, nrCandidates, "test")


if __name__ == '__main__':
    generate()
