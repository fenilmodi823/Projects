import requests
import smtplib
import time
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# ====================
# USER CONFIGURATION
# ====================

# Set your location coordinates (in decimal degrees)
MY_LAT = 23.184445      # e.g., 40.7128 for New York City; fill in your latitude
MY_LON = 72.611403      # e.g., -74.0060 for New York City; fill in your longitude

# Overhead threshold (in km): ISS must be within this distance of your subpoint
THRESHOLD_KM = 300

# Email configuration (using Gmail in this example)
SENDER_EMAIL = "fenilmmodi162@gmail.com"         # Replace with your Gmail address
SENDER_PASSWORD = "FenilModi1602"  # Replace with your Gmail password or app-specific password
RECEIVER_EMAIL = "fenilmmodi@gmail.com"     # Replace with the recipient's email address
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ====================
# HELPER FUNCTIONS
# ====================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute the great-circle distance between two points on Earth.
    All latitudes/longitudes are in decimal degrees.
    Returns distance in kilometers.
    """
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def iss_is_overhead():
    """
    Fetch the current ISS position and return True if it is within THRESHOLD_KM of your location.
    """
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
    except Exception as e:
        print("Error fetching ISS data:", e)
        return False

    data = response.json()
    iss_position = data["iss_position"]
    iss_lat = float(iss_position["latitude"])
    iss_lon = float(iss_position["longitude"])
    
    distance = haversine_distance(MY_LAT, MY_LON, iss_lat, iss_lon)
    print(f"ISS position: ({iss_lat}, {iss_lon}); Your position: ({MY_LAT}, {MY_LON}); Distance: {distance:.2f} km")
    
    return distance <= THRESHOLD_KM

def is_night_time(lat, lon):
    """
    Determine whether it is currently night time at the given latitude and longitude.
    Uses the Sunrise-Sunset API (which returns times in UTC).
    Returns True if it's night (i.e., current UTC time is before sunrise or after sunset).
    """
    try:
        params = {
            "lat": lat,
            "lng": lon,
            "formatted": 0  # Returns ISO 8601 formatted times in UTC
        }
        response = requests.get("https://api.sunrise-sunset.org/json", params=params)
        response.raise_for_status()
        data = response.json()
        sunrise_str = data["results"]["sunrise"]
        sunset_str = data["results"]["sunset"]
        # Convert ISO 8601 strings to datetime objects
        sunrise = datetime.datetime.fromisoformat(sunrise_str)
        sunset = datetime.datetime.fromisoformat(sunset_str)
        now = datetime.datetime.utcnow()
        # It's night if current UTC time is before sunrise or after sunset.
        if now < sunrise or now > sunset:
            return True
        else:
            return False
    except Exception as e:
        print("Error determining day/night:", e)
        return False

def send_email_alert():
    """
    Sends an email alert that the ISS is overhead.
    """
    subject = "ISS Overhead Alert!"
    body = "The ISS is currently overhead your location. Look up and enjoy the view!"
    
    # Set up the MIME message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

# ====================
# MAIN LOOP
# ====================

def main():
    print("Starting ISS overhead notifier. Checking every 10 minutes...")
    while True:
        if iss_is_overhead():
            if is_night_time(MY_LAT, MY_LON):
                print("ISS is overhead and it's night time! Sending email alert.")
                send_email_alert()
            else:
                print("ISS is overhead but it's daytime. No alert sent.")
        else:
            print("ISS is not overhead.")
        # Wait for 10 minutes (600 seconds) before checking again
        time.sleep(600)

if __name__ == "__main__":
    main()
