import subprocess

# Start main.py in a new process
process = subprocess.Popen(["python", "scripts/main.py"])
print(f"Started main.py with PID {process.pid}")

# Save PID to a file
with open("process.pid", "w") as f:
    f.write(str(process.pid))
