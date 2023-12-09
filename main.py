# main.py

import subprocess
from multiprocessing import Process

def run_microservice(service_name, port):
    subprocess.run(["uvicorn", f"{service_name}.main:app", "--port", str(port), "--reload"])

def main():
    # Define your microservices and their associated ports
    services = [
        ('commit_service', 8001),
        ('pullRequest_service', 8002),
        ('issue_service', 8003),
    ]

    # Create a process for each microservice
    processes = []
    for service_name, port in services:
        process = Process(target=run_microservice, args=(service_name, port))
        process.start()
        processes.append(process)

    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
