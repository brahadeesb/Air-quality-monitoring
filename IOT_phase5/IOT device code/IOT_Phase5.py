//Python file for IOT device
import requests
import time
from picozero import Speaker
import asyncio
import websockets
import json
import csv

greenled = Pin(5, Pin.OUT)
redled = Pin(7, Pin.OUT)
speaker = Pin(9, Pin.OUT)

# Define the CSV file name
CSV_FILE = 'sensor_data.csv'

# Define the URL where you want to send the data
POST_URL = "http://example.com/api/endpoint"  # Replace with your actual URL

# Define the analog input pin connected to AO
ANALOG_PIN = 17

# Define the voltage reference (typically 3.3V for Raspberry Pi)
VOLTAGE_REFERENCE = 3.3

# Set up GPIO (for analog input)
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:
    pass


####### Define air quality thresholds (you can adjust these as needed)
RLOAD=10.0
RZERO=76.63
#Parameters for calculating ppm of CO2 from sensor resistance
PARA=116.6020682
PARB=2.769034857
# Parameters to model temperature and humidity dependence
CORA=0.00035
CORB=0.02718
CORC=1.39538
CORD=0.0018
# Atmospheric CO2 level for calibration purposes
ATMOCO2=397.13
############

#For predictive analytics, linear regression is used
def linear_regression(array):
    features = range(1,len(array)+1)
    targets = array
    mean_features = sum(features) / len(features)
    mean_targets = sum(targets) / len(targets)

    # Calculate the slope (beta1) and intercept (beta0) of the regression line
    numerator = sum((x - mean_features) * (y - mean_targets) for x, y in zip(features, targets))
    denominator = sum((x - mean_features) ** 2 for x in features)

    beta1 = numerator / denominator  # Slope of the regression line
    beta0 = mean_targets - beta1 * mean_features
    return beta0 + beta1 * (len(array)+1)

# Define a function to read sensor data and send it to the website
rec_data = []
def read_sensor():
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
            # Read the analog sensor value (0 to 1.0)
        try:
            analog_value = GPIO.input(ANALOG_PIN) / 1024.0  # 10-bit ADC on Raspberry Pi
	    #Since this can't be done in real life, we have simulated the values using random.random()

            voltage = analog_value * VOLTAGE_REFERENCE
        except NameError:
            voltage = 1.0  # If GPIO is not available, use a placeholder value
        #print(f"Analog voltage: {voltage} V")

        # Determine air quality based on thresholds
        # calculations done to caluculate ppm value from analog output.

        air_qual=((1023/voltage) * 5 - 1)*RLOAD
        air_quality = PARA * ((resistance/RZERO)**(-PARB))
        
        if air_quality < 800:
            air_quality_condition = "Good quality Air"
            greenled.on()
            speaker.off()
            redled.off()
        elif(( air_quality > 800 )&&( air_quality <2000)):
            air_quality_condition = "Average quality air"
            redled.on()
            greenled.off()
            speaker.off()
        else:
            redled.on()
            air_quality_condition = "Bad quality air"
            speaker.on()
	    greenled.off()
     
        #Saving data in a file for predictive analytics
        timestamp = time.time()
        row = [timestamp, air_quality]
        writer.writerow(row)
        if(len(rec_data) > 25):
            rec_data.pop(0)
        rec_data.append(air_quality)
	print("Air Quality: ", air_quality ," Air Quality Condition: ", air_quality_condition, " Predicted Value: ", pred_val)
        pred_val = linear_regression(rec_data)
        return(air_quality, pred_val)



async def server(websocket, path):
    print("WebSocket connection established")
    while True:
        # Simulate AQI data for demonstration purposes (replace this with your actual AQI calculation logic)
        aqi_value, pred_value = read_sensor()

        # Send AQI data to the connected client (HTML webpage)
	data_to_be_sent = str(aqi_value) + "," + str(pred_value)
        await websocket.send(data_to_be_sent)

        #Data updates every minute
        await asyncio.sleep(60)	

start_server = websockets.serve(server, "localhost", 8765)  # You can use any available port number

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
