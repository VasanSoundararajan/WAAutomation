import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from twilio.rest import Client

from database import supabase
import remainder
load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

client = Client(
    os.getenv("TWILIO_SID"),
    os.getenv("TWILIO_AUTH")
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    data = supabase.table("appointments") \
        .select("*") \
        .execute()

    appointments = data.data

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "appointments": appointments
        }
    )

@app.post("/add")
async def add_appointment(
    customer_name: str = Form(...),
    phone: str = Form(...),
    appointment_time: str = Form(...)
):

    supabase.table("appointments").insert({
        "customer_name": customer_name,
        "phone": phone,
        "appointment_time": appointment_time
    }).execute()

    return {"message": "Appointment Added"}