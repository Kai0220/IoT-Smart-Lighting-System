from curses import flash
from flask import Flask, render_template, request
import mysql.connector
import serial
import threading
from flask import redirect, url_for
from flask_socketio import SocketIO, emit
import time
import sqlite3
from flask import jsonify
import asyncio
import discord
from discord import Webhook
import aiohttp

async def anything(request):
    async with aiohttp.ClientSession() as session:
        Webhook =Webhook.from_url(request,session=session)
        embed = discord.Embed("This is from a webhook.")
        await Webhook.send(embed=embed,Username="Webhook")

app = Flask(__name__)
socketio = SocketIO(app)
# Establish connection to MySQL database
 # Connect to MySQL database
mydb = mysql.connector.connect(host="ajksmarthomeapplicationdatabase.cgbowllugjv1.us-east-1.rds.amazonaws.com", user="admin", password="password", database="AJKSmartHomeApplication")
cursor = mydb.cursor()

# Establish serial connection with Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.flush()

# Function to update LED status in the database
def update_led_status(relay_status, brightness_level):
    cursor.execute("UPDATE LED_Status SET Relay_Status = %s, Brightness_Level = %s WHERE id = 1;", (relay_status, brightness_level))
    mydb.commit()
    cursor.fetchall()

@app.route("/toggle_relay", methods=["POST"])
def toggle_relay():
    cursor.execute("SELECT Relay_Status FROM LED_Status WHERE id = 1;")
    relay_status = cursor.fetchone()[0]  # Fetch current relay status
    # Toggle the relay status
    relay_status = not relay_status
    # Update the relay status in the database
    cursor.execute("UPDATE LED_Status SET Relay_Status = %s WHERE id = 1", (relay_status,))
    mydb.commit()
    # Update brightness level based on the new relay status
    brightness_level = 1 if relay_status else 0
    # Update the brightness level in the database
    cursor.execute("UPDATE LED_Status SET Brightness_Level = %s WHERE id = 1", (brightness_level,))
    mydb.commit()
    # Write the corresponding command to the Arduino to toggle the relay
    ser.write(b"1")
    cursor.fetchall()
    # Return to the index page
    return redirect(url_for("index")) 

@app.route("/increase_brightness", methods=["POST"])  # Define the route for toggling relay
# Function to increase brightness
def increase_brightness():
    cursor.execute("SELECT Brightness_Level FROM LED_Status WHERE id = 1;")
    brightness_level = cursor.fetchone()[0]  # Fetch brightness level
    if brightness_level < 3:
        brightness_level += 1  # Increase brightness level
        ser.write(b"2")  # Send command to Arduino to increase brightness
        cursor.execute("SELECT Relay_Status FROM LED_Status WHERE id = 1;")
        relay_status = cursor.fetchone()[0]  # Fetch relay status
        update_led_status(relay_status, brightness_level)  # Update database
    cursor.fetchall()
    return redirect(url_for("index"))  

@app.route("/decrease_brightness", methods=["POST"])  # Define the route for toggling relay
# Function to decrease brightness
def decrease_brightness():
    cursor.execute("SELECT Brightness_Level FROM LED_Status WHERE id = 1;")
    brightness_level = cursor.fetchone()[0]  # Fetch brightness level
    if brightness_level > 1:
        brightness_level -= 1  # Decrease brightness level
        ser.write(b"3")  # Send command to Arduino to decrease brightness
        cursor.execute("SELECT Relay_Status FROM LED_Status WHERE id = 1;")
        relay_status = cursor.fetchone()[0]  # Fetch relay status
        update_led_status(relay_status, brightness_level)  # Update database
    cursor.fetchall()
    return redirect(url_for("index"))   

@app.route("/toggle_button", methods=["POST"])
def toggle_button():
    # Get the current button value from the database
    cursor.execute("SELECT Button FROM Sensor_Availability WHERE id = 1;")
    current_button_value = cursor.fetchone()[0]
    # Toggle the button value between 0 and 1
    new_button_value = 1 if current_button_value == 0 else 0
    # Write the corresponding command to the Arduino to toggle the button
    ser.write(b"4")
    # Update the database with the new button value
    cursor.execute("UPDATE Sensor_Availability SET Button = %s WHERE id = 1;", (new_button_value,))
    mydb.commit()
    cursor.fetchall()
    return redirect(url_for("index"))  

