import random
import string
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional

from app.game_state import GameState


def draw_letter() -> str:
    return random.choice(string.ascii_letters)


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
        return [c.category_name for c in self.categories]

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

    def fill_is_legit(self):
        for category in self.categories:
            if category.legit_score >= 0:
                category.is_legit = True

    def fill_is_unique(self):
        for category in self.categories:
            if category.word not in [c.word for c in self.categories if
                                     c.category_name == category.category_name and c.player_id != category.player_id]:
                category.is_unique = True

    def fill_is_only_word_in_category(self):
        for category in self.categories:
            if len([c for c in self.categories if
                    c.category_name == category.category_name and c.player_id != category.player_id]) == 0:
                category.is_only_word_in_category = True

    def fill_scores(self):
        for category in self.categories:
            if category.is_legit:
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


def count_overall_score(categories) -> int:
    return sum([c.score for c in categories])


def count_overall_legit_score(categories) -> int:
    return sum([c.legit_score for c in categories])


class Game:
    def __init__(self, custom_categories=None):
        self.game_state: GameState = GameState.lobby
        self.letter: str = draw_letter()
        self.categories: Categories = self.setup_categories(custom_categories)
        self.responses: dict = {}
        self.votes: dict = {}

    def get_current_state(self) -> dict:
        game_state = {}
        if self.game_state is GameState.lobby:
            pass
        elif self.game_state is GameState.completing:
            game_state["categories"] = self.categories.get_categories_names()  # todo do it once!
            game_state["letter"] = self.letter
        elif self.game_state is GameState.voting:
            game_state["candidates"] = self.get_voting_candidates()  # todo do it once!
        elif self.game_state is GameState.score_display:
            game_state["results"] = self.get_result()  # todo do it once!
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
        self.categories.fill_is_legit()
        self.categories.fill_is_only_word_in_category()
        self.categories.fill_is_unique()
        self.categories.fill_scores()

    def setup_categories(self, custom_categories=None) -> Categories:
        if custom_categories is None:
            custom_categories = ["Panstwa", "Miasta", "Rzeczy", "Zwierzeta", "Imie", "Rzecz"]
        categories = Categories()
        for category in custom_categories:
            c = Category(category)
            categories.append(c)
        return categories

    def get_voting_candidates(self):
        return self.categories.get_voting_candidates()

    def get_result(self) -> dict:
        player_oriented_categories = self.categories.get_player_oriented_categories()
        results = {}
        for player in player_oriented_categories:
            player_overall_score = count_overall_score(player_oriented_categories[player])
            player_results = []
            for category in player_oriented_categories[player]:
                player_results.append({'category_name': category.category_name,
                                       'score': category.score,
                                       'word': category.word})
            results[player] = {"results": player_results, "score": player_overall_score}
        return results

    def handle_complete(self, player_id, player_move):
        print(len(self.categories.categories))
        for category in player_move:
            new_category = Category(category)
            new_category.word = player_move[category]
            new_category.player_id = player_id
            self.categories.append(new_category)
        print(len(self.categories.categories))

    def handle_voting(self, player_id, first_player_voting):
        # todo check if player hasn't voted
        for category in first_player_voting:
            for word in first_player_voting[category]:
                items = [c for c in self.categories.categories if
                         c.category_name == category and c.word == word]
                for item in items:
                    if first_player_voting[category][word] is True:
                        item.legit_score += 1
                    elif first_player_voting[category][word] is False:
                        item.legit_score -= 1
        # todo player.has_voted = True
