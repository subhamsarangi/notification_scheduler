import time

def fetch_data(user_id):
    print(f"Fetching data for user {user_id}...")
    time.sleep(2)  # Simulate
    print(f"Data fetched for user {user_id}")
    return f"Data for user {user_id}"

def main():
    users = [1, 2, 3, 4, 5] 
    results = []

    for user_id in users:
        result = fetch_data(user_id)
        results.append(result)

    print("All data fetched:")
    for result in results:
        print(result)

start_time = time.time()
main()
end_time = time.time()

print(f"Time taken (non-async): {end_time - start_time} seconds")
