"""
Test configuration and fixtures.
"""

import os
import shutil
from datetime import datetime, timedelta
import pytest
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs', 'tests')
os.makedirs(LOGS_DIR, exist_ok=True)

@pytest.fixture
def model_name():
    """Fixture to provide a test model name."""
    return "mistral"  # Using the installed Mistral model

def setup_logging():
    """Set up logging configuration."""
    # Remove any existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create a timestamped log file
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(LOGS_DIR, f'test_run_{timestamp}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=1024*1024,  # 1MB
                backupCount=10,
                mode='w'  # Overwrite mode to ensure clean logs
            ),
            logging.StreamHandler()
        ]
    )
    
    # Clean up old log files
    cleanup_old_logs()
    
    return log_file

def cleanup_old_logs():
    """Clean up log files older than 30 days."""
    now = datetime.now()
    for filename in os.listdir(LOGS_DIR):
        if filename.startswith('test_run_') and filename.endswith('.log'):
            filepath = os.path.join(LOGS_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if now - file_time > timedelta(days=30):
                try:
                    os.remove(filepath)
                    logging.info(f"Removed old log file: {filename}")
                except Exception as e:
                    logging.error(f"Failed to remove old log file {filename}: {str(e)}")

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Set up test logging at the start of the test session."""
    log_file = setup_logging()
    logging.info(f"Starting test session. Logging to: {log_file}")
    yield
    logging.info("Test session completed")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Log test results."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if report.passed:
            logging.info(f"Test passed: {item.name}")
        elif report.failed:
            logging.error(f"Test failed: {item.name}")
            if report.longrepr:
                logging.error(f"Failure details:\n{report.longrepr}")
        elif report.skipped:
            logging.warning(f"Test skipped: {item.name}")
            if report.longrepr:
                logging.warning(f"Skip reason:\n{report.longrepr}")
    elif report.when == "setup":
        if report.failed:
            logging.error(f"Test setup failed: {item.name}")
            if report.longrepr:
                logging.error(f"Setup failure details:\n{report.longrepr}")
    elif report.when == "teardown":
        if report.failed:
            logging.error(f"Test teardown failed: {item.name}")
            if report.longrepr:
                logging.error(f"Teardown failure details:\n{report.longrepr}") 