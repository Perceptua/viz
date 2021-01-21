import plotly.graph_objects as go
from connections import Connections
import networkx as nx

def map_to_primary_key(connections):
    uid_to_key = {}

    for c in connections:
        pk = c['pk']
        uid = c['uid']
        uid_to_key[uid] = pk

    for c in connections:
        c['connections'] = [uid_to_key[i] if len(i) else None for i in c['connections']]

    return connections

def generate_graph(connections):
    G = nx.Graph()
    G.add_nodes_from([c['pk'] for c in connections])

    edge_list = []

    for c in connections:
        [edge_list.append((c['pk'], i)) if i else None for i in c['connections']]

    G.add_edges_from(edge_list)

    return G

def get_layout(nodes, threshold):
    info_string = (
        '<br>connections between '
        '{num_nodes} <a href="https://twitter.com/wydna00">wydna.research</a> twitter followers '
        '(threshold={threshold} connections).'
    ).format(num_nodes=str(len(nodes)), threshold=threshold)

    axis = dict(showbackground=False,showline=False,
                zeroline=False,showgrid=False,
                showticklabels=False,title='')

    return go.Layout(
        title=info_string, titlefont_size=16,
        showlegend=False, hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[ dict(
            text='created by <a href="https://twitter.com/Aphorikles">@Aphorikles</a>',
            showarrow=False, xref="paper", yref="paper",
            x=0.005, y=-0.002 ) ],
       scene=dict(xaxis=dict(axis), yaxis=dict(axis),zaxis=dict(axis)))

def get_node_info(G, connections):
    node_adjacencies = []
    node_text = []

    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('connections: '+str(len(adjacencies[1])))

    return node_adjacencies, node_text


def plot(G, connections, threshold):
    layt = nx.spring_layout(G, dim=3)

    node_x = [layt[str(k)][0] for k in G.nodes]
    node_y = [layt[str(k)][1] for k in G.nodes]
    node_z = [layt[str(k)][2] for k in G.nodes]

    edge_x = []
    edge_y = []
    edge_z = []

    for e in G.edges():
        edge_x+=[layt[e[0]][0],layt[e[1]][0], None]
        edge_y+=[layt[e[0]][1],layt[e[1]][1], None]
        edge_z+=[layt[e[0]][2],layt[e[1]][2], None]

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=0.75, color='#888'),
        hoverinfo='none', mode='lines')

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers', hoverinfo='text',
        marker=dict(
            showscale=True, colorscale='Inferno',
            reversescale=True, color=[], size=10,
            line_width=2, colorbar=dict(
                thickness=15, title='node connections',
                xanchor='left', titleside='right'
            )))

    node_adjacencies, node_text = get_node_info(G, connections)
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace], layout=get_layout(G.nodes, threshold))
    fig.write_html('network.html', auto_open=True)

if __name__ == '__main__':
    c = Connections(testing=False, threshold=3)
    c.connections = map_to_primary_key(c.connections)

    graph = generate_graph(c.connections)
    plot(graph, c.connections, c.threshold)
