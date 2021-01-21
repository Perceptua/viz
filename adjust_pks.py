import csv


headers = None
data = {}

'''
with open('connections.csv', 'r', newline='\n') as i:
    reader = csv.reader(i)
    headers = next(reader)

    row_num = 1
    for row in reader:
        data[row_num] = row
        row_num += 1

# changes original pk to row_num
for d in data:
    data[d][0] = d

with open('connections.csv', 'w', newline='\n') as o:
    writer = csv.writer(o)
    writer.writerow(headers)
    for d in data:
        writer.writerow(data[d])
'''

uids = []
all_connections = []

with open('connections.csv', 'r', newline='\n') as i:
    reader = csv.reader(i)
    headers = next(reader)

    for row in reader:
        uids.append(row[1])
        connections = row[2].replace(' ','').replace('[','').replace(']','').split(',')
        all_connections += connections
        data[row[0]] = [row[0], row[1], connections]

no_uid = []
[no_uid.append(c) for c in all_connections if c not in uids]

no_uid_res = []
[no_uid_res.append(n) for n in no_uid if n not in no_uid_res]

for d in data:
    data[d][2] = [t for t in data[d][2] if t not in no_uid_res]

with open('connections.csv', 'w', newline='\n') as o:
    writer = csv.writer(o)
    writer.writerow(headers)
    for d in data:
        writer.writerow(data[d])
