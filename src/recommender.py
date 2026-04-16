import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a single song and all its numeric/categorical attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Stores a listener's taste preferences used by the OOP Recommender class."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP recommender that scores Song dataclass objects against a UserProfile."""

    def __init__(self, songs: List[Song]):
        """Initialize with a list of Song objects to recommend from."""
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Return a numeric score for one Song against a UserProfile."""
        score = 0.0

        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.0

        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        score += energy_sim * 2.0

        if user.likes_acoustic:
            score += song.acousticness * 0.5
        else:
            score += (1.0 - song.acousticness) * 0.5

        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given UserProfile."""
        scored = [(song, self._score_song(user, song)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-English sentence explaining why a Song was recommended."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({user.favorite_genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({user.favorite_mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff < 0.15:
            reasons.append(f"energy is very close to your target ({user.target_energy})")
        elif energy_diff < 0.30:
            reasons.append(f"energy is near your target ({user.target_energy})")

        if user.likes_acoustic and song.acousticness > 0.7:
            reasons.append("strong acoustic feel you prefer")
        elif not user.likes_acoustic and song.acousticness < 0.3:
            reasons.append("electronic/produced sound you prefer")

        if not reasons:
            reasons.append("overall vibe aligns with your profile")

        return "Recommended because it " + " and ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Functional API (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


# Default scoring weights — change these to run experiments.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": 2.0,   # flat bonus for an exact genre match
    "mood": 1.0,    # flat bonus for an exact mood match
    "energy": 2.0,  # max points available from energy proximity
    "valence": 1.0, # max points available from valence proximity
}


def score_song(
    user_prefs: Dict, song: Dict, weights: Dict[str, float] = DEFAULT_WEIGHTS
) -> Tuple[float, List[str]]:
    """Score one song dict against user_prefs; return (total_score, reasons_list).

    Pass a custom weights dict to run experiments without changing the defaults.
    Max possible score = weights['genre'] + weights['mood'] + weights['energy'] + weights['valence'].
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song["genre"] == user_prefs.get("genre", ""):
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match (+{pts:.1f})")

    # Mood match
    if song["mood"] == user_prefs.get("mood", ""):
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match (+{pts:.1f})")

    # Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_pts = round((1.0 - abs(song["energy"] - target_energy)) * weights["energy"], 2)
    score += energy_pts
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    # Valence proximity
    target_valence = user_prefs.get("valence", 0.5)
    valence_pts = round((1.0 - abs(song["valence"] - target_valence)) * weights["valence"], 2)
    score += valence_pts
    reasons.append(f"valence proximity (+{valence_pts:.2f})")

    return round(score, 2), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Dict[str, float] = DEFAULT_WEIGHTS,
) -> List[Tuple[Dict, float, List[str]]]:
    """Score every song, sort highest-to-lowest, and return the top-k results.

    Pass a custom weights dict to run scoring experiments without mutating defaults.
    sorted() is used so the original songs list is never modified.
    """
    scored = [
        (song, *score_song(user_prefs, song, weights))
        for song in songs
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
