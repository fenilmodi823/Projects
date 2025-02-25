from tkinter import *
import requests
import json

root = Tk()
root.title("Air Quality Detector")
root.geometry("800x100")
root.configure(background='green')

try:
    api_request = requests.get("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=20002&distance=10&API_KEY=YOUR_API_KEY")
    api = json.loads(api_request.content)
    
    if len(api) > 0:
        city = api[0]['ReportingArea']
        quality = api[0]['AQI']
        category = api[0]['Category']['Name']
        output = f"{city} Air Quality: {quality} ({category})"
    else:
        output = "No data available for the specified location."
except Exception as e:
    output = "Error fetching data: " + str(e)

myLabel = Label(root, text=output, font=("Helvetica", 20), background="green", wraplength=700, justify="center")
myLabel.pack(pady=20)

root.mainloop()
