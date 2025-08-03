from datetime import datetime


def log(message):
    """Logs messages with a timestamp."""
    print(f"[{datetime.now()}] {message}")


def parse_status_update(scrapper_id, status_data):
    status = status_data.get('status', 'unknown')

    if status == 'running':
        last_update_dt = status_data.get('last_update')
        time_since_update = (datetime.now() - last_update_dt).total_seconds()

        count = status_data.get('count')
        msg = f"✅ *{scrapper_id}*: Running\n" \
            f"   - Last update: {int(time_since_update)}s ago\n" \
            f"   - Current count: {count}"
    elif status == 'initializing':
        msg = f"⏳ *{scrapper_id}*: Initializing..."
    elif status == 'crashed':
        error_msg = status_data.get('error', 'Unknown error')
        msg = f"❌ *{scrapper_id}*: Crashed\n" \
            f"   - Error: {error_msg}"
    else:
        msg = f"❓ *{scrapper_id}*: Status unknown"
    return msg