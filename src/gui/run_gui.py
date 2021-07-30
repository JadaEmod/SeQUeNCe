import json
import os
import networkx as nx
import pandas as pd
import numpy as np
from .app import Quantum_GUI
from .graph_comp import GraphNode


class run_gui():
    def __init__(self):
        graph = nx.DiGraph()
        tdm_table = pd.DataFrame()
        delay_table = pd.DataFrame()
        self.gui = Quantum_GUI(
            graph,
            delays=delay_table,
            tdm=tdm_table
        ).get_app()

    def load_graph(self, path_to_topology=None):
        # JSON
        if path_to_topology is None:
            DIRECTORY, _ = os.path.split(__file__)
            with open(DIRECTORY+'/starlight.json') as json_file:
                network_in = json.load(json_file)
        else:
            with open(path_to_topology) as json_file:
                network_in = json.load(json_file)

        # Delay table initialization
        pd.options.display.float_format = '{:.2e}'.format
        table = network_in['cchannels_table']
        delay_table = pd.DataFrame(table['table'])
        delay_table.columns = table['labels']

        # TDM table initialization
        tdm_default = np.empty(
            [len(table['labels']), len(table['labels'])],
            dtype=int
        )
        tdm_default.fill(20000)

        index = 0

        for x in range(tdm_default.shape[0]):
            tdm_default[x][index] = 0
            index += 1

        tdm_table = pd.DataFrame(tdm_default)
        tdm_table.columns = table['labels']

        # Network initialization
        graph = nx.DiGraph()

        for node in network_in['nodes']:
            if node['type'] == 'QuantumRouter':
                node['type'] = 'Quantum_Router'
            new_node = GraphNode(node['name'], node['type'], 'default_router')
            graph.add_node(
                node['name'],
                label=node['name'],
                node_type=node['type'],
                data=new_node.__dict__
            )

        for edge in network_in['qconnections']:
            graph.add_edge(
                edge['node1'],
                edge['node2'],
                data={
                    'source': edge['node1'],
                    'target': edge['node2'],
                    'distance': edge['distance'],
                    'attenuation': edge['attenuation'],
                    'link_type': 'Quantum'
                }
            )

        input = nx.readwrite.cytoscape_data(graph)['elements']

        ###############################################

        self.gui = Quantum_GUI(
            graph,
            delays=delay_table,
            tdm=tdm_table
        ).get_app()
