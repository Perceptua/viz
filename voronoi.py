import plotly.graph_objects as go
import numpy as np

# generates a Voronoi diagram
# note: points must be in n-dimensional Euclidian space

class Voronoi:
    def __init__(self, sites, dims):
        self.sites = sites
        self.dims = dims

if __name__ == '__main__':
    sites = np.random.randint(0, 10, size=(100, 3))
    voronoi = Voronoi(sites, dims=3)