@app.route("/toggle_ir", methods=["POST"])
def toggle_ir():
    # Get the current IR availability status from the database
    cursor.execute("SELECT IR FROM Sensor_Availability WHERE id = 1;")
    current_ir_value = cursor.fetchone()[0]
    # Toggle the IR availability status between 0 and 1
    new_ir_value = 1 if current_ir_value == 0 else 0
    # Write the corresponding command to the Arduino to toggle IR availability
    # Adjust the command according to your Arduino code
    ser.write(b"5")
    # Update the database with the new IR availability status
    cursor.execute("UPDATE Sensor_Availability SET IR = %s WHERE id = 1;", (new_ir_value,))
    mydb.commit()
    cursor.fetchall()

    return redirect(url_for("index"))  

@app.route("/toggle_ldr", methods=["POST"])
def toggle_ldr():
    # Get the current LDR availability status from the database
    cursor.execute("SELECT LDR FROM Sensor_Availability WHERE id = 1;")
    current_ldr_value = cursor.fetchone()[0]
    # Toggle the LDR availability status between 0 and 1
    new_ldr_value = 1 if current_ldr_value == 0 else 0
    # Write the corresponding command to the Arduino to toggle LDR availability
    # Adjust the command according to your Arduino code
    ser.write(b"6")
    # Update the database with the new LDR availability status
    cursor.execute("UPDATE Sensor_Availability SET LDR = %s WHERE id = 1;", (new_ldr_value,))
    mydb.commit()
    cursor.fetchall()
    return redirect(url_for("index"))


@app.route("/update_ldr_duration", methods=["POST"])
def update_ldr_duration():
    new_ldr_duration_minutes = float(request.form["ldr_duration"])
    # Convert the duration from minutes to milliseconds
    new_ldr_duration_ms = int(new_ldr_duration_minutes * 60 * 1000)
    print(new_ldr_duration_ms)
    ser.write(b"7" + str(new_ldr_duration_ms).encode() + b"\n")
    # Update the ldr_duration in the database
    cursor.execute("UPDATE Sensor_Availability SET ldr_duration = %s WHERE id = 1", (new_ldr_duration_ms,))
    mydb.commit()
    cursor.fetchall()
    # Return to the index page
    return redirect(url_for("index")) 

@app.route("/toggle_ultrasonic", methods=["POST"])
def toggle_ultrasonic():
    # Get the current Ultrasonic sensor availability status from the database
    cursor.execute("SELECT Ultrasonic FROM Sensor_Availability WHERE id = 1;")
    current_ultrasonic_value = cursor.fetchone()[0]
    # Toggle the Ultrasonic sensor availability status between 0 and 1
    new_ultrasonic_value = 1 if current_ultrasonic_value == 0 else 0
    # Write the corresponding command to the Arduino to toggle Ultrasonic sensor availability
    # Adjust the command according to your Arduino code
    ser.write(b"8")
    # Update the database with the new Ultrasonic sensor availability status
    cursor.execute("UPDATE Sensor_Availability SET Ultrasonic = %s WHERE id = 1;", (new_ultrasonic_value,))
    mydb.commit()

    return redirect(url_for("index"))

@app.route("/update_ultrasonic_duration", methods=["POST"])
def update_ultrasonic_duration():
    new_ultrasonic_duration_minutes = float(request.form["ultrasonic_duration"])
    # Convert the duration from minutes to milliseconds
    new_ultrasonic_duration_ms = int(new_ultrasonic_duration_minutes * 60 * 1000)
    # Write the corresponding command to the Arduino to update Ultrasonic sensor duration
    # Adjust the command according to your Arduino code
    ser.write(b"9" + str(new_ultrasonic_duration_ms).encode() + b"\n")
    
    # Update the ultrasonic_duration in the database
    cursor.execute("UPDATE Sensor_Availability SET Ultrasonic_Duration = %s WHERE id = 1", (new_ultrasonic_duration_ms,))
    mydb.commit()
    cursor.fetchall()
    # Return to the index page
    return redirect(url_for("index"))

