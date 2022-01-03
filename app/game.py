import random
import string
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional

from app.game_state import GameState


def count_overall_score(categories) -> int:
    return sum([c.score for c in categories])


class Categories:
    def __init__(self):
        self.categories: List[Category] = []

    def filter_by_category(self, name: str):
        filtered = filter(lambda category: category.category_name == name, self.categories)
        return list(filtered)

    def filter_by_player(self, player_id: str):
        filtered = filter(lambda category: category.player_id == player_id, self.categories)
        return list(filtered)

    def append(self, category):
        if isinstance(category, Category):
            self.categories.append(category)
        else:
            raise TypeError

    def get_categories_names(self) -> List[str]:
        seen = set()
        return [c.category_name for c in self.categories if not (c.category_name in seen or seen.add(c.category_name))]

    def get_voting_candidates(self) -> dict:
        groups = defaultdict(list)

        for category in self.categories:
            groups[category.category_name].append(category.word) \
                if category.word != '' and category.word not in groups[category.category_name] else ...
        return dict(groups)

    def group_categories_by_name(self) -> dict:
        groups = defaultdict(list)

        for category in self.categories:
            groups[category.category_name].append(category) \
                if category.word != '' and category.word not in groups[category.category_name] else ...
        return dict(groups)

    def get_player_oriented_categories(self):
        groups = defaultdict(list)

        for category in self.categories:
            if hasattr(category, 'player_id'):
                groups[category.player_id].append(category)
        return dict(groups)

    def fill_is_legit(self, letter: str):
        for category in self.categories:
            if category.legit_score >= 0:
                category.is_legit = True
                try:
                    first_letter = category.word[0]
                except Exception as e:
                    first_letter = ""
                if first_letter != letter:
                    category.is_legit = False

    def fill_is_unique(self):
        for category in self.categories:
            if category.word not in [c.word for c in self.categories if
                                     c.category_name == category.category_name and c.player_id != category.player_id]:
                category.is_unique = True

    def fill_is_only_word_in_category(self):
        for category in self.categories:
            other_legit = [c.is_legit for c in self.categories if
                           c.category_name == category.category_name and c.player_id != category.player_id]
            if not any(other_legit):
                category.is_only_word_in_category = True

    def fill_scores(self):
        for category in self.categories:
            if category.word == "":
                category.score = 0

            elif category.is_legit:
                if category.is_only_word_in_category is True:
                    category.score = 15
                elif category.is_unique is True:
                    category.score = 10
                else:
                    category.score = 5

    def filter_empty(self):
        self.categories = list(filter(lambda c: c.player_id, self.categories))


@dataclass
class Category:
    def __init__(self, category_name):
        self.category_name: str = category_name
        self.word: str = ''
        self.player_id: Optional[str] = None
        self.is_unique: bool = False
        self.legit_score: int = 0
        self.is_legit: bool = False
        self.is_only_word_in_category: bool = False
        self.score: int = 0


def count_overall_legit_score(categories) -> int:
    return sum([c.legit_score for c in categories])


def setup_letters():
    letters = string.ascii_lowercase
    letters = letters.replace("v", "").replace("x", "").replace("q", "").replace("y", "")
    return letters


class Game:
    def __init__(self, custom_categories=None):
        self.letters = setup_letters()
        self.last_letter = None
        self.custom_categories = custom_categories
        self.game_state: GameState = GameState.lobby
        self.letter: str = self.draw_letter()
        self.temporary_categories = {}
        self.categories: Categories = self.setup_categories()
        self.responses: dict = {}
        self.votes: dict = {}

    def get_current_state(self, player_nicks=None) -> dict:
        game_state = {}
        if self.game_state is GameState.lobby:
            pass
        elif self.game_state is GameState.completing:
            game_state["categories"] = self.categories.get_categories_names()
            game_state["letter"] = self.letter
        elif self.game_state is GameState.voting:
            game_state["candidates"] = self.get_voting_candidates()
        elif self.game_state is GameState.score_display:
            game_state["results"] = self.get_result(player_nicks)
        return game_state

    def summary_completing(self) -> dict:
        name_oriented_categories_words = {}
        for category in self.setup_categories().categories:
            name_oriented_categories_words[category.category_name] = \
                list(filter(None, set(map(lambda c: c.word,
                                          self.categories.filter_by_category(category.category_name)))))
        return name_oriented_categories_words

    def summary_voting(self):
        self.categories.filter_empty()
        print("summary voting", self.categories)
        self.count_votes()
        self.categories.fill_is_unique()
        self.categories.fill_is_legit(self.letter)
        self.categories.fill_is_only_word_in_category()
        self.categories.fill_scores()

    def setup_categories(self) -> Categories:
        if self.custom_categories is None:
            custom_categories = ["Country", "City", "Item", "Animal", "Plant", "Name"]
        else:
            custom_categories = self.custom_categories
        categories = Categories()
        for category in custom_categories:
            c = Category(category)
            categories.append(c)
        return categories

    def get_voting_candidates(self):
        return self.categories.get_voting_candidates()

    def get_result(self, player_nicks: dict) -> dict:
        player_oriented_categories = self.categories.get_player_oriented_categories()
        results = {}
        for player in player_oriented_categories:
            player_overall_score = count_overall_score(player_oriented_categories[player])
            player_results = []
            for category in player_oriented_categories[player]:
                player_results.append({'category_name': category.category_name,
                                       'score': category.score,
                                       'word': category.word})
            try:
                results[player_nicks[player]] = {"results": player_results, "score": player_overall_score}
            except KeyError:
                pass
        return results

    def handle_complete(self, player_id, player_move: dict):
        for category in player_move:
            new_category = Category(category)
            players_word: str = player_move[category].strip(' ').strip('\u200b').strip(' ').lower()
            try:
                new_category.word = players_word if players_word[0] == self.letter else ""
            except IndexError:
                new_category.word = ""
            new_category.word = players_word
            new_category.player_id = player_id
            self.categories.append(new_category)

    def count_votes(self):
        for player in self.votes:
            for p_category in self.votes[player]:
                for word in self.votes[player][p_category]:
                    try:
                        voting = self.votes[player][p_category][word]  # TypeError
                        for category in self.categories.categories:
                            if category.word == word and category.category_name == p_category:
                                if voting is True:
                                    category.legit_score += 1
                                    print(word, "is legit")
                                if voting is False:
                                    category.legit_score -= 1
                                    print(word, "is not legit")
                    except (TypeError, KeyError):
                        pass

    def build_full_categories(self):
        for client_id in self.temporary_categories:
            self.handle_complete(client_id, self.temporary_categories[client_id])  # todo cut this line

    def draw_letter(self) -> str:
        drawn_letter = random.choice(self.letters)
        while drawn_letter == self.last_letter:
            drawn_letter = random.choice(self.letters)
        self.last_letter = drawn_letter
        return drawn_letter
