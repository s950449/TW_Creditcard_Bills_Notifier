from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import Database
from main import run_fetch, run_notify
import os

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
db = Database()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    bills = list(db.db["bills"].rows_where(order_by="due_date desc"))
    return templates.TemplateResponse("index.html", {"request": request, "bills": bills})

@app.post("/sync")
async def sync_bills(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch)
    return {"status": "Sync started in background"}

@app.post("/notify")
async def trigger_notify(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_notify)
    return {"status": "Notification check started in background"}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram updates.
    """
    try:
        data = await request.json()
        print(f"Received Telegram Update: {data}")
        
        # Extract basic info useful for user setup
        if "message" in data:
            chat = data["message"].get("chat", {})
            chat_id = chat.get("id")
            chat_type = chat.get("type")
            text = data["message"].get("text", "")
            print(f"👉 Telegram Message from Chat ID: {chat_id} (Type: {chat_type}, Text: {text!r})")
            
        elif "my_chat_member" in data:
             # Bot added to a group/channel
            chat = data["my_chat_member"].get("chat", {})
            chat_id = chat.get("id")
            chat_type = chat.get("type")
            print(f"👉 Bot added to Chat ID: {chat_id} (Type: {chat_type})")

        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
