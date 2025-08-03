from datetime import datetime


def log(message):
    """Logs messages with a timestamp."""
    print(f"[{datetime.now()}] {message}")
