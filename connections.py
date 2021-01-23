import csv, pprint

class Connections:
    def __init__(self, handle, threshold=1):
        self.handle = handle
        self.threshold = int(threshold)
        self.filename = self.handle + '\\connections.csv'
        self.uids = []
        self.init_connections = self.read_connections()
        self.connections = self.prune_connections()

    def read_connections(self):
        connections = []

        with open(self.filename, 'r', newline='\n') as f:
            reader = csv.reader(f)
            next(reader) # skip headers

            for row in reader:
                self.uids.append(row[1])
                # row format is [primary_key, uid, [connections]]
                connections.append({
                    'pk': row[0],
                    'uid': row[1],
                    'connections': row[2].replace('[', '').replace(']', '').replace(' ', '').replace('\'','').split(',')
                })

        return connections

    def prune_connections(self):
        first_prune = self.remove(self.init_connections, self.check_has_uid(self.init_connections))
        second_prune = self.remove(first_prune, self.check_meets_threshold(first_prune))

        return self.reindex(second_prune)

    def check_has_uid(self, connections):
        prune = []

        for c in connections:
            for u in c['connections']:
                if u not in self.uids:
                    prune.append(c['uid'])

        return prune

    def check_meets_threshold(self, connections):
        prune = []

        for c in connections:
            if len(c['connections']) < self.threshold:
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

    def write_connections(self):
        with open(self.filename, 'w', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(['pk','uid', 'connetions'])

            count = 1
            for c in self.connections:
                writer.writerow([count, self.connections[c][0], self.connections[c][1]])
                count += 1

    def show_connections(self, connections):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(connections)

if __name__ == '__main__':
    connections = Connections(handle='Aphorikles')
    connections.show_connections(connections.connections)
