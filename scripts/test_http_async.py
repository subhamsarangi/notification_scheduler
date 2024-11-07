import asyncio
import time
import aiohttp

async def fetch_user_data(user_id: int):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    # url = f"http://127.0.0.1:5000/users/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data

async def run_with_create_task():
    start_time = time.time()
    task1 = asyncio.create_task(fetch_user_data(1))
    task2 = asyncio.create_task(fetch_user_data(2))
    task3 = asyncio.create_task(fetch_user_data(3))
    task4 = asyncio.create_task(fetch_user_data(4))

    await task1
    await task2
    await task3
    await task4
    
    return time.time() - start_time

async def run_with_gather():
    start_time = time.time()
    
    await asyncio.gather(
        fetch_user_data(1),
        fetch_user_data(2),
        fetch_user_data(3),
        fetch_user_data(4)
    )
    
    return time.time() - start_time


async def run_with_create_task_and_gather():
    start_time = time.time()
    task1 = asyncio.create_task(fetch_user_data(1))
    task2 = asyncio.create_task(fetch_user_data(2))
    task3 = asyncio.create_task(fetch_user_data(3))
    task4 = asyncio.create_task(fetch_user_data(4))

    await asyncio.gather(task1, task2, task3, task4)
    
    return time.time() - start_time


# async def main():
#     await run_with_create_task()
#     await run_with_gather()
#     await run_with_create_task_and_gather()
# asyncio.run(main())

async def run_multiple_times(func, num_runs):
    total_time = 0
    for _ in range(num_runs):
        total_time += await func()
    return total_time / num_runs


async def main():
    num_runs = 10
    
    print(f"\nRunning {num_runs} times and calculating average times:\n")
    
    avg_create_task_time = await run_multiple_times(run_with_create_task, num_runs)
    avg_gather_time = await run_multiple_times(run_with_gather, num_runs)
    avg_create_task_and_gather_time = await run_multiple_times(run_with_create_task_and_gather, num_runs)
    
    print(f"Average time for run_with_create_task: {avg_create_task_time:.4f} seconds")
    print(f"Average time for run_with_gather: {avg_gather_time:.4f} seconds")
    print(f"Average time for run_with_create_task_and_gather: {avg_create_task_and_gather_time:.4f} seconds")


asyncio.run(main())