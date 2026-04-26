from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from datetime import datetime

# Add root to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import run_full_agent

app = FastAPI()

# In-memory status for the UI
task_status = {"status": "idle", "last_run": None, "logs": []}

@app.get("/api/status")
def get_status():
    return task_status

@app.post("/api/run")
def trigger_run(background_tasks: BackgroundTasks, product: str = None):
    if task_status["status"] == "running":
        return {"message": "Agent is already running"}
    
    task_status["status"] = "running"
    task_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Manual trigger started for {product if product else 'all products'}...")
    
    background_tasks.add_task(execute_agent, product)
    return {"message": "Agent started in background"}

def execute_agent(product):
    try:
        run_full_agent(product=product)
        task_status["status"] = "idle"
        task_status["last_run"] = datetime.now().isoformat()
        task_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Run completed successfully.")
    except Exception as e:
        task_status["status"] = "error"
        task_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)}")

# Serve the static frontend
@app.get("/")
def read_index():
    return FileResponse("public/index.html")
