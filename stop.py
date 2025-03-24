import os
import signal

try:
    with open("process.pid", "r") as f:
        pid = int(f.read().strip())

    os.kill(pid, signal.SIGTERM)  # Send termination signal
    print(f"Stopped process with PID {pid}")
    os.remove("process.pid")  # Clean up PID file
except FileNotFoundError:
    print("No running process found.")
except ProcessLookupError:
    print("Process already stopped.")
