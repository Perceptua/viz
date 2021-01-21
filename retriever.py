import twitter, os, csv, sys, random

class Retriever:
    def __init__(self, handle):
        self.handle = handle
        self.api = self.load_api()
        self.uid, self.followers = self.get_followers()
        self.complete = []
        self.incomplete = self.followers.copy()
        self.write_id = random.randint(0, 999999999)

    def load_api(self):
        # load Twitter app credentials from environment variables
        api_key = os.environ['TWITTER_API']
        api_secret = os.environ['TWITTER_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_secret = os.environ['TWITTER_ACCESS_SECRET']

        # instantiate Twitter API object
        api = twitter.Api(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token_key=access_token,
            access_token_secret=access_secret,
            sleep_on_rate_limit=True
        )

        return api

    def get_followers(self):
        user = api.GetUser(screen_name=self.handle)
        return user.id, api.GetFollowerIDs(user_id=user.id, total_count=request_limit)


    def find_connections(self, uid):
        connections = []
        followers = api.GetFollowerIDs(user_id=uid, total_count=request_limit)

        for f in followers:
            if f in self.followers:
                connections.append(f)

        return connections


    def get_batch_connections(self):
        connections = []
        errors = []

        self.api.InitializeRateLimit()
        limit_status = self.api.rate_limit.get_limit('https://api.twitter.com/1.1/followers/ids.json')

        for f in range(len(self.followers)):
            if limit_status.remaining != 0:

                try:
                    connections.append({
                        'pk': f,
                        'uid': self.followers[f],
                        'connections': find_connections(self.followers[f]),
                    })

                except Exception as e:
                    # exceptions occur when user account is private
                    errors.append(f)

                self.complete.append(f)
                self.incomplete.remove(f)
                print('progress: ', str((len(self.complete) / len(self.followers)) / 100), '%', sep='')
            else:
                self.write_batch(connections)

    def write_batch(self, connections):
        filename = 'connections' + str(self.write_id) + '.csv'

        with open(filename, 'a', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=['pk', 'uid', 'connections'])
            writer.writeheader()
            for c in connections:
                writer.writerow(c)


def check_is_test():
    try:
        options = {'y': True, 'n': False}
        answer = str(input('is this a test? (y/n): '))
        is_test = options[answer.lower()]
        return is_test
    except:
        print('error: please indicate whether you are running a test (y/n).')
        return check_is_test()

if __name__ == '__main__':
    request_limit = None

    if check_is_test():
        request_limit = 5

    wydna_retriever = Retriever('wydna00')
    wydna_retriever.get_batch_connections()
