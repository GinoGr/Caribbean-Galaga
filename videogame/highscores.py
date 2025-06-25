"""
Handle the logic behind saving highscores inspired by:
https://stackoverflow.com/questions/16726354/saving-the-highscore-for-a-game?
"""

import pickle
from pathlib import Path

SCORE_FILE = "highscores.pkl"
MAX_SCORES = 5


def load_highscores():
    """Get scores from pickle file"""
    if Path(SCORE_FILE).exists():
        with open(SCORE_FILE, "rb") as scores:
            return pickle.load(scores)
    return []


def save_highscores(highscores):
    """Save scores to pickle file"""
    with open(SCORE_FILE, "wb") as scores:
        pickle.dump(highscores, scores)


def add_score(name, score):
    """Append new score to pickle"""
    scores = load_highscores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    save_highscores(scores[:MAX_SCORES])
