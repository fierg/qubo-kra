
# QUBO Kemeny Rank Aggregation


A tool for calculating diverse soluitions for kemeny rank

------

### DWave Account
[Create personal dwave account](https://cloud.dwavesys.com/leap/) to use their SAPI for the hybrid and dwave solver

### Installation:
Run ```./installer/install-dwave-locally.sh ``` to install python dependencies and run dwave init

### Usage:
```
usage: kra_solver.py [-h] [--debug {True,False}] [--quiet {True,False}]
                     [--splitmode {candidates,condorcet,none}]
                     [--solver {exact,steepest-decent,simulated,hybrid,dwave,approx-insertion-sort,approx-default-sort,approx-merge-sort,approx-quick-sort,approx-borda,approx-local,diverse-local}]
                     [--num_reads NUM_READS] [--chain_strength CHAIN_STRENGTH]
                     [--inputformat {ranking,pwg}] [--quality {True,False}]
                     inputfile

A tool for calculating the optimal kemeny rank score

positional arguments:
  inputfile             the location of the input data

optional arguments:
  -h, --help            show this help message and exit
  --debug {True,False}  enable debug output (Values: True, False)
  --quiet {True,False}  enable less log, output for benchmark values (Values:
                        True, False)
  --splitmode {candidates,condorcet,none}
                        choose the kernelization method (Values: candidates,
                        condorcet, none)
  --solver {exact,steepest-decent,simulated,hybrid,dwave,approx-insertion-sort,approx-default-sort,approx-merge-sort,approx-quick-sort,approx-borda,approx-local,diverse-local}
                        choose the solver (Values: exact, steepest-decent,
                        simulated, hybrid, dwave, approx-default-sort, approx-
                        insertion-sort, approx-merge-sort, approx-quick-sort,
                        approx-borda, approx-local)
  --num_reads NUM_READS
                        choose the solver (Values: 1-10000), only applied when
                        solving with a (simulated) quantum solver
  --chain_strength CHAIN_STRENGTH
                        sets the coupling strength between qubits representing
                        variables.
  --inputformat {ranking,pwg}
                        choose the input file format (Values: ranking, pwg)
  --quality {True,False}
                        compare quality of results with exact solution (in
                        generated-sosts.json) (Values: True, False)

```