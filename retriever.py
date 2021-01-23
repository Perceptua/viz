import twitter, os, csv, sys, random, time

class Retriever:
    def __init__(self, handle, request_limit):
        self.handle = handle
        self.out_file = self.handle + '\\connections.csv'
        self.request_limit = request_limit
        self.api = self.load_api()
        self.uid, self.followers = self.get_user_info()

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

    def get_user_info(self):
        user = self.api.GetUser(screen_name=self.handle)
        followers = self.get_followers(user.id)

        return user, followers

    def get_followers(self, uid):
        followers = self.api.GetFollowerIDs(user_id=uid, total_count=self.request_limit)

        return followers

    def get_user_connections(self, uid):
        connections = []
        followers = self.get_followers(uid)

        for f in followers:
            if f in self.followers:
                connections.append(f)

        return connections

    def get_all_connections(self):
        errors = []
        complete = []
        incomplete = self.followers.copy()

        for f in range(len(self.followers)):
            connections = []

            try:
                connections.append({
                    'pk': f + 1,
                    'uid': self.followers[f],
                    'connections': self.get_user_connections(self.followers[f]),
                })
            except Exception as e:
                # exceptions occur when user account is private
                errors.append(self.followers[f])

            self.write_batch(connections)
            complete.append(self.followers[f])
            incomplete.remove(self.followers[f])
            print('progress: ', str((len(complete) / len(self.followers)) * 100), '%', sep='')

        print('errors:', errors)

    def write_headers(self):
        with open(self.out_file, 'a', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=['pk', 'uid', 'connections'])
            writer.writeheader()

    def write_batch(self, connections):
        with open(self.out_file, 'a', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=['pk', 'uid', 'connections'])
            writer.writerows(connections)


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

    handle = input('enter the twitter handle whose followers you want to retrieve: ')
    retriever = Retriever(handle, request_limit)
    retriever.write_headers()
    retriever.get_all_connections()
