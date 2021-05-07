##################################BASIC FUNCTIONS

# This library includes several functions that are used in most of the developed scripts
import networkx as nx


def obtencion_sucesores(input_graph, nodo):
    """"it obtain the decedents from a single node"""
    # print("el nodo a checar es", nodo)
    lista_total_sucesores = []
    lista_sucesores = nx.dfs_successors(input_graph, nodo)
    # print(lista_sucesores)
    # print("obtencion de sucesores funcion")
    for element in lista_sucesores:
        # print("element",element,lista_sucesores[element])
        if element not in lista_total_sucesores:
            lista_total_sucesores.append(element)
        grupo = lista_sucesores[element]
        # print("grupo",grupo)
        for item in grupo:
            if item not in lista_total_sucesores:
                lista_total_sucesores.append(item)

        # lista_total_sucesores.append(lista_sucesores[element][0])
    # print(lista_total_sucesores)
    if lista_total_sucesores:
        lista_total_sucesores.remove(nodo)
    return lista_total_sucesores


def sink_node_from_any_node(input_graph, sinks, nodo):
    for nodo_sink in sinks:
        path = simple_paths_from_two_nodes(input_graph, nodo, nodo_sink)
        if path:
            return nodo_sink
    return None


def simple_paths_from_two_nodes(input_graph, nodo_source, node_sink):
    paths = list(nx.all_simple_paths(input_graph, source=nodo_source, target=node_sink))
    return paths


def source_node_from_any_node(input_graph, sources, nodo):
    for nodo_source in sources:
        path = simple_paths_from_two_nodes(input_graph, nodo_source, nodo)
        if path:
            return nodo_source


def sink_from_datapath(input_graph, path):
    # print(path)
    # print(input_graph.nodes)
    sink = None
    for nodo in path:
        # print(nodo)
        if input_graph.out_degree(nodo) == 0:
            sink = nodo
    return sink


def sources_nodes_of_a_graph(input_graph):
    # print("entrada funcion obtencion de sources")
    lista_sources = []
    lista_de_nodos = list(input_graph.nodes)
    for node in lista_de_nodos:
        if input_graph.in_degree(node) == 0:
            # print("este nodo tiene input degree zero", node)
            lista_sources.append(node)
    # print(lista_sources)
    return lista_sources

def sinks_nodes_of_a_graph(input_graph):
    lista_sinks = []
    for node in input_graph.nodes:

        # for node in range(0, len(input_graph.nodes)):
        if input_graph.out_degree(node) == 0:
            # print("este nodo tiene input degree zero", node)
            lista_sinks.append(node)
    return lista_sinks

def obtencion_sources(input_graph):
    """it only obtain all the sources nodes of a graph"""
    lista_nodos = []
    for nodos in input_graph.nodes:
        if input_graph.in_degree(nodos) == 0:
            lista_nodos.append(nodos)
    return lista_nodos

def obtencion_sinks(input_graph):
    """it only obtain all the sinks nodes of a graph"""
    lista_nodos = []
    for nodos in input_graph.nodes:
        if input_graph.out_degree(nodos) == 0:
            lista_nodos.append(nodos)
    return lista_nodos