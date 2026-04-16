"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs, DEFAULT_WEIGHTS

# ---------------------------------------------------------------------------
# User profiles for stress-testing
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "valence": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "valence": 0.45,
    },
    # Adversarial: conflicting preferences — very high energy but a sad, low-valence mood.
    # Tests whether the system handles contradictory signals gracefully.
    "Adversarial (High-Energy + Sad)": {
        "genre": "metal",
        "mood": "sad",
        "energy": 0.90,
        "valence": 0.20,
    },
}

# Experiment weights: genre halved (1.0), energy doubled (4.0)
EXPERIMENT_WEIGHTS = {
    "genre": 1.0,
    "mood": 1.0,
    "energy": 4.0,
    "valence": 1.0,
}


def print_recommendations(label: str, user_prefs: dict, songs: list, weights=None) -> None:
    """Print a formatted recommendation block for one user profile."""
    w = weights or DEFAULT_WEIGHTS
    max_score = w["genre"] + w["mood"] + w["energy"] + w["valence"]

    print(f"\n{'=' * 60}")
    print(f"  Profile: {label}")
    print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}  valence={user_prefs['valence']}")
    if weights:
        print(f"  [EXPERIMENT weights: genre={w['genre']} mood={w['mood']} "
              f"energy={w['energy']} valence={w['valence']}]")
    print(f"{'=' * 60}\n")

    recs = recommend_songs(user_prefs, songs, k=5, weights=w)
    for rank, (song, score, reasons) in enumerate(recs, start=1):
        print(f"  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"       Score: {score:.2f} / {max_score:.1f}")
        for reason in reasons:
            print(f"         * {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # --- Step 1: Stress test with all four profiles ---
    for label, prefs in PROFILES.items():
        print_recommendations(label, prefs, songs)

    # --- Step 3: Experiment — halve genre weight, double energy weight ---
    print("\n" + "#" * 60)
    print("  EXPERIMENT: genre weight 2.0->1.0  |  energy weight 2.0->4.0")
    print("  Testing profile: Deep Intense Rock")
    print("#" * 60)
    print_recommendations(
        "Deep Intense Rock  [DEFAULT weights]",
        PROFILES["Deep Intense Rock"],
        songs,
    )
    print_recommendations(
        "Deep Intense Rock  [EXPERIMENT weights]",
        PROFILES["Deep Intense Rock"],
        songs,
        weights=EXPERIMENT_WEIGHTS,
    )


if __name__ == "__main__":
    main()
