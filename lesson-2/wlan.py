import network
import urequests
import dht
import utime
from machine import Pin

SSID = "Wokwi-GUEST"
PASSWORD = ""

API_KEY = "X0O4X49FR8K06Y19"
ENDPOINT = "https://api.thingspeak.com/update"

sensor = dht.DHT22(Pin(28))

wlan = network.WLAN(network.STA_IF)  # Create a WLAN object in station mode, the device connects to a Wi-Fi network as a client. 
wlan.active(True)                    # Activate the Wi-Fi interface
wlan.connect(SSID, PASSWORD)         # Connect to the specified Wi-Fi network

print("Connecting to Wi-Fi...", end="")
while not wlan.isconnected():
    print(".", end="")               # Print dots while waiting
    utime.sleep(0.5)                  # Wait half a second before retrying

print("\nConnected!\n")

def send_to_thingspeak(temp):
    if temp is None:
        print("No temperature data to send.")
        return

    try:
        # Send HTTP POST request to ThingSpeak with temperature data
        response = urequests.post(
            ENDPOINT,
            data= f'api_key={API_KEY}&field1={temp}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print("ThingSpeak response:", response.text)  # Print server response
        response.close()  # Close the connection

    except Exception as e:
        print("Failed to send data:", e)  # Handle any errors

while True:
    try:
        sensor.measure()                      # Trigger sensor measurement
        temperature = sensor.temperature()    # Read temperature in Celsius
        print("Temperature:", temperature, "°C")  # Display temperature
        send_to_thingspeak(temperature)     # Send data to ThingSpeak

    except Exception as e:
        print("Error reading sensor or sending data:", e)  # Handle errors

    utime.sleep(15)  # Wait 15 seconds before next reading