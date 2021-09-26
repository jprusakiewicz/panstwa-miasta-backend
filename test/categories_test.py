import unittest

from app.game import Categories, Category


class MyTestCase(unittest.TestCase):
    def test_filtering_categories(self):
        categories = Categories()
        category_one = Category("one")
        category_two = Category("two")
        categories.append(category_one)
        categories.append(category_two)
        c_two = categories.filter_by_category("two")

        self.assertEqual(len(c_two), 1)  # add assertion here
        self.assertEqual(c_two[0].category_name, "two")  # add assertion here

    def test_filtering_enpty_strings_in_categories(self):
        categories = Categories()
        category_one = Category("one")
        category_two = Category("two")
        categories.append(category_one)
        categories.append(category_two)
        c_two = categories.filter_by_category("two")

        self.assertEqual(len(c_two), 1)  # add assertion here
        self.assertEqual(c_two[0].category_name, "two")  # add assertion here


if __name__ == '__main__':
    unittest.main()
