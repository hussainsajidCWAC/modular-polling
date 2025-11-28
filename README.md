# Modular Polling System

This document was created with a generative model

## Description
A Python-based polling system that executes scheduled integration jobs with support for conditional logic, blackout days, and error handling. This project implements a modular framework designed to run functions on a scheduled basis, orchestrating multiple integrations in sequence while passing data between them to create complex workflows.

## Features
- **Scheduled Job Execution**: Jobs defined in `config.json` with specific execution times
- **Integration Chaining**: Multiple integrations chained sequentially with output from one serving as input to the next
- **Conditional Execution**: Skip integrations based on response token values or execute jobs on specific days
- **Blackout Days**: Skip entire jobs on specified days of the week (0=Monday, 6=Sunday)
- **Error Handling**: Automatic retry logic with exponential backoff (up to 5 retries)
- **Dynamic Configuration**: Automatically reloads jobs when `config.json` changes
- **Authentication**: Handles session management with cookies and unique request IDs

## Project Structure
- `lambda_function.py` - Main function that processes integration chains
- `lookup.py` - Integration client for API authentication and execution
- `app.py` - Scheduler that manages job execution and configuration reloading
- `config.json` - Job configuration with schedules, integration chains, and conditions
- `test.py` - Unit tests for Lambda handler functionality
- `logfile.log` - Application logs

## Installation
1. Clone the repository
2. Install dependencies: `pip install requests schedule`
3. Configure your jobs in `config.json`

## Usage
To start the polling scheduler:
```bash
python app.py
```

The scheduler will:
- Load configuration from `config.json`
- Schedule all active jobs
- Monitor for configuration changes
- Execute jobs at specified times

### Configuration Example
```json
{
    "time": "00:00",
    "integrationIDs": [["66c6eb17b4d36"], ["5dd2b6522be4c"]],
    "blackout_days": [6],
    "environment": "live",
    "label": "Example Job"
}
```

## Testing
Run unit tests with:
```bash
python -m pytest test.py
```

Tests cover integration chains, value conditions, blackout logic, and error handling.

## Support
Check `logfile.log` for detailed error messages.