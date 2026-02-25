import time
import os
import hashlib

# 1. Force MAVLink 2.0 (Required for signatures)
os.environ["MAVLINK20"] = "1"
from pymavlink import mavutil

# 2. Boot up the Mock Drone (System ID 1)
print("[BOOT] Starting Mock Drone...")
drone = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=1, source_component=1)

# ====================================================================
# --- THE MAVLINK PASSWORD ---
# You can change your 32-byte password right here!
#SECRET_KEY = b"password123456789012345678901234"

# --- THE GCS HASHING MECHANISM (From the Academic Paper) ---

# 1. A normal human password (must be inside your words.py wordlist!)
HUMAN_PASSWORD = "ardupilot"

# 2. Hash the password with SHA-256 to create the 32-byte MAVLink key
SECRET_KEY = hashlib.sha256(HUMAN_PASSWORD.encode('utf-8')).digest()



# --- THE REPORTING FIREWALL ---
# This function catches packets right before pymavlink drops them.
def catch_unsigned(mav, msgId):
    # Message ID 76 is COMMAND_LONG
    if msgId == mavutil.mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
        print(f"\n[INCOMING] Attack Detected! (Command ID: {msgId})")
        print(" -> [FIREWALL BLOCKED] WARNING: Dropped unsigned and wrong password attack packet!")
        print(" -> [DRONE STATE] Drone ignoring attack and flying safely.")
        print("-----------------------------------------------------")
        return False # 'False' tells pymavlink to destroy the packet!
    
    return True # Allow harmless unsigned things (like QGC pings) through


# Give the password to the drone so it can mathematically verify attackers
drone.setup_signing(SECRET_KEY, sign_outgoing=False, allow_unsigned_callback=catch_unsigned)
print(f"[SECURITY] Drone locked with key: {HUMAN_PASSWORD}")
# ====================================================================

print("[BOOT] Drone is airborne and broadcasting heartbeats.")
print("-----------------------------------------------------")

last_heartbeat = 0

# 3. The Drone's Main Brain Loop
while True:
    current_time = time.time()
    
    # --- A. SEND HEARTBEATS ---
    if current_time - last_heartbeat > 1.0:
        drone.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_PX4,
            0, 0, 0
        )
        last_heartbeat = current_time

    # --- B. LISTEN FOR ATTACKS & FIREWALL ---
    msg = drone.recv_match(blocking=False)
    
    # Because our callback destroys unsigned and wrong password commands, ONLY signed ones with right password make it here!
    if msg and msg.get_type() == 'COMMAND_LONG':
        print(f"\n[INCOMING] Received Command ID: {msg.get_msgId()} from System {msg.get_srcSystem()}")
        print(" -> [FIREWALL PASSED] Cryptographic signature matches the password!")
        print(" -> [DRONE STATE] Executing Disarm. Drone Crashing!")
        print("-----------------------------------------------------")
            
    time.sleep(0.01)
