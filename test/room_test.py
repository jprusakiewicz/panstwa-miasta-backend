import os
import unittest

from app.room import Room


class MyTestCase(unittest.TestCase):
    def test_exporting_room_status(self):
        os.environ[
            'EXPORT_RESULTS_URL'] = "https://backend-dev.capgemini.enl-projects.com"
        r = Room(2)
        r.export_score()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
