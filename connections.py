import csv, pprint

class Connections:
    def __init__(self, testing=False, threshold=1):
        self.threshold = threshold
        self.connections = self.prune_connections(self.read_connections())

    def read_connections(self):
        connections = []
        with open('connections.csv', 'r', newline='\n') as f:
            reader = csv.reader(f)
            next(reader) # skip headers
            for row in reader:
                # row format is [primary_key, uid, [connections]]
                connections.append({
                    'pk': row[0],
                    'uid': row[1],
                    'connections': row[2].replace('[', '').replace(']', '').replace(' ', '').replace('\'','').split(',')
                })

        return connections

    def prune_connections(self, connections):
        prune = []
        for c in connections:
            if len(c['connections']) < self.threshold:
                prune.append(c['uid'])

        return self.remove(prune, connections)

    def remove(self, uid_list, connections):
        for uid in uid_list:
            connections = [c for c in connections if c['uid'] != uid]

            for c in connections:
                c['connections'] = [u for u in c['connections'] if u != uid]

        return connections

    def write_connections(self):
        with open('connections.csv', 'w', newline='\n') as f:
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
    testing = True
    connections = Connections(testing=testing)
    # connections.write_connections()
    connections.show_connections(connections.connections)
