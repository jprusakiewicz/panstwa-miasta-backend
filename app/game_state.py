from enum import Enum


class GameState(Enum):
    lobby = "LOBBY"
    completing = "COMPLETING"
    voting = "VOTING"
    score_display = "SCORE_DISPLAY"
