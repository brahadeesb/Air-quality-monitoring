import asyncio
import websockets
import numpy.random as random

async def server(websocket, path):
    print("WebSocket connection established")
    while True:
        # Simulate AQI data for demonstration purposes (replace this with your actual AQI calculation logic)
        aqi_value = random.randint(0, 2000)

        # Send AQI data to the connected client (HTML webpage)
        await websocket.send(str(aqi_value)+","+str(aqi_value + random.randint(-100,100)))

        # Wait for a few seconds before sending the next data
        await asyncio.sleep(5)  # Adjust this interval based on your requirements

start_server = websockets.serve(server, "localhost", 8765)  # You can use any available port number

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
