import asyncio

from src.processor.processor import Processor


async def main():
    processor = Processor()
    await processor.process(
        base_url="https://jsonplaceholder.typicode.com",
        endpoint="/posts",
        method="GET",
    )


if __name__ == "__main__":
    asyncio.run(main())
