import logging
from processor import Processor

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - [%(levelname)-5s] %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


def main():
    pcs = Processor(logger, 'config.ini')
    pcs.run()


if __name__ == "__main__":
    main()