@app.route("/update_ultrasonic_distance", methods=["POST"])
def update_ultrasonic_distance():
    new_ultrasonic_distance = int(request.form["ultrasonic_distance"])
    # Write the corresponding command to the Arduino to update Ultrasonic sensor distance
    # Adjust the command according to your Arduino code
    ser.write(b"0" + str(new_ultrasonic_distance).encode() + b"\n")
    # Update the ultrasonic_distance in the database
    cursor.execute("UPDATE Sensor_Availability SET ultrasonic_distance = %s WHERE id = 1", (new_ultrasonic_distance,))
    mydb.commit()
    cursor.fetchall()
    # Return to the index page
    return redirect(url_for("index"))

@app.route("/toggle_advanced_automation", methods=["POST"])
def toggle_advanced_automation():
    # Fetch current advanced automation availability
    cursor.execute("SELECT Advance_Availability FROM Advanced_Automation WHERE id = 1")
    current_available = cursor.fetchone()[0]
    # Toggle the advanced automation availability
    new_available = 1 if current_available == 0 else 0
    ser.write(b"a")  
    # Update the database with the new advanced automation availability
    cursor.execute("UPDATE Advanced_Automation SET Advance_Availability = %s WHERE id = 1", (new_available,))
    mydb.commit()
    cursor.fetchall()
    # Redirect back to the index page
    return redirect(url_for("index"))

def insert_lighting_data(cursor, light_condition, brightness_level):
    try:
        # SQL query to insert data into the table
        sql = "INSERT INTO Lighting_Data (light_condition, brightness_level) VALUES (%s, %s)"
        # Execute the query with the provided data
        cursor.execute(sql, (light_condition, brightness_level))
        # Commit the transaction
        mydb.commit()
        cursor.fetchall()
        print("Data inserted into the database successfully.")
    except mysql.connector.Error as err:
        print("Error inserting data into the database:", err)

def insert_energy_consumption(cursor, energy_consumption):
    try:
        # SQL statement to insert energy consumption data
        sql_insert = "INSERT INTO Energy_Management (Energy_Consumption, Timestamp) VALUES (%s, CURRENT_TIMESTAMP)"
        # Execute the SQL statement with the energy consumption value
        cursor.execute(sql_insert, (energy_consumption,))
        # Commit the transaction
        mydb.commit()
        print("Energy consumption data inserted successfully.")
        cursor.fetchall()
    except Exception as e:
        print("Error inserting energy consumption data:", e)

def update_distance(cursor, distance):
    try:
        # SQL statement to insert distance data
        cursor.execute("UPDATE Sensor_Availability SET Current_Distance = %s WHERE id = 1", (distance,))
        # Commit the transaction
        mydb.commit()
        cursor.fetchall()
        print("Distance data inserted successfully.")
    except Exception as e:
        print("Error inserting distance data:", e)

def arduino_data_receiver(cursor):
    # Default brightness level
    while True:
        try:
            # Read data from serial port
            serial_data = ser.readline().decode().strip()
            print("Received from Arduino:", serial_data)
            # Handle the received data
            if serial_data in ("relay_on", "level2_on", "level3_on", "all_off"):
                # Handle control signals
                if serial_data == "relay_on":
                    update_led_status(1, 1)
                elif serial_data == "level2_on":
                    update_led_status(1, 2)
                elif serial_data == "level3_on":
                    update_led_status(1, 3)
                elif serial_data == "all_off":
                    update_led_status(0, 0)
                # Emit socketio event
                socketio.emit('data_update', {'data': 'new data'})
            elif serial_data.startswith("Energy consumed:"):
                # Extract energy consumption value from serial data
                energy_consumption = float(serial_data.split(":")[1].strip().split()[0])
                
                # Insert energy consumption data into the database
                insert_energy_consumption(cursor, energy_consumption)
            elif serial_data.startswith("Distance:"):
                # Extract distance value from serial data
                distance_str = serial_data.split(":")[1].strip()
                distance = int(distance_str.split()[0])  # Extract only the distance value
                update_distance(cursor,distance)
            else:
                # Extract and process LDR data
                if serial_data.startswith("Voltage:"):
                    # Extract the light condition from the serial data
                    light_condition = serial_data.split("-")[1].strip()  # Extract only the light condition part
                
                    # Initialize level with a default value
                    # Perform actions based on the light condition
                    if light_condition == "Very dark":
                        update_led_status(1, 3)
                        brightness_level = 3
                        # Perform specific actions for very dark condition
                    elif light_condition == "Dark":
                        update_led_status(1, 2)
                        brightness_level = 2
                        # Perform specific actions for dark condition
                    elif light_condition == "Not enough Light":
                        update_led_status(1, 1)
                        brightness_level = 1
                        # Perform specific actions for not enough light condition
                    elif light_condition == "Bright":
                        update_led_status(0, 0)
                        brightness_level = 0
                        # Perform specific actions for bright condition
                    insert_lighting_data(cursor, light_condition, brightness_level)
             
        except Exception as e:
            print("Error:", e)


