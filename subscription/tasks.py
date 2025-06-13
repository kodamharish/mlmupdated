import threading
import time
from datetime import date
from .models import Subscription

def update_subscription_status():
    while True:
        try:
            today = date.today()

            # Fetch only active (paid) subscriptions
            subscriptions = Subscription.objects.filter(subscription_status='paid')

            for sub in subscriptions:
                if sub.subscription_end_date <= today:
                    sub.subscription_status = "unpaid"
                    sub.save()
                    #print(f"[{today}] Subscription ID {sub.subscription_id} status updated to 'unpaid'")

        except Exception as e:
            print(f"[{date.today()}] Error in update_subscription_status: {e}")

        time.sleep(86400)  # sleep for 1 day (for production)

        # For testing, you can reduce this to:
        #time.sleep(10)


def start_thread():
    #print("Subscription thread starting...")  # ✅ Debug print
    printer_thread = threading.Thread(target=update_subscription_status)
    printer_thread.daemon = True
    printer_thread.start()


