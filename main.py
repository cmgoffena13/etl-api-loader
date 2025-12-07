import asyncio

from src.logging_conf import setup_logging
from src.processor.processor import Processor


async def main():
    setup_logging()
    processor = Processor()
    await processor.process_endpoint(
        name="dummyjson",
        endpoint="products",
    )


if __name__ == "__main__":
    asyncio.run(main())