# Start a new thread to receive data from Arduino
arduino_thread = threading.Thread(target=arduino_data_receiver, args=(cursor,))
arduino_thread.daemon = True
arduino_thread.start()

def milliseconds_to_minutes(milliseconds):
    return milliseconds / (1000 * 60)  # Convert milliseconds to minutes

@app.route("/")
def index():
    try:
        # Create a cursor for executing SQL queries
        cursor = mydb.cursor()
        # Fetch LED status data from the database
        cursor.execute("SELECT Relay_Status, Brightness_Level FROM LED_Status WHERE id = 1;")
        led_row = cursor.fetchone()
        led_status = (led_row[0], led_row[1])

        # Fetch button value from the Sensor_Availability table
        cursor.execute("SELECT Button, IR, LDR, LDR_Duration, Ultrasonic, Ultrasonic_Duration, Ultrasonic_Distance, Current_Distance FROM Sensor_Availability WHERE id = 1;")
        sensor_row = cursor.fetchone()
        button_value = sensor_row[0]
        ir_available = sensor_row[1]
        ldr_available = sensor_row[2]
        ldr_duration = sensor_row[3]
        ultrasonic_available = sensor_row[4]
        ultrasonic_duration = sensor_row[5]
        ultrasonic_distance = sensor_row[6]
        current_distance = sensor_row[7]

        # Fetch advanced automation data
        cursor.execute("SELECT Advance_Availability, Mean_Brightness FROM Advanced_Automation WHERE id = 1;")
        advanced_row = cursor.fetchone()
        advanced_available = advanced_row[0]
        mean_brightness = advanced_row[1]
        ser.write(b"b" + str(mean_brightness).encode() + b"\n")

        # Convert ldr_duration from milliseconds to minutes
        ldr_duration_minutes = milliseconds_to_minutes(ldr_duration)
        ultrasonic_duration_minutes = milliseconds_to_minutes(ultrasonic_duration)
        
        # Close the cursor after executing all queries
        cursor.close()
        # Render the index template with LED status data, button value, and IR availability status
        return render_template('index.html', led_status=led_status, button_value=button_value, ir_available=ir_available,
                               ldr_available=ldr_available, ldr_duration=ldr_duration_minutes,
                               ultrasonic_available=ultrasonic_available, ultrasonic_duration=ultrasonic_duration_minutes,
                               ultrasonic_distance=ultrasonic_distance, current_distance=current_distance,
                               advanced_available=advanced_available, mean=mean_brightness)
    except mysql.connector.Error as error:
        # Log the error and handle it appropriately
        app.logger.error(f"MySQL Error: {error}")
        # Optionally, return an error page or message to the user
        return "An error occurred while processing your request.", 500

# Define WebSocket event handler
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@app.route("/light")
def show_statistics():
    return render_template("light.html")

@app.route("/light", methods=["GET", "POST"])
def statistics():
    if request.method == "POST":
        # Get selected date from form data
        selected_date = request.form.get("selected_date")
        # Query the database for data on the selected date
        cursor.execute("SELECT timestamp, brightness_level FROM Lighting_Data WHERE DATE(timestamp) = %s ORDER BY timestamp ASC", (selected_date,))
        data = cursor.fetchall()
        timestamps = []
        brightness_levels = []
        for entry in data:
            timestamps.append(entry[0])  # Assuming the timestamp is in the first position of each tuple
            brightness_levels.append(entry[1])  # Assuming the brightness level is in the second position

        if data is not None:
            # Render template with data
            return render_template("light.html", timestamps=timestamps, brightness_levels=brightness_levels)
        else:
            # No data available for the selected date
            flash("No data available for the selected date", "warning")
            return render_template("light.html")
    else:
        # Render the form to choose the date
        return render_template("light.html")


