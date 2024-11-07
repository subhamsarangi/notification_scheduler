import asyncio
import time

async def fetch_data(user_id):
    print(f"Fetching data for user {user_id}...")
    await asyncio.sleep(2)  # Simulate
    print(f"Data fetched for user {user_id}")
    return f"Data for user {user_id}"

async def main():
    users = [1, 2, 3, 4, 5]
    tasks = []

    for user_id in users:
        task = asyncio.create_task(fetch_data(user_id))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    print("All data fetched:")
    for result in results:
        print(result)


start_time = time.time()
asyncio.run(main())
end_time = time.time()

print(f"Time taken (async): {end_time - start_time} seconds")
