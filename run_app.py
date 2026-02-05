import subprocess
import time

# Start backend
backend = subprocess.Popen(["python", "backend.py"])
time.sleep(2)  # wait for Flask to start

# Start frontend
subprocess.call(["streamlit", "run", "frontend.py"])

backend.terminate()