@app.route("/fetch_data", methods=["POST"])
def fetch_data():
    selected_date = request.json.get("selected_date")

    # Query the database for data on the selected date
    cursor.execute("SELECT timestamp, brightness_level FROM Lighting_Data WHERE DATE(timestamp) = %s", (selected_date,))
    data = cursor.fetchall()
    timestamps = []
    brightness_levels = []
    for entry in data:
        timestamps.append(entry[0])  # Assuming the timestamp is in the first position of each tuple
        brightness_levels.append(entry[1])  # Assuming the brightness level is in the second position
    cursor.fetchall()
    return jsonify({"timestamps": timestamps, "brightnessLevels": brightness_levels})

@app.route("/energy")
def show_energy():
    return render_template("energy.html")

@app.route("/fetch_energy_data", methods=["POST"])
def fetch_energy_data():
    selected_month = request.json.get("selected_month")

    # Query the database for energy consumption data for the selected month
    cursor.execute("SELECT DATE(timestamp), SUM(Energy_Consumption) FROM Energy_Management WHERE MONTH(timestamp) = %s GROUP BY DATE(timestamp)", (selected_month,))
    energy_data = cursor.fetchall()

    # Extract timestamps and energy consumption
    timestamps = [entry[0] for entry in energy_data]
    energy_consumption = [entry[1] for entry in energy_data]
    cursor.fetchall()
    # Prepare the response
    response_data = {"timestamps": timestamps, "energy_consumption": energy_consumption}
    return jsonify(response_data)


@app.route("/fetch_energy_data", methods=["POST"])
def fetch_energy_data():
    try:
        db = mysql.connector.connect(host="ajksmarthomeapplicationdatabase.cgbowllugjv1.us-east-1.rds.amazonaws.com", user="admin", password="password", database="AJKSmartHomeApplication")
        cursor = db.cursor()

        selected_month = request.json.get("selected_month")

        cursor.execute("SELECT ParamValue FROM ParamTable WHERE ParamName = 'CurrentRoom';")
        currentRoom = cursor.fetchone()[0]

        if currentRoom == 1:
            cursor.execute("SELECT DATE(Date), SUM(EnergyConsumption) FROM EnergyDataRoom1 WHERE MONTH(Date) = %s GROUP BY DATE(Date)", (selected_month,))
        elif currentRoom == 2:
            cursor.execute("SELECT DATE(Date), SUM(EnergyConsumption) FROM EnergyDataRoom2 WHERE MONTH(Date) = %s GROUP BY DATE(Date)", (selected_month,))
        else:
            return jsonify({"error": "Invalid current room number"})

        energy_data = cursor.fetchall()
        timestamps = [entry[0] for entry in energy_data]
        energy_consumption = [entry[1] for entry in energy_data]

        response_data = {"timestamps": timestamps, "energy_consumption": energy_consumption}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})


def update_average_brightness(mean_brightness_level):
    try:
        # Update the Advanced_Automation table with the average brightness level
        cursor.execute("UPDATE Advanced_Automation SET Mean_Brightness = %s", (mean_brightness_level,))
        # Commit the transaction
        mydb.commit()
        cursor.fetchall()
        print("Average brightness level updated successfully.")
    except Exception as e:
        # Rollback the transaction in case of an error
        mydb.rollback()
        print("Error updating average brightness level:", e)


def calculate_mean_brightnessForAutomation():
    # Query the database for all brightness levels
    cursor.execute("SELECT brightness_level FROM Lighting_Data")
    data = cursor.fetchall()
    # Extract brightness levels from the fetched data
    brightness_levels = [entry[0] for entry in data]
    # Calculate the mean brightness level
    if brightness_levels:
        mean_brightness_level = sum(brightness_levels) / len(brightness_levels)
    else:
        mean_brightness_level = 0
    update_average_brightness(mean_brightness_level)
    return mean_brightness_level

# Define a function to continuously update the mean brightness level
def continuous_update():
    while True:
        mean_brightness_level = calculate_mean_brightnessForAutomation()
        time.sleep(600)  # Wait for 600 seconds before updating again

# Create a new thread for continuous updating
update_thread = threading.Thread(target=continuous_update)
# Start the thread
update_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)