# EcoSense Edge Layer 🏭

This repository contains the IoT logic for the EcoSense Air Quality System.

## Contents
- **Python Simulation**: Generates realistic CO2, PM2.5, and Temperature data with pollution scenarios.
- **Node-RED Flows**: Handles MQTT aggregation, AI inference (HuggingFace), and MongoDB storage.

## How to run
1. Install Python dependencies: `pip install paho-mqtt`
2. Run simulation: `python smart_sensors.py`
3. Import `node-red-flows.json` into your Node-RED instance.
