import logging
import sys


def setup_logging():
    logging.basicConfig(stream=sys.stdout,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
                        )
    logging.getLogger("unige_data_vis_data_collector").setLevel(logging.INFO)
