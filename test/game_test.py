import unittest

from app.game import Category, Game
from app.game_state import GameState


class TestGame(unittest.TestCase):
    def test_completing_summary(self):
        game = Game(["one", "two", "three"])
        c1 = Category(category_name="one")
        c1.word = 'a'
        c2 = Category(category_name="one")
        c2.word = 'a'
        c3 = Category(category_name="two")
        c3.word = 'b'
        c4 = Category(category_name="two")
        c4.word = 'c'
        c5 = Category(category_name="three")
        c5.word = 'd'

        game.categories.categories = []
        game.categories.append(c1)
        game.categories.append(c2)
        game.categories.append(c3)
        game.categories.append(c4)
        game.categories.append(c5)


        completing_summary = game.summary_completing()
        self.assertEqual(['a'], completing_summary['one'])
        self.assertIn('b', completing_summary['two'])
        self.assertIn('c', completing_summary['two'])
        self.assertEqual(['d'], completing_summary['three'])

    def test_getting_completing_state(self):
        expected_categories = ['first', 'second', 'third']
        game = Game()
        game.categories = game.setup_categories(expected_categories)
        game.game_state = GameState.completing
        current_state = game.get_current_state()
        self.assertEqual(expected_categories, current_state["categories"])

    def test_getting_voting_state(self):
        category1_1 = Category(category_name="first_category")
        category2_1 = Category(category_name="second_category")
        category3_1 = Category(category_name="third_category")

        category1_2 = Category(category_name="first_category")
        category2_2 = Category(category_name="second_category")
        category3_2 = Category(category_name="third_category")

        category1_3 = Category(category_name="first_category")
        category2_3 = Category(category_name="second_category")
        category3_3 = Category(category_name="third_category")

        category1_1.word = "first_word"
        category2_1.word = "first_word"
        category3_1.word = "first_word"

        category1_2.word = "second_word"
        category2_2.word = "second_word"
        category3_2.word = "second_word"

        category1_3.word = "second_word"
        category2_3.word = "first_word"
        category3_3.word = "third_word"

        expected_voting_state = {'first_category': ['first_word', 'second_word'],
                                 "second_category": ["first_word", "second_word"],
                                 "third_category": ["first_word", "second_word", "third_word"]}
        game = Game()

        game.categories.append(category1_1)
        game.categories.append(category2_1)
        game.categories.append(category3_1)
        game.categories.append(category1_2)
        game.categories.append(category2_2)
        game.categories.append(category3_2)
        game.categories.append(category1_3)
        game.categories.append(category2_3)
        game.categories.append(category3_3)

        game.game_state = GameState.voting

        current_state = game.get_current_state()
        self.assertEqual(expected_voting_state, current_state["candidates"])

    def test_getting_score_display_state(self):
        # given
        expected_results = {
            'player_1': {'results': [{'category_name': 'first_category', 'word': 'faaa', 'score': 0},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'fsecond_word', 'score': 10}],
                         "score": 15},
            'player_2': {'results': [{'category_name': 'first_category', 'word': 'first_word', 'score': 5},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'first_word', 'score': 10}],
                         "score": 20},
            'player_3': {'results': [{'category_name': 'first_category', 'word': 'first_word', 'score': 5},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'fthird_word', 'score': 10},
                                     {'category_name': 'fourth_category', 'word': 'fourth_word', 'score': 15}],
                         "score": 35}}

        category1_1 = Category(category_name="first_category")
        category2_1 = Category(category_name="first_category")
        category3_1 = Category(category_name="first_category")

        category1_2 = Category(category_name="second_category")
        category2_2 = Category(category_name="second_category")
        category3_2 = Category(category_name="second_category")

        category1_3 = Category(category_name="third_category")
        category2_3 = Category(category_name="third_category")
        category3_3 = Category(category_name="third_category")

        category3_4 = Category(category_name="fourth_category")

        category1_1.word = "faaa"
        category2_1.word = "first_word"
        category3_1.word = "first_word"

        category1_2.word = "fsecond_word"
        category2_2.word = "fsecond_word"
        category3_2.word = "fsecond_word"

        category1_3.word = "fsecond_word"
        category2_3.word = "first_word"
        category3_3.word = "fthird_word"

        category3_4.word = "fourth_word"

        category1_1.player_id = "player_1"
        category2_1.player_id = "player_2"
        category3_1.player_id = "player_3"

        category1_2.player_id = "player_1"
        category2_2.player_id = "player_2"
        category3_2.player_id = "player_3"

        category1_3.player_id = "player_1"
        category2_3.player_id = "player_2"
        category3_3.player_id = "player_3"
        category3_4.player_id = "player_3"

        category1_1.legit_score = -2
        category2_1.legit_score = 2
        category3_1.legit_score = 2
        category1_2.legit_score = 3
        category2_2.legit_score = 3
        category3_2.legit_score = 3
        category1_3.legit_score = 3
        category2_3.legit_score = 3
        category3_3.legit_score = 0
        category3_4.legit_score = 1

        game = Game()
        game.letter = "f"

        game.categories.append(category1_1)
        game.categories.append(category2_1)
        game.categories.append(category3_1)

        game.categories.append(category1_2)
        game.categories.append(category2_2)
        game.categories.append(category3_2)

        game.categories.append(category1_3)
        game.categories.append(category2_3)
        game.categories.append(category3_3)
        game.categories.append(category3_4)

        # when
        game.game_state = GameState.score_display
        game.summary_voting()

        # then
        current_game_state = game.get_current_state()
        self.assertEqual(expected_results['player_1']['score'], current_game_state["results"]['player_1']['score'])
        self.assertEqual(expected_results['player_1']['results'], current_game_state["results"]['player_1']['results'])
        self.assertEqual(expected_results['player_2']['score'], current_game_state["results"]['player_2']['score'])
        self.assertEqual(expected_results['player_2']['results'], current_game_state["results"]['player_2']['results'])
        self.assertEqual(expected_results['player_3']['results'], current_game_state["results"]['player_3']['results'])
        self.assertEqual(expected_results['player_3']['score'], current_game_state["results"]['player_3']['score'])

    def test_completing_players_move(self):
        # given
        expected_game_state = {'first_category': ['aaa', 'first_word'], 'second_category': ['second_word'],
                               'third_category': ['second_word', 'first_word', 'third_word'],
                               'fourth_category': ['fourth_word']}

        first_player_completing = {"first_category": "aaa", "second_category": "second_word",
                                   "third_category": "second_word"}
        second_player_completing = {"first_category": "first_word", "second_category": "second_word",
                                    "third_category": "first_word"}
        third_player_completing = {"first_category": "first_word", "second_category": "second_word",
                                   "third_category": "third_word", "fourth_category": "fourth_word"}
        # when
        game = Game()
        game.handle_complete("player_1", first_player_completing)
        game.handle_complete("player_2", second_player_completing)
        game.handle_complete("player_3", third_player_completing)

        game.game_state = GameState.voting
        # then
        current_game_state = game.get_current_state()
        self.assertEqual(expected_game_state, current_game_state["candidates"])

    def test_is_only_word(self):
        # given
        expected_results = {
            'player_1': {'results': [{'category_name': 'first_category', 'word': 'faaa', 'score': 15},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'fsecond_word', 'score': 10}],
                         "score": 30},
            'player_2': {'results': [{'category_name': 'first_category', 'word': 'rasa', 'score': 0},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'first_word', 'score': 10}],
                         "score": 15},
            'player_3': {'results': [{'category_name': 'first_category', 'word': '', 'score': 0},
                                     {'category_name': 'second_category', 'word': 'fsecond_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'fthird_word', 'score': 10},
                                     {'category_name': 'fourth_category', 'word': 'fourth_word', 'score': 15}],
                         "score": 30}}

        category1_1 = Category(category_name="first_category")
        category2_1 = Category(category_name="first_category")
        category3_1 = Category(category_name="first_category")

        category1_2 = Category(category_name="second_category")
        category2_2 = Category(category_name="second_category")
        category3_2 = Category(category_name="second_category")

        category1_3 = Category(category_name="third_category")
        category2_3 = Category(category_name="third_category")
        category3_3 = Category(category_name="third_category")

        category3_4 = Category(category_name="fourth_category")

        category1_1.word = "faaa"
        category2_1.word = "rasa"
        category3_1.word = ""

        category1_2.word = "fsecond_word"
        category2_2.word = "fsecond_word"
        category3_2.word = "fsecond_word"

        category1_3.word = "fsecond_word"
        category2_3.word = "first_word"
        category3_3.word = "fthird_word"

        category3_4.word = "fourth_word"

        category1_1.player_id = "player_1"
        category2_1.player_id = "player_2"
        category3_1.player_id = "player_3"

        category1_2.player_id = "player_1"
        category2_2.player_id = "player_2"
        category3_2.player_id = "player_3"

        category1_3.player_id = "player_1"
        category2_3.player_id = "player_2"
        category3_3.player_id = "player_3"
        category3_4.player_id = "player_3"

        category1_1.legit_score = 2
        category2_1.legit_score = 2
        category3_1.legit_score = 2
        category1_2.legit_score = 3
        category2_2.legit_score = 3
        category3_2.legit_score = 3
        category1_3.legit_score = 3
        category2_3.legit_score = 3
        category3_3.legit_score = 0
        category3_4.legit_score = 1

        game = Game()
        game.letter = "f"

        game.categories.append(category1_1)
        game.categories.append(category2_1)
        game.categories.append(category3_1)

        game.categories.append(category1_2)
        game.categories.append(category2_2)
        game.categories.append(category3_2)

        game.categories.append(category1_3)
        game.categories.append(category2_3)
        game.categories.append(category3_3)
        game.categories.append(category3_4)

        # when
        game.game_state = GameState.score_display
        game.summary_voting()

        # then
        current_game_state = game.get_current_state()
        self.assertEqual(expected_results['player_1']['score'], current_game_state["results"]['player_1']['score'])
        self.assertEqual(expected_results['player_1']['results'],
                         current_game_state["results"]['player_1']['results'])
        self.assertEqual(expected_results['player_2']['score'], current_game_state["results"]['player_2']['score'])
        self.assertEqual(expected_results['player_2']['results'],
                         current_game_state["results"]['player_2']['results'])
        self.assertEqual(expected_results['player_3']['results'],
                         current_game_state["results"]['player_3']['results'])
        self.assertEqual(expected_results['player_3']['score'], current_game_state["results"]['player_3']['score'])

    def test_voting(self):
        # given
        expected_results = {
            'player_1': {'results': [{'category_name': 'first_category', 'word': 'aaa', 'score': 0},
                                     {'category_name': 'second_category', 'word': 'second_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'second_word', 'score': 10}],
                         "score": 15},
            'player_2': {'results': [{'category_name': 'first_category', 'word': 'first_word', 'score': 5},
                                     {'category_name': 'second_category', 'word': 'second_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'first_word', 'score': 10}],
                         "score": 20},
            'player_3': {'results': [{'category_name': 'first_category', 'word': 'first_word', 'score': 5},
                                     {'category_name': 'second_category', 'word': 'second_word', 'score': 5},
                                     {'category_name': 'third_category', 'word': 'third_word', 'score': 10},
                                     {'category_name': 'fourth_category', 'word': 'fourth_word', 'score': 15}],
                         "score": 35}}

        first_player_completing = {"first_category": "aaa", "second_category": "second_word",
                                   "third_category": "second_word"}
        second_player_completing = {"first_category": "first_word", "second_category": "second_word",
                                    "third_category": "first_word"}
        third_player_completing = {"first_category": "first_word", "second_category": "second_word",
                                   "third_category": "third_word", "fourth_category": "fourth_word"}

        first_player_voting = {"first_category": {"aaa": False, "first_word": True},
                               "second_category": {"second_word": True},
                               "third_category": {"second_word": True, "first_word": True}}
        second_player_voting = {"first_category": {"aaa": False, "first_word": True},
                                "second_category": {"second_word": True},
                                "fourth_category": {"fourth_word": True},
                                "third_category": {"second_word": True, "first_word": True}}
        third_player_voting = {"first_category": {"first_word": True},
                               "second_category": {"second_word": True},
                               "fourth_category": {"fourth_word": True},
                               "third_category": {"second_word": True, "first_word": True}}
        # when
        game = Game()
        game.handle_complete("player_1", first_player_completing)
        game.handle_complete("player_2", second_player_completing)
        game.handle_complete("player_3", third_player_completing)

        game.game_state = GameState.voting

        game.handle_voting("player_1", first_player_voting)
        game.handle_voting("player_2", second_player_voting)
        game.handle_voting("player_3", third_player_voting)

        game.summary_voting()
        game.game_state = GameState.score_display

        # then
        current_game_state = game.get_current_state()
        self.assertEqual(expected_results, current_game_state["results"])


if __name__ == '__main__':
    unittest.main()
