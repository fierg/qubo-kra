import logging

import modules.config as config
import modules.data as data
import modules.kernelgeneration as kernelgeneration
from modules import approximation

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    # Initialize configuration
    config.init()

    # Initialize data
    data.init()

    # Generate solution
    if str(config.solver).startswith("approx") | str(config.solver).startswith("diverse"):
        approximation.generate_solution()
    else:
        kernelgeneration.generate_solution()
