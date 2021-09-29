import asyncio
import json
import os
import random
import threading
import uuid
from datetime import datetime, timedelta
from typing import List

import requests

from .connection import Connection
from .game import Game
from .game_state import GameState


def get_timeout():
    try:
        timeout = float(os.path.join(os.getenv('TIMEOUT_SECONDS')))
    except TypeError:
        timeout = 20  # if theres no env var
    return timeout


class Room:
    def __init__(self, room_id: str, max_players: int = 8):
        self.full_results = []
        self.short_results = None
        self.id = room_id
        self.active_connections: List[Connection] = []
        self.game: Game = Game()
        self.number_of_players = max_players
        self.game_id: str
        self.timeout = get_timeout()
        self.timer = threading.Timer(self.timeout, self.handle_timeout)

    def handle_timeout(self):
        asyncio.run(self.next_stage())

    async def append_connection(self, connection):
        self.active_connections.append(connection)
        self.export_room_status()
        if len(self.active_connections) >= 2 and self.game.game_state is GameState.lobby:
            await self.start_game()
        await connection.ws.send_text(self.get_game_state(connection.player.id))

    def get_taken_ids(self):
        taken_ids = [connection.player.id for connection in self.active_connections]
        return taken_ids

    def get_player(self, id):
        player = next(
            connection.player for connection in self.active_connections if connection.player.id == id)
        return player

    def get_players_in_game_ids(self) -> List[str]:
        taken_ids = [connection.player.id for connection in self.active_connections]
        return taken_ids

    async def remove_connection(self, connection_with_given_ws):
        self.active_connections.remove(connection_with_given_ws)
        self.export_room_status()
        if len(self.get_players_in_game_ids()) <= 1:
            await self.end_game()

    async def broadcast_json(self):
        for connection in self.active_connections:
            await connection.ws.send_text(
                self.get_game_state(connection.player.id))

    async def restart_game(self):
        self.export_score()
        await self.start_game()

    async def start_game(self):
        self.game = Game()
        self.game.game_state = GameState.completing
        self.game_id = str(uuid.uuid4().hex)
        self.restart_timer()
        await self.broadcast_json()

    async def end_game(self):
        self.timer.cancel()
        self.export_score()
        self.game = Game()
        await self.broadcast_json()

    async def restart_or_end_game(self):
        if len(self.active_connections) >= 2:
            await self.restart_game()
        else:
            await self.end_game()

    def handle_players_move(self, client_id, player_move):
        print(player_move, " ", self.game.game_state)
        if self.game.game_state is GameState.lobby or self.game.game_state is GameState.score_display:
            pass  # do nothing
        elif self.game.game_state is GameState.completing:
            self.game.handle_complete(client_id, player_move)
        elif self.game.game_state is GameState.voting:
            self.game.votes[client_id] = player_move["votes"]

    def get_timestamp(self, delta=2):
        t = self.timestamp - timedelta(0, delta)
        return t.isoformat()

    def get_game_state(self, client_id) -> str:
        if self.game.game_state is GameState.lobby:
            game_state = dict(game_state=self.game.game_state.value)
        elif self.game.game_state is GameState.completing:
            game_state = dict(game_state=self.game.game_state.value, nicks=self.get_enemies_nicks(client_id),
                              timestamp=self.get_timestamp(), game_data=self.game.get_current_state())
        elif self.game.game_state is GameState.voting:
            game_state = dict(game_state=self.game.game_state.value, nicks=self.get_enemies_nicks(client_id),
                              timestamp=self.get_timestamp(), game_data=self.game.get_current_state())
        elif self.game.game_state is GameState.score_display:
            game_state = dict(game_state=self.game.game_state.value, nicks=self.get_enemies_nicks(client_id),
                              timestamp=self.get_timestamp(), game_data=self.game.get_current_state())
        else:
            raise ValueError
        return json.dumps(game_state)

    def get_enemies_nicks(self, player_id):
        return [connection.player.nick for connection in self.active_connections
                if connection.player.id is not player_id]

    def draw_random_player_id(self):
        return random.choice(self.get_players_in_game_ids())

    @property
    def get_stats(self):
        if self.game.game_state == GameState.lobby:
            stats = {'game_state': self.game.game_state,
                     "number_of_players": self.number_of_players,
                     "number_of_connected_players": len(self.active_connections)}
        else:
            stats = {'game_state': self.game.game_state,
                     "number_of_players": self.number_of_players,
                     "number_of_connected_players": len(self.active_connections)}
        return stats

    async def remove_player_by_id(self, id):
        connection = next(
            connection for connection in self.active_connections if connection.player.id == id)
        await self.remove_connection(connection)

    async def kick_player(self, player_id):  # probably have to leave this
        await self.remove_player_by_id(player_id)
        self.export_room_status()

    def export_score(self):
        try:
            result = requests.post(url=os.getenv('EXPORT_RESULTS_URL'),
                                   json=dict(roomId=self.id, results=self.short_results))
            if result.status_code == 200:
                print("export succesfull")
            else:
                print("export failed: ", result.text, result.status_code)
                print(self.short_results)
        except (KeyError, requests.exceptions.MissingSchema):
            print("failed to get EXPORT_RESULT_URL env var")

    def export_room_status(self):
        try:
            result = requests.post(
                url=os.path.join(os.getenv('EXPORT_RESULTS_URL'), "rooms/update-room-status"),
                json=dict(roomId=self.id, activePlayers=self.get_players_in_game_ids()))
            if result.status_code == 200:
                print("export succesfull")
            else:
                print("export failed: ", result.text, result.status_code)
        except Exception as e:
            print(e.__class__.__name__)
            print("failed to get EXPORT_RESULTS_URL env var")

    def restart_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.handle_timeout)
        self.timer.start()
        self.timestamp = datetime.now() + timedelta(0, self.timeout)

    async def next_stage(self):
        if self.game.game_state is GameState.lobby:
            await self.start_game()
        elif self.game.game_state is GameState.completing:
            self.game.summary_completing()  # przelicz to co dostałeś
            self.game.game_state = GameState.voting
            self.restart_timer()
            await self.broadcast_json()
        elif self.game.game_state is GameState.voting:
            self.game.summary_voting()
            self.game.game_state = GameState.score_display
            self.restart_timer()
            await self.broadcast_json()
        elif self.game.game_state is GameState.score_display:
            await self.restart_or_end_game()
