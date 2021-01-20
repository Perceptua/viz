import csv, pprint

class Connections:
    def __init__(self, testing=False):
        self.connections = self.read_connections()

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
                    'connections': row[2].replace('[', '').replace(']', '').replace(' ', '').split(',')
                })

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
