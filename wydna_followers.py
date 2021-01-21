import plotly.graph_objects as go
from connections import Connections
import networkx as nx
import math

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
        title=info_string, titlefont_size=16,paper_bgcolor='black', titlefont_color='white',
        showlegend=False, hovermode='closest', margin=dict(b=100,l=5,r=5,t=100), font={'color': 'white'},
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

def get_node_pos(G):
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

    return layt, [node_x, node_y, node_z], [edge_x, edge_y, edge_z]


def network_plot(G, connections, threshold):
    layt, nodes, edges = get_node_pos(G)

    edge_trace = go.Scatter3d(
        x=edges[0], y=edges[1], z=edges[2],
        line=dict(width=0.75, color='#888'),
        hoverinfo='none', mode='lines')

    node_trace = go.Scatter3d(
        x=nodes[0], y=nodes[1], z=nodes[2],
        mode='markers', hoverinfo='text',
        marker=dict(
            showscale=True, colorscale='Viridis',
            reversescale=True, color=[], size=10,
            line_width=2, colorbar=dict(
                thickness=15, title='node connections',
                xanchor='left', titleside='right'
            )))

    node_adjacencies, node_text = get_node_info(G, connections)
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace], layout=get_layout(G.nodes, threshold))
    fig.write_html('network.html', auto_open=False)

def surface_plot(G, threshold):
    layt, nodes, edges = get_node_pos(G)
    fig = go.Figure(
        data=[go.Mesh3d(x=nodes[0], y=nodes[1], z=nodes[2],opacity=0.5, color='rgba(244,22,100,0.6)')],
        layout=get_layout(G.nodes, threshold))

    fig.write_html('surface.html', auto_open=False)

def heat_plot(G, connections, threshold):
    row_length = round(len(connections) / 14)
    count = 0
    row = []
    z = []

    for c in connections:
        if count < row_length:
            row += [len(c['connections'])]
            count += 1
        else:
            z += [row]
            row = [len(c['connections'])]
            count = 1

    fig = go.Figure(data=[go.Heatmap(z=z, colorscale='Viridis')],layout=get_layout(G.nodes, threshold))
    fig.write_html('heatmap.html', auto_open=True)

if __name__ == '__main__':
    c = Connections(testing=False, threshold=3)
    c.connections = map_to_primary_key(c.connections)

    graph = generate_graph(c.connections)
    network_plot(graph, c.connections, c.threshold)
    surface_plot(graph, c.threshold)
    heat_plot(graph, c.connections, c.threshold)
