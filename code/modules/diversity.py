import neal
from dwave.system import EmbeddingComposite, DWaveSampler

if __name__ == '__main__':
    # sampler = neal.SimulatedAnnealingSampler()
    sampler = EmbeddingComposite(DWaveSampler())
    test = sampler.sample_ising({}, {('s1', 's2'): 0.5, ('s1', 's3'): 0.5, ('s2', 's3'): 0.5}, num_reads=1000,
                                max_answers=5)
    print(test)
