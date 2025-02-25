from tkinter import *
import requests # type: ignore
import json

root = Tk()
root.title("Air Quality Detector")
root.geometry("800x100")  # Increased height for better content display
root.configure(background='green')

try:
    # Replace with your valid API key
    api_request = requests.get("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=20002&distance=10&API_KEY=YOUR_API_KEY")
    api = json.loads(api_request.content)
    
    if len(api) > 0:  # Ensure there's data in the response
        city = api[0]['ReportingArea']
        quality = api[0]['AQI']
        category = api[0]['Category']['Name']
        output = f"{city} Air Quality: {quality} ({category})"
    else:
        output = "No data available for the specified location."
except Exception as e:
    output = "Error fetching data: " + str(e)

# Display the result
myLabel = Label(root, text=output, font=("Helvetica", 20), background="green", wraplength=700, justify="center")
myLabel.pack(pady=20)

root.mainloop()
