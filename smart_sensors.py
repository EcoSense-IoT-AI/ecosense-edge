import paho.mqtt.client as mqtt
import json
import time
import random
import math

# --- CONFIGURATION ---
HOST = "localhost" 
PORT = 1883
TOPIC_PREFIX = "AirQuality"

# --- ETAT INITIAL ---
sensors_state = { "co2": 420.0, "pm25": 10.0, "temp": 22.0, "hum": 50.0 }
cycle_pos = 0 
scenario = "NORMAL"

def generate_smart_values(current_state, mode, spike=False):
    new_state = {}
    
    # --- 1. DÉFINITION DES CIBLES (TARGETS) ---
    if mode == "POLLUTION_EVENT":
        # Cibles très hautes (Incendie / Embouteillage)
        target_co2 = 1800 + random.randint(-100, 100)
        target_pm25 = 450 + random.randint(-50, 50)
    elif spike:
        # Pic temporaire (ex: un camion passe)
        target_co2 = 600
        target_pm25 = 150 # Pic soudain de poussière
    else:
        # Retour à la normale (Air pur)
        target_co2 = 420 + random.randint(-20, 20)
        target_pm25 = 10 + random.randint(-2, 5)

    # --- 2. CALCUL AVEC INERTIE (SMOOTHING) ---
    
    # CO2 : Monte doucement, descend doucement
    diff_co2 = target_co2 - current_state["co2"]
    # Si pollution, on monte vite (0.2), sinon on ajuste doucement (0.1)
    rate_co2 = 0.2 if mode == "POLLUTION_EVENT" else 0.1
    new_state["co2"] = current_state["co2"] + (diff_co2 * rate_co2) + random.uniform(-5, 5)

    # PM2.5 : Monte TRÈS vite (fumée), descend moyennement
    diff_pm25 = target_pm25 - current_state["pm25"]
    rate_pm25 = 0.4 if diff_pm25 > 0 else 0.1 
    new_state["pm25"] = current_state["pm25"] + (diff_pm25 * rate_pm25) + random.uniform(-2, 2)

    # Température : Cycle sinusoïdal plus rapide (pour voir la courbe bouger)
    # On divise par 5 au lieu de 10 pour accélérer l'onde
    base_temp = 24 + (3 * math.sin(cycle_pos * 0.2)) 
    new_state["temp"] = base_temp + random.uniform(-0.1, 0.1)

    # Humidité : Opposée à la température
    target_hum = 50 - (new_state["temp"] - 24) * 3
    new_state["hum"] = current_state["hum"] + ((target_hum - current_state["hum"]) * 0.1)

    return {k: round(v, 2) for k, v in new_state.items()}

# --- CONNEXION MQTT ---
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
try:
    client.connect(HOST, PORT, 60)
    print(f"✅ Simulation SMART connectée sur {HOST}")
except Exception:
    print("❌ Erreur Mosquitto (Vérifie qu'il est lancé !)")
    exit()

print("🚀 Simulation active : Cycle court (45s) + Pics aléatoires")

try:
    while True:
        cycle_pos += 1
        position_in_cycle = cycle_pos % 20
        
        is_spike = False

        if position_in_cycle > 14: 
            scenario = "POLLUTION_EVENT"
            print(f"\n⚠️  ALERTE MAXIMALE (Incendie/Fumée)...")
            
        else:
            scenario = "NORMAL"
            if random.random() < 0.2:
                is_spike = True
                print(f"\n🚚  Event: Pic passager (Camion)")
            else:
                print(f"\n🌱  Status: Normal")

        # Génération
        sensors_state = generate_smart_values(sensors_state, scenario, is_spike)
        timestamp = time.time()

        # Envoi
        for sensor, val in sensors_state.items():
            topic = f"{TOPIC_PREFIX}/{sensor}"
            payload = {
                "value": val,
                "sensor_id": f"sim_{sensor}",
                "timestamp": timestamp
            }
            client.publish(topic, json.dumps(payload))
            print(f"   📡 {sensor.upper().ljust(5)} : {str(val)}")
            time.sleep(0.05) 

        time.sleep(20.0) 

except KeyboardInterrupt:
    print("\n🛑 Arrêt des capteurs.")
    client.disconnect()

