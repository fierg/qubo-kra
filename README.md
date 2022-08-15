
# QUBO Kemeny Rank Aggregation

------

### DWave Account
[Create personal dwave account](https://cloud.dwavesys.com/leap/) to use their SAPI for the hybrid and dwave solver

### Installation:
Run ```./installer/install-dwave-locally.sh ``` to install python dependencies and run dwave init. Here you set your SAPI.

### Usage:
```shell
usage: kra_solver.py [-h] [--debug {True,False}]
                     [--splitmode {candidates,condorcet,none}]
                     [--solver {exact,steepest-decent,simulated,hybrid,dwave}]
                     [--num_reads NUM_READS] [--inputformat {ranking,pwg}]
                     [--quality {True,False}]
                     inputfile
```