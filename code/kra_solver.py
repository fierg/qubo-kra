import logging

import modules.config as config
import modules.data as data
import modules.kernelgeneration as kernelgeneration

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    # Initialize configuration
    config.init()

    # Initialize data
    data.init()

    # Generate solution
    kernelgeneration.generate_solution()
