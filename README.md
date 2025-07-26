A project submitted for SWE30011 IoT Programming — Semester 1, 2024
Developed by Jesse Ting Wen Kai | Student ID: 102769808

📘 Overview
This IoT-based Smart Lighting and Monitoring System is designed to automate lighting based on environmental inputs and user interaction. It combines hardware sensors, actuators, and a web dashboard to enable both manual and automated lighting control, along with real-time monitoring and statistics.

⚙️ Features
Four-level brightness control: 0 (OFF) to 3 (Maximum Brightness)

Multiple control interfaces:

Physical Button

Infrared Remote

Web Dashboard (Flask-based)

Sensors:

IR Sensor

Button

Light Dependent Resistor (LDR)

Ultrasonic Sensor

Automation Rules:

LDR auto-adjusts brightness based on ambient light

Ultrasonic sensor detects presence to turn lights on/off

Advanced automation adjusts initial brightness based on historical averages

Real-time Dashboard:

Control sensors and lighting remotely

Set sensor intervals and thresholds

View light condition trends and energy consumption stats

Data Analytics:

MariaDB stores real-time sensor and actuator data

Chart.js used for graphing energy and brightness over time

🖥️ System Architecture
The system architecture is based on a Microcontroller (Arduino Uno) and an Edge Device (Raspberry Pi):

Arduino handles sensor input, relay switching, and LED control.

Raspberry Pi hosts the dashboard (Flask server), manages database (MariaDB), and handles bi-directional serial communication.

🧪 Technologies Used
Backend
Python 3

Flask

MariaDB

Serial Communication

Socket.IO (Real-time sync)

Multithreading

Frontend
HTML, CSS, JavaScript

Chart.js (Graph rendering)

Hardware
Arduino Uno

Raspberry Pi

LDR Sensor

IR Receiver

Ultrasonic Sensor

12V Relay Module

LEDs & Light Bulb
