import csv, pprint

class Scrubber:
    def __init__(self, handle, threshold, test=False):
        self.handle = handle
        self.threshold = int(threshold)
        self.filename = self.handle + '\\connections.csv'

        if test:
            self.filename = self.handle + '\\test_connections.csv'

        self.uids = []
        self.init_connections = self.read_connections()
        self.connections = self.prune_connections()

    def read_connections(self):
        read = []

        with open(self.filename, 'r', newline='\n') as f:
            reader = csv.reader(f)
            next(reader) # skip headers

            for row in reader:
                user = self.format_user(row[1])
                self.uids.append(user[0])

                # csv row format is [primary_key, [uid, handle], [connections]]
                read.append({
                    'pk': row[0],
                    'uid': user[0],
                    'handle': user[1],
                    'connections': self.format_connections(row[2])})

        return read

    def format_user(self, string):
        return string.replace('[', '').replace(']', '').replace(' ', '').replace('\'','').split(',')

    def format_connections(self, string):
        sub_lists = [s for s in string.split('[') if s]
        formatted = [s.replace(']','').replace('\'','').replace(' ','').split(',') for s in sub_lists]
        [f.remove('') for f in formatted if '' in f]

        if formatted[0]:
            return formatted
        else:
            return []

    def prune_connections(self):
        first_prune = self.remove(self.init_connections, self.check_has_uid(self.init_connections))
        second_prune = self.remove(first_prune, self.check_meets_threshold(first_prune))

        return self.reindex(second_prune)

    def check_has_uid(self, connections):
        prune = []

        for c in connections:
            for u in c['connections']:
                if u and u[0] not in self.uids:
                    # print(u[1], 'does not have a matching uid')
                    prune.append(u[1])

        return prune

    def check_meets_threshold(self, connections):
        prune = []

        for c in connections:
            if len(c['connections']) < self.threshold - 1:
                # print(c['handle'], 'has less than', self.threshold, 'connection(s)' )
                prune.append(c['uid'])

        return prune

    def remove(self, connections, prune_list):
        for uid in prune_list:
            connections = [i for i in connections if i['uid'] != uid]

            for c in connections:
                c['connections'] = [u for u in c['connections'] if u != uid]

        return connections

    def reindex(self, connections):
        pk = 1

        for c in connections:
            c['pk'] = str(pk)
            pk += 1

        return connections

    def show_connections(self, connections):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(connections)
        print(len(connections))

if __name__ == '__main__':
    scrubber = Scrubber(handle='Aphorikles', threshold=10, test=False)
    scrubber.show_connections(scrubber.connections)
