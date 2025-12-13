from src.logging_conf import setup_logging
from src.process.processor import Processor


def main():
    setup_logging()
    processor = Processor()
    processor.process()


if __name__ == "__main__":
    main()
