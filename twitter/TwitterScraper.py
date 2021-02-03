import twitter, os, csv, time

class TwitterScraper:
    def __init__(self, handle, request_limit, start_at):
        self.handle = handle
        self.max_requests = 10000
        self.request_limit = min(self.max_requests, request_limit) # limit to 10,000 requests
        self.start_at = max(0, start_at)
        self.out_file = self.get_file()

        self.api = self.load_api()
        time.sleep(5) # allow api to initialize
        self.user, self.followers = self.get_user_info()

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

        api.InitializeRateLimit()

        return api

    def get_file(self):
        if not os.path.isdir(self.handle):
            os.mkdir(self.handle)

        out_file = self.handle + '\\connections.csv'

        if self.request_limit < self.max_requests:
            out_file = self.handle + '\\test_connections.csv'

        return out_file

    def get_user_info(self):
        user = self.api.GetUser(screen_name=self.handle)
        followers = self.get_followers(user.id)

        return user, followers

    def get_followers(self, uid):
        followers = self.api.GetFollowers(user_id=uid,
            total_count=self.request_limit, include_user_entities=False)

        followers = [[f.id, f.screen_name] for f in followers]

        return followers

    def get_user_connections(self, user):
        connections = []
        followers = self.get_followers(user[0])

        for f in followers:
            if f in self.followers:
                connections.append(f)

        return connections

    def get_all_connections(self):
        # if running for 1st time, make .csv file for user
        if self.start_at == 0:
            self.write_initial()
        else:
            self.resume_session()

        errors = []

        start = max(0, self.start_at - 1)
        for f in range(start, len(self.followers)):
            connections = []

            try:
                connections.append({
                    'pk': f + 2, # skip 1 for headers & 1 for user
                    'user': self.followers[f],
                    'connections': self.get_user_connections(self.followers[f]),
                })
            except Exception as e:
                # exceptions occur e.g. when an account is private
                errors.append((self.followers[f], e))

            self.write_batch(connections)

        print('errors:', errors)

    def write_initial(self):
        initial_user = {
            'pk': 1,
            'user': [self.user.id, self.user.screen_name],
            'connections': self.followers,
        }

        with open(self.out_file, 'w', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=['pk', 'user', 'connections'])
            writer.writeheader()
            writer.writerow(initial_user)

    def resume_session(self):
        with open(self.out_file, 'r', newline='\n') as i:
            connections = list(csv.reader(i))

        with open(self.out_file, 'w', newline='\n') as o:
            writer = csv.writer(o)
            writer.writerow(connections[0])
            connections = connections[1:]
            writer.writerows([c for c in connections if int(c[0]) <= self.start_at])

    def write_batch(self, connections):
        with open(self.out_file, 'a', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=['pk', 'user', 'connections'])
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

def get_start(handle):
    start_at = 0
    resume = input('would you like to (0) start a new run or (1) resume a previous run?: ')

    try:
        if (int(resume)):
            prompt = 'enter the pk in ' + handle + '/connections.csv at which you wish to resume: '
            start_at = int(input(prompt))
        return start_at
    except:
        print('please enter only integers')
        return get_start

if __name__ == '__main__':
    handle = input('enter the twitter handle whose followers you want to retrieve: ')
    request_limit = 10000 # default request limit

    if check_is_test():
        request_limit = 3

    print('proceeding with request limit', request_limit)

    start_at = get_start(handle)
    scraper = TwitterScraper(handle, request_limit, start_at)
    scraper.get_all_connections()
