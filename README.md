# 💡 Smart Lighting and Monitoring System

> **Course**: SWE30011 - IoT Programming (Semester 1, 2024)  
> **Author**: Jesse Ting Wen Kai  
> **Student ID**: 102769808

---


## 📘 Overview

This IoT project demonstrates a **Smart Lighting and Monitoring System** that integrates Arduino and Raspberry Pi to control lighting levels based on sensor inputs and user interactions.

It features real-time control, sensor-based automation, and energy tracking — all accessible through a Flask-powered web dashboard.

---

## ⚙️ Features

- 🔘 **Manual Controls**:
  - Button (digital)
  - IR remote (analog)
  - Web dashboard

- 📡 **Sensor Automation**:
  - **LDR sensor**: adjusts brightness based on light intensity
  - **Ultrasonic sensor**: detects presence to turn light on/off
  - **Advanced automation**: uses average historical brightness data

- 📊 **Monitoring Dashboard**:
  - Toggle sensor states
  - Modify detection thresholds
  - View energy usage and light condition graphs

---

## 🧠 System Architecture

- **Microcontroller**: Arduino Uno
- **Edge Device**: Raspberry Pi
- **Communication**: Serial (USB)
- **Web Server**: Flask
- **Database**: MariaDB
- **Frontend**: HTML, CSS, JavaScript (Chart.js)


---

## 🗺️ System Flow

```
User Input / Sensor Trigger
        ↓
    Arduino Logic
        ↓
  Serial Communication
        ↓
 Raspberry Pi (Flask + DB)
        ↓
 Web Dashboard (Live Sync)
```

---



---

## 📦 Technologies Used

### ➤ Arduino
- `IRremote.h`
- Digital and analog I/O
- Relay control

### ➤ Raspberry Pi (Python)
- Flask
- `serial`
- `mysql.connector`
- `threading`
- `socket.io`
- Chart.js for graphs

### ➤ Web
- HTML/CSS/JS
- Flask templates
- Live sensor/LED status updates via WebSocket

---

## 🧪 Sensors & Actuators

| Type         | Component         | Functionality                                  |
|--------------|-------------------|-----------------------------------------------|
| Input        | IR Receiver       | Remote control for toggle/brightness          |
| Input        | Button            | Physical toggle with cyclic brightness levels |
| Input        | LDR               | Auto-adjust brightness based on light         |
| Input        | Ultrasonic        | Detects presence and toggles lights           |
| Output       | Relay             | Controls 12V LED light bulb                   |
| Output       | Red/Blue LEDs     | Simulate brightness levels (Level 2, 3)       |

---




