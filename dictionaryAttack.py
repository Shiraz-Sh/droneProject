import hashlib
import struct
import multiprocessing as mp

def sha256(b):
    return hashlib.sha256(b).digest()

def compute_sig(password, header, payload, crc, link_id, timestamp):
    key = sha256(password.encode())
    mac = sha256(key + header + payload + crc + link_id + timestamp)
    return mac[:6]

def worker(args):
    password, fields, target = args
    sig = compute_sig(password, *fields)
    if sig == target:
        return password
    return None

def dictionary_attack(
    wordlist, header, payload, crc, link_id, timestamp, target_sig
):
    fields = (header, payload, crc, link_id, timestamp)
    with mp.Pool(mp.cpu_count()) as pool:
        for result in pool.imap_unordered(
            worker,
            [(w, fields, target_sig) for w in wordlist],
            chunksize=1000,
        ):
            if result:
                pool.terminate()
                return result
    return None
