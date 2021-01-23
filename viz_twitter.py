import plotly.graph_objects as go
from connections import Connections
from scipy.spatial import Voronoi
import networkx as nx
import numpy as np
import os

class VizTwitter:
    def __init__(self, handle, threshold):
        self.handle = handle
        self.threshold = int(threshold)
        self.plots = {
            1: 'network',
            2: 'surface',
            3: 'heatmap',
            4: 'voronoi',
        }

        self.connections = self.get_connections()
        self.G = self.generate_graph()

    def get_connections(self):
        c = Connections(self.handle, threshold=self.threshold)
        c.connections = self.map_to_primary_key(c.connections)

        return c.connections

    def map_to_primary_key(self, connections):
        uid_to_key = {}

        for c in connections:
            pk = c['pk']
            uid = c['uid']
            uid_to_key[uid] = pk

        for c in connections:
            c['connections'] = [uid_to_key[i] if len(i) else None for i in c['connections']]

        return connections

    def generate_graph(self):
        G = nx.Graph()
        G.add_nodes_from([c['pk'] for c in self.connections])

        edge_list = []

        for c in self.connections:
            [edge_list.append((c['pk'], i)) if i else None for i in c['connections']]

        G.add_edges_from(edge_list)

        return G

    def plot(self):
        codes = self.plots.keys()

        if 1 in codes:
            self.network_plot()
        if 2 in codes:
            self.surface_plot()
        if 3 in codes:
            self.heat_plot()
        if 4 in codes:
            self.voronoi_plot()

    def get_layout(self):
        info_string = (
            '<br>connections between {num_nodes} followers of '
            '<a href="https://twitter.com/{handle}">@{handle}</a> '
            '(threshold={threshold} connections).'
        ).format(num_nodes=str(len(self.G.nodes)), handle=self.handle, threshold=self.threshold)

        axis_2d = dict(showline=False,zeroline=False,showgrid=False,
            showticklabels=False,title='')

        axis_3d = dict(showbackground=False,showline=False,zeroline=False,
            showgrid=False,showticklabels=False,title='')

        return go.Layout(
            title=info_string, titlefont_size=16,paper_bgcolor='pink', plot_bgcolor='pink', titlefont_color='black',
            showlegend=False, hovermode='closest', margin=dict(b=100,l=5,r=5,t=100), font={'color': 'white'},
            annotations=[dict(text='created by <a href="https://twitter.com/Aphorikles">@Aphorikles</a>',
                showarrow=False, xref="paper", yref="paper",x=0.005, y=-0.002)],
           scene=dict(xaxis=dict(axis_3d), yaxis=dict(axis_3d), zaxis=dict(axis_3d)), xaxis=dict(axis_2d), yaxis=dict(axis_2d))

    def get_node_info(self):
        node_adjacencies = []
        node_text = []

        for node, adjacencies in enumerate(self.G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append('connections: '+str(len(adjacencies[1])))

        return node_adjacencies, node_text

    def get_node_pos(self, dims):
        layt = nx.spring_layout(self.G, dim=dims)

        node_x = [layt[str(k)][0] for k in self.G.nodes]
        node_y = [layt[str(k)][1] for k in self.G.nodes]
        node_z = []
        if dims == 3:
            node_z = [layt[str(k)][2] for k in self.G.nodes]

        edge_x = []
        edge_y = []
        edge_z = []

        for e in self.G.edges():
            edge_x+=[layt[e[0]][0],layt[e[1]][0], None]
            edge_y+=[layt[e[0]][1],layt[e[1]][1], None]
            if dims == 3:
                edge_z+=[layt[e[0]][2],layt[e[1]][2], None]

        return layt, [node_x, node_y, node_z], [edge_x, edge_y, edge_z]


    def network_plot(self):
        layt, nodes, edges = self.get_node_pos(3)

        edge_trace = go.Scatter3d(
            x=edges[0], y=edges[1], z=edges[2],
            line=dict(width=0.75, color='#888'),
            hoverinfo='none', mode='lines')

        node_trace = go.Scatter3d(
            x=nodes[0], y=nodes[1], z=nodes[2],
            mode='markers', hoverinfo='text',
            marker=dict(
                showscale=True, colorscale='Aggrnyl',
                reversescale=True, color=[], size=10,
                line_width=2, colorbar=dict(
                    thickness=15, title='node connections',
                    xanchor='left', titleside='right'
                )))

        node_adjacencies, node_text = self.get_node_info()
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text

        fig = go.Figure(data=[edge_trace, node_trace], layout=self.get_layout())
        fig.write_html(self.handle+'\\network.html', auto_open=False)

    def surface_plot(self):
        layt, nodes, edges = self.get_node_pos(3)
        fig = go.Figure(
            data=[go.Mesh3d(x=nodes[0], y=nodes[1], z=nodes[2],opacity=0.5, color='rgba(244,22,100,0.6)')],
            layout=self.get_layout())

        fig.write_html(self.handle+'\\surface.html', auto_open=False)

    def heat_plot(self):
        row_length = round(len(self.connections) / 14)
        count = 0
        row = []
        z = []

        for c in self.connections:
            if count < row_length:
                row += [len(c['connections'])]
                count += 1
            else:
                z += [row]
                row = [len(c['connections'])]
                count = 1

        fig = go.Figure(data=[go.Heatmap(z=z, colorscale='Aggrnyl')],layout=self.get_layout())
        fig.write_html(self.handle+'\\heatmap.html', auto_open=False)

    def voronoi_plot(self, infinite=False):
        layt, nodes, edges = self.get_node_pos(2)
        x, y = np.array(nodes[0]), np.array(nodes[1])
        points = np.stack((x, y), axis=1)
        vor = Voronoi(points)
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=points[:,0], y=points[:,1],
            mode='markers', hoverinfo='text', name='points',
            marker=dict(color=points[:,0], colorscale='Aggrnyl')))

        fig.add_trace(go.Scatter(
            x=vor.vertices[:,0], y=vor.vertices[:,1],
            mode='markers', hoverinfo='text', name='vertices',
            marker=dict(color=vor.vertices[:,0], colorscale='Aggrnyl')))

        for simplex in vor.ridge_vertices:
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                fig.add_trace(go.Scatter(
                    x=vor.vertices[simplex, 0], y=vor.vertices[simplex, 1], mode='lines',
                    line=dict(color='floralwhite')))

        fig.update_layout(self.get_layout())
        fig.write_html(self.handle+'\\voronoi.html', auto_open=True)

        if infinite:
            fig = self.infinite_voronoi(vor, points, fig)
            fig.write_html(self.handle+'\\infinite_voronoi.html', auto_open=False)

    def infinite_voronoi(self, vor, points, fig):
        center = points.mean(axis=0)

        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)

            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0] # finite end Voronoi vertex
                t = points[pointidx[1]] - points[pointidx[0]]  # tangent
                t = t / np.linalg.norm(t)
                n = np.array([-t[1], t[0]]) # normal
                midpoint = points[pointidx].mean(axis=0)
                far_point = vor.vertices[i] + np.sign(np.dot(midpoint - center, n)) * n * 100

                fig.add_trace(go.Scatter(x=[vor.vertices[i,0], far_point[0]], y=[vor.vertices[i,1], far_point[1]],
                    mode='lines', line=dict(color='floralwhite')))

        return fig


if __name__ == '__main__':
    print('which user\'s data do you want to visualize?', next(os.walk('.'))[1], sep='\n')
    handle = input('username: ')
    threshold = input('enter connection threshold (\#): ')

    viz = VizTwitter(handle, threshold)

    print(viz.plots)
    original = set(viz.plots.keys())
    selected = set(
        [int(i) for i in input(
            'enter the plots you wish to generate (\# separated by spaces): '
        ).split(' ')]
    )

    diff = original - selected
    [viz.plots.pop(d) for d in diff]

    print('plotting:', viz.plots.values())

    viz.plot()
