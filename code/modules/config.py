import logging
import sys
import argparse


def init():
    # Define global variables to prevent shadowing
    global debug
    global quiet
    global splitmode
    global solver
    global s
    global inputformat
    global inputfile
    global num_reads
    global quality
    global chain_strength

    # Create argument parser object
    args = argparse.ArgumentParser(description="A tool for calculating the optimal kemeny rank score")

    # Define arguments
    args.add_argument("--debug", help="enable debug output (Values: True, False)", default="False",
                      choices=["True", "False"])
    args.add_argument("--quiet", help="enable less log, output for benchmark values (Values: True, False)",
                      default="False", choices=["True", "False"])
    args.add_argument("--splitmode", help="choose the kernelization method (Values: candidates, condorcet, none)",
                      default="none", choices=["candidates", "condorcet", "none"])
    args.add_argument("--solver",
                      help="choose the solver (Values: exact, steepest-decent, simulated, hybrid, dwave, "
                           "approx-default-sort, approx-insertion-sort, approx-merge-sort, approx-quick-sort, "
                           "approx-borda, approx-local)",
                      default="none",
                      choices=["exact", "steepest-decent", "simulated", "hybrid", "dwave", "approx-insertion-sort",
                               "approx-default-sort", "approx-merge-sort", "approx-quick-sort", "approx-borda",
                               "approx-local", "diverse-local"])
    args.add_argument("--num_reads", type=int,
                      help="choose the solver (Values: 1-10000), only applied when solving with a (simulated) quantum "
                           "solver")
    args.add_argument("--chain_strength", type=int,
                      help="sets the coupling strength between qubits representing variables.")
    args.add_argument("--inputformat", help="choose the input file format (Values: ranking, pwg)", default="ranking",
                      choices=["ranking", "pwg"])
    args.add_argument("--quality",
                      help="compare quality of results with exact solution (in generated-sosts.json) (Values: True, "
                           "False)",
                      default="False", choices=["True", "False"])
    args.add_argument("inputfile", help="the location of the input data", nargs=1)

    # Read argument values
    cli_args = args.parse_args()

    # Set configuration value: debug
    if cli_args.debug == "True":
        debug = True
        logging.RootLogger.setLevel(self=logging.RootLogger.root, level=logging.DEBUG)
    else:
        debug = False

    if cli_args.quiet == "True":
        quiet = True
        print(f'Solving file {cli_args.inputfile[0]}.')
        logging.RootLogger.setLevel(self=logging.RootLogger.root, level=logging.ERROR)
    else:
        quiet = False

    if cli_args.quality == "True":
        quality = True
    else:
        quality = False

    # Set configuration value: splitmode
    splitmode = cli_args.splitmode

    # Set configuration value: debug
    if splitmode == "candidates":
        s = 0.75
    else:
        s = 0.5

    # Set configuration value: inputformat
    inputformat = cli_args.inputformat

    # Set configuration value: inputfile
    inputfile = cli_args.inputfile[0]

    solver = cli_args.solver
    num_reads = cli_args.num_reads
    chain_strength = cli_args.chain_strength


def error_message_exit(messages):
    for message in messages:
        logging.error(str(message))
    sys.exit(1)
