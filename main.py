import asyncio

from src.logging_conf import setup_logging
from src.processor.processor import Processor


async def main():
    setup_logging()
    processor = Processor()
    await processor.process_endpoint(
        base_url="https://dummyjson.com",
        endpoint="/products",
        method="GET",
    )


if __name__ == "__main__":
    asyncio.run(main())
