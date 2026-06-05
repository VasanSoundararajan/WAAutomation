from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from database import supabase

from twilio.rest import Client
from dotenv import load_dotenv

import os

load_dotenv()

# Twilio Client
client = Client(
    os.getenv("TWILIO_SID"),
    os.getenv("TWILIO_AUTH")
)

def send_reminders():

    try:

        now = datetime.now()

        next_hour = now + timedelta(hours=1)

        # Fetch all appointments
        data = supabase.table("appointments") \
            .select("*") \
            .execute()

        appointments = data.data

        for appointment in appointments:

            # Skip if reminder already sent
            if appointment.get("reminder_sent"):
                continue

            try:

                appointment_time = datetime.strptime(
                    appointment["appointment_time"][:19],
                    "%Y-%m-%dT%H:%M:%S"
                )- timedelta(hours=5, minutes=30)
                print(appointment_time)

            except Exception as e:

                print("Date Parsing Error:", e)
                continue

            if now <= appointment_time <= next_hour:
                try:

                    # Send WhatsApp/SMS Reminder
                    message = client.messages.create(
                        body=(
                            f"Reminder: \nHello Vasan S \n"
                            f"you have a appointment with \n"
                            f"{appointment['customer_name']}, at "
                            f"{appointment['appointment_time']}"
                        ),
                        from_=f"whatsapp:{os.getenv('TWILIO_PHONE')}",
                        to=f"whatsapp:{os.getenv('phone')}"
                    )

                    print(message.sid)
                    print(message.status)

                # Update reminder status
                supabase.table("appointments") \
                    .update({
                        "reminder_sent": True
                    }) \
                    .eq("id", appointment["id"]) \
                    .execute()

                print(
                    f"Reminder sent to "
                    f"{appointment['customer_name']}"
                )

            except Exception as e:

                print("Twilio Error:", e)

    except Exception as e:

        print("Scheduler Error:", e)

# Start Scheduler
scheduler = BackgroundScheduler()
print("Scheduler Running")
scheduler.add_job(
    send_reminders,
    "interval",
    minutes=1
)

scheduler.start()

print("Reminder scheduler started...")