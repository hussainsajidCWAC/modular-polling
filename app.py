import schedule
import time
import logging
import json
import os
import signal
import sys
import threading
from lambda_function import lambda_handler

# Configure logging
logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logging.info("Received shutdown signal. Exiting gracefully...")
    sys.exit(0)

# Attach signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def job_wrapper(event, label):
    try:
        logging.info(f"Starting job with label = {label}")
        outcome = lambda_handler(event, None)
        logging.info(f"Job completed with label = {label}, outcome = {outcome}")
    except Exception as e:
        logging.error(f"Error running job with label = {label} - {str(e)}", exc_info=True)

def threaded_job(event, label):
    thread = threading.Thread(target=job_wrapper, args=(event, label))
    thread.start()

def heartbeat():
    logging.info("Heartbeat - System is running")

def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        validate_config(config)
        return config
    except Exception as e:
        logging.error(f"Error loading config file: {str(e)}")
        return None

def validate_config(config):
    if 'jobs' not in config or not isinstance(config['jobs'], list):
        raise ValueError("Invalid configuration: 'jobs' key is missing or not a list")
    for job in config['jobs']:
        if 'time' not in job or 'integrationIDs' not in job:
            raise ValueError(f"Invalid job configuration: {job}")

def schedule_jobs(config):
    schedule.clear()
    for job in config['jobs']:
        time_str = job['time']
        label = job['label']

        event = {
            "queryStringParameters": {
                "environment": job['environment'],
                "integrationIDs": job['integrationIDs']
            }
        }

        if 'conditions' in job:
            event["queryStringParameters"]["conditions"] = job["conditions"]

        if 'blackout_days' in job:
            event["queryStringParameters"]["blackout_days"] = job["blackout_days"]

        schedule.every().day.at(time_str).do(threaded_job, event=event, label=label)

    heartbeat_interval = config.get('heartbeat_interval_minutes', 10)
    schedule.every(heartbeat_interval).minutes.do(heartbeat)

def reload_config_if_updated(config_file, last_mod_time):
    try:
        current_mod_time = os.path.getmtime(config_file)

        if current_mod_time != last_mod_time:
            logging.info("Reloading configuration file due to detected changes.")
            config = load_config(config_file)

            if config:
                schedule_jobs(config)

            return config, current_mod_time
        
    except Exception as e:
        logging.error(f"Error checking config file modification time: {str(e)}")

    return None, last_mod_time

if __name__ == "__main__":
    config_file = 'config.json'
    config = load_config(config_file)
    
    if config:
        schedule_jobs(config)
        last_mod_time = os.path.getmtime(config_file)
    
        while True:
            schedule.run_pending()
            config, last_mod_time = reload_config_if_updated(config_file, last_mod_time)
            time.sleep(1)
    else:
        logging.error("Failed to load initial configuration. Exiting.")