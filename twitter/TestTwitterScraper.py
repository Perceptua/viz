import unittest, csv
from TwitterScraper import TwitterScraper

class TestTwitterScraper(unittest.TestCase):
    def setUp(self):
        self. request_limit = 4
        self.start_at = 3

        self.scraper = TwitterScraper(
            handle='Aphorikles',
            request_limit=self.request_limit,
            start_at=self.start_at
        )

        self.scraper.get_all_connections()

    def tearDown(self):
        self.scraper.requests_sent = 0

    def get_connections(self):
        with open(self.scraper.out_file, 'r', newline='\n') as f:
            return list(csv.reader(f))

    def test_requests_sent(self):
        sent = self.request_limit - self.start_at + 1 # add 1 for initial user
        
        self.assertEqual(self.scraper.requests_sent, sent,
            'unexpected number of requests')

    def test_limit_followers(self):
        # id for an account w/ > 100k followers (you may need to find another)
        large_account_id = 37002399
        followers = self.scraper.get_followers(large_account_id)

        self.assertEqual(len(followers), self.request_limit,
            'unexpected number of followers')

    def test_scraper_start(self):
        connections = self.get_connections()
        last_pk = int(connections[-1][0])

        self.assertEqual(last_pk, self.request_limit,
            'unmatched start_at')

    def test_resume_session(self):
        self.scraper.resume_session()
        connections = self.get_connections()
        last_pk = int(connections[-1][0])

        self.assertEqual(last_pk, self.start_at,
            'pks do not match')


if __name__ == '__main__':
    unittest.main()
