from itertools import product

def generate_wordlist(
    max_number=10000,
    years=range(2020, 2026),
    min_suffixes=0,        # 👈 minimum number of suffixes
    max_suffixes=3,        # 👈 maximum number of suffixes
):
    base_words = [
        # generic
        "admin", "password", "root", "test",

        # MAV / UAV specific
        "drone", "uav", "mav", "mavlink",
        "mission", "planner", "ardupilot",
        "pixhawk", "sitl", "copilot",

        # human
        "user", "pilot", "operator",
    ]

    suffix_atoms = [
        "1", "12", "123", "!",
        "@", "#", "!!", "01"
    ]

    separators = ["", "_", "-", "."]

    wordlist = set()

    # ----------------------------
    # Base word variants
    # ----------------------------
    word_variants = set()
    for w in base_words:
        word_variants.add(w)
        word_variants.add(w.capitalize())
        word_variants.add(w.upper())

    # ----------------------------
    # Generate suffix combinations
    # ----------------------------
    suffixes = set()

    if min_suffixes == 0:
        suffixes.add("")

    for depth in range(max(1, min_suffixes), max_suffixes + 1):
        for combo in product(suffix_atoms, repeat=depth):
            suffixes.add("".join(combo))

    # ----------------------------
    # Apply suffixes to words
    # ----------------------------
    for w, s in product(word_variants, suffixes):
        wordlist.add(w + s)

    # ----------------------------
    # Year-based passwords
    # ----------------------------
    for w, y in product(word_variants, years):
        wordlist.add(f"{w}{y}")
        for s in suffixes:
            if s:
                wordlist.add(f"{w}{y}{s}")

    # ----------------------------
    # Joined words
    # ----------------------------
    for a, b, sep in product(base_words, base_words, separators):
        if a != b:
            wordlist.add(f"{a}{sep}{b}")
            wordlist.add(f"{a.capitalize()}{sep}{b}")

    # ----------------------------
    # Pure numeric passwords
    # ----------------------------
    for i in range(max_number):
        wordlist.add(str(i))

    return list(wordlist)
