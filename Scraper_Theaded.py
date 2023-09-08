import queue
import requests
import multiprocessing
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urljoin
from multiprocessing import Manager
import os

# Function to take user input and return the target URL
def take_input():
    domain = input("Welcome to the scraper, please enter your domain (e.g., https://example.com): ")
    depth = int(input("Please enter the target depth: "))
    url = input("Please enter the target URL: ")
    return domain, depth, url

# Function to make an HTTP request and extract links
def make_request(url, domain):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.netloc == domain:
                        links.append(absolute_url)
            return links
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def trim_list(masterlist, urls, lock):
    """Returns a list of non-duplicate urls compared to masterlist"""
    returnlist = []
    with lock:
        unique_urls = set(masterlist)  # Create a set of unique URLs from the masterlist

    for url in urls:
        if url not in unique_urls:
            returnlist.append(url)
            unique_urls.add(url)  # Add the URL to the set of unique URLs

    return returnlist
# Function to write data to a CSV file, creating the file if it doesn't exist
def write_to_csv(masterlist, filename):
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as new_csvfile:
            csv_writer = csv.writer(new_csvfile)
            csv_writer.writerow(['Linked_URLs'])  # Write header if the file is created

    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
          # Extract the Linked_URLs from the data
        csv_writer.writerow(masterlist)  # Write a single row with each URL in a separate cell



# Function for worker processes to scrape and process URLs
def proccess_target(domain, depth, workqueue, output_list, lock):
    while True:
        try:
            url, current_depth = workqueue.get(timeout=5)
        except queue.Empty:
            break

        if current_depth <= depth:
            urls = make_request(url, domain)
            unique_urls = trim_list(output_list, urls, lock)  # Remove duplicates
            with lock:
                output_list.extend(unique_urls)  # Add unique URLs to the masterlist
                for link in unique_urls:
                    workqueue.put((link, current_depth + 1))
    print(f"Process {multiprocessing.current_process().name} finished.")
# Main function
if __name__ == "__main__":
    domain, depth, start_url = take_input()

    # Initialize shared data structures
    manager = Manager()
    masterlist = manager.list()
    lock = manager.Lock()
    workqueue = manager.Queue()

    # Initialize the work queue with the starting URL
    workqueue.put((start_url, 0))

    # Create and start worker processes
    processes = []
    for i in range(os.cpu_count()):
        process = multiprocessing.Process(target=proccess_target, args=(domain, depth, workqueue, masterlist, lock))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Write the data to a CSV file
    write_to_csv(masterlist, f"web_scraped_data_{domain}_depth_{depth}.csv")

    print("Scraping completed. Data written to CSV file.")
