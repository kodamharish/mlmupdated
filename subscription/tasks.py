import threading
import time
from datetime import date
from .models import Subscription
from users.models import *


def update_subscription_status():
    from .models import Subscription
    from users.models import User  # or specific model used

    while True:
        try:
            today = date.today()
            subscriptions = Subscription.objects.filter(subscription_status='paid')

            for sub in subscriptions:
                if sub.subscription_end_date <= today:
                    sub.subscription_status = "unpaid"
                    sub.save()
                    user = sub.user_id
                    user.status = 'inactive'
                    user.save()

        except Exception as e:
            print(f"[{date.today()}] Error in update_subscription_status: {e}")

        time.sleep(86400)  # 24 hours
        #time.sleep(10)  # For testing


def start_thread():
    print("Subscription thread starting...")  # ✅ Debug print
    printer_thread = threading.Thread(target=update_subscription_status)
    printer_thread.daemon = True
    printer_thread.start()


