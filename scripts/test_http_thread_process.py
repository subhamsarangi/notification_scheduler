import time
import requests
import concurrent.futures
import multiprocessing

def fetch_user_data(user_id: int):
    try:
        url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return f"Error fetching user {user_id}: {e}"

def run_with_threads():
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_user_data, 1),
                   executor.submit(fetch_user_data, 2),
                   executor.submit(fetch_user_data, 3),
                   executor.submit(fetch_user_data, 4)]
        for future in futures:
            future.result()
    
    return time.time() - start_time

def run_with_multiprocessing():
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(fetch_user_data, 1),
                   executor.submit(fetch_user_data, 2),
                   executor.submit(fetch_user_data, 3),
                   executor.submit(fetch_user_data, 4)]
        for future in futures:
            future.result()
    
    return time.time() - start_time

def run_multiple_times(func, num_runs):
    total_time = 0
    for _ in range(num_runs):
        total_time += func()
    return total_time / num_runs

def main():
    num_runs = 10
    
    avg_thread_time = run_multiple_times(run_with_threads, num_runs)
    print(f"Average time for run_with_threads: {avg_thread_time:.4f} seconds")
    
    avg_process_time = run_multiple_times(run_with_multiprocessing, num_runs)
    print(f"Average time for run_with_multiprocessing: {avg_process_time:.4f} seconds")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Ensuring the spawn method is used
    main()
