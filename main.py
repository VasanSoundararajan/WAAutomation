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

    try:
        message = client.messages.create(
            body=(
                f"Reminder: Hello "
                f"{appointment['customer_name']}, "
                f"your appointment is at "
                f"{appointment['appointment_time']}"
            ),
            from_=f"whatsapp:{os.getenv('TWILIO_PHONE')}",
            to=f"whatsapp:{appointment['phone']}"
        )
        print(message.sid)
        print(message.status)

    except Exception as e:
        print(e)

    return {"message": "Appointment Added"}