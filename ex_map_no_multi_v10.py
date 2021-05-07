import networkx as nx
import time
import gc
from graphviz import Digraph
from itertools import permutations
import copy
import pickle
import os

import multiprocessing



from multiprocessing import Queue


from datetime import datetime
from pympler.asizeof import asizeof
# from memory_profiler import memory_usage
from basic_functions import obtencion_sources,obtencion_sinks,simple_paths_from_two_nodes,source_node_from_any_node,\
    sink_node_from_any_node,obtencion_sucesores


def sink_nodes_no_processing_resources(input_graph, dict_nodes):
    lista_sinks = []
    print(dict_nodes)
    for node in input_graph.nodes:
        if input_graph.out_degree(node) == 0 and dict_nodes[node]['type'] != 'rp':
            lista_sinks.append(node)
    return lista_sinks


def verificacion_lista(lista01, lista02):
    if len(lista01) != len(lista02):
        return False
    else:
        vector_valores = []
        for n in range(0, len(lista02)):
            if lista01[n] == lista02[n]:
                vector_valores.append(True)
            else:
                vector_valores.append(False)
        if all(vector_valores):
            return False





class ex_map_no_multi:
    """the class benchmark new version is in fact the exhaustive algorithm, in here we condense all the functions
    for the mapping. The inputs of this class are:

        DG = hardware graph without the rd, rw, ri and rm nodes. In this graph we only have the rp and rmux, because 
        those are the only ones that can be mapped (note that rmux can not be mapped but it affects the datapaths)

        In the init we copy this graph to the following variables:

        self.DG
        self.DG_original
        self.DG_copia

        AG = application graph without the interface nodes, only the tasks.

        In the init we copy this graph to the following variables:

        self.AG
        self.AG_original
        self.AG_copia

        datapaths = originally this input was a list of the possible datapaths of the hardware but in this class is not
        used as it is an exhaustive mapping.

        In the init we copy this variable to self.datapaths

        vector_type_of_tasks = originally this was a list with all the types of the tasks, also is no longer used in 
        this class.

        In the init we copy this variable to self.vector_types_of_tasks

        dict_nodes = dictionary with the information of the nodes that integrates the DG graph, the contents and 
        structure is defined in the parser_info readme

        In the init we copy this dictionary to self.dict_nodes

        dict_info = dictionary with the information of the configuration and latency functions, the contents and 
        structure is defined in the parser_info readme

        In the init we copy this dictionary to self.dict_info

        selection_prints = variable that defines the verbosity 

        In the init we copy this variable to self.s_prints

        dict_nodes_a = dictionary with the information of the nodes thazt integrates the AG graph, the contents and 
        structure is defined in the parser_info readme

        In the init we copy this dictionary to self.dict_nodes_a

        selection_pause = variable that defines if we are going to have the pauses during the mapping process

        In the init we copy this variable to self.s_pause

        dict_info_a = dictionary with the information of the total application graph, which is the graph that includes 
        the interface nodes and the tasks

        In the init we copy this dictionary to self.dict_info_a

        DG_total = hardware graph that includes all the hardware resources

        In the init we copy this graph to the following graphs

        self.DG_total
        self.DG_total_original

        AG_total = application graph that includes all the tasks and interfaces nodes

        In the init we copy this graph to the following graphs

        self.AG_total
        self.AG_total_original

        dict_total = dictionary with the information of the nodes that integrates the DG_total graph, the contents and
        structure are defined in the parser_info readme

        In the init we copy this dictionary to self.dict_total

        lista_constraints = list with the hardware resources that are going to be used to allocate a certain set of 
        tasks, this is used to debug or to define the allocation of a special task

        In the init we copy this list to self.lista_constraints

        lista_tareas_constrains = list with the tasks that are going to be allocated to a certain set of hardware 
        resources, this list is related to the lista_constraints, in the sense that the first element (task) of this 
        list will be mapped to the first element of the lista_constraints (hardware resource).

        In the init we copy this list to self.lista_tareas_constrains

    The main function of this class is the mapping function, which produce the list of all the mappings with its 
    corresponding list of the special nodes, the outputs that we require to perform the evaluation. 

    """""

    def __init__(self, DG, AG, debug_info, vector_type_of_tasks, dict_nodes,
                 dict_info, selection_prints, dict_nodes_a, selection_pause, dict_info_a, DG_total, AG_total,
                 dict_total,
                 lista_constraints, lista_tareas_constrains,directorio):
        """
        in here we copy the inputs to attributes of the class. Another process is the obtention of two types of sinks
        of the DG_total, one all the sinks (using obtencion_sinks function) and the other the sinks that are
        connected to a rw (using sinks_connected_to_rc function). We make a distintion because the sinks that are
        connected to a rw are the only one that can be used to memorize (store) partial results to be used or in
        another pipeline or in another time slot.

        :param DG: hardware graph with only rp and rmux
        :param AG: application graph with only tasks
        :param debug_info: type of debug
        :param vector_type_of_tasks: not used
        :param dict_nodes: dictionary of the DG graph
        :param dict_info: dictionary with the functions of latency and configuration of the hardware model
        :param selection_prints: variable that defines the verbosity
        :param dict_nodes_a: dictionary of the AG graph
        :param selection_pause: variable that defines if we will have pauses or not during the mapping process
        :param dict_info_a: dictionary with the information of the AG_total
        :param DG_total: complete hardware graph with all the types of nodes
        :param AG_total: complete application graph with all the types of nodes
        :param dict_total: dictionary with the information of the DG_total graph
        :param lista_constraints: list that contains the constraints, both the task to the assigned resource
        :param lista_tareas_constrains: list of the constrained tasks
                examples:
                self.lista_constraints = [['t0','r0'],['t1','r1'],['t2','r2'],['t3','r3'],['t4','r6']]
                self.lista_tareas_constrains = ['t1','t0','t2','t3','t4']
        """

        self.AG_original = AG.copy()
        self.AG = AG.copy()
        self.AG_copia = AG.copy()
        self.dict_nodes_a = dict_nodes_a

        self.DG_original = DG.copy()
        self.DG = DG.copy()
        self.DG_copia = DG.copy()
        self.dict_nodes = dict_nodes

        self.AG_total_original = AG_total.copy()
        self.AG_total = AG_total.copy()
        self.dict_info_a = dict_info_a

        self.DG_total_original = DG_total.copy()
        self.DG_total = DG_total.copy()
        self.dict_total = dict_total

        self.dict_info = dict_info

        self.s_pause = selection_pause
        self.s_prints = selection_prints

        self.debug_info = debug_info
        self.vector_type_of_tasks = vector_type_of_tasks

        self.lista_constraints = lista_constraints
        self.lista_tareas_constrains = lista_tareas_constrains

        self.list_sinks_connected_to_rc = self.sinks_connected_to_rc()

        self.lista_sinks_DG_total = obtencion_sinks(DG_total)
        self.bandera_time_slots = False
        self.directorio = directorio


    def sinks_connected_to_rc(self):
        list_sinks_connected_to_rc = []
        bandera_salida = True
        for nodo in self.DG_original.nodes:
            # print(nodo)
            # print(self.dict_nodes[nodo])
            edges_nodo = self.dict_nodes[nodo]['edges']
            bandera_salida = True
            for i in edges_nodo:
                # print(f"edge {i}")
                if i:
                    for n, data in self.dict_total.items():
                        if data['name'] == i:
                            if data['type'] == 'rw' or data['type'] == 'ri':
                                list_sinks_connected_to_rc.append(nodo)
                                bandera_salida = False
                                break
                if not bandera_salida:
                    break
        # if list_sinks_connected_to_rc:
        #     pass
        # else:
        #     list_sinks_connected_to_rc = obtencion_sinks(self.DG_copia)
        # print(list_sinks_connected_to_rc)
        # input("detalles")
        return list_sinks_connected_to_rc

    def verification_of_dependence(self, predecessors, element_list, element_buffer, resource, nodo_AG, instancia):
        """
        in this function we verify the data dependence between a task and its predecessors, the idea is to find where
        the predecessors are mapped and then try to see if there is a path that connects those resources to the
        resource where we want to map the task, and by doing that we obtain also the copy nodes necessary for the
        mapping
        :param predecessors: list of the predecessors of the task (nodo_AG)
        :param element_list: preliminary mapping (current slot)
        :param element_buffer: preliminary mapping (all slots)
        :param resource:  the candidate
        :param nodo_AG:  the task
        :param instancia: im not sure if we use this
        :return: a flag that represents if we can map the task to the resource or not, a list of the special nodes
        and also inside this function we update the list of copy nodes to be added
        todo: verify the instancia input
        """
        # first we reinitialize the list of copy nodes
        self.lista_nodos_copy = []
        if nodo_AG == 2 and resource == 1:
            self.bandera_debug = False
        else:
            self.bandera_debug = False
        if self.bandera_debug or self.s_prints == 'testexh':
            print("inside of the verification of dependence function ")
        if self.s_prints == 'testexh':
            print("new item")
        # some internal variables
        special_nodes_list = []
        same_time_slot = True
        # final flag True if the data dependency is correct
        valid_place = False
        vector_valid_places = []
        self.bandera_time_slots = False
        # now we are going to iterate for each predecessor
        for predecessor in predecessors:
            if self.s_prints == 'basic' or self.bandera_debug:
                print("predecesor", predecessor)
            # we check if the predecessor is in the same slot using the attribute self.lista_mapping
            node_place = None
            for h in self.lista_mapping:
                if h[0]:
                    if predecessor == h[1]:
                        node_place = h[2]
            if self.s_prints == 'debug' or self.bandera_debug:
                print(f"the node place is {node_place}")
            # if the predecessor is not in the same time slot we need to iterate over the previous time slots
            if self.s_prints == 'testexh':
                # print(f"JISDJSDJD {predecessors} kdsjksd {predecessor}")
                print(f"the element list is  {element_list}")
                print(node_place)
            if node_place == None:
                same_time_slot = False
                contador_time_slots = 0
                if self.s_prints == 'testexh':
                    print("the predecessors and the task ", predecessors, predecessor, nodo_AG)
                    print("the element buffer is ", element_buffer)

                for n_time_slot in range(0, len(element_buffer)):
                    ins = element_buffer[n_time_slot]
                    if self.s_prints == 'testexh':
                        print("the instance is ", ins)
                    for u in ins:
                        if self.s_prints == 'debug' or self.bandera_debug:
                            print(u)
                        if u[0]:
                            if predecessor == u[1]:
                                node_place = u[2]
                                contador_time_slots += n_time_slot
                                break

                # except:
                #     pass
                #     # for instancia in element_list:
                #     #     if self.s_prints == 'testexh':
                #     #         print("la instancia", instancia)
                #     #     for u in instancia:
                #     #         if self.s_prints == 'debug' or self.bandera_debug:
                #     #             print(u)
                #     #         if u[0]:
                #     #             if predecessor == u[1]:
                #     #                 node_place = u[2]
                #     #                 break
                #     #     contador_time_slots += 1

                if self.s_prints == 'testexh' or self.bandera_debug:
                    print("node place", node_place, " and it is in time slot ", contador_time_slots)
            # now we have the place of the predecessor
            # we are going to have two cases, if the predecessor is in the same slot or not
            if same_time_slot:
                if self.s_prints == 'testexh':
                    print("mismo slot ", node_place,resource)
                # we obtain the paths from the predecessor to the resource
                paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                if self.s_prints == 'testexh':
                    print("We are going to print the paths", paths, " between ", node_place, "and ", resource)
                # in this list we are going to store the data of the nodes of the path
                vector_dependency_02 = []
                flag_recomputation = False
                bandera_salida = False
                if paths:
                    # if there are paths it means that there is no need for a recomputation node
                    # for path_b in paths:
                    # print("jbksdfs")
                    while paths:
                        # print("test entry to paths")
                        path_b = min(paths, key=len)
                        paths_copy = paths.copy()
                        for i in range(0, len(paths_copy)):
                            if paths_copy[i] == path_b:
                                dummy = paths.pop(i)
                        path = list(path_b)
                        path.remove(node_place)

                        # esto es para indicar los nodos copy
                        path_buffer = list(path)
                        path_buffer.remove(resource)

                        ##################################

                        vector_dependency_01 = []
                        for node in path:

                            if self.lista_mapping[node][0]:  # and self.lista_mapping[node][2] != 'copy':#

                                vector_dependency_01 = vector_dependency_01 + [self.lista_mapping[node][0]]
                        if True in vector_dependency_01:
                            vector_dependency_02 = vector_dependency_02 + [False]
                        else:  #
                            self.lista_nodos_copy = self.lista_nodos_copy + path_buffer  #
                            bandera_salida = True
                        if bandera_salida:
                            break

                    if not False in vector_dependency_02:
                        valid_place = True
                else:
                    # because the predecessor is not in the same path we assume that we need a recomputation node
                    # we are going to verify two things, that the predecessor is mapped to a resources that is a sink
                    # or has a direct path to a sink without any mapped node, and that the resource candidate is a source
                    # or he can be reached from a source node without any mapped node in the path
                    flag_recomputation = True
                    # print\
                    #     ("There are not paths, we are going to verify the dependency in the others paths", node_place,self.list_sinks_connected_to_rc)
                    valid_sink = False
                    valid_source = False
                    # if the predecesor is a sink or has a direct path to a sink without any mapped node
                    if node_place in self.list_sinks_connected_to_rc:
                        sink_buffer = node_place
                        valid_sink = True
                    else:
                        # because the predecessor is not a sink node we search for a sink node that is reachable from
                        # the predecessor
                        # print("We are going to check if the predecessor is mapped to a node that can reach a sink")

                        #############""
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            # print(sink_nodo_sink_task,resource)
                            if self.lista_mapping[sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    # copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place)
                                    done = False
                                    break

                            else:
                                done = False
                                break

                        #########"""

                        sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)
                        if self.s_prints == 'testexh':
                            print("el sink en verificacion de algo ",sink)
                        path_to_sink = simple_paths_from_two_nodes(self.DG, node_place, sink)
                        vector_02 = []
                        if path_to_sink:
                            while path_to_sink:
                                # for single_path in path_to_sink:
                                path_b = min(path_to_sink, key=len)
                                paths_copy = path_to_sink.copy()
                                for i in range(0, len(paths_copy)):
                                    if paths_copy[i] == path_b:
                                        dummy = path_to_sink.pop(i)
                                single_buffer = list(path_b)
                                single_buffer.remove(node_place)

                                # esto es para indicar los nodos copy
                                path_buffer = list(single_buffer)
                                if resource in path_buffer:
                                    path_buffer.remove(resource)
                                self.lista_nodos_copy = self.lista_nodos_copy + path_buffer
                                # self.lista_nodos_copy = path_buffer
                                ##################################

                                vector_01 = []
                                for no in single_buffer:
                                    vector_01 = vector_01 + [self.lista_mapping[no][0]]
                                # print(vector_01)
                                if True in vector_01:
                                    vector_02 = vector_02 + [False]
                                else:
                                    vector_02 = vector_02 + [True]
                                    break
                            if False in vector_02:
                                valid_sink = False
                            else:
                                valid_sink = True
                                # path_buffer = list(single_buffer)
                                # if resource in path_buffer:
                                #     path_buffer.remove(resource)
                                # self.lista_nodos_copy = self.lista_nodos_copy + path_buffer
                                sink_buffer = sink

                        else:
                            valid_sink = False
                    # After the verification of the predecessor, we need to verify also de resource candidate
                    # print("odsfsdfds",resource,self.sources_DG)
                    if resource in self.sources_DG:
                        valid_source = True
                        source_buffer = resource
                    else:
                        # print("We are going to check if the resource is reachable from a source node")
                        source = source_node_from_any_node(self.DG, self.sources_DG, resource)
                        path_to_source = simple_paths_from_two_nodes(self.DG, source, resource)
                        vector_02 = []
                        if path_to_source:
                            # while path_to_source:
                            for single_path in path_to_source:
                                # path_b = min(path_to_source, key=len)
                                # paths_copy = path_to_sink.copy()
                                # for i in range(0, len(paths_copy)):
                                #     if paths_copy[i] == path_b:
                                #         dummy = path_to_sink.pop(i)
                                # single_buffer = list(path_b)
                                single_buffer = list(single_path)
                                single_buffer.remove(resource)

                                # esto es para indicar los nodos copy
                                path_buffer = list(single_buffer)
                                if resource in path_buffer:
                                    path_buffer.remove(resource)
                                self.lista_nodos_copy = self.lista_nodos_copy + path_buffer
                                ##################################

                                vector_01 = []
                                for no in single_buffer:
                                    vector_01 = vector_01 + [self.lista_mapping[no][0]]
                                # print(vector_01)
                                if True in vector_01:
                                    vector_02 = vector_02 + [False]
                                # else:
                                #     vector_02 = vector_02 + [True]
                                #     break
                            if False in vector_02:
                                valid_source = False
                            else:
                                valid_source = True
                                source_buffer = source
                        else:
                            valid_source = False
                    # if both conditions are meet we can say that the predecessor is in a valid place
                    if valid_source and valid_sink:
                        valid_place = True
                        # as the mapping is valid we create a special node to specify the re-computation
                        # print("test of recomputation node",sink_buffer,source_buffer,nodo_AG)

                        if not isinstance(element_buffer[0][0], bool):
                            numero_time_slots = len(element_buffer) - 1

                        else:
                            numero_time_slots = 0

                        dummy_buffer = [False, sink_buffer, source_buffer, numero_time_slots, 0]
                        special_nodes_list.append(dummy_buffer)
                    # valid_place = False
            else:
                # in this case, the predecessor is not mapped in the same time slot
                try:
                    if self.s_prints == 'basic':
                        print(node_place, self.sinks_DG)
                        if node_place == None:
                            print(element_buffer)
                        print("The predecessor is not in the same time slot")
                    if node_place in self.list_sinks_connected_to_rc:
                        nodo_sink = node_place
                    else:
                        #### este es un bug tenemos que checar bien que pasa
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            # print(sink_nodo_sink_task,resource)
                            if element_buffer[contador_time_slots][sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    # copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()

                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place)
                                    done = False
                                    break

                            else:
                                done = False
                                break

                        nodo_sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)
                        # nodo_sink = sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc.sort(reverse=True), node_place)
                    # print("bug 05")
                    if resource in self.sources_DG:
                        nodo_source = resource
                    else:
                        nodo_source = source_node_from_any_node(self.DG, self.sources_DG, resource)

                    #############proceso para el source dentro de lista mapping
                    bandera_mapping_valido_time_slots_source = False
                    bandera_mapping_valido_time_slots_sink = False
                    paths_sources = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                    if paths_sources:

                        while paths_sources:
                            # for path in paths_sources:

                            path_buffer = paths_sources.pop()
                            path_buffer.remove(nodo_source)
                            path_buffer.remove(resource)

                            vector_01 = []
                            for no in path_buffer:
                                vector_01 = vector_01 + [self.lista_mapping[no][0]]
                            # print(vector_01)
                            if not True in vector_01:
                                bandera_mapping_valido_time_slots_source = True
                                vector_02 = vector_02 + [False]
                                self.lista_nodos_copy = self.lista_nodos_copy + path_buffer
                                break

                    ############proceso para el sink dentro de element buffer
                    paths_sinks = simple_paths_from_two_nodes(self.DG, node_place, nodo_sink)
                    if paths_sinks:
                        # for path in paths_sinks:
                        while paths_sinks:

                            path_b = min(paths_sinks, key=len)

                            path_buffer_respaldo = list(path_b)
                            path_b.remove(node_place)
                            path_b.remove(nodo_sink)
                            vector_01 = []
                            if path_b:
                                for nod_path in path_b:
                                    vector_01 = element_buffer[contador_time_slots][nod_path][0] + vector_01
                            if not True in vector_01:
                                bandera_mapping_valido_time_slots_sink = True
                                break
                            else:
                                for n in range(0, len(paths_sinks)):
                                    if paths_sinks[n] == path_buffer_respaldo:
                                        paths_sinks.remove(n)
                                        # break

                    self.lista_nodos_copy_time_slot = []
                    if bandera_mapping_valido_time_slots_sink and bandera_mapping_valido_time_slots_source:

                        self.lista_nodos_copy_time_slot = self.lista_nodos_copy_time_slot + path_buffer_respaldo

                        # item_to_append = [True, nodo_sink, nodo_source, len(element_buffer)-1, 0]
                        item_to_append = [True, nodo_sink, nodo_source, contador_time_slots, 0]
                        special_nodes_list.append(item_to_append)
                        valid_place = True
                        # tenemos que obtener los paths para agregar los nodos copy
                        # empecemos
                        # paths_sources = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                        # if paths_sources:
                        #     for path in paths_sources:
                        #         path_buffer = list(path)
                        #         path_buffer.remove(nodo_source)
                        #         path_buffer.remove(resource)
                        #         self.lista_nodos_copy = self.lista_nodos_copy + path_buffer

                        self.time_slot_copy_nodes = contador_time_slots
                        self.bandera_time_slots = True
                        # paths_sinks = simple_paths_from_two_nodes(self.DG, node_place, nodo_sink)
                        # if paths_sinks:
                        #     for path in paths_sinks:
                        #         path_b = min(paths_sinks, key=len)
                        #
                        #         path_buffer = list(path_b)
                        #         path_buffer.remove(node_place)
                        #         path_buffer.remove(nodo_sink)
                        #         self.lista_nodos_copy_time_slot = self.lista_nodos_copy_time_slot + path_buffer
                        #         break
                    else:
                        valid_place = False
                except:
                    valid_place = False

            vector_valid_places = vector_valid_places + [valid_place]
        if self.bandera_debug or self.s_prints == 'testexh':
            print("vector valid places", vector_valid_places)
            # input("debug verification of dependence - Enter to continue")
        if False in vector_valid_places:
            final_valid = False
            self.bandera_time_slots = False
        else:
            final_valid = True
            # for i in self.lista_nodos_copy_time_slot:

        return final_valid, special_nodes_list

    def verification_of_parameters(self, node_AG, resource):
        """
        in this function we verify that all the parameters of the task are compatible with the parameters of the
        resource
        :param node_AG: task to map
        :param resource:  resource where the task are going to map
        :return: a list where if all its elements are True the task can be mapped to the resource, otherwise no
        """
        # this is the list where we are going to store the info (True or False elements)
        new_validacion_parameters = []
        # we verify if the type of task is in the list of tasks that the resource can perform, this is a double check
        # normally this is checked before of the function call, but for the constraints mapping it could be not done
        # so we need to check, if it is not in the list we raise an error
        try:
            test_01 = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']
        except:
            print(f" A possible error in the constrain file occurred, as this part is verified otherwise")
            raise ValueError(f" The task name is {self.dict_nodes_a[node_AG]['name']}, please verify the constrain")

        if self.s_prints == 'basic':
            # basic validation of data
            print("we enter the function of verification of parameters")
            print(self.AG_copia[node_AG])

        # the task may have or not parameters, if the task does not have parameters it should appear as None
        # because of this the first verification is that one
        if self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'] == None:
            # because the task does not have parameters we dont need to do more, we append the list with a True
            new_validacion_parameters.append(True)
        else:
            # Now because the task has parameters we need to check each one of them, so we use a for loop
            for param in self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']:
                # we check if the parameters values are a range of values of a set of fixed values
                if isinstance(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0],
                              str):
                    # for this case the parameters are a set of fixed values
                    # first we grab all the values, what we do is from the dict_nodes we retrieve all the parameters
                    # we check if the parameters are a list of values, strings of boolean and we store them
                    vector_param_values = []
                    if len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][
                               0]) == 1:
                        vector_buffer = [
                            self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]]
                    else:
                        vector_buffer = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                            param]
                    for param_value in vector_buffer:  # self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]:
                        try:
                            vector_param_values.append(int(param_value))
                        except:
                            vector_param_values.append(param_value)
                    if vector_param_values == ['boolean']:
                        vector_param_values = ['False', 'True']
                        if self.s_prints == 'basic':
                            print("validation of the boolean verification", vector_param_values)
                            print(self.dict_nodes_a)
                    for param_value in self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                        param]:
                        try:
                            vector_param_values.append(int(param_value))
                        except:
                            vector_param_values.append(param_value)

                    # we got the values, so we check if the value that we want to assign to this resource is valid,
                    # also we verify if the parameter is in the list if not we raise an error
                    if param in self.dict_nodes_a[node_AG]['param']:
                        if self.dict_nodes_a[node_AG]['param'][param] in vector_param_values:
                            new_validacion_parameters.append(True)
                            # print("the value is valid")
                        else:
                            new_validacion_parameters.append(False)
                            # print("the value is not valid")
                    else:
                        raise UnboundLocalError(
                            f"parameter {param} is not described in the parameters of task {self.dict_nodes_a[node_AG]['name']}")
                else:
                    if self.s_prints == 'basic':
                        # basic validation that the parameter is a range
                        print(param)
                    # in here the value is in a range, in the parsing we put only two values the lower and upper limit
                    # first we check if the parameter in part of the parameters of the task, if not we can either put false and
                    # not use the resource or if the resource has default values we can go with it, this feature needs to be added
                    try:
                        if self.dict_nodes_a[node_AG]['param'][param] >= \
                                self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                    param][0] and self.dict_nodes_a[node_AG]['param'][param] <= \
                                self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                    param][1]:
                            if self.s_prints == 'basic':
                                print("the value is valid 01")
                            new_validacion_parameters.append(True)
                        else:
                            if self.s_prints == 'basic':
                                print("the value is not valid 01")
                            new_validacion_parameters.append(False)
                    except:
                        raise UnboundLocalError(
                            f"parameter {param} is not described in the parameters of task {self.dict_nodes_a[node_AG]['name']}")
        if self.s_prints == 'basic':
            print(f" we exit the verification of parameters function, the fina result is {new_validacion_parameters}")
        return new_validacion_parameters

    def verification_of_source(self, node_AG, resource):
        """
        in this function we verify that the sources of both the application total graph and the hardware total graph
        are compatible, in this sense, if the task that we want to map is a source node of the application graph we
        verify that the source node connected to this task is compatible with the sources nodes that are connected
        to the resources where we want to map the task, if the node is not a source node of the application graph we
        only retrieve the information about the sensor

        :param node_AG: node of the application graph
        :param resource:  node of the hardware graph
        :return:    bandera_source_of_data that represents if the sources are compatible or not
                    info_sensor information about that particular sensor
        """
        bandera_source_of_data = False
        info_sensor = []
        if self.s_prints == 'basic':
            print(f"we are at the verification source function with the task {node_AG} and resource {resource}")

        # if the task node is a source node we enter the main cycle if not we retrive only the information about
        # the sensor
        if node_AG in self.sources_AG:
            if self.s_prints == 'basic':
                print("it is a source node")
            # the task node is a source node so we need to retrieve its information and find its predecessor in the
            # application total graph
            lugar_nodo = None
            # we find the node number in the dictionary of the application total graph
            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            # lista_sources_ag_total = obtencion_sources(self.AG_total)
            # we obtain its predecessor in the application total graph
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         self.sources_AG_total,
                                                         lugar_nodo)

            if self.s_prints == 'basic':
                print("data verification of the source node", self.AG_total.nodes[source_total_app]['par']['height'])

            # now we have the source node in the application total graph, we need the source node in the hardware
            # total graph
            lugar_nodo = None
            for n, data in self.dict_total.items():
                if self.dict_nodes[resource]['name'] == self.dict_total[n][
                    'name']:
                    lugar_nodo = n
            # lista_sources_dg_total = obtencion_sources(self.DG_total)
            # we obtain the source node from the hardware total graph
            source_total_hw = source_node_from_any_node(self.DG_total,
                                                        self.sources_DG_total,
                                                        lugar_nodo)
            if self.s_prints == 'basic':
                print(f"the source in app total is {source_total_app} the source in hw total is {source_total_hw}")

            ########################################
            ## in this process we verify that the types are the same, we make a distinction between
            ## memory and interface, memory refers to a memory block maybe a debug module or something like that and
            ## interface is a normal source of data

            # we check the properties of both source nodes to be sure that they are compatible, in here we only check
            # the types but we can add another verification of parameters
            # todo: add the verification of parameters
            if self.dict_total[source_total_hw]['type'] == 'ri' and \
                    self.dict_info_a[source_total_app][
                        'op'] == 'interface':
                bandera_source_of_data = True
            elif self.dict_total[source_total_hw]['type'] == 'rm' and \
                    self.dict_info_a[source_total_app]['op'] == 'memory':
                bandera_source_of_data = True
            else:
                bandera_source_of_data = False

            # now we verify if the sources are compatible and store the result in bandera_source_of_data, next we
            # retrieve the information of the sensor and store in info_sensor, and the information is
            # 1.- the name of the source node
            # 2.- the height
            # 3.- the width
            # todo: in here we need to generalize to not only images but a matrix or something like that
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
        else:

            # if we enter this branch it means that the task is not a source node of the application graph, so we only
            # retrieve the information of the sensor node associate to this task
            # lista_sources_ag_total = obtencion_sources(self.AG_total)
            if node_AG in self.sources_AG_total:
                source_total_app = node_AG
            else:
                source_total_app = source_node_from_any_node(self.AG_total,
                                                             self.sources_AG_total,
                                                             node_AG)

            if self.s_prints == 'basic':
                print(
                    f"the tasks is not a source task, but the information of the source is {self.AG_total.nodes[source_total_app]}")
            # we retrieve the information of the source task and store it to the same variable info_sensor with the
            # same structure and put the bandera_source_of_data in true
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
            bandera_source_of_data = True

        if self.s_prints == 'basic':
            print(
                f"we exit the verification of source function and the data of the source is {info_sensor} and the flag is {bandera_source_of_data}")
        return bandera_source_of_data, info_sensor

    def verification_of_source_dummy(self, node_AG, resource):
        bandera_source_of_data = False
        if self.s_prints == 'basic':
            print("ANOTHER CHANGE")
            print(self.sources_AG)
        if node_AG in self.sources_AG:
            if self.s_prints == 'basic':
                print("it is a source node")
                print(self.dict_nodes_a)
                print(self.dict_info_a)
                print(self.dict_total)
                print(self.dict_nodes)
            lugar_nodo = None
            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         lugar_nodo)
            lugar_nodo = None
            for n, data in self.dict_total.items():
                if self.dict_nodes[resource]['name'] == self.dict_total[n][
                    'name']:
                    lugar_nodo = n
            lista_sources_dg_total = obtencion_sources(self.DG_total)
            source_total_hw = source_node_from_any_node(self.DG_total,
                                                        lista_sources_dg_total,
                                                        lugar_nodo)
            # print(source_total_app,source_total_hw)
            ########################################
            ############ aqui podemos cambiar lo que checamos y sus nombres
            if self.dict_total[source_total_hw]['type'] == 'ri' and \
                    self.dict_info_a[source_total_app][
                        'op'] == 'interface':
                bandera_source_of_data = True
            elif self.dict_total[source_total_hw]['type'] == 'rm' and \
                    self.dict_info_a[source_total_app]['op'] == 'memory':
                bandera_source_of_data = True
            else:
                bandera_source_of_data = False
        else:
            bandera_source_of_data = True

        return bandera_source_of_data

    def info_resource(self, name_task):
        """
        this function returns the information of the resources which is linked to a task by the list of contrains.
        one of the features of the framework is that we can provide a list of constrains where we assign directly
        a task to a resource. This function is part of that process.
        :param name_task: the name of the task according to the application dictionary
        :return: the resource name and node number
        """
        # first we obtain the name of the resource, because in the list of constrains we only define the names of the
        # task and the resource, so we retrieve this information from the self.lista_constraints and assign it to the
        # variable name_resource
        name_resource = None
        for parejas in self.lista_constraints:
            if parejas[0] == name_task:
                name_resource = parejas[1]
        # now that we have the name of the resource we look for the node number from the hardware resources dictionary,
        # then we assing this information to the variable resource
        resource = None
        for n, data in self.dict_nodes.items():
            if name_resource == data['name']:
                resource = n
        # now that we have both the name and the node number we return those values
        return resource, name_resource

    def obtention_latency_copy_node(self, resource):
        """
        in this function we retrieve the information about the latency of the copy operation, with the resource
        as input we search in the dict_nodes from the specific latency
        :param resource:
        :return: latency of the copy operation of a specific resource
        """
        latency_variable = self.dict_nodes[resource]['ops']['copy']['clk']
        # print(self.dict_info)
        latency = None
        for n in self.dict_info['functions_res']:
            if n == latency_variable:
                latency = self.dict_info['functions_res'][n]
        return latency

    def only_actuator_sink(self, node_AG, resource):
        actuator_sink = None
        if node_AG in self.sinks_AG and resource not in self.sinks_DG:
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                          self.sinks_DG,
                                                          resource)
            path_sink_node = simple_paths_from_two_nodes(self.DG_copia,
                                                         resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'basic':
                print("the paths between the sink task and the sink hardware",
                      path_sink_node)
                print(
                    f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            single_path = path_sink_node.pop()
            single_path.remove(resource)
            # for nodo_a_sink in single_path:
            #     self.lista_mapping[nodo_a_sink] = [True, None, 'copy', 'copy', 0, nodo_a_sink,
            #                                        0, 0, latency, latency, 0, 0, 0]
            lugar_sink_t = None
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == \
                        self.DG_copia.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.lista_sinks_DG_total.copy()
            while done:
                sink_test = copia_sinks.pop()
                if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t, sink_test):
                    actuator_sink = sink_test
                    done = False
                    break
        return actuator_sink

    def generation_copy_nodes_time_slot(self, node_AG, resource, first_time_special, bandera_anexion_time, nodo_sink,
                                        node_place_buffer, element_buffer, nodo_source, node_place,
                                        contador_time_slots):
        p_buffer = []
        latency = self.obtention_latency_copy_node(resource)
        bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)

        elemento_buffer_copy = copy.deepcopy(element_buffer)
        if self.s_prints == 'testexh':
            print(elemento_buffer_copy)
            print("estamos en algo generacion copy nodes", node_AG, first_time_special, bandera_anexion_time, nodo_sink,
                  node_place_buffer, node_place, self.list_sinks_connected_to_rc)
        # input("testtsts")
        #### aqui hay un error en las banderas asi que para un quick fix se adicionara un try

        try:
            if first_time_special or not bandera_anexion_time:
                if node_place_buffer not in self.list_sinks_connected_to_rc:
                    if element_buffer[nodo_sink][0]:
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        copy_list_sinks_connected_to_rc.remove(nodo_sink)

                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            # print("testetstetst",sink_nodo_sink_task,resource,copy_list_sinks_connected_to_rc)

                            if element_buffer[sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place_buffer)
                                    done = False
                                    break

                            else:
                                done = False
                                break
                        nodo_sink = sink_nodo_sink_task
                    else:
                        pass

                    # input("verificacion")
                    path = simple_paths_from_two_nodes(self.DG, node_place_buffer, nodo_sink)
                    # print(path,node_place_buffer,nodo_sink,min(path, key=len))
                    if path:
                        p_buffer = min(path, key=len)
                        if node_place_buffer in p_buffer:
                            p_buffer.remove(node_place_buffer)
                        # for p in path:
                        #     p_buffer = list(p)
                        #     p_buffer.remove(node_place_buffer)
                    ########aqui estaos haciendo los cambios entre self.lista_mapping y elemento_buffer
                    if p_buffer:
                        for nodo in p_buffer:
                            # if element_buffer[nodo][0] and element_buffer[nodo][3] != 'copy':
                            if element_buffer[nodo][0] and element_buffer[nodo][3] != 'copy':
                                pass
                            else:

                                element_buffer[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]
                    if self.s_prints == 'basic':
                        print("testbu", p_buffer, node_place)
                        print(element_buffer)
                        # input("verificacion")
                path = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                p_buffer_ss = []
                for p in path:
                    p_buffer_ss = list(p)
                    p_buffer_ss.remove(resource)
                if p_buffer_ss:
                    for nodo in p_buffer_ss:
                        if self.lista_mapping[nodo][0] and self.lista_mapping[nodo][3] != 'copy':
                            pass
                        else:
                            self.lista_mapping[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]

            else:
                if self.s_prints == 'testexh':
                    print("estamos en no se que cosq 01 - test", element_buffer[contador_time_slots - 1][nodo_sink][0])
                    print(nodo_sink)
                ####
                if node_place_buffer not in self.list_sinks_connected_to_rc:
                    if element_buffer[contador_time_slots - 1][nodo_sink][0]:
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        copy_list_sinks_connected_to_rc.remove(nodo_sink)
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            # print(sink_nodo_sink_task,resource)
                            if element_buffer[contador_time_slots - 1][sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place_buffer)
                                    done = False
                                    break

                            else:
                                done = False
                                break
                        nodo_sink = sink_nodo_sink_task
                    else:
                        if self.s_prints == 'testexh':
                            print("algo pasa aqui",nodo_sink,node_place_buffer)
                        pass
                    # if self.s_prints == 'testexh':
                    #     print("pasamos",nodo_sink,node_place_buffer)
                    path = simple_paths_from_two_nodes(self.DG, node_place_buffer, nodo_sink)
                    if path:
                        p_buffer = min(path, key=len)
                        if node_place_buffer in p_buffer:
                            p_buffer.remove(node_place_buffer)
                        # for p in path:
                        #     p_buffer = list(p)
                        #     p_buffer.remove(node_place)
                    # element_buffer = self.master_elemento_buffer.copy()
                    if p_buffer:
                        for nodo in p_buffer:
                            if element_buffer[contador_time_slots - 1][nodo][0] and \
                                    element_buffer[contador_time_slots - 1][nodo][3] != 'copy':
                                pass
                            else:
                                # pass
                                element_buffer[contador_time_slots - 1][nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                                                 0, 0, latency, latency, info_sensor, 0, 0]

                path = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                p_buffer_ss = []
                for p in path:
                    p_buffer_ss = list(p)
                    p_buffer_ss.remove(resource)
                if p_buffer_ss:
                    for nodo in p_buffer_ss:
                        if self.lista_mapping[nodo][0] and self.lista_mapping[nodo][3] != 'copy':
                            pass
                        else:
                            self.lista_mapping[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]
        except:
            # pass # esta seccion puede no ser ya necesaria

            element_buffer = copy.deepcopy(elemento_buffer_copy)
            # element_buffer = elemento_buffer_copy.copy()
            ##########
            if self.s_prints == 'testexh':
                print("estamos en no se que cosq 08", element_buffer[nodo_sink])
                print(nodo_sink, contador_time_slots)

            if contador_time_slots > 0:
                if node_place_buffer not in self.list_sinks_connected_to_rc:
                    if element_buffer[contador_time_slots - 1][nodo_sink][0]:
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        copy_list_sinks_connected_to_rc.remove(nodo_sink)
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            # print(sink_nodo_sink_task,resource)
                            if element_buffer[contador_time_slots - 1][sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place_buffer)
                                    done = False
                                    break

                            else:
                                done = False
                                break
                        nodo_sink = sink_nodo_sink_task
                    else:
                        pass

                    ###########
                    path = simple_paths_from_two_nodes(self.DG, node_place_buffer, nodo_sink)
                    if path:
                        p_buffer = min(path, key=len)
                        if node_place_buffer in p_buffer:
                            p_buffer.remove(node_place_buffer)
                        # for p in path:
                        #     p_buffer = list(p)
                        #     p_buffer.remove(node_place)
                    if p_buffer:
                        for nodo in p_buffer:
                            if element_buffer[contador_time_slots - 1][nodo][0] and \
                                    element_buffer[contador_time_slots - 1][nodo][3] != 'copy':
                                pass
                            else:
                                element_buffer[contador_time_slots - 1][nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                                                 0, 0, latency, latency, info_sensor, 0, 0]
                path = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                p_buffer_ss = []
                for p in path:
                    p_buffer_ss = list(p)
                    p_buffer_ss.remove(resource)
                if p_buffer_ss:
                    for nodo in p_buffer_ss:
                        if self.lista_mapping[nodo][0] and self.lista_mapping[nodo][3] != 'copy':
                            pass
                        else:
                            self.lista_mapping[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]



            else:
                if node_place_buffer not in self.list_sinks_connected_to_rc:
                    if element_buffer[nodo_sink][0]:
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        copy_list_sinks_connected_to_rc.remove(nodo_sink)
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place_buffer)
                            print(sink_nodo_sink_task, resource)
                            if element_buffer[sink_nodo_sink_task][0]:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place_buffer)
                                    done = False
                                    break

                            else:
                                done = False
                                break
                        nodo_sink = sink_nodo_sink_task
                    else:
                        pass

                    ###########
                    path = simple_paths_from_two_nodes(self.DG, node_place_buffer, nodo_sink)
                    if path:
                        p_buffer = min(path, key=len)
                        if node_place_buffer in p_buffer:
                            p_buffer.remove(node_place_buffer)
                        # for p in path:
                        #     p_buffer = list(p)
                        #     p_buffer.remove(node_place)
                    if p_buffer:
                        for nodo in p_buffer:
                            if element_buffer[nodo][0] and \
                                    element_buffer[nodo][3] != 'copy':
                                pass
                            else:
                                element_buffer[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]
                path = simple_paths_from_two_nodes(self.DG, nodo_source, resource)
                p_buffer_ss = []
                for p in path:
                    p_buffer_ss = list(p)
                    p_buffer_ss.remove(resource)
                if p_buffer_ss:
                    for nodo in p_buffer_ss:
                        if self.lista_mapping[nodo][0] and self.lista_mapping[nodo][3] != 'copy':
                            pass
                        else:
                            self.lista_mapping[nodo] = [True, None, 'copy', 'copy', 0, nodo,
                                                        0, 0, latency, latency, info_sensor, 0, 0]

        actuator_sink = None
        # In here the idea is that if the task is a sink task but the resources where we are going to mapped it is not
        # we need to add the copy nodes
        # there is a bug that maps the copy nodes to a resource that is not connected to a memory, we need to be sure
        # that the list of sinks consists of only resources with connection to a memory block to store the data

        # in here there is a bug where we assign copy nodes to wrong places, we change the list self.sinks_DG to
        # self.list_sinks_connected_to_rc

        if node_AG in self.sinks_AG and resource not in self.list_sinks_connected_to_rc:
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES 01")
            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                          self.list_sinks_connected_to_rc,
                                                          resource)
            path_sink_node = simple_paths_from_two_nodes(self.DG_copia,
                                                         resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'basic':
                print("the paths between the sink task and the sink hardware",
                      path_sink_node)
                print(
                    f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            single_path = path_sink_node.pop()
            # single_path = min(path_sink_node, key=len)
            single_path.remove(resource)
            for nodo_a_sink in single_path:
                if self.lista_mapping[nodo_a_sink][0] and self.lista_mapping[nodo_a_sink][3] != 'copy':
                    pass
                else:
                    self.lista_mapping[nodo_a_sink] = [True, None, 'copy', 'copy', 0, nodo_a_sink,
                                                       0, 0, latency, latency, info_sensor, 0, 0]

            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == \
                        self.DG_copia.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.lista_sinks_DG_total.copy()
            if self.s_prints == 'basic':
                print(copia_sinks, lugar_sink_t)
            if lugar_sink_t in copia_sinks:
                actuator_sink = lugar_sink_t
            else:
                while done:
                    sink_test = copia_sinks.pop()
                    if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t,
                                                   sink_test):
                        actuator_sink = sink_test
                        done = False
                        break
            # self.lista_sinks_DG_total = self.lista_sinks_DG_total.remove(
            #     actuator_sink)
            # print(actuator_sink)

        counter_error = 0

        if node_AG in self.sources_AG and resource not in self.sources_DG:
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES 02")
            source_nodo_sink_task = source_node_from_any_node(self.DG_copia,
                                                              self.sources_DG,
                                                              resource)
            path_source_node = simple_paths_from_two_nodes(self.DG_copia,
                                                           source_nodo_sink_task,
                                                           resource)
            if self.s_prints == 'basic':
                print(
                    "the paths between the source task and the osusdofsdf hardware",
                    path_source_node)
                print(
                    f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            single_path = path_source_node.pop()
            single_path.remove(resource)
            for nodo_a_source in single_path:
                if self.lista_mapping[nodo_a_source][0] and self.lista_mapping[nodo_a_source][3] != 'copy':
                    pass
                else:
                    self.lista_mapping[nodo_a_source] = [True, None, 'copy', 'copy', 0, nodo_a_source,
                                                         0, 0, latency, latency, info_sensor, 0, 0]
        if self.s_prints == 'testexh':
            print("acabamos con la funcion de generacion de copy nodes")

        return element_buffer, actuator_sink

    def generation_copy_nodes(self, node_AG, resource):
        """
        in this function we assing the copy operation to all the resources that are in the path from the resources
        that will be assigned with the task and its actuator
        :param node_AG: task to assign
        :param resource: resource that will be assigned with the task
        :return: actuator_sink todo verify what we return
        """

        # internal variable for debugging purposes
        debug = False
        # if node_AG == 1 and resource == 5:
        #     debug = True

        # because we need to include the latency of the operation into the elements of the mapping list we retrieve
        # that information with the following function
        latency = self.obtention_latency_copy_node(resource)

        # now we also need information about the info_sensor so we use the verification of source function
        bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)
        actuator_sink = None

        # we are going to change self.sinks_DG for sinks_connected_to_rc in lines 849 and 853
        # now we are going to change to the global self.list_sinks_connected_to_rc

        # we have two cases if the task is in the sinks of the application but is going to be mapped to a resource
        # which is not in the sinks of the hardware graph, and the other is if the task is in the sources of the
        # application but is going to be mapped to a resources which is not in the sources of the hardware graph
        # for both cases we need to put copy nodes to the datapaths

        if node_AG in self.sinks_AG and resource not in self.list_sinks_connected_to_rc:
            # for the first case, as the task is a sink of the application but is going to be mapped to a not sink
            # resource of the hardware, we need to find a path from the resource to an actual sink and assign copy
            # operations to those resources
            # a particular characteristic is that the only sinks that we take into account are the sinks that are
            # connected to a communication resource, namely a rw

            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            # we obtain a sink node from the resource
            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
            copy_list_sinks_connected_to_rc.reverse()
            done = True
            counter_internal = 0

            while done:
                if copy_list_sinks_connected_to_rc:
                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                  copy_list_sinks_connected_to_rc,
                                                                  resource)
                else:
                    counter_internal = counter_internal + 1
                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                  copy_list_sinks_connected_to_rc,
                                                                  resource)
                # print(sink_nodo_sink_task,resource)
                if self.lista_mapping[sink_nodo_sink_task][0]:
                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                    if counter_internal == 5:
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                        done = False
                        break

                else:
                    done = False
                    break

            # now we obtain the path from the resource to the sink node
            path_sink_node = simple_paths_from_two_nodes(self.DG_copia,
                                                         resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'basic' or debug:
                # basic validation
                print("the paths between the sink task and the sink hardware",
                      path_sink_node)
                print(
                    f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            # now we obtain the shortest path
            single_path = min(path_sink_node, key=len)
            # single_path = path_sink_node.pop()
            # we remove the resource from that path
            single_path.remove(resource)
            # and now we start assingning copy operations to all the nodes in the path
            for nodo_a_sink in single_path:
                if self.lista_mapping[nodo_a_sink][0] and self.lista_mapping[nodo_a_sink][3] != 'copy':
                    pass
                else:
                    self.lista_mapping[nodo_a_sink] = [True, None, 'copy', 'copy', 0, nodo_a_sink,
                                                       0, 0, latency, latency, info_sensor, 0, 0]
            # now we end the addition of the copy nodes we need to find the name of the actuator that we used
            lugar_sink_t = None
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == \
                        self.DG_copia.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.lista_sinks_DG_total.copy()
            # normally we use an actuator so the next process could be removed, but we still double check if we do have
            # an actuator
            # todo : check if this is necessary
            if lugar_sink_t in copia_sinks:
                actuator_sink = lugar_sink_t
            else:
                while done:
                    sink_test = copia_sinks.pop()
                    if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t, sink_test):
                        actuator_sink = sink_test
                        done = False
                        break
            # self.lista_sinks_DG_total = self.lista_sinks_DG_total.remove(actuator_sink)
            # print(actuator_sink)

        if node_AG in self.sources_AG and resource not in self.sources_DG:
            # the second case is when we have a task which is a source in the application graph that are going to be
            # mapped in a resource which is not a source in the hardware graph, in order to fill the datapath from
            # an actual source to the resource

            # we start with the search, because sometimes there could be source nodes that are already ocuppied, we
            # implement a for loop that goes source node by source node until we have one which is available
            # the following code does that, it goes from source node to source node verifying that it can be used
            bandera_salida = False
            for source_nodo in self.sources_DG:
                path_source_node = simple_paths_from_two_nodes(self.DG_copia, source_nodo,
                                                               resource)
                # print(path_source_node)
                if self.s_prints == 'basic' or debug:
                    print("the paths between the source task and the osusdofsdf hardware",
                          path_source_node)
                    print(
                        f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
                # for path in path_source_node:
                while path_source_node:
                    single_path = min(path_source_node, key=len)
                    dummy_path = path_source_node.copy()
                    for i in range(0, len(dummy_path)):
                        if single_path == dummy_path[i]:
                            dummy_01 = path_source_node.pop(i)
                    # single_path = path.copy()
                    single_path.remove(resource)

                    vector_test = []
                    for no in single_path:
                        if self.lista_mapping[no][2] != 'copy':
                            vector_test.append(self.lista_mapping[no][0])
                    if debug:
                        print(single_path)
                    if not True in vector_test:
                        for nodo_a_source in single_path:
                            if debug:
                                print(nodo_a_source)
                            if self.lista_mapping[nodo_a_source][0] and self.lista_mapping[nodo_a_source][3] != 'copy':
                                pass
                            else:
                                self.lista_mapping[nodo_a_source] = [True, None, 'copy', 'copy', 0, nodo_a_source,
                                                                     0, 0, latency, latency, info_sensor, 0, 0]
                        bandera_salida = True
                        break
                if bandera_salida:
                    if debug:
                        print(self.lista_mapping)
                    break

            # if self.s_prints == 'basic':
            #     print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            #     print(self.sources_DG, resource)
            # source_nodo_sink_task = source_node_from_any_node(self.DG_copia,
            #                                                   self.sources_DG,
            #                                                   resource)
            # if self.s_prints == 'basic':
            #     print(source_nodo_sink_task)
            # path_source_node = simple_paths_from_two_nodes(self.DG_copia, source_nodo_sink_task,
            #                                                resource)
            # if self.s_prints == 'basic':
            #     print("the paths between the source task and the osusdofsdf hardware",
            #           path_source_node)
            #     print(
            #         f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            # single_path = path_source_node.pop()
            # single_path.remove(resource)
            # for nodo_a_source in single_path:
            #     self.lista_mapping[nodo_a_source] = [True, None, 'copy', 'copy', 0, nodo_a_source,
            #                                            0, 0, latency, latency, 0, 0, 0]

        return actuator_sink

    def info_actuator_generator(self, node_AG):
        """
        this function retrieves the information about the sensor nodes from the application total graph
        :param node_AG:
        :return: information about the sensor
        todo we need to make changes in this function to be able to generalize to other applications, in the sense
        that we need to change the height and the width
        """
        lugar_n = None
        if node_AG in self.sinks_AG:
            for nodo_total in self.AG_total.nodes:
                # print(nodo_total)
                if self.AG_original.nodes[node_AG]['name'] == \
                        self.AG_total.nodes[nodo_total]['name']:
                    # print("encontrado")
                    lugar_n = nodo_total

            sinks_ag_total = obtencion_sinks(self.AG_total)
            actuator_info = sink_node_from_any_node(self.AG_total, sinks_ag_total, lugar_n)
            info_actuator = [self.AG_total.nodes[actuator_info]['name'],
                             self.AG_total.nodes[actuator_info]['par']['height'],
                             self.AG_total.nodes[actuator_info]['par']['width']]
        else:
            info_actuator = [None, None, None]
        return info_actuator

    def dependency_vector_generator(self, predecessor, resource):
        """
        in this function we verify that there is a path from a resource to another and we return a list
        that contains information of the datapath, if there is something mapped in the datapath or not
        :param predecessor:
        :param resource:
        :return: a list of True or False elements that correspond of a datapath between the predecessor and the
        resource
        """
        node_place = None
        if self.s_prints == 'basic':
            print(predecessor, resource)
            print(self.lista_mapping)
            print(self.lista_AG_nodes)
        for element in self.lista_mapping:
            if predecessor == element[1]:
                node_place = element[2]
        paths = simple_paths_from_two_nodes(self.DG, node_place, resource)
        vector_dependency_02 = []
        for path_b in paths:
            path = list(path_b)
            path.remove(node_place)
            vector_dependency_01 = []
            for node in path:
                vector_dependency_01 = vector_dependency_01 + [self.lista_mapping[node][0]]
            if True in vector_dependency_01:
                vector_dependency_02 = vector_dependency_02 + [False]
        return vector_dependency_02

    def available_nodes_function(self, element_in_list, nodo_task):
        available_nodes = []
        debug = False
        if nodo_task == 2:
            debug = False
        if self.s_prints == 'testexh' or self.s_prints == 'basic' or debug:
            print("Current list last item", element_in_list, " y su longitud es ", len(element_in_list))
        first_time = True
        bandera_validacion = False
        for elemento in range(0, len(element_in_list)):
            if self.s_prints == 'testexh' or debug:
                print("elemento de la lista ", element_in_list[elemento])

            predecesores = self.AG_copia.predecessors(nodo_task)
            if element_in_list[elemento][0] and element_in_list[elemento][2] != 'copy':
                if element_in_list[elemento][1] in list(predecesores):
                    bandera_validacion = True
                    if self.s_prints == 'testexh' or debug:
                        print("ESTA EN LOS PREDECESORES DDDD")

            if element_in_list[elemento][0]:  ####  and element_in_list[elemento][2] != 'copy'
                if not bandera_validacion:
                    pass
                else:
                    diferentes = []
                    descendientes = obtencion_sucesores(self.DG_copia, elemento)
                    if self.s_prints == 'testexh' or debug:
                        print("descendants", descendientes)
                    if first_time:
                        if self.s_prints == 'testexh' or debug:
                            print("test de entrada de ciclo 01")
                        available_nodes = descendientes
                        first_time = False
                    else:
                        available_nodes_copy = available_nodes.copy()
                        for j in available_nodes_copy:
                            if j in self.sources_DG:
                                descendientes.append(j)

                        diferentes = list(set(available_nodes) - set(descendientes))
                        if self.s_prints == 'testexh' or debug:
                            print("test de entrada de ciclo 02", diferentes, available_nodes)
                        if diferentes:
                            for o in diferentes:
                                available_nodes.remove(o)
                    if self.s_prints == 'testexh' or debug:
                        print(available_nodes)
            else:
                available_nodes = available_nodes + [elemento]
                first_time = False
            bandera_validacion = False
            if self.s_prints == 'testexh' or debug:
                print("los nodos disponibles hasta ahora son ", available_nodes)
        if self.s_prints == 'basic' or debug:
            if available_nodes:
                print("iteration within the same time slot")
            print(available_nodes)

        available_nodes = list(set(available_nodes))
        if self.s_prints == 'testexh' or debug:
            print("los nodos disponibles son  ", available_nodes)
            # input("available nodes function - Enter to continue ...")
        return available_nodes

    def list_process(self, element_buffer, first_time_special):
        if self.s_prints == 'testexh' or self.s_prints == 'basic':
            print("The element of the current list that we will work on is")
            print(element_buffer)

            # we saw a problem with the append of the lists, this following lines solves that problem
        bandera_anexion_time = False
        special_buffer = []
        if not first_time_special:

            # lineas para solucionar el problema de los indices en la evaluacion de desempeno
            for elemento in self.current_list_special_nodes:
                special_buffer = elemento
                break
            # special_buffer = self.current_list_special_nodes.pop()
            for time_elemento in self.time_slot_list_02:
                bandera_anexion_time = time_elemento
                break
            # bandera_anexion_time = self.time_slot_list_02.pop()

        else:
            special_buffer = []
            bandera_anexion_time = False
        # as the list can be integrated by several times slots, we only take the last item, because in the
        # first step we only try to map the task into the remaining resources available, we dont create any
        # time slot at this point, so the following lines helps to only select the last item of the list

        if isinstance(element_buffer[0][0], bool):

            if self.s_prints == 'debug':
                print("bug when we have just one instance from the first stage")
            # if any(isinstance(el, list) for el in element_buffer[0]):
        if not isinstance(element_buffer[0][0], bool):
            element_in_list = list(element_buffer[len(element_buffer) - 1])
        else:
            element_in_list = element_buffer.copy()
        return element_in_list, bandera_anexion_time, special_buffer

    def update_lists_case_04(self, element_buffer, bandera_anexion_time):
        dummy_01 = []
        dummy_02 = [[] for r in range(0, len(element_buffer) + 1)]
        # there was an issue with the append of the list but we solved with the
        # following lines

        # if self.s_prints == 'debug' or contador_bug == 19 or contador_bug == 10:
        #     print("elemento buffer")
        #     print(element_buffer)
        # bandera_anexion_time = True
        if bandera_anexion_time:
            # if self.s_prints == 'debug' or contador_bug == 19 or contador_bug == 10:
            #     print("bug lista", bandera_anexion_time)
            for t in range(0, len(element_buffer)):
                # if self.s_prints == 'debug' or contador_bug == 19 or contador_bug == 10:
                #     print(element_buffer[t])
                dummy_02[t] = element_buffer[t]
            dummy_02[len(element_buffer)] = self.lista_mapping
            dummy_01 = dummy_02
        else:
            # if contador_bug == 19: print("lago sdonfosdnoidsfnoJONJOSF")
            dummy_01 = element_buffer, list(self.lista_mapping)
        # if self.s_prints == 'debug' or self.s_prints == 'basic' or contador_bug == 19 or contador_bug == 10:
        #     print("a mapping list is going to be store stage 2 step 6")
        #     print("the mapping list is")
        #     print(list(dummy_01))
        self.next_list.append(list(dummy_01))
        # if verificacion_lista(self.lista_bug, list(dummy_01)):
        #     print("error 14", contador_bug)
        #     time.sleep(5)
        if self.s_prints == 'basic':
            print("la lista hasta ahora es 11 ")
            for lista_intermedia in self.next_list:
                print(lista_intermedia)
            # print(self.next_list)
            print("se termino de imprimir la lista 11")
        # time.sleep(2)
        self.time_slot_list_01.append(True)
        return dummy_01

    def update_lists_case_03(self, bandera_anexion_time, element_buffer):
        dummy_01 = []
        dummy_02 = [[] for r in range(0, len(element_buffer) + 1)]
        # there was an issue with the append of the list but we solved with the
        # following lines
        if self.s_prints == 'debug' or self.s_prints == 'basic':
            print("esto es un buggazo pero no se deja")
            print(element_buffer)
            print(self.lista_mapping)
            print("va esto acabo aqui")
        if bandera_anexion_time:
            if self.s_prints == 'basic':
                print("bug lista", bandera_anexion_time)
            for t in range(0, len(element_buffer)):
                if self.s_prints == 'debug' or self.s_prints == 'basic':
                    print(element_buffer[t])
                dummy_02[t] = element_buffer[t]

            dummy_02[len(element_buffer)] = self.lista_mapping
            element_buffer_dummy = element_buffer.copy()
            element_buffer_dummy[len(element_buffer_dummy) - 1] = self.lista_mapping
            dummy_01 = element_buffer_dummy  # dummy_02
        else:
            dummy_01 = element_buffer, list(self.lista_mapping)
        if self.s_prints == 'debug' or self.s_prints == 'basic':
            print("a mapping list is going to be store stage 2 step 4")
            print(self.lista_mapping)
            print("the mapping list is")
            print(list(dummy_01))
        self.next_list.append(list(dummy_01))
        # if verificacion_lista(self.lista_bug, list(dummy_01)):
        #     print("error 11 ")
        #     time.sleep(5)
        if self.s_prints == 'basic':
            print("la lista hasta ahora es 07")
            for lista_intermedia in self.next_list:
                print(lista_intermedia)
            print("se termino de imprimir la lista 07")
            # print(self.next_list)

        self.time_slot_list_01.append(True)
        return

    def update_lists_case_02(self, element_buffer):
        if self.s_prints == 'debug':
            print("BUG 01")
        elemento_01 = element_buffer[0:len(element_buffer) - 1].copy()
        # elemento_01 = elemento_01 + self.lista_mapping.copy()
        elemento_01.append(self.lista_mapping.copy())
        if self.s_prints == 'debug':
            print("a mapping list is going to be store stage 2 step 1")
            print("the mapping list is")
            print(elemento_01)
        self.next_list.append(elemento_01)

        # if verificacion_lista(self.lista_bug, elemento_01):
        #     print("error 02")
        #     time.sleep(5)
        if self.s_prints == 'basic':
            print("la lista hasta ahora es 02")
            for lista_intermedia in self.next_list:
                print(lista_intermedia)
            print("se termino de imprimir la lista 02")
            # print(self.next_list)
        self.time_slot_list_01.append(False)
        return

    def update_lists_case_01(self, element_buffer, bandera_anexion_time):
        dummy_01 = []
        dummy_02 = [[] for r in range(0, len(element_buffer) + 1)]
        # there was an issue with the append of the list but we solved with the
        # following lines
        if self.s_prints == 'debug':
            print(element_buffer)
        if bandera_anexion_time:
            # print("bug lista", bandera_anexion_time)
            for t in range(0, len(element_buffer)):
                if self.s_prints == 'debug':
                    print(element_buffer[t])
                dummy_02[t] = element_buffer[t]
            dummy_02[len(element_buffer)] = self.lista_mapping
            dummy_01 = dummy_02
        else:
            dummy_01 = element_buffer, list(self.lista_mapping)
        if self.s_prints == 'debug':
            print("a mapping list is going to be store stage 2 step 1")
            print("the mapping list is")
            print(list(dummy_01))
        self.next_list.append(list(dummy_01))

        # if verificacion_lista(self.lista_bug, list(dummy_01)):
        #     print("error 11111")
        #     time.sleep(5)

        if self.s_prints == 'basic':
            print("la lista hasta ahora es 01")
            for lista_intermedia in self.next_list:
                print(lista_intermedia)
            print("se termino de imprimir la lista 01")
        self.time_slot_list_01.append(True)
        return

    def variable_separation(self, function_formula):
        """
        in this function we separate the variables in the formula function (latency equation)
        :param function_formula: the equation as a string
        :return: vector_total_parametros which is a list  with the parameters as elements of it
        """
        # initialization of variables
        contador_linea = 0
        bandera_primera_vez_letra = True
        vector_parametro = []
        vector_total_parametros = []
        # we are going to go letter by letter of the equation (string)
        for letra in function_formula:
            # print(letra,contador_linea,len(function_formula))
            # we make a distinction between the first element of the string because it may be a sign and because we
            # are looking for letters we need to discard those
            if bandera_primera_vez_letra:
                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                    pass
                else:
                    vector_parametro.append(letra)
                    bandera_primera_vez_letra = False
            else:
                # after we detect the first letter we start the second stage, where when we encounter a sign we split
                # the string and store the variable
                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ' or contador_linea == len(
                        function_formula):
                    # print(vector_parametro)
                    vector_total_parametros.append(vector_parametro)
                    vector_parametro = []
                else:
                    # there was an error on when we store the variable that lead to trunc names, we solved by
                    # integrating this counter which counts the number of elements of the string and if we reach the
                    # end we store the parameter name
                    if contador_linea == len(function_formula) - 1:
                        vector_parametro.append(letra)
                        vector_total_parametros.append(vector_parametro)
                    else:
                        vector_parametro.append(letra)
            contador_linea = contador_linea + 1

        # finally we return a list with the variable names as elements
        return vector_total_parametros

    def obtention_latency(self, resource, node_AG):
        """
        this function computes the input latency and the computing latency of the resources if a certain task is
        mapped to it
        :param resource: resource where we want to map the task
        :param node_AG:  task to map
        :return:    resultado_latencia which is the input latency
                    resultado_latencia_total which is the overall latency if the resource is the last element of the
                                        critical path
        """

        # first we obtain the name of the latency function of the resource according to the type of task that we
        # want to assign
        name_function = \
            self.dict_nodes[resource]['ops'][self.AG.nodes[node_AG]['op']]['latency']

        # now we are going to look for the actual function in the info dict
        for data in self.dict_info['functions_res']:
            if data == name_function:
                function_formula = self.dict_info['functions_res'][data]

        # as part of this function is to compute the overall latency if the element is the last one of the critical path
        # we need to retrieve the information about the sensor and we do it with the following code

        # first we obtain the information about the task in the application total dictionary, namely the node number
        lugar_nodo = None
        for n, data in self.dict_info_a.items():
            if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                lugar_nodo = n

        # lista_sources_ag_total = obtencion_sources(self.AG_total)
        # now that we have the node number we can search for the source node that is connnected to this node and
        # retrieve the information about the resolution
        source_total_app = source_node_from_any_node(self.AG_total, self.sources_AG_total,
                                                     lugar_nodo)

        # we assing the values to the variables height and width, these variables are keywords and they should not be
        # used for other purposes
        # todo: to generalize the framework we need to change this and remove the height and the width
        height = self.dict_info_a[source_total_app]['param']['height']
        width = self.dict_info_a[source_total_app]['param']['width']

        # we have the name of the formula and the keywords variables, so will start to parse the formula and assign
        # values to it, the idea behind is that if equation is a constant it will skip all the following process,
        # but if not it will enter and the variables in the equation will be assigned with a value

        # initialization of variables
        contador_parametros = 0
        contador_linea = 0
        bandera_primera_vez_letra = True
        vector_parametro = []
        vector_total_parametros = []
        if self.s_prints == 'basic':
            # simple verification of the formula
            print(f"we are in the obtention latency function and the formula is {function_formula}")

        # first we check if the formula is actually a formula or a constant
        if isinstance(function_formula, str):
            # because it is a constant we first separate the variables and store them in a variable
            vector_total_parametros = self.variable_separation(function_formula)

        # now that we have either the variables names in a list or we have the equation as a constant we move to the
        # next stage

        # we check the variables that we got from the variable_separation function, if they are strings we need to
        # store them to be able to assing them a value, so we check if they are integers we dont keep them, if they
        # are not integers we store the in the variable vector_parametro
        vector_parametro = []
        for it in vector_total_parametros:
            dummy = "".join(it)
            if dummy:
                try:
                    int(dummy)
                except:
                    if dummy not in vector_parametro:
                        vector_parametro.append(dummy)

        if self.s_prints == 'basic':
            # basic validation of the values that we have
            print(vector_parametro)
            print(self.dict_nodes_a[node_AG]['param'])

        # now that we have only the variables(strings) of the equation, we assign them a value
        for param_formula in vector_parametro:
            # because height and width are keywords words we pass them
            if param_formula == 'width':
                pass
            elif param_formula == 'height':
                pass
            else:
                # in here we only have not keywords which are the real variables of the equation
                if self.s_prints == 'basic':
                    # basic validation of the variable
                    print(param_formula)
                # in here we are going to look the value in the dict of the nodes and use globals to assign the value
                # to the variable
                # todo: maybe in here we can introduce other equations or other function like sin or cos
                for pa in self.dict_nodes_a[node_AG]['param']:
                    if self.s_prints == 'basic':
                        print("formula test ")
                        print(pa, self.dict_nodes_a[node_AG]['param'][pa])
                    if param_formula == pa:
                        globals()[pa] = self.dict_nodes_a[node_AG]['param'][pa]

        # the next step is the computing latency, in the framework it is also an equation so we need to perform some
        # steps
        # first we obtain the name of the equation
        name_clk = self.dict_nodes[resource][
            'ops'][
            self.AG.nodes[node_AG]['op']][
            'clk']
        if self.s_prints == 'debug':
            print(self.dict_info)

        # second we obtain the actual equation from the info dict
        value_clk = None
        for el in self.dict_info['functions_res']:
            if el == name_clk:
                value_clk = self.dict_info['functions_res'][el]

        # if we dont find the equation we raise an error
        if value_clk == None:
            raise UnboundLocalError(f"Parameter {name_clk} is not described in the functions section")

            ######ahora obtendremos el valor de la latencia de computo, debido a que puede ser una ecuacion o una
            # constante necesitamos hacer una verificacion previa y tambien sacar los valores
            # normalmente ya tenemos la ecuacion, entonces es separarla y asignar valores
        # now we have the equation, it can be a string or a constant so we verify which one is it
        if isinstance(value_clk, str):
            # if the computing latency is an equation
            print("The computing latency is an equation")
            # we call again the variable_separation function
            vector_total_parametros = self.variable_separation(value_clk)
            vector_parametro = []
            # we perform the same process that before, where we test if the parameter is an integer or not
            for it in vector_total_parametros:
                dummy = "".join(it)
                if dummy:
                    try:
                        int(dummy)
                    except:
                        if dummy not in vector_parametro:
                            vector_parametro.append(dummy)

            if self.s_prints == 'basic':
                # basic validation of the parameters that we obtain before
                print(f"the vector_parametro for the computing latency is {vector_parametro}")
            # we perform again the assigment of values to the parameters and discard the keywords
            for param_formula in vector_parametro:

                if param_formula == 'width':
                    pass
                elif param_formula == 'height':
                    pass
                else:
                    # in here we are going to look the value in the dict of the nodes
                    for pa in self.dict_nodes_a[node_AG]['param']:
                        if param_formula == pa:
                            globals()[pa] = self.dict_nodes_a[node_AG]['param'][pa]
            # now we can evaluate the formula
            value_clk = eval(value_clk)
            if self.s_prints == 'basic':
                print("the final value of the equation is  ", value_clk)
        else:
            # if the equation is an integer we dont do anything
            value_clk = value_clk

        # now we have the computing latency and the paramters and we can evaluate the entire equation, but as we said
        # it can be an integer or a string so we check it
        if isinstance(function_formula, str):
            resultado_latencia = eval(function_formula) * self.dict_info['max_clk'] + value_clk
        else:
            resultado_latencia = function_formula * self.dict_info['max_clk'] + value_clk
        # finally we evaluate the latency if this resource is the last item of the critical path
        # todo: in here we need to change this to a general form
        resultado_latencia_total = width * height * value_clk

        if self.s_prints == 'basic':
            print(
                f"we exit the obtention latency function, the values are {resultado_latencia} and {resultado_latencia_total}")
        return resultado_latencia, resultado_latencia_total

    def mapping(self):

        """
        This is the main function of the class, is the core of the exhaustive algorithm. It is divided in several parts



        :return:
        """
        a = datetime.now() ##### overall beggining
        # with this we are going to print everythig about the algorithm (memory and timing values)
        # self.debug_info = 'remove'
        # this variable helps to store the resources that will have assigned a copy operation
        self.lista_nodos_copy = []
        # initialization of the counter of errors in the mapping, if we reach a certain number of errors that means that
        # the mapping can not be achieved
        counter_error = 0

        ### if we want to create time slots not only on demand the following should be true
        bandera_time_slots_creation = True
        bandera_need_of_time_slot = True

        # we need to know if there is only one task or more. If there is only one task only the first stage of the
        # mapping process will be perform
        bandera_una_tarea = False
        if self.s_prints == 'exh':
            print(f"The total amount of tasks is {len(self.AG.nodes)}")
        if len(self.AG.nodes) == 1:
            bandera_una_tarea = True

        # because the sources tasks of the application graph will be used in several stages of the mapping we put them
        # as an attribute of the class
        self.sources_AG = obtencion_sources(self.AG)

        ####################################################################################
        #############The following code correspond to the solution of the bug that does not allow us to obtain all
        #############the possible mappings (bug 0)
        # there is a problem with the production of all possible mappings, so we need to add one more process
        # we take all the source nodes of the application graph and create several lists
        ###################
        ######if we want to obtain all the possible lists the following flag should be True
        bandera_multiple_lists = False
        # in this lsit we will put all the lists that we obtain from the permutations of the source nodes and the rest
        # of the nodes
        vector_listas = []
        if bandera_una_tarea:
            if self.s_prints == 'exh':
                print("lines to fix the bug that make us not get all the possible mappings")
            # now we have the sources we perform a topological sorting of the application graph
            lista_dummy_01 = list(nx.topological_sort(self.AG_copia))
            if self.s_prints == 'exh':
                print(f"the nodes of the application graph are {self.AG.nodes}, the source nodes are {self.sources_AG},"
                      f" and the node of the copy of the application graph are {self.AG_copia.nodes}")
            # now we obtain the possible permutations of the list, what it means is that if the list of source nodes are
            # [0,1], we want a list such a [[0,1],[1,0]]
            l = list(permutations((self.sources_AG)))
            # now that we have all the source nodes we remove them from the topological sorting
            for h in self.sources_AG:
                lista_dummy_01.remove(h)
            if self.s_prints == 'exh':
                # simple verification that we remove all the source nodes
                print(f"the remaining nodes of the list are {lista_dummy_01} - lista_dummy_01")
            # now we traverse through the list of permutations, and add the rest of the nodes
            # for each permutation of source nodes we create a list and add the rest of the nodes, for example we have
            # a complete list of nodes [0,1,2,3,4,5], where the source nodes are [0,1], we will end up with the following
            # lists [[0,1,2,3,4,5],[1,0,2,3,4,5]]
            # with this arrangement we can obtain all the possible mappings, maybe several duplicate
            for perm in l:
                buffer = list(perm) + lista_dummy_01
                vector_listas.append(buffer)
        else:
            vector_listas.append(list(nx.topological_sort(self.AG_copia)))

        #######this was the code that solves bug 0
        ##########################################################
        if self.s_prints == 'exh':
            # simple verification of the previous process and the data of the graphs
            print("we will print the information of the input graphs")

            for nodo in self.AG.nodes:
                print(f"the task {nodo} has the information {self.AG.nodes[nodo]}")
            for nodo in self.DG_copia.nodes:
                print(f"the resource {nodo} has the information {self.DG_copia.nodes[nodo]}")
            print(f"the final list for the mapping is {vector_listas}")
            print("we end printing the information of the input graphs")

        # self.lista_constraints = [['t0','r0'],['t1','r1'],['t2','r2'],['t3','r3'],['t4','r6']]
        # self.lista_tareas_constrains = ['t1','t0','t2','t3','t4']

        # in these list we will store the final mappings for each stage, list total refers to the mappings and
        # lista_total_nodes refers to the special nodes
        self.lista_total = []
        self.lista_total_nodes = []

        # this counter if for the iterations which are the stages for each task, it also depends on the number of list
        # that previously we obtained from the permutations of the source nodes of the application graph
        counter_iter = 0

        # we initialize the mapping list, in here we will store the preliminary mappings, this list has an element for
        # each resource, and each element will store some information related to the mapping. In particular each
        # element consists of
        # 1.- If it has a task assigned (True or False)
        # 2.- the assigned task
        # 3.- the resource, for easy search we store the index of the resource in here
        # 4.- the type of task assigned
        # 5.- the latency of the task
        # 6.- the parameters of the task
        # 7.- the parameters of the task duplicated
        # 8.- the computing clock of the task
        # 9.- the computed input latency
        # 10.- the computed computing cost if this is the last element of the critical path
        # 11.- the information about the sensor (resolution)
        # 12.- the information about the actuator that is possible connected to this resource
        # 13.- the information about the actuator

        self.lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n in
                              range(0, len(self.DG.nodes))]

        # before the mapping lets obtain some information about the graphs like source and sinks nodes
        self.sources_DG = obtencion_sources(self.DG)
        self.sinks_DG = obtencion_sinks(self.DG)
        self.sinks_AG = obtencion_sinks(self.AG)
        self.sources_AG_total = obtencion_sources(self.AG_total)
        self.sources_DG_total = obtencion_sources(self.DG_total)
        self.TOTAL_RESOURCES = len(self.DG_copia.nodes)
        # todo: in here we can obtain a table where we can stablish which task can be mapped in which resource

        if self.s_prints == 'iter':
            print("------------------------------------------------------------")
            print("Exhaustive algorithm")
            print("We are going to start the mapping")
            print("------------------------------------------------------------")

        # now we start the mapping, we will go through the list, which has been previously obtained, that contains the
        # lists of the permutations of the sources nodes. There are two main stages of the mapping, the first stage we
        # try to map the first task and then the second stage we try to map all the reamining tasks. We make this
        # distinction because we need a starting point for the iterations, so we use the first task to create those
        # starting points. The process is for each list of the permutations list, so for each list of the permutation
        # list there will be two stages.
        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"initialization of variables, obtention of sources and sinks, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

        for lista in vector_listas:
            a = datetime.now()
            if self.s_prints == 'exh':
                # Simple print each time we grab a new list
                print("BEGINNING OF THE LIST SDFSDFS", lista)

            #####################initialization of the variables
            # in the previous version we only used one topological sorting and due to the bug 0 we now use several
            # so in order to not change all the code we comment the command and now we assign the list to the
            # self.lista_AG_nodes variable which we use throughout the rest of the code
            self.lista_AG_nodes = lista  # list(nx.topological_sort(self.AG_copia))

            # we set a limit of the time slots that we can create, which corresponds to the number of resources(nodes)
            # of the hardware graph
            self.limite_time_slots = len(self.DG.nodes)

            # variables that we use throughout the mapping
            self.lista_mapping_slot = []
            self.lista_nodos = []
            self.lista_DG_nodes = list(self.DG_copia.nodes)
            first_iteration = True
            self.current_list = []
            self.next_list = []
            self.next_list_special_nodes = []
            self.current_list_special_nodes = []
            self.contador_recomputacion = 0
            contador_time_slots = 0
            bandera_anexion_time = False
            first_time_special = True
            self.time_slot_list_01 = []
            self.time_slot_list_02 = []

            if self.s_prints == 'exh':
                # basic verification of the information of the nodes of the application graph
                print("we are at the beggining of the list and the info about the application is")
                for n in self.AG.nodes:
                    print(f"task {n} with information {self.AG.nodes[n]}")

            ###end of the initialization of the variables
            ####################################################################################

            ##############################################################################################
            ####Now we are going to start with the mapping of the first task, this process is divided in two
            ####first we select the task and then we map the task to any available resource. This second process is also
            ####divided in two, first we check if the task is part of the constraints lists or not. If the task is part
            ####of the list we immediately map the task according to that specification and we move to the next step
            ####of the mapping with only one list, if not we try to map the task to any available resource and we
            ####may end up with one to several lists

            # this first iteration serves as a starting point, we take the first node of the graph and we iterative
            # try to map it to all the resources, each feasible mapping will represent a list in the current list.
            # In the next step, we will iterative in the current list to continue the mapping of all the remaining tasks
            # in here we dont need time slots nor special nodes

            # we select the first task and remove it from the tasks list
            node_AG = self.lista_AG_nodes.pop(0)


            if self.s_prints == 'basic' or self.s_prints == 'iter':
                print("------------------------------------------------------------")
                counter_iter += 1
                print(f"iteration {counter_iter}")
                print(f"First stage, we traverse the graph for the first task {self.dict_nodes_a[node_AG]['name']}")
            elif self.s_prints == 'debug' or self.s_prints == 'exh':
                print("First stage, we traverse the graph for the first task ", self.lista_AG_nodes)
                print("the first tasks is ", node_AG)

            # we initialize again the error counter, this is because we keep track of the number of attempts per task,
            # the logic behing is that if we the counter equals the number of resource means that there is no way we
            # can map the task to any resource, so in that case we raise an error
            counter_error = 0

            # to verify is the task is part of the constrained tasks we obtain the name if the task from the dictionary
            # that has all the information about the tasks
            name_task = self.dict_nodes_a[node_AG]['name']

            ##########################################################################
            ####in here we branch, if the task is part of the constrained tasks we go directly to map it to the
            ####corresponding resource and move to the next stage of the mapping process, if not we need to try to map
            ####the task to any available resource

            if name_task in self.lista_tareas_constrains:
                # the task is in the list of constrained tasks
                if self.s_prints == 'exh':
                    # basic verification to see if we enter this branch
                    print("we enter the branch for the contrained tasks in cycle 1")

                # we are going to map this task directly and move to the next stage
                # first we obtain the name of the resource and the resource data using the function
                # self.info_resource()
                resource, name_resource = self.info_resource(name_task)
                # before we map the task to the resource we obtain some information and verify the feasibility of
                # the mapping

                # first we check that the source nodes are compatible and retrieve the sensor info
                bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)
                # next we evaluate the equations and obtain the input latency and the overall latency
                resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, node_AG)

                if self.s_prints == 'exh':
                    print("we finish the verification of source and obtention of latency", resultado_latencia_total,
                          resultado_latencia)

                # now we need to assing the copy operation to the resources in the path to the actuator and retrieve
                # the info of the actuator from the hardware side that is going to be used
                actuator_sink = self.generation_copy_nodes(node_AG, resource)
                # we retrieve information about the sensor from the application side
                info_actuator = self.info_actuator_generator(node_AG)
                # we reinitialize the error counter
                counter_error = 0
                # we map the task to the resource
                self.lista_mapping[resource] = [True, node_AG, resource, self.AG.nodes[node_AG]['op'],
                                                self.dict_nodes[resource]['ops'][
                                                    self.AG.nodes[node_AG]['op']]['latency'],
                                                self.AG.nodes[node_AG]['par'],
                                                self.AG.nodes[node_AG]['par'],
                                                self.dict_nodes[resource]['ops'][
                                                    self.AG.nodes[node_AG]['op']]['clk'],
                                                resultado_latencia, resultado_latencia_total, info_sensor,
                                                info_actuator, actuator_sink]

                # when we have more than one parameters todo we need to change it to an automatic assignation
                # self.lista_mapping[resource] = [True, node_AG, resource,self.AG.node[node_AG]['op'],self.DG.node[resource]['lat'],\
                #                                 self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                if self.s_prints == 'exh':
                    print("a mapping list is going to be store stage 1 step 1")
                    print("this is the mapping list")
                    print(self.lista_mapping)
                elif self.s_prints == 'basic' or self.s_prints == 'iter':
                    print(
                        f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to resource {self.dict_nodes[resource]['name']}")
                    # print(
                    #     f"we add this mapping to the current list, which has a length of {len(self.current_list)}")

                    print("------------------------------------------------------------")
                # we update the current list
                self.current_list.append(self.lista_mapping)



            else:
                # because the task is not in the constraint list we go to this branch
                # in here the idea is to map the task to all the available resources and store each prelimiry mapping
                # to the current list which is going to be used in the next big stage

                # for each resource in the hardware graph
                for resource in (self.DG_copia.nodes):
                    # increment counter of error
                    counter_error = counter_error + 1
                    # if the counter is greater than the number of resources we raise an error
                    if counter_error > self.TOTAL_RESOURCES:
                        raise Exception(
                            f"The mapping cycle, please verify your input files, the exception occured at the first stage")

                    if self.s_prints == 'exh':
                        # basic validation
                        print("error 01", self.AG_copia.nodes[node_AG]['op'], self.DG_copia.nodes[resource]['op'])

                    d = datetime.now()
                    # if the type of task is one of the type of tasks that the resource can implement
                    if self.AG_copia.nodes[node_AG]['op'] in self.DG_copia.nodes[resource]['op']:
                        if self.debug_info == 'remove' or self.debug_info == 'total':
                            b = datetime.now()
                            now = b.strftime("%H:%M:%S.%f")
                            c = b - d
                            print(
                                f"Verification of type of task, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                        d = datetime.now()

                        # for the following verifications we have two branches, one if the task is a source task or if
                        # it is not
                        # if node_AG in self.sources_AG:
                        # if the task is a source task we dont need to verify if the predecessors are mapped
                        # correctly, but we do check the paramters and the source
                        # we verify the that the parameters match the parameters of the resource
                        new_validacion_parameters = self.verification_of_parameters(node_AG, resource)

                        if self.debug_info == 'remove' or self.debug_info == 'total':
                            b = datetime.now()
                            now = b.strftime("%H:%M:%S.%f")
                            c = b - d
                            print(
                                f"Verification of parameters, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                        # we verify is the source of data is the correct one and we retrieve the information
                        # about the sensor on the side of the hardware
                        d = datetime.now()
                        bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)
                        if self.debug_info == 'remove' or self.debug_info == 'total':
                            b = datetime.now()
                            now = b.strftime("%H:%M:%S.%f")
                            c = b - d
                            print(
                                f"Verification of sensor info, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                        if self.s_prints == 'exh':
                            # basic validation
                            print("new validation vector stage 01", all(new_validacion_parameters))
                            print("flag of the source of data", bandera_source_of_data, " sensors info",
                                  info_sensor)

                        # because there is no predecessor we can map the task anywhere we want
                        if all(new_validacion_parameters) and bandera_source_of_data:

                            if self.s_prints == 'exh':
                                # basic validation
                                print("verification of entering of cycle 01")
                            # we retrieve the information about the latency

                            d = datetime.now()
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, node_AG)
                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Retrieve latency info, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")


                            if self.s_prints == 'exh':
                                print("the resulting latencies are", resultado_latencia_total, resultado_latencia)

                            # we generate the copy nodes and we retrieve the information about the actuator from
                            # the application side
                            d = datetime.now()
                            actuator_sink = self.generation_copy_nodes(node_AG, resource)
                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Generation of copy nodes, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                            d = datetime.now()
                            info_actuator = self.info_actuator_generator(node_AG)
                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Retrieve actuator info, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                            d = datetime.now()
                            # reinitialize the counter
                            counter_error = 0
                            # map the task to the resource
                            self.lista_mapping[resource] = [True, node_AG, resource, self.AG.nodes[node_AG]['op'],
                                                            self.dict_nodes[resource]['ops'][
                                                                self.AG.nodes[node_AG]['op']]['latency'],
                                                            self.AG.nodes[node_AG]['par'],
                                                            self.AG.nodes[node_AG]['par'],
                                                            self.dict_nodes[resource]['ops'][
                                                                self.AG.nodes[node_AG]['op']]['clk'],
                                                            resultado_latencia, resultado_latencia_total,
                                                            info_sensor,
                                                            info_actuator, actuator_sink]

                            if self.s_prints == 'exh':
                                # basic validation
                                print("a mapping list is going to be store stage 1 step 1")
                                print("this is the mapping list")
                                print(self.lista_mapping)
                            elif self.s_prints == 'basic' or self.s_prints == 'iter':
                                print(
                                    f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to resource {self.dict_nodes[resource]['name']}")
                                # print(
                                #     f"we add this mapping to the current list, which has a length of {len(self.current_list)}")

                                print("------------------------------------------------------------")
                            # update of the current list
                            self.current_list.append(self.lista_mapping)
                            # print(self.current_list)
                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Mapping and append, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                    # we reset the mapping list to obtain another mapping
                    self.lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n in
                                          range(0, len(self.DG.nodes))]
            # deactivate the first iteration flag
            first_iteration = False
            if self.s_pause:
                input("Press Enter to continue...")

            ##########################
            # we transform the list into a generator to decrease the memory use
            if self.s_prints == 'exh':
                for nodo_hw in self.DG.nodes:
                    print(f"nodo {nodo_hw} with the info {self.DG.nodes[nodo_hw]}")
                print("we are going to print the current list after the first stage")
                for elemento_test in self.current_list:
                    print(elemento_test)
                # print(self.current_list)
                # input("Enter to continue...")
            if self.debug_info == 'remove' or self.debug_info == 'total' or self.debug_info == 'memory':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"Mapping of the first task, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                print(f"The memory usage of the current list is {asizeof(self.current_list)} bytes")
            d = datetime.now()

            #####################we are going to store the list on pickles in the first stage

            number_of_pickles = 0
            limit_number_list = 1000
            number_of_lists = len(self.current_list)
            inicio_lista = len(self.current_list)
            # print(inicio_lista)
            no_zero = True
            bandera_pickle = False
            previous_task = node_AG
            while no_zero:
                if number_of_lists - limit_number_list > 0:
                    name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(number_of_pickles)
                    # print(lista_total_mapping[0:1])
                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                        pickle.dump(self.current_list[number_of_lists - limit_number_list:number_of_lists], f)
                    # name_pickle = 'specialnodes' + str(number_of_pickles)
                    # with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                    #     pickle.dump(self.current_list[number_of_lists - limit_number_list:number_of_lists], f)
                    number_of_lists = number_of_lists - limit_number_list
                else:
                    name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(number_of_pickles)
                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                        pickle.dump(self.current_list[0:number_of_lists], f)
                    # name_pickle = 'specialnodes' + str(number_of_pickles)
                    # with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                    #     pickle.dump(self.current_list[0:number_of_lists], f)
                    no_zero = False
                number_of_pickles = number_of_pickles + 1


            self.current_list = []
            # self.current_list = self.function_generador_listas(self.current_list)


            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - d
                print(
                    f"List conversion, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")


            while self.lista_AG_nodes:
                a = datetime.now()
                # now we will start the iteration of the current list, in the first time we will iterate
                # the current list created in the previous step. During this first time, we will create the next list,
                # in this list, we will add all the mappings that we create, and at the end, we will copy the contents
                # of the next list to the current list and iterate again the new current list repeating the
                # same process: iterate upon the current list meanwhile adding the mappings to the next list,
                # at the end transfer the contents of next list to current list, and so on until
                # there are no more tasks to map.

                node_AG = self.lista_AG_nodes.pop(0)
                if self.s_prints == 'debugexh':
                    print(f"we will work with the task {node_AG} cycle 02")

                if self.s_prints == 'debug' or self.s_prints == 'basic' or self.s_prints == 'testexh':
                    # print(self.current_list)
                    print("Second stage, we will traverse the resources for the remaining tasks")
                    print(self.lista_AG_nodes)
                    # time.sleep(5)
                    # print(len(self.current_list),len(self.current_list_special_nodes))
                    # initialization of the variables

                    print("the task that we are going to map is ", node_AG)
                elif self.s_prints == 'basic' or self.s_prints == 'iter':
                    counter_iter += 1
                    print("------------------------------------------------------------")
                    print(f"iteration {counter_iter}")
                    print("we are going to start the second stage")
                    print(f"the task that we will try to map is {self.dict_nodes_a[node_AG]['name']}")

                # bandera_no_mapping = True

                n_pickles_next = 0
                for n_pickles in range(0, number_of_pickles):
                    name_pickle = 'currentlist' + '_' + str(previous_task) + '_' + str(n_pickles)
                    with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                        current_list_pickle = pickle.load(f)
                    os.remove(os.path.join(self.directorio, name_pickle))
                    if bandera_pickle:
                        name_pickle = 'specialnodes' + '_' + str(previous_task) + '_' + str(n_pickles)
                        with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                            special_nodes_pickle = pickle.load(f)
                        os.remove(os.path.join(self.directorio, name_pickle))
                        name_pickle = 'banderaanexion' + '_' + str(previous_task) + '_' + str(n_pickles)
                        with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                            bandera_anexion_time_pickle = pickle.load(f)
                        os.remove(os.path.join(self.directorio, name_pickle))
                    self.next_list = []
                    self.next_list_special_nodes = []
                    self.time_slot_list_01 = []
                    contador_bug = 0
                    bandera_need_of_time_slot = True

                    next_list_total = []
                    time_slots_total = []
                    special_nodes_total = []


                    # for l in range(0,len(current_list_pickle)):
                    #     # print(lista_del_generador)
                    #     # while self.current_list:
                    #     self.next_list = []
                    #     self.next_list_special_nodes = []
                    #     self.time_slot_list_01 = []
                    #     contador_bug = contador_bug + 0
                    #
                    #     d = datetime.now()
                    #     element_buffer = current_list_pickle[l] # self.current_list.pop(0)
                    #     # elemento_buffer_copy = list(element_buffer)
                    #     self.master_elemento_buffer = copy.deepcopy(element_buffer)
                    #     elemento_buffer_copy = element_buffer.copy()
                    #     # what we obtain is the last element in the preliminary mapping, a flag that tell us if there is
                    #     # a set of time slots or not, and finally the special nodes
                    #     element_in_list, bandera_anexion_time_dummy, special_buffer_dummy = self.list_process(element_buffer,
                    #                                                                               first_time_special)
                    #
                    #     if bandera_pickle:
                    #         bandera_anexion_time = bandera_anexion_time_pickle[l]
                    #         special_buffer = special_nodes_pickle[l]
                    #     else:
                    #         bandera_anexion_time = False
                    #         special_buffer = []
                    #     element_in_list_copy = element_in_list.copy()
                    #
                    #
                    #     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #         b = datetime.now()
                    #         now = b.strftime("%H:%M:%S.%f")
                    #         c = b - d
                    #         print(
                    #             f"Retrieve of the current list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #
                    #
                    #
                    #     #### in here we obtain the resources that can be used in the last time slot, if there is
                    #     # no resources we need to create another time slot
                    #     d = datetime.now()
                    #     available_nodes = self.available_nodes_function(element_in_list, node_AG)
                    #     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #         b = datetime.now()
                    #         now = b.strftime("%H:%M:%S.%f")
                    #         c = b - d
                    #         print(
                    #             f"Retrieve of available nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #
                    #
                    #     # print(available_nodes)
                    #     if self.s_prints == 'testexh':
                    #         print("we are in the beggining of a new preliminary mapping")
                    #         print("the preliminary mapping is  ")
                    #         print(element_buffer)
                    #         print("the last time slot is ")
                    #         print(element_in_list)
                    #         print("the special nodes are ")
                    #         print(special_buffer)
                    #         print("The available resources to use are ", available_nodes, "task ", node_AG)
                    #         # input("Press Enter to continue...")
                    #
                    #     # Now, we will try to map the task into the available nodes, we need to verify in here data dependence
                    #     # types and so on
                    #     name_task = self.dict_nodes_a[node_AG]['name']
                    #     pareja = None
                    #     contador_mapeo_antes_time_slot = 0
                    #     if name_task in self.lista_tareas_constrains:
                    #
                    #         elemento, name_resource = self.info_resource(name_task)
                    #
                    #         if elemento in available_nodes:
                    #
                    #             ###################
                    #             self.lista_mapping = element_in_list_copy.copy()
                    #             vector_validacion_parametros = self.verification_of_parameters(node_AG, elemento)
                    #             bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, elemento)
                    #
                    #             ############
                    #             if all(vector_validacion_parametros) and bandera_source_of_data:
                    #                 dummy_bug_01 = False
                    #                 if node_AG in self.sources_AG:
                    #                     # print("dfsdf")
                    #                     # because there is no predecessor we can map the task
                    #                     if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                         print(
                    #                             f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                    #                         print(
                    #                             f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                         print("------------------------------------------------------------")
                    #
                    #                     resultado_latencia, resultado_latencia_total = self.obtention_latency(elemento,
                    #                                                                                           node_AG)
                    #                     if self.s_prints == 'basic':
                    #                         print("estamos checando las latencias", resultado_latencia_total,
                    #                               resultado_latencia)
                    #
                    #                     actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                    #                     info_actuator = self.info_actuator_generator(node_AG)
                    #                     contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                    #                     bandera_need_of_time_slot = False
                    #                     self.lista_mapping[elemento] = [True, node_AG, elemento,
                    #                                                     self.AG.nodes[node_AG]['op'],
                    #                                                     self.dict_nodes[elemento]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['latency'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.dict_nodes[elemento]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                     resultado_latencia, resultado_latencia_total,
                    #                                                     info_sensor, info_actuator, actuator_sink]
                    #
                    #                     # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                    #                     #                             self.AG.node[node_AG]['par'],self.AG.node[node_AG]['par'],self.AG.node[node_AG]['lat']]
                    #                     # TODO: this is a bug where we mixup the lists, in the sense that we though that it was a list
                    #                     # with several time slots but it wasn't so i add this verification, i think that we can
                    #                     # remove it because i fixed the error with the append
                    #                     if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):
                    #
                    #                         # this is to keep control of the creation of time slots, it has to do with a
                    #                         # problem of the append and all the same lines as the following take care of that
                    #                         # problem
                    #                         # todo there is a issue with the list the following lines could solve it i dont know
                    #                         if bandera_anexion_time:
                    #                             self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                         else:
                    #                             self.update_lists_case_02(element_buffer)
                    #                         if self.s_prints == 'basic':
                    #                             print("regreso de procesamiento de listas modulo 77")
                    #                         # in here maybe we are not going to create any special node, but because the list of
                    #                         # special nodes needs to have the same length as the next list, every time that we
                    #                         # append the next list we need to append the special nodes list at least with an
                    #                         # empty list
                    #                         if self.s_prints == 'debug':
                    #                             print("a special nodes list is going to be store stage 2 step 1")
                    #                             print(list(special_buffer))
                    #                         self.next_list_special_nodes.append(list(special_buffer))
                    #                     else:
                    #
                    #                         # todo verify if this part is necessary
                    #                         if bandera_anexion_time:
                    #                             self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                         else:
                    #                             if self.s_prints == 'debug':
                    #                                 print("a mapping list is going to be store stage 2 step 2")
                    #                                 print("the mapping list is")
                    #                                 print(self.lista_mapping)
                    #                             self.next_list.append(self.lista_mapping.copy())
                    #                             # if verificacion_lista(self.lista_bug, self.lista_mapping):
                    #                             #     print("error 08 ")
                    #                             #     time.sleep(5)
                    #
                    #                             if self.s_prints == 'basic':
                    #                                 print("la lista hasta ahora es 04")
                    #                                 for lista_intermedia in self.next_list:
                    #                                     print(lista_intermedia)
                    #                                 print("se termino de imprimir la lista 04")
                    #                                 # print(self.next_list)
                    #                             self.time_slot_list_01.append(False)
                    #                         if self.s_prints == 'basic':
                    #                             print("regreso de procesamiento de listas 88")
                    #
                    #                         if self.s_prints == 'debug':
                    #                             print("a special nodes list is going to be store stage 2 step 2")
                    #                             print(list(special_buffer))
                    #                         self.next_list_special_nodes.append(list(special_buffer))
                    #                 else:
                    #
                    #                     # Because the task is not a source task we need to verify the data dependency
                    #                     # we obtain all the predecessor and we verify the data dependency
                    #                     if self.s_prints == 'debug':
                    #                         print("We are going to check the data dependency of the task ", node_AG)
                    #                     predecessors = self.AG.predecessors(node_AG)
                    #                     # We noticed a bug related to the number of time slots, this created an issue with the
                    #                     # module of graph creation, the following lines solves that problem
                    #                     if bandera_anexion_time:
                    #                         instancia = len(element_buffer)
                    #                     else:
                    #                         instancia = 0
                    #                     self.bandera_debug = False
                    #                     if self.s_prints == 'basic' and self.s_pause == True and elemento == 2 and node_AG == 2:
                    #                         self.bandera_debug = True
                    #                     else:
                    #                         self.bandera_debug = False
                    #
                    #                     valid_place, special_nodes_01 = self.verification_of_dependence(predecessors,
                    #                                                                                     element_in_list,
                    #                                                                                     element_buffer,
                    #                                                                                     elemento,
                    #                                                                                     node_AG, instancia)
                    #
                    #                     if self.s_prints == 'basic':
                    #                         print(
                    #                             f"predecesores de la tarea {node_AG}, son {list(self.AG.predecessors(node_AG))} y el elemento es {elemento} y la bandera es {valid_place}")
                    #                         print(f"y la lista hasta ahora es {element_buffer}")
                    #
                    #                     # after a succesful verification we map the task
                    #                     # if valid_place and all(vector_validacion_parametros) and not bandera_no_match_parameters:
                    #                     #####################################################################
                    #                     #############this is the one that is not working
                    #
                    #                     if valid_place:
                    #                         # if not False in vector_dependency_02 :
                    #                         if self.s_prints == 'debug':
                    #                             print("Map")
                    #                         elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                             print(
                    #                                 f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                    #                             print(
                    #                                 f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                             print("------------------------------------------------------------")
                    #
                    #                         ############this is the new way to obtain the latency
                    #
                    #                         resultado_latencia, resultado_latencia_total = self.obtention_latency(elemento,
                    #                                                                                               node_AG)
                    #                         if self.s_prints == 'basic':
                    #                             print("estamos checando las latencias 03", resultado_latencia_total,
                    #                                   resultado_latencia)
                    #
                    #                             # we are going to add the copy nodes
                    #                         if self.s_prints == 'basic' or self.s_prints == 'debug':
                    #                             print(self.lista_nodos_copy)
                    #                             print("we are going to map something so we need to add the copy nodes")
                    #                         latency_copy = self.obtention_latency_copy_node(elemento)
                    #                         for copy_node in self.lista_nodos_copy:
                    #                             self.lista_mapping[copy_node] = [True, None, 'copy', 'copy', 0, 0,
                    #                                                              0, 0, latency_copy, latency_copy, 0, 0, 0]
                    #
                    #                         contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                    #                         actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                    #                         info_actuator = self.info_actuator_generator(node_AG)
                    #                         bandera_need_of_time_slot = False
                    #                         self.lista_mapping[elemento] = [True, node_AG, elemento,
                    #                                                         self.AG.nodes[node_AG]['op'],
                    #                                                         self.dict_nodes[elemento]['ops'][
                    #                                                             self.AG.nodes[node_AG]['op']]['latency'],
                    #                                                         self.AG.nodes[node_AG]['par'],
                    #                                                         self.AG.nodes[node_AG]['par'],
                    #                                                         self.dict_nodes[elemento]['ops'][
                    #                                                             self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                         resultado_latencia, resultado_latencia_total,
                    #                                                         info_sensor, info_actuator, actuator_sink]
                    #                         # todo change this
                    #                         # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                    #                         #                         self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                    #                         if self.s_prints == 'basic':
                    #                             print("aqui aparece un buggazo", self.lista_mapping)
                    #                         if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):
                    #
                    #                             # todo verify if this is necessary
                    #                             if bandera_anexion_time:
                    #                                 self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                             else:
                    #
                    #                                 self.update_lists_case_02(element_buffer)
                    #                             if self.s_prints == 'basic':
                    #                                 print("regreso de procesamiento de listas 99")
                    #                             # we are going to add the special nodes
                    #                             # we notice a small bug with the append, so the next few lines solves that
                    #                             if special_buffer and special_nodes_01:
                    #                                 if self.s_prints == 'debug':
                    #                                     print("bug append special nodes")
                    #                                 # print(len(special_buffer))
                    #                                 dummy_01 = []
                    #                                 dummy_02 = [[] for r in
                    #                                             range(0, len(special_buffer) + len(special_nodes_01))]
                    #                                 # print("test de algo special")
                    #                                 # print(len(element_buffer))
                    #                                 if self.s_prints == 'debug':
                    #                                     print(len(special_nodes_01) + len(special_buffer))
                    #                                 for t in range(0, len(special_buffer)):
                    #                                     # print(t)
                    #                                     dummy_02[t] = special_buffer[t]
                    #                                 for u in range(0, len(special_nodes_01)):
                    #                                     # print(u)
                    #                                     dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                    #                                 # print(dummy_02)
                    #                                 # time.sleep(5)
                    #                                 buffer_special_node = dummy_02
                    #                             else:
                    #                                 if special_buffer:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("if we dont have any new created especial nodes")
                    #                                     buffer_special_node = special_buffer
                    #                                 else:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("if we dont have any previous created special nodes")
                    #                                     buffer_special_node = special_nodes_01
                    #                             if self.s_prints == 'debug':
                    #                                 print("a special nodes list is going to be store stage 2 step 3")
                    #                                 print(list(buffer_special_node))
                    #                             self.next_list_special_nodes.append(list(buffer_special_node))
                    #
                    #                         else:
                    #
                    #                             # todo verify this part
                    #                             if bandera_anexion_time:
                    #                                 self.update_lists_case_03(bandera_anexion_time, element_buffer)
                    #
                    #                             else:
                    #                                 if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                                     print("a mapping list is going to be store stage 2 step 4b")
                    #                                     print("the mapping list is")
                    #                                     print(self.lista_mapping)
                    #                                 self.next_list.append(list(self.lista_mapping))
                    #                                 # if verificacion_lista(self.lista_bug, list(self.lista_mapping)):
                    #                                 #     print("error 12 ")
                    #                                 #     time.sleep(5)
                    #                                 if self.s_prints == 'basic':
                    #                                     print("la lista hasta ahora es 08")
                    #                                     for lista_intermedia in self.next_list:
                    #                                         print(lista_intermedia)
                    #                                     # print(self.next_list)
                    #                                 self.time_slot_list_01.append(False)
                    #                             # we are going to add the special nodes
                    #                             # we notice a small bug with the append, so the next few lines solves that
                    #                             if special_buffer and special_nodes_01:
                    #                                 if self.s_prints == 'debug':
                    #                                     print("bug append special nodes")
                    #                                 # print(len(special_buffer))
                    #                                 dummy_01 = []
                    #                                 dummy_02 = [[] for r in
                    #                                             range(0, len(special_buffer) + len(special_nodes_01))]
                    #                                 if self.s_prints == 'debug':
                    #                                     print(len(special_nodes_01) + len(special_buffer))
                    #                                 for t in range(0, len(special_buffer)):
                    #                                     # print(t)
                    #                                     dummy_02[t] = special_buffer[t]
                    #                                 for u in range(0, len(special_nodes_01)):
                    #                                     # print(u)
                    #                                     dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                    #                                 # print(dummy_02)
                    #                                 # time.sleep(5)
                    #                                 buffer_special_node = dummy_02
                    #                             else:
                    #                                 if special_buffer:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("if we dont have any new created especial nodes")
                    #                                     buffer_special_node = special_buffer
                    #                                 else:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("if we dont have any previous created special nodes")
                    #                                     buffer_special_node = special_nodes_01
                    #                             if self.s_prints == 'debug':
                    #                                 print("a special nodes list is going to be store stage 2 step 4")
                    #                                 print(list(buffer_special_node))
                    #                             self.next_list_special_nodes.append(list(buffer_special_node))
                    #
                    #
                    #
                    #
                    #     else:
                    #         f = datetime.now()
                    #         for elemento in available_nodes:
                    #             if self.s_prints == 'testexh':
                    #                 print(elemento)
                    #             d = datetime.now()
                    #             element_buffer = elemento_buffer_copy.copy()
                    #             self.lista_mapping = element_in_list_copy.copy()
                    #             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                 b = datetime.now()
                    #                 now = b.strftime("%H:%M:%S.%f")
                    #                 c = b - d
                    #                 print(
                    #                     f"Copy of the list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #             # change made to have a list of operations in the resources not only one type of operation
                    #             if self.s_prints == 'basic':
                    #                 print("something is not right")
                    #             d = datetime.now()
                    #             if self.AG_copia.nodes[node_AG]['op'] in self.DG_copia.nodes[elemento]['op']:
                    #                 # print("dsfsd")
                    #                 # if self.DG_copia.node[elemento]['op'] == self.AG_copia.node[node_AG]['op']:
                    #                 #######################################################################################
                    #                 #############this is a change made 20112019
                    #                 ###########################################################
                    #                 if self.s_prints == 'basic':
                    #                     print("EMPEZAREMOS CON LOS CAMBIOS 05")
                    #
                    #                     print(elemento)
                    #                     for bla in self.dict_nodes.items():
                    #                         print(bla)
                    #                     print(self.dict_nodes[elemento]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'])
                    #                 if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                     b = datetime.now()
                    #                     now = b.strftime("%H:%M:%S.%f")
                    #                     c = b - d
                    #                     print(
                    #                         f"Verification of the type for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                 d = datetime.now()
                    #                 vector_validacion_parametros = self.verification_of_parameters(node_AG, elemento)
                    #                 if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                     b = datetime.now()
                    #                     now = b.strftime("%H:%M:%S.%f")
                    #                     c = b - d
                    #                     print(
                    #                         f"Validation of parameters for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                 d = datetime.now()
                    #                 bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, elemento)
                    #                 if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                     b = datetime.now()
                    #                     now = b.strftime("%H:%M:%S.%f")
                    #                     c = b - d
                    #                     print(
                    #                         f"Retrieve of sensor info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                 debug_interno = False
                    #                 # if node_AG == 2 and elemento == 1:
                    #                 #     debug_interno = False
                    #                 if self.s_prints == 'basic' or debug_interno:
                    #                     print("test de algo bug 08")
                    #                     print(
                    #                         f"vector validacion de parametros {vector_validacion_parametros} bandera source {bandera_source_of_data}")
                    #                     print(self.lista_mapping)
                    #
                    #                 # we verify if the data dependency is correct
                    #                 # TODO increase the comparative, this is not the complete verification
                    #                 ### this variable is to check a bug where the list is append at the last element
                    #                 if all(vector_validacion_parametros) and bandera_source_of_data:
                    #                     dummy_bug_01 = False
                    #                     if self.s_prints == 'basic':
                    #                         print("parece que entroe aqui hay que checar")
                    #                     d = datetime.now()
                    #                     if node_AG in self.sources_AG:
                    #                         # print("dfsdf")
                    #                         # because there is no predecessor we can map the task
                    #                         if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                             print(
                    #                                 f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                    #                             print(
                    #                                 f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                             print("------------------------------------------------------------")
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         resultado_latencia, resultado_latencia_total = self.obtention_latency(elemento,
                    #                                                                                               node_AG)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         if self.s_prints == 'basic':
                    #                             print("estamos checando las latencias", resultado_latencia_total,
                    #                                   resultado_latencia)
                    #                         d = datetime.now()
                    #                         #todo verification of this thing
                    #                         actuator_sink = self.only_actuator_sink(node_AG, elemento)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Validation of the actuator for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         info_actuator = self.info_actuator_generator(node_AG)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Retrieve of actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                    #                         bandera_need_of_time_slot = False
                    #                         self.lista_mapping[elemento] = [True, node_AG, elemento,
                    #                                                         self.AG.nodes[node_AG]['op'],
                    #                                                         self.dict_nodes[elemento]['ops'][
                    #                                                             self.AG.nodes[node_AG]['op']]['latency'],
                    #                                                         self.AG.nodes[node_AG]['par'],
                    #                                                         self.AG.nodes[node_AG]['par'],
                    #                                                         self.dict_nodes[elemento]['ops'][
                    #                                                             self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                         resultado_latencia, resultado_latencia_total,
                    #                                                         info_sensor, info_actuator, actuator_sink]
                    #
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                    #                         #                             self.AG.node[node_AG]['par'],self.AG.node[node_AG]['par'],self.AG.node[node_AG]['lat']]
                    #                         # TODO: this is a bug where we mixup the lists, in the sense that we though that it was a list
                    #                         # with several time slots but it wasn't so i add this verification, i think that we can
                    #                         # remove it because i fixed the error with the append
                    #                         d = datetime.now()
                    #                         if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):
                    #
                    #                             # this is to keep control of the creation of time slots, it has to do with a
                    #                             # problem of the append and all the same lines as the following take care of that
                    #                             # problem
                    #                             # todo there is a issue with the list the following lines could solve it i dont know
                    #                             if bandera_anexion_time:
                    #                                 self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                             else:
                    #                                 self.update_lists_case_02(element_buffer)
                    #                             if self.s_prints == 'basic':
                    #                                 print("regreso de procesamiento de listas 44")
                    #                             # in here maybe we are not going to create any special node, but because the list of
                    #                             # special nodes needs to have the same length as the next list, every time that we
                    #                             # append the next list we need to append the special nodes list at least with an
                    #                             # empty list
                    #                             if self.s_prints == 'debug':
                    #                                 print("a special nodes list is going to be store stage 2 step 1")
                    #                                 print(list(special_buffer))
                    #                             self.next_list_special_nodes.append(list(special_buffer))
                    #                         else:
                    #
                    #                             # todo verify if this part is necessary
                    #                             if bandera_anexion_time:
                    #                                 self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                             else:
                    #                                 if self.s_prints == 'testexh':
                    #                                     print("a mapping list is going to be store stage 2 step 2")
                    #                                     print("the mapping list is")
                    #                                     print(self.lista_mapping)
                    #                                 self.next_list.append(self.lista_mapping.copy())
                    #                                 # if verificacion_lista(self.lista_bug, self.lista_mapping):
                    #                                 #     print("error 08 ")
                    #                                 #     time.sleep(5)
                    #
                    #                                 if self.s_prints == 'basic':
                    #                                     print("la lista hasta ahora es 04")
                    #                                     for lista_intermedia in self.next_list:
                    #                                         print(lista_intermedia)
                    #                                     # print(self.next_list)
                    #                                 self.time_slot_list_01.append(False)
                    #
                    #                             if self.s_prints == 'basic':
                    #                                 print("regreso de procesamiento de listas 55")
                    #                             if self.s_prints == 'testexh':
                    #                                 print("a special nodes list is going to be store stage 2 step 2")
                    #                                 print(list(special_buffer))
                    #                             self.next_list_special_nodes.append(list(special_buffer))
                    #
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Update of the lists for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #                         if self.debug_info == 'memory':
                    #                             print(
                    #                             f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                    #
                    #
                    #                     else:
                    #                         # Because the task is not a source task we need to verify the data dependency
                    #                         # we obtain all the predecessor and we verify the data dependency
                    #                         if self.s_prints == 'basic':
                    #                             print("We are going to check the data dependency of the task ", node_AG)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         predecessors = self.AG.predecessors(node_AG)
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Retrieve of the predecessors for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         # We noticed a bug related to the number of time slots, this created an issue with the
                    #                         # module of graph creation, the following lines solves that problem
                    #                         if bandera_anexion_time:
                    #                             instancia = len(element_buffer)
                    #                         else:
                    #                             instancia = 0
                    #                         self.bandera_debug = False
                    #                         # if self.s_prints == 'basic' and self.s_pause == True and elemento == 2 and node_AG == 2:
                    #                         #     self.bandera_debug = True
                    #                         # else:
                    #                         #     self.bandera_debug = False
                    #                         if self.s_prints == 'testexh':
                    #                             print("EL ERROR ES OSDOFNSDFNS")
                    #                         d = datetime.now()
                    #                         valid_place, special_nodes_01 = self.verification_of_dependence(predecessors,
                    #                                                                                         element_in_list,
                    #                                                                                         element_buffer,
                    #                                                                                         elemento,
                    #                                                                                         node_AG,
                    #                                                                                         instancia)
                    #
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Verification of data dependence for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         if self.s_prints == 'basic':
                    #                             print(
                    #                                 f"predecesores de la tarea {node_AG}, son {list(self.AG.predecessors(node_AG))} y el elemento es {elemento} y la bandera es {valid_place}")
                    #                             print(f"y la lista hasta ahora es {element_buffer}")
                    #                         # if debug_interno:
                    #                         #     input("debug interno - enter continue")
                    #
                    #                         # after a succesful verification we map the task
                    #                         # if valid_place and all(vector_validacion_parametros) and not bandera_no_match_parameters:
                    #                         #####################################################################
                    #                         #############this is the one that is not working
                    #
                    #                         if valid_place:
                    #                             # if not False in vector_dependency_02 :
                    #                             if self.s_prints == 'debug':
                    #                                 print("Map")
                    #                             elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                                 print(
                    #                                     f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                    #                                 print(
                    #                                     f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                                 print("------------------------------------------------------------")
                    #
                    #                             ############this is the new way to obtain the latency
                    #                             d = datetime.now()
                    #                             resultado_latencia, resultado_latencia_total = self.obtention_latency(
                    #                                 elemento, node_AG)
                    #
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             if self.s_prints == 'basic':
                    #                                 print("estamos checando las latencias 03", resultado_latencia_total,
                    #                                       resultado_latencia)
                    #
                    #                                 # we are going to add the copy nodes
                    #                             if self.s_prints == 'basic' or self.s_prints == 'debug':
                    #                                 print(self.lista_nodos_copy)
                    #                                 print("we are going to map something so we need to add the copy nodes")
                    #
                    #                             d = datetime.now()
                    #                             latency_copy = self.obtention_latency_copy_node(elemento)
                    #
                    #                             # d = datetime.now()
                    #                             for copy_node in self.lista_nodos_copy:
                    #                                 self.lista_mapping[copy_node] = [True, None, 'copy', 'copy', 0, 0,
                    #                                                                  0, 0, latency_copy, latency_copy, 0, 0,
                    #                                                                  0]
                    #                             # if self.bandera_time_slots:
                    #                             #     try:
                    #                             #         for i in self.lista_nodos_copy_time_slot:
                    #                             #             element_buffer[self.time_slot_copy_nodes][i] = [True, None, 'copy', 'copy', 0, 0,
                    #                             #                                      0, 0, latency_copy, latency_copy, 0, 0, 0]
                    #                             #     except:
                    #                             #         pass
                    #                             contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                    #                             actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             # if node_AG in self.sinks_AG:
                    #                             #     self.generation_copy_nodes(node_AG,elemento)
                    #                             # self.generation_copy_nodes(node_AG,elemento)
                    #
                    #                             d = datetime.now()
                    #                             info_actuator = self.info_actuator_generator(node_AG)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             bandera_need_of_time_slot = False
                    #                             self.lista_mapping[elemento] = [True, node_AG, elemento,
                    #                                                             self.AG.nodes[node_AG]['op'],
                    #                                                             self.dict_nodes[elemento]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']][
                    #                                                                 'latency'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.dict_nodes[elemento]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                             resultado_latencia,
                    #                                                             resultado_latencia_total, info_sensor,
                    #                                                             info_actuator, actuator_sink]
                    #
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             # todo change this
                    #                             # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                    #                             #                         self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                    #                             if self.s_prints == 'basic':
                    #                                 print("aqui aparece un buggazo", self.lista_mapping)
                    #                             d = datetime.now()
                    #                             if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):
                    #
                    #                                 # todo verify if this is necessary
                    #                                 if bandera_anexion_time:
                    #                                     self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #
                    #                                 else:
                    #                                     self.update_lists_case_02(element_buffer)
                    #                                 if self.s_prints == 'basic':
                    #                                     print("regreso de procesamiento de listas 11")
                    #                                 # we are going to add the special nodes
                    #                                 # we notice a small bug with the append, so the next few lines solves that
                    #                                 if special_buffer and special_nodes_01:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("bug append special nodes")
                    #                                     # print(len(special_buffer))
                    #                                     dummy_01 = []
                    #                                     dummy_02 = [[] for r in
                    #                                                 range(0, len(special_buffer) + len(special_nodes_01))]
                    #                                     # print("test de algo special")
                    #                                     # print(len(element_buffer))
                    #                                     if self.s_prints == 'debug':
                    #                                         print(len(special_nodes_01) + len(special_buffer))
                    #                                     for t in range(0, len(special_buffer)):
                    #                                         # print(t)
                    #                                         dummy_02[t] = special_buffer[t]
                    #                                     for u in range(0, len(special_nodes_01)):
                    #                                         # print(u)
                    #                                         dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                    #                                     # print(dummy_02)
                    #                                     # time.sleep(5)
                    #                                     buffer_special_node = dummy_02
                    #                                 else:
                    #                                     if special_buffer:
                    #                                         if self.s_prints == 'debug':
                    #                                             print("if we dont have any new created especial nodes")
                    #                                         buffer_special_node = special_buffer
                    #                                     else:
                    #                                         if self.s_prints == 'debug':
                    #                                             print("if we dont have any previous created special nodes")
                    #                                         buffer_special_node = special_nodes_01
                    #                                 if self.s_prints == 'debug':
                    #                                     print("a special nodes list is going to be store stage 2 step 3")
                    #                                     print(list(buffer_special_node))
                    #                                 self.next_list_special_nodes.append(list(buffer_special_node))
                    #
                    #                             else:
                    #
                    #                                 # todo verify this part
                    #                                 if bandera_anexion_time:
                    #                                     self.update_lists_case_03(bandera_anexion_time, element_buffer)
                    #
                    #                                 else:
                    #                                     if self.s_prints == 'testexh' or self.s_prints == 'basic':
                    #                                         print("a mapping list is going to be store stage 2 step 4b")
                    #                                         print("the mapping list is")
                    #                                         print(self.lista_mapping)
                    #                                     self.next_list.append(list(self.lista_mapping))
                    #                                     # if verificacion_lista(self.lista_bug, list(self.lista_mapping)):
                    #                                     #     print("error 12 ")
                    #                                     #     time.sleep(5)
                    #                                     if self.s_prints == 'basic':
                    #                                         print("la lista hasta ahora es 08")
                    #                                         for lista_intermedia in self.next_list:
                    #                                             print(lista_intermedia)
                    #                                         # print(self.next_list)
                    #                                     self.time_slot_list_01.append(False)
                    #                                 # we are going to add the special nodes
                    #                                 # we notice a small bug with the append, so the next few lines solves that
                    #                                 if special_buffer and special_nodes_01:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("bug append special nodes")
                    #                                     # print(len(special_buffer))
                    #                                     dummy_01 = []
                    #                                     dummy_02 = [[] for r in
                    #                                                 range(0, len(special_buffer) + len(special_nodes_01))]
                    #                                     if self.s_prints == 'debug':
                    #                                         print(len(special_nodes_01) + len(special_buffer))
                    #                                     for t in range(0, len(special_buffer)):
                    #                                         # print(t)
                    #                                         dummy_02[t] = special_buffer[t]
                    #                                     for u in range(0, len(special_nodes_01)):
                    #                                         # print(u)
                    #                                         dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                    #                                     # print(dummy_02)
                    #                                     # time.sleep(5)
                    #                                     buffer_special_node = dummy_02
                    #                                 else:
                    #                                     if special_buffer:
                    #                                         if self.s_prints == 'debug':
                    #                                             print("if we dont have any new created especial nodes")
                    #                                         buffer_special_node = special_buffer
                    #                                     else:
                    #                                         if self.s_prints == 'debug':
                    #                                             print("if we dont have any previous created special nodes")
                    #                                         buffer_special_node = special_nodes_01
                    #                                 if self.s_prints == 'debug':
                    #                                     print("a special nodes list is going to be store stage 2 step 4")
                    #                                     print(list(buffer_special_node))
                    #                                 self.next_list_special_nodes.append(list(buffer_special_node))
                    #                             if self.debug_info == 'memory':
                    #                                 print(
                    #                                     f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #             b = datetime.now()
                    #             now = b.strftime("%H:%M:%S.%f")
                    #             c = b - f
                    #             print(
                    #                 f"Finish of the first stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #
                    #
                    #
                    #     bandera_no_mapping = False
                    #     f = datetime.now()
                    #
                    #     # in here we will add the time slot
                    #     if bandera_time_slots_creation or  bandera_need_of_time_slot:
                    #     # if True:
                    #         # Now we start the addition of a new time slot
                    #         if self.s_prints == 'testexh' or self.s_prints == 'basic' or self.s_prints == 'iter':
                    #             # print("------------------------------------------------------------")
                    #             print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
                    #             print(f"Addition of a time slot {contador_time_slots + 1}")
                    #             print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
                    #         if self.s_pause:
                    #             input("Press Enter to continue...")
                    #
                    #         d = datetime.now()
                    #         element_buffer = copy.deepcopy(self.master_elemento_buffer)
                    #         self.lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n in
                    #                               range(0, len(self.DG.nodes))]
                    #         # The purpose is to map the task in any feasible resource in the new time slot, this will required
                    #         # the addition of special nodes and in general the verification of data dependency
                    #         # For each resource in the hardware graph
                    #         counter_error = 0
                    #         bandera_no_mapping = True
                    #         copia_elemento_buffer = element_buffer.copy()
                    #         if self.s_prints == 'testexh':
                    #             print("ELEMENTO COPIA BUG 0000")
                    #             print(copia_elemento_buffer)
                    #
                    #         name_task = self.dict_nodes_a[node_AG]['name']
                    #
                    #         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #             b = datetime.now()
                    #             now = b.strftime("%H:%M:%S.%f")
                    #             c = b - d
                    #             print(
                    #                 f"Copy stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #
                    #         if name_task in self.lista_tareas_constrains:
                    #
                    #
                    #             resource, name_resource = self.info_resource(name_task)
                    #
                    #             vector_validacion_parametros = self.verification_of_parameters(node_AG, resource)
                    #             bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)
                    #
                    #             # we verify if the data dependency is correct
                    #             # TODO increase the comparative, this is not the complete verification
                    #             # The task is a source task so we dont need data dependency verification
                    #             if node_AG in self.sources_AG:
                    #                 if all(vector_validacion_parametros) and bandera_source_of_data:
                    #                     # because there is no predecessor we can map the task and also we dont need any special node
                    #                     if self.s_prints == 'debug':
                    #                         print("Map")
                    #                     elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                         print(
                    #                             f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                    #                         print(
                    #                             f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                         print("------------------------------------------------------------")
                    #
                    #                     ##############################
                    #                     # todo check if this is necessary
                    #                     predecessors = list(self.AG.predecessors(node_AG))
                    #                     if self.s_prints == 'testexh' or self.s_prints == 'basic':
                    #                         print(" 01 - set of predecessors of task ", node_AG, " is ", predecessors)
                    #                         print("modulo 5 we try to map ", node_AG, " on the resource ", resource)
                    #                     lista_nodos_copy_01 = []
                    #                     lista_nodos_copy_02 = []
                    #                     for predecessor in predecessors:
                    #                         # Now, the issue in here is that we need to check de data dependency in the
                    #                         # previous time slots
                    #                         contador_time_slots = 0
                    #                         if self.s_prints == 'basic': print(element_buffer)
                    #                         # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                    #                         # un time slot entonces iteraremos sobre ese mismo time slot
                    #                         if first_time_special:
                    #                             for u in element_buffer:
                    #                                 if self.s_prints == 'basic':
                    #                                     print("stest", u)
                    #                                 if u[0]:
                    #                                     if predecessor == u[1]:
                    #                                         node_place = u[2]
                    #                                         break
                    #                         else:
                    #                             # como no es la primera vez tenemos que iterar sobre time slots
                    #                             for u in element_buffer:
                    #                                 for elemento_en_time_slot in u:
                    #                                     if elemento_en_time_slot[0]:
                    #                                         if predecessor == elemento_en_time_slot[1]:
                    #                                             node_place = elemento_en_time_slot[2]
                    #                                             break
                    #                                 contador_time_slots += 1
                    #                         node_place_buffer = node_place
                    #                         if self.s_prints == 'basic':
                    #                             print("bug 30 bueno pues el lugar es ", node_place, " y el time slot es ",
                    #                                   contador_time_slots)
                    #                             if first_time_special:
                    #                                 print(element_buffer[node_place])
                    #                             else:
                    #                                 print(element_buffer[contador_time_slots][node_place])
                    #
                    #                         if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                             print("the node place is ", node_place, "on time slot", contador_time_slots)
                    #                         # we check if the if the predecessor is mapped on a sink or it can reach a sink
                    #                         # print("bug 06")
                    #
                    #                     resultado_latencia, resultado_latencia_total = self.obtention_latency(resource,
                    #                                                                                           node_AG)
                    #
                    #                     if self.s_prints == 'basic':
                    #                         print("estamos checando las latencias 02", resultado_latencia_total,
                    #                               resultado_latencia)
                    #
                    #                     actuator_sink = self.generation_copy_nodes(node_AG, resource)
                    #                     info_actuator = self.info_actuator_generator(node_AG)
                    #
                    #                     bandera_no_mapping = False
                    #                     self.lista_mapping[resource] = [True, node_AG, resource,
                    #                                                     self.AG.nodes[node_AG]['op'],
                    #                                                     self.dict_nodes[resource]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['latency'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.dict_nodes[resource]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                     resultado_latencia, resultado_latencia_total,
                    #                                                     info_sensor,
                    #                                                     info_actuator, actuator_sink]
                    #
                    #                     self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #                     if self.s_prints == 'basic':
                    #                         print("regreso de procesamiento de listas 33")
                    #                     if self.s_prints == 'debug':
                    #                         print("a special nodes list is going to be store stage 2 step 5")
                    #                         print(list(special_buffer))
                    #                     self.next_list_special_nodes.append(list(special_buffer))
                    #
                    #             else:
                    #                 # because the task is not a source task we verify the data dependency
                    #                 # this part can use the function of verification, but i havent done it yet
                    #                 predecessors = list(self.AG.predecessors(node_AG))
                    #                 if self.s_prints == 'testexh' or self.s_prints == 'basic':
                    #                     print("02 - set of predecessors of task ", node_AG, " is ", predecessors)
                    #                     print("modulo 4 we try to map ", node_AG, " on the resource ", resource)
                    #                 lista_nodos_copy_01 = []
                    #                 lista_nodos_copy_02 = []
                    #                 vector_dependency_02 = []
                    #                 for predecessor in predecessors:
                    #                     # Now, the issue in here is that we need to check de data dependency in the
                    #                     # previous time slots
                    #                     contador_time_slots = 0
                    #                     if self.s_prints == 'basic': print(element_buffer)
                    #                     # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                    #                     # un time slot entonces iteraremos sobre ese mismo time slot
                    #                     if first_time_special or not bandera_anexion_time:
                    #                         for u in element_buffer:
                    #                             if self.s_prints == 'debug':
                    #                                 if self.s_prints == 'basic':
                    #                                     print("stest", u)
                    #                             if u[0]:
                    #                                 if predecessor == u[1]:
                    #                                     node_place = u[2]
                    #                                     break
                    #                     else:
                    #                         # como no es la primera vez tenemos que iterar sobre time slots
                    #                         if self.s_prints == 'basic':
                    #                             print("buggazo")
                    #                             print(element_buffer)
                    #                         for u in element_buffer:
                    #                             for elemento_en_time_slot in u:
                    #                                 if elemento_en_time_slot[0]:
                    #                                     if predecessor == elemento_en_time_slot[1]:
                    #                                         node_place = elemento_en_time_slot[2]
                    #                                         break
                    #                             contador_time_slots += 1
                    #                     node_place_buffer = node_place
                    #                     if self.s_prints == 'basic':
                    #                         print("bug 20 bueno pues el lugar es ", node_place, " y el time slot es ",
                    #                               contador_time_slots)
                    #                         if first_time_special or not bandera_anexion_time:
                    #                             print(element_buffer[node_place])
                    #                         else:
                    #                             print(element_buffer[contador_time_slots - 1][node_place])
                    #
                    #                     if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                         print("the node place is ", node_place, "on time slot", contador_time_slots)
                    #                         print(resource, self.sources_DG)
                    #                     # we check if the if the predecessor is mapped on a sink or it can reach a sink
                    #                     # print("bug 06")
                    #                     ## change 12062020 self.list_sinks_connected_to_rc for self.sinks_DG
                    #                     if node_place in self.list_sinks_connected_to_rc:
                    #                         nodo_sink = node_place
                    #                     else:
                    #
                    #                         copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    #                         done = True
                    #                         counter_internal = 0
                    #                         # copy_list_sinks_connected_to_rc.remove(nodo_sink)
                    #                         while done:
                    #                             if copy_list_sinks_connected_to_rc:
                    #                                 sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                    #                                                                               copy_list_sinks_connected_to_rc,
                    #                                                                               node_place)
                    #                             else:
                    #                                 counter_internal = counter_internal + 1
                    #                                 copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    #                                 sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                    #                                                                               copy_list_sinks_connected_to_rc,
                    #                                                                               node_place)
                    #                             # print(sink_nodo_sink_task,resource)
                    #                             if element_buffer[contador_time_slots - 1][sink_nodo_sink_task][0]:
                    #                                 copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                    #                                 if counter_internal == 5:
                    #                                     sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                    #                                                                                   copy_list_sinks_connected_to_rc,
                    #                                                                                   node_place)
                    #                                     done = False
                    #                                     break
                    #
                    #                             else:
                    #                                 done = False
                    #                                 break
                    #                         nodo_sink = sink_nodo_sink_task
                    #
                    #                         # nodo_sink = sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)
                    #                     # print("bug 05")
                    #                     if resource in self.sources_DG:
                    #                         nodo_source = resource
                    #                     else:
                    #                         nodo_source = source_node_from_any_node(self.DG, self.sources_DG, resource)
                    #                     for element in self.lista_mapping:
                    #                         if predecessor == element[1]:
                    #                             node_place = element[2]
                    #                     if self.s_prints == 'debug':
                    #                         print(" we find the place  ", node_place, resource)
                    #                     paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                    #                     # vector_dependency_02 = []
                    #                     # print("the paths ", paths)
                    #                     for path_b in paths:
                    #                         path = list(path_b)
                    #                         # path.remove(node_place)
                    #                         path_buffer = list(path)
                    #                         path_buffer.remove(node_place)
                    #                         path_buffer.remove(resource)
                    #                         lista_nodos_copy_01 = lista_nodos_copy_01 + path_buffer
                    #
                    #                         vector_dependency_01 = []
                    #                         for node in path:
                    #                             vector_dependency_01 = vector_dependency_01 + [self.lista_mapping[node][0]]
                    #                         if True in vector_dependency_01:
                    #                             vector_dependency_02 = vector_dependency_02 + [False]
                    #
                    #                     ####################se cambiara de indent
                    #                 if not False in vector_dependency_02 and all(
                    #                         vector_validacion_parametros) and bandera_source_of_data:
                    #                     if self.s_prints == 'debug':
                    #                         print("Map")
                    #                     elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                         print(
                    #                             f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                    #                         print(
                    #                             f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                         print("------------------------------------------------------------")
                    #
                    #                     resultado_latencia, resultado_latencia_total = self.obtention_latency(resource,
                    #                                                                                           node_AG)
                    #
                    #                     if self.s_prints == 'basic':
                    #                         print("estamos checando las latencias 01", resultado_latencia_total,
                    #                               resultado_latencia)
                    #                         print(self.lista_mapping)
                    #
                    #                     # we are going to add the copy nodes
                    #                     if self.s_prints == 'basic' or self.s_prints == 'testexh':
                    #                         # print(self.lista_nodos_copy)
                    #                         print(
                    #                             "we are going to map something so we need to add the copy nodes stage 2")
                    #
                    #                         print(node_place_buffer, nodo_sink, nodo_source, resource)
                    #                     # empecemos con los nodos en el time slot anterior
                    #
                    #                     element_buffer, actuator_sink = self.generation_copy_nodes_time_slot(node_AG,
                    #                                                                                          resource,
                    #                                                                                          first_time_special,
                    #                                                                                          bandera_anexion_time,
                    #                                                                                          nodo_sink,
                    #                                                                                          node_place_buffer,
                    #                                                                                          element_buffer,
                    #                                                                                          nodo_source,
                    #                                                                                          node_place,
                    #                                                                                          contador_time_slots)
                    #
                    #                     info_actuator = self.info_actuator_generator(node_AG)
                    #                     bandera_no_mapping = False
                    #                     self.lista_mapping[resource] = [True, node_AG, resource,
                    #                                                     self.AG.nodes[node_AG]['op'],
                    #                                                     self.dict_nodes[resource]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['latency'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.AG.nodes[node_AG]['par'],
                    #                                                     self.dict_nodes[resource]['ops'][
                    #                                                         self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                     resultado_latencia, resultado_latencia_total,
                    #                                                     info_sensor, info_actuator, actuator_sink]
                    #                     # todo we need to change this
                    #                     # self.lista_mapping[resource] = [True, node_AG, resource,self.AG.node[node_AG]['op'],self.DG.node[resource]['lat'],\
                    #                     #                     self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                    #                     dummy_01 = self.update_lists_case_04(element_buffer, bandera_anexion_time)
                    #                     #
                    #                     # time.sleep(5)
                    #                     item_to_append = [True, nodo_sink, nodo_source, len(dummy_01) - 1,
                    #                                       self.contador_recomputacion]
                    #
                    #                     # the following lines are for the append of the special nodes list
                    #                     if special_buffer:
                    #                         # print(len(special_buffer))
                    #                         dummy_01 = []
                    #                         dummy_02 = [[] for r in range(0, len(special_buffer) + 1)]
                    #                         # print("test de algo special")
                    #                         # print(len(element_buffer))
                    #                         for t in range(0, len(special_buffer)):
                    #                             # print(t)
                    #                             dummy_02[t] = special_buffer[t]
                    #                         dummy_02[len(special_buffer)] = item_to_append
                    #                         buffer_special_node = dummy_02
                    #                     else:
                    #                         buffer_special_node = [item_to_append]
                    #                     if self.s_prints == 'debug':
                    #                         print("a special nodes list is going to be store stage 2 step 4")
                    #                         print(list(buffer_special_node))
                    #                     self.next_list_special_nodes.append(list(buffer_special_node))
                    #                     self.contador_recomputacion = self.contador_recomputacion + 1
                    #
                    #             ###############
                    #
                    #
                    #
                    #
                    #         else:
                    #
                    #             for resource in (self.DG_copia.nodes):
                    #                 element_buffer = copy.deepcopy(self.master_elemento_buffer)
                    #                 # element_buffer = copia_elemento_buffer.copy()
                    #                 if self.s_prints == 'testexh':
                    #                     print("por cada resource", resource, counter_error, len(self.DG_copia.nodes),
                    #                           node_AG, self.AG_copia.nodes[node_AG]['name'])
                    #                     print("el elemento buffer")
                    #                     print(element_buffer)
                    #                     print("elemento copia")
                    #                     print(copia_elemento_buffer)
                    #
                    #                 # print(resource)
                    #
                    #                 # verify if the types are compatible
                    #                 d = datetime.now()
                    #                 if self.AG_copia.nodes[node_AG]['op'] in self.DG_copia.nodes[resource]['op']:
                    #                     # if self.DG_copia.node[resource]['op'] == self.AG_copia.node[node_AG]['op']:
                    #                     #######################################################################################
                    #                     #############this is a change made 20112019
                    #                     ###########################################################
                    #                     if self.s_prints == 'basic':
                    #                         print("EMPEZAREMOS CON LOS CAMBIOS")
                    #                     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                         b = datetime.now()
                    #                         now = b.strftime("%H:%M:%S.%f")
                    #                         c = b - d
                    #                         print(
                    #                             f"Verification of type for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                     d = datetime.now()
                    #
                    #                     vector_validacion_parametros = self.verification_of_parameters(node_AG, resource)
                    #                     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                         b = datetime.now()
                    #                         now = b.strftime("%H:%M:%S.%f")
                    #                         c = b - d
                    #                         print(
                    #                             f"Validation of parameters for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                     d = datetime.now()
                    #                     bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)
                    #                     if self.s_prints == 'basic':
                    #                         print("regreso de las funciones de validacion", vector_validacion_parametros,
                    #                               bandera_source_of_data, info_sensor)
                    #                     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                         b = datetime.now()
                    #                         now = b.strftime("%H:%M:%S.%f")
                    #                         c = b - d
                    #                         print(
                    #                             f"Retrieve sensor info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                     # we verify if the data dependency is correct
                    #                     # TODO increase the comparative, this is not the complete verification
                    #                     # The task is a source task so we dont need data dependency verification
                    #                     d = datetime.now()
                    #                     if node_AG in self.sources_AG:  # and all(vector_validacion_parametros) and bandera_source_of_data:
                    #                         # because there is no predecessor we can map the task and also we dont need any special node
                    #
                    #                         if all(vector_validacion_parametros) and bandera_source_of_data:
                    #                             if self.s_prints == 'debug':
                    #                                 print("Map")
                    #                             elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    #                                 print(
                    #                                     f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                    #                                 print(
                    #                                     f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                                 print("------------------------------------------------------------")
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             resultado_latencia, resultado_latencia_total = self.obtention_latency(
                    #                                 resource, node_AG)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             if self.s_prints == 'basic':
                    #                                 print("estamos checando las latencias 02", resultado_latencia_total,
                    #                                       resultado_latencia)
                    #                             d = datetime.now()
                    #                             actuator_sink = self.generation_copy_nodes(node_AG, resource)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             info_actuator = self.info_actuator_generator(node_AG)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             bandera_no_mapping = False
                    #                             self.lista_mapping[resource] = [True, node_AG, resource,
                    #                                                             self.AG.nodes[node_AG]['op'],
                    #                                                             self.dict_nodes[resource]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']][
                    #                                                                 'latency'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.dict_nodes[resource]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                             resultado_latencia,
                    #                                                             resultado_latencia_total, info_sensor,
                    #                                                             info_actuator, actuator_sink]
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             self.update_lists_case_01(element_buffer, bandera_anexion_time)
                    #                             if self.s_prints == 'basic':
                    #                                 print("regreso de procesamiento de listas 00")
                    #                                 for n_lista in self.next_list:
                    #                                     print(n_lista)
                    #                                 print("termino de")
                    #                             if self.s_prints == 'debug':
                    #                                 print("a special nodes list is going to be store stage 2 step 5")
                    #                                 print(list(special_buffer))
                    #                             self.next_list_special_nodes.append(list(special_buffer))
                    #                             if self.debug_info == 'memory':
                    #                                 print(
                    #                                     f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                     else:
                    #                         # because the task is not a source task we verify the data dependency
                    #                         # this part can use the function of verification, but i havent done it yet
                    #
                    #                         d = datetime.now()
                    #                         predecessors = list(self.AG.predecessors(node_AG))
                    #                         if self.s_prints == 'testexh' or self.s_prints == 'basic':
                    #                             print("03 - set of predecessors of task ", node_AG, " is ", predecessors)
                    #                             print("modulo 2 we try to map ", node_AG, " on the resource ", resource)
                    #                             print(element_buffer)
                    #                         lista_nodos_copy_01 = []
                    #                         lista_nodos_copy_02 = []
                    #                         vector_dependency_02 = []
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Predecessors for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         d = datetime.now()
                    #                         for predecessor in predecessors:
                    #                             # Now, the issue in here is that we need to check de data dependency in the
                    #                             # previous time slots
                    #                             contador_time_slots = 0
                    #                             node_place = None
                    #                             if self.s_prints == 'testexh':
                    #                                 print(
                    #                                     f"el elemento buffer se imprimira las bandera primera vez {first_time_special} y anexion tiempo {bandera_anexion_time}")
                    #                                 print(element_buffer)
                    #                                 # for uno in element_buffer:
                    #                                 #     print(uno)
                    #                             # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                    #                             # un time slot entonces iteraremos sobre ese mismo time slot
                    #                             if first_time_special or not bandera_anexion_time:
                    #                                 if self.s_prints == 'basic':
                    #                                     print("estamos en el if de algo rro bug 08")
                    #                                 for u in element_buffer:
                    #                                     if self.s_prints == 'debug':
                    #                                         print("stest", u)
                    #                                     if u[0]:
                    #                                         if predecessor == u[1]:
                    #                                             node_place = u[2]
                    #                                             break
                    #                             else:
                    #                                 # como no es la primera vez tenemos que iterar sobre time slots
                    #                                 if self.s_prints == 'basic':
                    #                                     print(f"el predeceso que estamos buscando es {predecessor}")
                    #                                     print(element_buffer)
                    #
                    #                                 for u in element_buffer:
                    #                                     for elemento_en_time_slot in u:
                    #
                    #                                         if elemento_en_time_slot[0]:
                    #                                             if predecessor == elemento_en_time_slot[1]:
                    #                                                 node_place = elemento_en_time_slot[2]
                    #                                                 break
                    #                                     contador_time_slots += 1
                    #
                    #                             ######esta parte del codigo es un quick fix para el problema de que no se encuentra el predecesor
                    #                             ######basicamente el detalle son las banderas pero mejor se anexa la siguiente parte, donde buscamos
                    #                             ######el predecesor
                    #                             contador_time_slots = 0
                    #                             bandera_salida_test = False
                    #                             if node_place == None:
                    #                                 for u in element_buffer:
                    #                                     contador_time_slots += 1
                    #                                     for elemento_en_time_slot in u:
                    #                                         if elemento_en_time_slot[0]:
                    #                                             if predecessor == elemento_en_time_slot[1]:
                    #                                                 node_place = elemento_en_time_slot[2]
                    #                                                 bandera_salida_test = True
                    #                                                 break
                    #
                    #                             node_place_buffer = node_place
                    #                             if self.s_prints == 'basic':
                    #                                 print("bug 10 bueno pues el lugar es ", node_place,
                    #                                       " y el time slot es ", contador_time_slots)
                    #                                 try:
                    #                                     if first_time_special or not bandera_anexion_time:
                    #                                         print(element_buffer[node_place])
                    #                                     else:
                    #                                         print(element_buffer[contador_time_slots - 1][node_place])
                    #                                 except:
                    #                                     pass
                    #
                    #                             if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                                 print("the node place is ", node_place, "on time slot",
                    #                                       contador_time_slots)
                    #                                 print(resource, self.sources_DG)
                    #                             # we check if the if the predecessor is mapped on a sink or it can reach a sink
                    #                             # print("bug 06")
                    #
                    #                             try:
                    #                                 # change 12062020 self.list_sinks_connected_to_rc for self.sinks_DG
                    #                                 if node_place in self.list_sinks_connected_to_rc:
                    #                                     nodo_sink = node_place
                    #                                 else:
                    #                                     ####################
                    #                                     copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    #                                     done = True
                    #                                     counter_internal = 0
                    #                                     while done:
                    #                                         if copy_list_sinks_connected_to_rc:
                    #                                             sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                    #                                                                                           copy_list_sinks_connected_to_rc,
                    #                                                                                           node_place)
                    #                                         else:
                    #                                             counter_internal = counter_internal + 1
                    #                                             copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    #                                             sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                    #                                                                                           copy_list_sinks_connected_to_rc,
                    #                                                                                           node_place)
                    #
                    #                                         if self.lista_mapping[sink_nodo_sink_task][0]:
                    #                                             copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                    #                                             if counter_internal == 5:
                    #                                                 copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc
                    #                                                 sink_nodo_sink_task = sink_node_from_any_node(
                    #                                                     self.DG_copia,
                    #                                                     copy_list_sinks_connected_to_rc,
                    #                                                     node_place)
                    #                                                 done = False
                    #                                                 break
                    #
                    #                                         else:
                    #                                             done = False
                    #                                             break
                    #
                    #                                     #################"""
                    #                                     # nodo_sink = sink_node_from_any_node(self.DG_original,self.list_sinks_connected_to_rc,node_place)
                    #
                    #                                     nodo_sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG_original,self.list_sinks_connected_to_rc,node_place)
                    #                                 # print("bug 05")
                    #                                 if resource in self.sources_DG:
                    #                                     nodo_source = resource
                    #                                 else:
                    #                                     nodo_source = source_node_from_any_node(self.DG, self.sources_DG,
                    #                                                                             resource)
                    #                                 for element in self.lista_mapping:
                    #                                     if predecessor == element[1]:
                    #                                         node_place = element[2]
                    #                                 if self.s_prints == 'debug':
                    #                                     print(" we find the place  ", node_place, resource)
                    #                                 paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                    #                                 # vector_dependency_02 = []
                    #                                 # print("the paths ", paths)
                    #                                 for path_b in paths:
                    #                                     path = list(path_b)
                    #                                     # path.remove(node_place)
                    #                                     path_buffer = list(path)
                    #                                     path_buffer.remove(node_place)
                    #                                     path_buffer.remove(resource)
                    #                                     lista_nodos_copy_01 = lista_nodos_copy_01 + path_buffer
                    #
                    #                                     vector_dependency_01 = []
                    #                                     for node in path:
                    #                                         vector_dependency_01 = vector_dependency_01 + [
                    #                                             self.lista_mapping[node][0]]
                    #                                     if True in vector_dependency_01:
                    #                                         vector_dependency_02 = vector_dependency_02 + [False]
                    #                             except:
                    #                                 vector_dependency_02 = vector_dependency_02 + [False]
                    #
                    #                         ##################################esta parte se cambiara de indent a uno menos
                    #                         # ####ahora aparecio un error de que vectordependecy no se encuentra pero es porque la tarea es source
                    #                         #
                    #                         # if node_AG in self.sources_AG:
                    #                         #     if self.s_prints == 'basic':
                    #                         #         print("la tarea es un source")
                    #                         #     vector_dependency_02 = [True]
                    #                         if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                             b = datetime.now()
                    #                             now = b.strftime("%H:%M:%S.%f")
                    #                             c = b - d
                    #                             print(
                    #                                 f"Validation of parameters and data dependence for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                         if not False in vector_dependency_02 and all(
                    #                                 vector_validacion_parametros) and bandera_source_of_data:
                    #                             if self.s_prints == 'debug':
                    #                                 print("Map")
                    #                             elif self.s_prints == 'basic' or self.s_prints == 'testexh' or self.s_prints == 'iter':
                    #                                 print(
                    #                                     f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                    #                                 print(
                    #                                     f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                    #                                 print("------------------------------------------------------------")
                    #                             d = datetime.now()
                    #                             resultado_latencia, resultado_latencia_total = self.obtention_latency(
                    #                                 resource, node_AG)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             if self.s_prints == 'basic':
                    #                                 print("estamos checando las latencias 01", resultado_latencia_total,
                    #                                       resultado_latencia)
                    #                                 print(self.lista_mapping)
                    #
                    #                             # we are going to add the copy nodes
                    #                             if self.s_prints == 'basic' or self.s_prints == 'testexh':
                    #                                 # print(self.lista_nodos_copy)
                    #                                 print(
                    #                                     "we are going to map something so we need to add the copy nodes stage 3")
                    #
                    #                                 print(node_place_buffer, nodo_sink, nodo_source, resource)
                    #                             # empecemos con los nodos en el time slot anterior
                    #                             d = datetime.now()
                    #                             element_buffer, actuator_sink = self.generation_copy_nodes_time_slot(
                    #                                 node_AG, resource, first_time_special, bandera_anexion_time, nodo_sink,
                    #                                 node_place_buffer, element_buffer, nodo_source, node_place,
                    #                                 contador_time_slots)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             info_actuator = self.info_actuator_generator(node_AG)
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             bandera_no_mapping = False
                    #                             self.lista_mapping[resource] = [True, node_AG, resource,
                    #                                                             self.AG.nodes[node_AG]['op'],
                    #                                                             self.dict_nodes[resource]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']][
                    #                                                                 'latency'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.AG.nodes[node_AG]['par'],
                    #                                                             self.dict_nodes[resource]['ops'][
                    #                                                                 self.AG.nodes[node_AG]['op']]['clk'],
                    #                                                             resultado_latencia,
                    #                                                             resultado_latencia_total, info_sensor,
                    #                                                             info_actuator, actuator_sink]
                    #                             # todo we need to change this
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                             d = datetime.now()
                    #                             dummy_01 = self.update_lists_case_04(element_buffer, bandera_anexion_time)
                    #                             item_to_append = [True, nodo_sink, nodo_source, len(dummy_01) - 1,
                    #                                               self.contador_recomputacion]
                    #                             # if node_AG == 1 and resource == 2:
                    #                             #     print(self.lista_mapping)
                    #                             #     print(element_buffer)
                    #                             #     input("input    ddd")
                    #
                    #                             # the following lines are for the append of the special nodes list
                    #                             if special_buffer:
                    #                                 # print(len(special_buffer))
                    #                                 dummy_01 = []
                    #                                 dummy_02 = [[] for r in range(0, len(special_buffer) + 1)]
                    #                                 # print("test de algo special")
                    #                                 # print(len(element_buffer))
                    #                                 for t in range(0, len(special_buffer)):
                    #                                     # print(t)
                    #                                     dummy_02[t] = special_buffer[t]
                    #                                 dummy_02[len(special_buffer)] = item_to_append
                    #                                 buffer_special_node = dummy_02
                    #                             else:
                    #                                 buffer_special_node = [item_to_append]
                    #                             if self.s_prints == 'testexh':
                    #                                 print("a special nodes list is going to be store stage 2 step 4")
                    #                                 print(list(buffer_special_node))
                    #                                 # print(element_buffer)
                    #                             self.next_list_special_nodes.append(list(buffer_special_node))
                    #                             self.contador_recomputacion = self.contador_recomputacion + 1
                    #                             if self.debug_info == 'memory':
                    #                                 print(
                    #                                     f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                    #                             if self.debug_info == 'remove' or self.debug_info == 'total':
                    #                                 b = datetime.now()
                    #                                 now = b.strftime("%H:%M:%S.%f")
                    #                                 c = b - d
                    #                                 print(
                    #                                     f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #                 #############################################################################################################################
                    #                 ###we reset the mapping list
                    #
                    #                 if counter_error >= len(self.DG_copia.nodes):
                    #                     pass
                    #                     # raise Exception(
                    #                     #     f"The mapping cycle, please verify your input files, the exception ocurred in the second stage")
                    #                 counter_error = counter_error + 1
                    #                 if self.s_prints == 'testexh':
                    #                     print("ESTAMOS BUSCANDO SOLUCIONAR EL BUG")
                    #                     print(element_buffer)
                    #                     print(" ")
                    #                     print(self.master_elemento_buffer)
                    #                 self.lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n
                    #                                       in range(0, len(self.DG.nodes))]
                    #
                    #     if self.debug_info == 'remove' or self.debug_info == 'total':
                    #         b = datetime.now()
                    #         now = b.strftime("%H:%M:%S.%f")
                    #         c = b - f
                    #         print(
                    #             f"Finish of the second stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                    #
                    #
                    #
                    #
                    #     first_time_special = False
                    #     if bandera_no_mapping:
                    #         raise Exception(
                    #             f"The mapping cycle, please verify your input files, the exception ocurred in the second stage")
                    #     if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #         print("we update the lists checando si se hacen los cambios")
                    #         print("el contenido de la lista next es")
                    #         for n_lista in self.next_list:
                    #             print(n_lista)
                    #             # input("Enter to continue...")
                    #         print("se termino de imprimir la lista")
                    #         # input("Enter to continue...")
                    #
                    #     if self.s_pause:
                    #         input("Press Enter to continue...")
                    #
                    #
                    #
                    #
                    #
                    #     next_list_total = next_list_total + self.next_list
                    #     special_nodes_total = special_nodes_total + self.next_list_special_nodes
                    #     time_slots_total = time_slots_total + self.time_slot_list_01

                    end_list = True
                    limit_number_current_list = 10
                    start_list = len(current_list_pickle)
                    current_list_section = []
                    special_nodes_section = []
                    time_slot_section = []


                    while end_list:
                        if start_list - limit_number_current_list > 0:
                            current_list_section = \
                                current_list_pickle[start_list - limit_number_current_list:start_list]

                            if bandera_pickle:
                                special_nodes_section = \
                                    special_nodes_pickle[start_list - limit_number_current_list:start_list]
                                time_slot_section = \
                                    bandera_anexion_time_pickle[start_list - limit_number_current_list:start_list]
                            start_list = start_list - limit_number_current_list
                        else:
                            current_list_section = \
                                current_list_pickle[0:start_list]
                            if bandera_pickle:
                                special_nodes_section = \
                                    special_nodes_pickle[0:start_list]
                                time_slot_section = \
                                    bandera_anexion_time_pickle[0:start_list]
                            end_list = False

                        for l in range(0, len(current_list_section)):
                            # print(lista_del_generador)
                            # while self.current_list:
                            d = datetime.now()
                            element_buffer = current_list_section[l]  # self.current_list.pop(0)
                            if bandera_pickle:
                                bandera_anexion_time = time_slot_section[l]
                                special_buffer = special_nodes_section[l]
                            else:
                                bandera_anexion_time = False
                                special_buffer = []


                            self.next_list = []
                            self.next_list_special_nodes = []
                            self.time_slot_list_01 = []
                            contador_bug = contador_bug + 0


                            # elemento_buffer_copy = list(element_buffer)
                            self.master_elemento_buffer = copy.deepcopy(element_buffer)
                            elemento_buffer_copy = element_buffer.copy()
                            # what we obtain is the last element in the preliminary mapping, a flag that tell us if there is
                            # a set of time slots or not, and finally the special nodes
                            element_in_list, bandera_anexion_time_dummy, special_buffer_dummy = self.list_process(
                                element_buffer,
                                first_time_special)


                            element_in_list_copy = element_in_list.copy()

                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Retrieve of the current list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                            #### in here we obtain the resources that can be used in the last time slot, if there is
                            # no resources we need to create another time slot
                            d = datetime.now()
                            available_nodes = self.available_nodes_function(element_in_list, node_AG)
                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - d
                                print(
                                    f"Retrieve of available nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                            # print(available_nodes)
                            if self.s_prints == 'testexh':
                                print("we are in the beggining of a new preliminary mapping")
                                print("the preliminary mapping is  ")
                                print(element_buffer)
                                print("the last time slot is ")
                                print(element_in_list)
                                print("the special nodes are ")
                                print(special_buffer)
                                print("The available resources to use are ", available_nodes, "task ", node_AG)
                                # input("Press Enter to continue...")

                            # Now, we will try to map the task into the available nodes, we need to verify in here data dependence
                            # types and so on
                            name_task = self.dict_nodes_a[node_AG]['name']
                            pareja = None
                            contador_mapeo_antes_time_slot = 0
                            if name_task in self.lista_tareas_constrains:

                                elemento, name_resource = self.info_resource(name_task)

                                if elemento in available_nodes:

                                    ###################
                                    self.lista_mapping = element_in_list_copy.copy()
                                    vector_validacion_parametros = self.verification_of_parameters(node_AG, elemento)
                                    bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, elemento)

                                    ############
                                    if all(vector_validacion_parametros) and bandera_source_of_data:
                                        dummy_bug_01 = False
                                        if node_AG in self.sources_AG:
                                            # print("dfsdf")
                                            # because there is no predecessor we can map the task
                                            if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                print(
                                                    f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                                                print(
                                                    f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                print("------------------------------------------------------------")

                                            resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                elemento,
                                                node_AG)
                                            if self.s_prints == 'basic':
                                                print("estamos checando las latencias", resultado_latencia_total,
                                                      resultado_latencia)

                                            actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                                            info_actuator = self.info_actuator_generator(node_AG)
                                            contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                                            bandera_need_of_time_slot = False
                                            self.lista_mapping[elemento] = [True, node_AG, elemento,
                                                                            self.AG.nodes[node_AG]['op'],
                                                                            self.dict_nodes[elemento]['ops'][
                                                                                self.AG.nodes[node_AG]['op']][
                                                                                'latency'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.dict_nodes[elemento]['ops'][
                                                                                self.AG.nodes[node_AG]['op']]['clk'],
                                                                            resultado_latencia,
                                                                            resultado_latencia_total,
                                                                            info_sensor, info_actuator, actuator_sink]

                                            # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                                            #                             self.AG.node[node_AG]['par'],self.AG.node[node_AG]['par'],self.AG.node[node_AG]['lat']]
                                            # TODO: this is a bug where we mixup the lists, in the sense that we though that it was a list
                                            # with several time slots but it wasn't so i add this verification, i think that we can
                                            # remove it because i fixed the error with the append
                                            if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):

                                                # this is to keep control of the creation of time slots, it has to do with a
                                                # problem of the append and all the same lines as the following take care of that
                                                # problem
                                                # todo there is a issue with the list the following lines could solve it i dont know
                                                if bandera_anexion_time:
                                                    self.update_lists_case_01(element_buffer, bandera_anexion_time)

                                                else:
                                                    self.update_lists_case_02(element_buffer)
                                                if self.s_prints == 'basic':
                                                    print("regreso de procesamiento de listas modulo 77")
                                                # in here maybe we are not going to create any special node, but because the list of
                                                # special nodes needs to have the same length as the next list, every time that we
                                                # append the next list we need to append the special nodes list at least with an
                                                # empty list
                                                if self.s_prints == 'debug':
                                                    print("a special nodes list is going to be store stage 2 step 1")
                                                    print(list(special_buffer))
                                                self.next_list_special_nodes.append(list(special_buffer))
                                            else:

                                                # todo verify if this part is necessary
                                                if bandera_anexion_time:
                                                    self.update_lists_case_01(element_buffer, bandera_anexion_time)

                                                else:
                                                    if self.s_prints == 'debug':
                                                        print("a mapping list is going to be store stage 2 step 2")
                                                        print("the mapping list is")
                                                        print(self.lista_mapping)
                                                    self.next_list.append(self.lista_mapping.copy())
                                                    # if verificacion_lista(self.lista_bug, self.lista_mapping):
                                                    #     print("error 08 ")
                                                    #     time.sleep(5)

                                                    if self.s_prints == 'basic':
                                                        print("la lista hasta ahora es 04")
                                                        for lista_intermedia in self.next_list:
                                                            print(lista_intermedia)
                                                        print("se termino de imprimir la lista 04")
                                                        # print(self.next_list)
                                                    self.time_slot_list_01.append(False)
                                                if self.s_prints == 'basic':
                                                    print("regreso de procesamiento de listas 88")

                                                if self.s_prints == 'debug':
                                                    print("a special nodes list is going to be store stage 2 step 2")
                                                    print(list(special_buffer))
                                                self.next_list_special_nodes.append(list(special_buffer))
                                        else:

                                            # Because the task is not a source task we need to verify the data dependency
                                            # we obtain all the predecessor and we verify the data dependency
                                            if self.s_prints == 'debug':
                                                print("We are going to check the data dependency of the task ", node_AG)
                                            predecessors = self.AG.predecessors(node_AG)
                                            # We noticed a bug related to the number of time slots, this created an issue with the
                                            # module of graph creation, the following lines solves that problem
                                            if bandera_anexion_time:
                                                instancia = len(element_buffer)
                                            else:
                                                instancia = 0
                                            self.bandera_debug = False
                                            if self.s_prints == 'basic' and self.s_pause == True and elemento == 2 and node_AG == 2:
                                                self.bandera_debug = True
                                            else:
                                                self.bandera_debug = False

                                            valid_place, special_nodes_01 = self.verification_of_dependence(
                                                predecessors,
                                                element_in_list,
                                                element_buffer,
                                                elemento,
                                                node_AG, instancia)

                                            if self.s_prints == 'basic':
                                                print(
                                                    f"predecesores de la tarea {node_AG}, son {list(self.AG.predecessors(node_AG))} y el elemento es {elemento} y la bandera es {valid_place}")
                                                print(f"y la lista hasta ahora es {element_buffer}")

                                            # after a succesful verification we map the task
                                            # if valid_place and all(vector_validacion_parametros) and not bandera_no_match_parameters:
                                            #####################################################################
                                            #############this is the one that is not working

                                            if valid_place:
                                                # if not False in vector_dependency_02 :
                                                if self.s_prints == 'debug':
                                                    print("Map")
                                                elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                    print(
                                                        f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                                                    print(
                                                        f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                    print(
                                                        "------------------------------------------------------------")

                                                ############this is the new way to obtain the latency

                                                resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                    elemento,
                                                    node_AG)
                                                if self.s_prints == 'basic':
                                                    print("estamos checando las latencias 03", resultado_latencia_total,
                                                          resultado_latencia)

                                                    # we are going to add the copy nodes
                                                if self.s_prints == 'basic' or self.s_prints == 'debug':
                                                    print(self.lista_nodos_copy)
                                                    print(
                                                        "we are going to map something so we need to add the copy nodes")
                                                latency_copy = self.obtention_latency_copy_node(elemento)
                                                for copy_node in self.lista_nodos_copy:
                                                    self.lista_mapping[copy_node] = [True, None, 'copy', 'copy', 0, 0,
                                                                                     0, 0, latency_copy, latency_copy,
                                                                                     0, 0, 0]

                                                contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                                                actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                                                info_actuator = self.info_actuator_generator(node_AG)
                                                bandera_need_of_time_slot = False
                                                self.lista_mapping[elemento] = [True, node_AG, elemento,
                                                                                self.AG.nodes[node_AG]['op'],
                                                                                self.dict_nodes[elemento]['ops'][
                                                                                    self.AG.nodes[node_AG]['op']][
                                                                                    'latency'],
                                                                                self.AG.nodes[node_AG]['par'],
                                                                                self.AG.nodes[node_AG]['par'],
                                                                                self.dict_nodes[elemento]['ops'][
                                                                                    self.AG.nodes[node_AG]['op']][
                                                                                    'clk'],
                                                                                resultado_latencia,
                                                                                resultado_latencia_total,
                                                                                info_sensor, info_actuator,
                                                                                actuator_sink]
                                                # todo change this
                                                # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                                                #                         self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                                                if self.s_prints == 'basic':
                                                    print("aqui aparece un buggazo", self.lista_mapping)
                                                if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):

                                                    # todo verify if this is necessary
                                                    if bandera_anexion_time:
                                                        self.update_lists_case_01(element_buffer, bandera_anexion_time)

                                                    else:

                                                        self.update_lists_case_02(element_buffer)
                                                    if self.s_prints == 'basic':
                                                        print("regreso de procesamiento de listas 99")
                                                    # we are going to add the special nodes
                                                    # we notice a small bug with the append, so the next few lines solves that
                                                    if special_buffer and special_nodes_01:
                                                        if self.s_prints == 'debug':
                                                            print("bug append special nodes")
                                                        # print(len(special_buffer))
                                                        dummy_01 = []
                                                        dummy_02 = [[] for r in
                                                                    range(0,
                                                                          len(special_buffer) + len(special_nodes_01))]
                                                        # print("test de algo special")
                                                        # print(len(element_buffer))
                                                        if self.s_prints == 'debug':
                                                            print(len(special_nodes_01) + len(special_buffer))
                                                        for t in range(0, len(special_buffer)):
                                                            # print(t)
                                                            dummy_02[t] = special_buffer[t]
                                                        for u in range(0, len(special_nodes_01)):
                                                            # print(u)
                                                            dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                                                        # print(dummy_02)
                                                        # time.sleep(5)
                                                        buffer_special_node = dummy_02
                                                    else:
                                                        if special_buffer:
                                                            if self.s_prints == 'debug':
                                                                print("if we dont have any new created especial nodes")
                                                            buffer_special_node = special_buffer
                                                        else:
                                                            if self.s_prints == 'debug':
                                                                print(
                                                                    "if we dont have any previous created special nodes")
                                                            buffer_special_node = special_nodes_01
                                                    if self.s_prints == 'debug':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 3")
                                                        print(list(buffer_special_node))
                                                    self.next_list_special_nodes.append(list(buffer_special_node))

                                                else:

                                                    # todo verify this part
                                                    if bandera_anexion_time:
                                                        self.update_lists_case_03(bandera_anexion_time, element_buffer)

                                                    else:
                                                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                                                            print("a mapping list is going to be store stage 2 step 4b")
                                                            print("the mapping list is")
                                                            print(self.lista_mapping)
                                                        self.next_list.append(list(self.lista_mapping))
                                                        # if verificacion_lista(self.lista_bug, list(self.lista_mapping)):
                                                        #     print("error 12 ")
                                                        #     time.sleep(5)
                                                        if self.s_prints == 'basic':
                                                            print("la lista hasta ahora es 08")
                                                            for lista_intermedia in self.next_list:
                                                                print(lista_intermedia)
                                                            # print(self.next_list)
                                                        self.time_slot_list_01.append(False)
                                                    # we are going to add the special nodes
                                                    # we notice a small bug with the append, so the next few lines solves that
                                                    if special_buffer and special_nodes_01:
                                                        if self.s_prints == 'debug':
                                                            print("bug append special nodes")
                                                        # print(len(special_buffer))
                                                        dummy_01 = []
                                                        dummy_02 = [[] for r in
                                                                    range(0,
                                                                          len(special_buffer) + len(special_nodes_01))]
                                                        if self.s_prints == 'debug':
                                                            print(len(special_nodes_01) + len(special_buffer))
                                                        for t in range(0, len(special_buffer)):
                                                            # print(t)
                                                            dummy_02[t] = special_buffer[t]
                                                        for u in range(0, len(special_nodes_01)):
                                                            # print(u)
                                                            dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                                                        # print(dummy_02)
                                                        # time.sleep(5)
                                                        buffer_special_node = dummy_02
                                                    else:
                                                        if special_buffer:
                                                            if self.s_prints == 'debug':
                                                                print("if we dont have any new created especial nodes")
                                                            buffer_special_node = special_buffer
                                                        else:
                                                            if self.s_prints == 'debug':
                                                                print(
                                                                    "if we dont have any previous created special nodes")
                                                            buffer_special_node = special_nodes_01
                                                    if self.s_prints == 'debug':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 4")
                                                        print(list(buffer_special_node))
                                                    self.next_list_special_nodes.append(list(buffer_special_node))




                            else:
                                f = datetime.now()
                                for elemento in available_nodes:
                                    if self.s_prints == 'testexh':
                                        print(elemento)
                                    d = datetime.now()
                                    element_buffer = elemento_buffer_copy.copy()
                                    self.lista_mapping = element_in_list_copy.copy()
                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                        b = datetime.now()
                                        now = b.strftime("%H:%M:%S.%f")
                                        c = b - d
                                        print(
                                            f"Copy of the list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                    # change made to have a list of operations in the resources not only one type of operation
                                    if self.s_prints == 'basic':
                                        print("something is not right")
                                    d = datetime.now()
                                    if self.AG_copia.nodes[node_AG]['op'] in self.DG_copia.nodes[elemento]['op']:
                                        # print("dsfsd")
                                        # if self.DG_copia.node[elemento]['op'] == self.AG_copia.node[node_AG]['op']:
                                        #######################################################################################
                                        #############this is a change made 20112019
                                        ###########################################################
                                        if self.s_prints == 'basic':
                                            print("EMPEZAREMOS CON LOS CAMBIOS 05")

                                            print(elemento)
                                            for bla in self.dict_nodes.items():
                                                print(bla)
                                            print(self.dict_nodes[elemento]['ops'][self.AG_copia.nodes[node_AG]['op']][
                                                      'param'])
                                        if self.debug_info == 'remove' or self.debug_info == 'total':
                                            b = datetime.now()
                                            now = b.strftime("%H:%M:%S.%f")
                                            c = b - d
                                            print(
                                                f"Verification of the type for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                        d = datetime.now()
                                        vector_validacion_parametros = self.verification_of_parameters(node_AG,
                                                                                                       elemento)
                                        if self.debug_info == 'remove' or self.debug_info == 'total':
                                            b = datetime.now()
                                            now = b.strftime("%H:%M:%S.%f")
                                            c = b - d
                                            print(
                                                f"Validation of parameters for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                        d = datetime.now()
                                        bandera_source_of_data, info_sensor = self.verification_of_source(node_AG,
                                                                                                          elemento)
                                        if self.debug_info == 'remove' or self.debug_info == 'total':
                                            b = datetime.now()
                                            now = b.strftime("%H:%M:%S.%f")
                                            c = b - d
                                            print(
                                                f"Retrieve of sensor info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                        debug_interno = False
                                        # if node_AG == 2 and elemento == 1:
                                        #     debug_interno = False
                                        if self.s_prints == 'basic' or debug_interno:
                                            print("test de algo bug 08")
                                            print(
                                                f"vector validacion de parametros {vector_validacion_parametros} bandera source {bandera_source_of_data}")
                                            print(self.lista_mapping)

                                        # we verify if the data dependency is correct
                                        # TODO increase the comparative, this is not the complete verification
                                        ### this variable is to check a bug where the list is append at the last element
                                        if all(vector_validacion_parametros) and bandera_source_of_data:
                                            dummy_bug_01 = False
                                            if self.s_prints == 'basic':
                                                print("parece que entroe aqui hay que checar")
                                            d = datetime.now()
                                            if node_AG in self.sources_AG:
                                                # print("dfsdf")
                                                # because there is no predecessor we can map the task
                                                if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                    print(
                                                        f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                                                    print(
                                                        f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                    print(
                                                        "------------------------------------------------------------")
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                    elemento,
                                                    node_AG)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                if self.s_prints == 'basic':
                                                    print("estamos checando las latencias", resultado_latencia_total,
                                                          resultado_latencia)
                                                d = datetime.now()
                                                # todo verification of this thing
                                                actuator_sink = self.only_actuator_sink(node_AG, elemento)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Validation of the actuator for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                info_actuator = self.info_actuator_generator(node_AG)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Retrieve of actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                                                bandera_need_of_time_slot = False
                                                self.lista_mapping[elemento] = [True, node_AG, elemento,
                                                                                self.AG.nodes[node_AG]['op'],
                                                                                self.dict_nodes[elemento]['ops'][
                                                                                    self.AG.nodes[node_AG]['op']][
                                                                                    'latency'],
                                                                                self.AG.nodes[node_AG]['par'],
                                                                                self.AG.nodes[node_AG]['par'],
                                                                                self.dict_nodes[elemento]['ops'][
                                                                                    self.AG.nodes[node_AG]['op']][
                                                                                    'clk'],
                                                                                resultado_latencia,
                                                                                resultado_latencia_total,
                                                                                info_sensor, info_actuator,
                                                                                actuator_sink]

                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                                                #                             self.AG.node[node_AG]['par'],self.AG.node[node_AG]['par'],self.AG.node[node_AG]['lat']]
                                                # TODO: this is a bug where we mixup the lists, in the sense that we though that it was a list
                                                # with several time slots but it wasn't so i add this verification, i think that we can
                                                # remove it because i fixed the error with the append
                                                d = datetime.now()
                                                if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):

                                                    # this is to keep control of the creation of time slots, it has to do with a
                                                    # problem of the append and all the same lines as the following take care of that
                                                    # problem
                                                    # todo there is a issue with the list the following lines could solve it i dont know
                                                    if bandera_anexion_time:
                                                        self.update_lists_case_01(element_buffer, bandera_anexion_time)

                                                    else:
                                                        self.update_lists_case_02(element_buffer)
                                                    if self.s_prints == 'basic':
                                                        print("regreso de procesamiento de listas 44")
                                                    # in here maybe we are not going to create any special node, but because the list of
                                                    # special nodes needs to have the same length as the next list, every time that we
                                                    # append the next list we need to append the special nodes list at least with an
                                                    # empty list
                                                    if self.s_prints == 'debug':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 1")
                                                        print(list(special_buffer))
                                                    self.next_list_special_nodes.append(list(special_buffer))
                                                else:

                                                    # todo verify if this part is necessary
                                                    if bandera_anexion_time:
                                                        self.update_lists_case_01(element_buffer, bandera_anexion_time)

                                                    else:
                                                        if self.s_prints == 'testexh':
                                                            print("a mapping list is going to be store stage 2 step 2")
                                                            print("the mapping list is")
                                                            print(self.lista_mapping)
                                                        self.next_list.append(self.lista_mapping.copy())
                                                        # if verificacion_lista(self.lista_bug, self.lista_mapping):
                                                        #     print("error 08 ")
                                                        #     time.sleep(5)

                                                        if self.s_prints == 'basic':
                                                            print("la lista hasta ahora es 04")
                                                            for lista_intermedia in self.next_list:
                                                                print(lista_intermedia)
                                                            # print(self.next_list)
                                                        self.time_slot_list_01.append(False)

                                                    if self.s_prints == 'basic':
                                                        print("regreso de procesamiento de listas 55")
                                                    if self.s_prints == 'testexh':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 2")
                                                        print(list(special_buffer))
                                                    self.next_list_special_nodes.append(list(special_buffer))

                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Update of the lists for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                                                if self.debug_info == 'memory':
                                                    print(
                                                        f"The memory usage of the next list is {asizeof(self.next_list)} bytes")


                                            else:
                                                # Because the task is not a source task we need to verify the data dependency
                                                # we obtain all the predecessor and we verify the data dependency
                                                if self.s_prints == 'basic':
                                                    print("We are going to check the data dependency of the task ",
                                                          node_AG)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                predecessors = self.AG.predecessors(node_AG)
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Retrieve of the predecessors for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                # We noticed a bug related to the number of time slots, this created an issue with the
                                                # module of graph creation, the following lines solves that problem
                                                if bandera_anexion_time:
                                                    instancia = len(element_buffer)
                                                else:
                                                    instancia = 0
                                                self.bandera_debug = False
                                                # if self.s_prints == 'basic' and self.s_pause == True and elemento == 2 and node_AG == 2:
                                                #     self.bandera_debug = True
                                                # else:
                                                #     self.bandera_debug = False
                                                if self.s_prints == 'testexh':
                                                    print("EL ERROR ES OSDOFNSDFNS")
                                                d = datetime.now()
                                                valid_place, special_nodes_01 = self.verification_of_dependence(
                                                    predecessors,
                                                    element_in_list,
                                                    element_buffer,
                                                    elemento,
                                                    node_AG,
                                                    instancia)

                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Verification of data dependence for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                if self.s_prints == 'basic':
                                                    print(
                                                        f"predecesores de la tarea {node_AG}, son {list(self.AG.predecessors(node_AG))} y el elemento es {elemento} y la bandera es {valid_place}")
                                                    print(f"y la lista hasta ahora es {element_buffer}")
                                                # if debug_interno:
                                                #     input("debug interno - enter continue")

                                                # after a succesful verification we map the task
                                                # if valid_place and all(vector_validacion_parametros) and not bandera_no_match_parameters:
                                                #####################################################################
                                                #############this is the one that is not working

                                                if valid_place:
                                                    # if not False in vector_dependency_02 :
                                                    if self.s_prints == 'debug':
                                                        print("Map")
                                                    elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                        print(
                                                            f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[elemento]['name']}")
                                                        print(
                                                            f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                        print(
                                                            "------------------------------------------------------------")

                                                    ############this is the new way to obtain the latency
                                                    d = datetime.now()
                                                    resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                        elemento, node_AG)

                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    if self.s_prints == 'basic':
                                                        print("estamos checando las latencias 03",
                                                              resultado_latencia_total,
                                                              resultado_latencia)

                                                        # we are going to add the copy nodes
                                                    if self.s_prints == 'basic' or self.s_prints == 'debug':
                                                        print(self.lista_nodos_copy)
                                                        print(
                                                            "we are going to map something so we need to add the copy nodes")

                                                    d = datetime.now()
                                                    latency_copy = self.obtention_latency_copy_node(elemento)

                                                    # d = datetime.now()
                                                    for copy_node in self.lista_nodos_copy:
                                                        self.lista_mapping[copy_node] = [True, None, 'copy', 'copy', 0,
                                                                                         0,
                                                                                         0, 0, latency_copy,
                                                                                         latency_copy, 0, 0,
                                                                                         0]
                                                    # if self.bandera_time_slots:
                                                    #     try:
                                                    #         for i in self.lista_nodos_copy_time_slot:
                                                    #             element_buffer[self.time_slot_copy_nodes][i] = [True, None, 'copy', 'copy', 0, 0,
                                                    #                                      0, 0, latency_copy, latency_copy, 0, 0, 0]
                                                    #     except:
                                                    #         pass
                                                    contador_mapeo_antes_time_slot = contador_mapeo_antes_time_slot + 1
                                                    actuator_sink = self.generation_copy_nodes(node_AG, elemento)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    # if node_AG in self.sinks_AG:
                                                    #     self.generation_copy_nodes(node_AG,elemento)
                                                    # self.generation_copy_nodes(node_AG,elemento)

                                                    d = datetime.now()
                                                    info_actuator = self.info_actuator_generator(node_AG)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    bandera_need_of_time_slot = False
                                                    self.lista_mapping[elemento] = [True, node_AG, elemento,
                                                                                    self.AG.nodes[node_AG]['op'],
                                                                                    self.dict_nodes[elemento]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'latency'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.dict_nodes[elemento]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'clk'],
                                                                                    resultado_latencia,
                                                                                    resultado_latencia_total,
                                                                                    info_sensor,
                                                                                    info_actuator, actuator_sink]

                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    # todo change this
                                                    # self.lista_mapping[elemento] = [True, node_AG, elemento,self.AG.node[node_AG]['op'],self.DG.node[elemento]['lat'],\
                                                    #                         self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                                                    if self.s_prints == 'basic':
                                                        print("aqui aparece un buggazo", self.lista_mapping)
                                                    d = datetime.now()
                                                    if dummy_bug_01:  # any(isinstance(el, list) for el in element_buffer[0]):

                                                        # todo verify if this is necessary
                                                        if bandera_anexion_time:
                                                            self.update_lists_case_01(element_buffer,
                                                                                      bandera_anexion_time)

                                                        else:
                                                            self.update_lists_case_02(element_buffer)
                                                        if self.s_prints == 'basic':
                                                            print("regreso de procesamiento de listas 11")
                                                        # we are going to add the special nodes
                                                        # we notice a small bug with the append, so the next few lines solves that
                                                        if special_buffer and special_nodes_01:
                                                            if self.s_prints == 'debug':
                                                                print("bug append special nodes")
                                                            # print(len(special_buffer))
                                                            dummy_01 = []
                                                            dummy_02 = [[] for r in
                                                                        range(0, len(special_buffer) + len(
                                                                            special_nodes_01))]
                                                            # print("test de algo special")
                                                            # print(len(element_buffer))
                                                            if self.s_prints == 'debug':
                                                                print(len(special_nodes_01) + len(special_buffer))
                                                            for t in range(0, len(special_buffer)):
                                                                # print(t)
                                                                dummy_02[t] = special_buffer[t]
                                                            for u in range(0, len(special_nodes_01)):
                                                                # print(u)
                                                                dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                                                            # print(dummy_02)
                                                            # time.sleep(5)
                                                            buffer_special_node = dummy_02
                                                        else:
                                                            if special_buffer:
                                                                if self.s_prints == 'debug':
                                                                    print(
                                                                        "if we dont have any new created especial nodes")
                                                                buffer_special_node = special_buffer
                                                            else:
                                                                if self.s_prints == 'debug':
                                                                    print(
                                                                        "if we dont have any previous created special nodes")
                                                                buffer_special_node = special_nodes_01
                                                        if self.s_prints == 'debug':
                                                            print(
                                                                "a special nodes list is going to be store stage 2 step 3")
                                                            print(list(buffer_special_node))
                                                        self.next_list_special_nodes.append(list(buffer_special_node))

                                                    else:

                                                        # todo verify this part
                                                        if bandera_anexion_time:
                                                            self.update_lists_case_03(bandera_anexion_time,
                                                                                      element_buffer)

                                                        else:
                                                            if self.s_prints == 'testexh' or self.s_prints == 'basic':
                                                                print(
                                                                    "a mapping list is going to be store stage 2 step 4b")
                                                                print("the mapping list is")
                                                                print(self.lista_mapping)
                                                            self.next_list.append(list(self.lista_mapping))
                                                            # if verificacion_lista(self.lista_bug, list(self.lista_mapping)):
                                                            #     print("error 12 ")
                                                            #     time.sleep(5)
                                                            if self.s_prints == 'basic':
                                                                print("la lista hasta ahora es 08")
                                                                for lista_intermedia in self.next_list:
                                                                    print(lista_intermedia)
                                                                # print(self.next_list)
                                                            self.time_slot_list_01.append(False)
                                                        # we are going to add the special nodes
                                                        # we notice a small bug with the append, so the next few lines solves that
                                                        if special_buffer and special_nodes_01:
                                                            if self.s_prints == 'debug':
                                                                print("bug append special nodes")
                                                            # print(len(special_buffer))
                                                            dummy_01 = []
                                                            dummy_02 = [[] for r in
                                                                        range(0, len(special_buffer) + len(
                                                                            special_nodes_01))]
                                                            if self.s_prints == 'debug':
                                                                print(len(special_nodes_01) + len(special_buffer))
                                                            for t in range(0, len(special_buffer)):
                                                                # print(t)
                                                                dummy_02[t] = special_buffer[t]
                                                            for u in range(0, len(special_nodes_01)):
                                                                # print(u)
                                                                dummy_02[u + len(special_buffer)] = special_nodes_01[u]
                                                            # print(dummy_02)
                                                            # time.sleep(5)
                                                            buffer_special_node = dummy_02
                                                        else:
                                                            if special_buffer:
                                                                if self.s_prints == 'debug':
                                                                    print(
                                                                        "if we dont have any new created especial nodes")
                                                                buffer_special_node = special_buffer
                                                            else:
                                                                if self.s_prints == 'debug':
                                                                    print(
                                                                        "if we dont have any previous created special nodes")
                                                                buffer_special_node = special_nodes_01
                                                        if self.s_prints == 'debug':
                                                            print(
                                                                "a special nodes list is going to be store stage 2 step 4")
                                                            print(list(buffer_special_node))
                                                        self.next_list_special_nodes.append(list(buffer_special_node))
                                                    if self.debug_info == 'memory':
                                                        print(
                                                            f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                    b = datetime.now()
                                    now = b.strftime("%H:%M:%S.%f")
                                    c = b - f
                                    print(
                                        f"Finish of the first stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                            bandera_no_mapping = False
                            f = datetime.now()

                            # in here we will add the time slot
                            if bandera_time_slots_creation or bandera_need_of_time_slot:
                                # if True:
                                # Now we start the addition of a new time slot
                                if self.s_prints == 'testexh' or self.s_prints == 'basic' or self.s_prints == 'iter':
                                    # print("------------------------------------------------------------")
                                    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
                                    print(f"Addition of a time slot {contador_time_slots + 1}")
                                    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
                                if self.s_pause:
                                    input("Press Enter to continue...")

                                d = datetime.now()
                                element_buffer = copy.deepcopy(self.master_elemento_buffer)
                                self.lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n
                                                      in
                                                      range(0, len(self.DG.nodes))]
                                # The purpose is to map the task in any feasible resource in the new time slot, this will required
                                # the addition of special nodes and in general the verification of data dependency
                                # For each resource in the hardware graph
                                counter_error = 0
                                bandera_no_mapping = True
                                copia_elemento_buffer = element_buffer.copy()
                                if self.s_prints == 'testexh':
                                    print("ELEMENTO COPIA BUG 0000")
                                    print(copia_elemento_buffer)

                                name_task = self.dict_nodes_a[node_AG]['name']

                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                    b = datetime.now()
                                    now = b.strftime("%H:%M:%S.%f")
                                    c = b - d
                                    print(
                                        f"Copy stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                if name_task in self.lista_tareas_constrains:

                                    resource, name_resource = self.info_resource(name_task)

                                    vector_validacion_parametros = self.verification_of_parameters(node_AG, resource)
                                    bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource)

                                    # we verify if the data dependency is correct
                                    # TODO increase the comparative, this is not the complete verification
                                    # The task is a source task so we dont need data dependency verification
                                    if node_AG in self.sources_AG:
                                        if all(vector_validacion_parametros) and bandera_source_of_data:
                                            # because there is no predecessor we can map the task and also we dont need any special node
                                            if self.s_prints == 'debug':
                                                print("Map")
                                            elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                print(
                                                    f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                                                print(
                                                    f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                print("------------------------------------------------------------")

                                            ##############################
                                            # todo check if this is necessary
                                            predecessors = list(self.AG.predecessors(node_AG))
                                            if self.s_prints == 'testexh' or self.s_prints == 'basic':
                                                print(" 01 - set of predecessors of task ", node_AG, " is ",
                                                      predecessors)
                                                print("modulo 5 we try to map ", node_AG, " on the resource ", resource)
                                            lista_nodos_copy_01 = []
                                            lista_nodos_copy_02 = []
                                            for predecessor in predecessors:
                                                # Now, the issue in here is that we need to check de data dependency in the
                                                # previous time slots
                                                contador_time_slots = 0
                                                if self.s_prints == 'basic': print(element_buffer)
                                                # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                                                # un time slot entonces iteraremos sobre ese mismo time slot
                                                if first_time_special:
                                                    for u in element_buffer:
                                                        if self.s_prints == 'basic':
                                                            print("stest", u)
                                                        if u[0]:
                                                            if predecessor == u[1]:
                                                                node_place = u[2]
                                                                break
                                                else:
                                                    # como no es la primera vez tenemos que iterar sobre time slots
                                                    for u in element_buffer:
                                                        for elemento_en_time_slot in u:
                                                            if elemento_en_time_slot[0]:
                                                                if predecessor == elemento_en_time_slot[1]:
                                                                    node_place = elemento_en_time_slot[2]
                                                                    break
                                                        contador_time_slots += 1
                                                node_place_buffer = node_place
                                                if self.s_prints == 'basic':
                                                    print("bug 30 bueno pues el lugar es ", node_place,
                                                          " y el time slot es ",
                                                          contador_time_slots)
                                                    if first_time_special:
                                                        print(element_buffer[node_place])
                                                    else:
                                                        print(element_buffer[contador_time_slots][node_place])

                                                if self.s_prints == 'debug' or self.s_prints == 'basic':
                                                    print("the node place is ", node_place, "on time slot",
                                                          contador_time_slots)
                                                # we check if the if the predecessor is mapped on a sink or it can reach a sink
                                                # print("bug 06")

                                            resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                resource,
                                                node_AG)

                                            if self.s_prints == 'basic':
                                                print("estamos checando las latencias 02", resultado_latencia_total,
                                                      resultado_latencia)

                                            actuator_sink = self.generation_copy_nodes(node_AG, resource)
                                            info_actuator = self.info_actuator_generator(node_AG)

                                            bandera_no_mapping = False
                                            self.lista_mapping[resource] = [True, node_AG, resource,
                                                                            self.AG.nodes[node_AG]['op'],
                                                                            self.dict_nodes[resource]['ops'][
                                                                                self.AG.nodes[node_AG]['op']][
                                                                                'latency'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.dict_nodes[resource]['ops'][
                                                                                self.AG.nodes[node_AG]['op']]['clk'],
                                                                            resultado_latencia,
                                                                            resultado_latencia_total,
                                                                            info_sensor,
                                                                            info_actuator, actuator_sink]

                                            self.update_lists_case_01(element_buffer, bandera_anexion_time)
                                            if self.s_prints == 'basic':
                                                print("regreso de procesamiento de listas 33")
                                            if self.s_prints == 'debug':
                                                print("a special nodes list is going to be store stage 2 step 5")
                                                print(list(special_buffer))
                                            self.next_list_special_nodes.append(list(special_buffer))

                                    else:
                                        # because the task is not a source task we verify the data dependency
                                        # this part can use the function of verification, but i havent done it yet
                                        predecessors = list(self.AG.predecessors(node_AG))
                                        if self.s_prints == 'testexh' or self.s_prints == 'basic':
                                            print("02 - set of predecessors of task ", node_AG, " is ", predecessors)
                                            print("modulo 4 we try to map ", node_AG, " on the resource ", resource)
                                        lista_nodos_copy_01 = []
                                        lista_nodos_copy_02 = []
                                        vector_dependency_02 = []
                                        for predecessor in predecessors:
                                            # Now, the issue in here is that we need to check de data dependency in the
                                            # previous time slots
                                            contador_time_slots = 0
                                            if self.s_prints == 'basic': print(element_buffer)
                                            # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                                            # un time slot entonces iteraremos sobre ese mismo time slot
                                            if first_time_special or not bandera_anexion_time:
                                                for u in element_buffer:
                                                    if self.s_prints == 'debug':
                                                        if self.s_prints == 'basic':
                                                            print("stest", u)
                                                    if u[0]:
                                                        if predecessor == u[1]:
                                                            node_place = u[2]
                                                            break
                                            else:
                                                # como no es la primera vez tenemos que iterar sobre time slots
                                                if self.s_prints == 'basic':
                                                    print("buggazo")
                                                    print(element_buffer)
                                                for u in element_buffer:
                                                    for elemento_en_time_slot in u:
                                                        if elemento_en_time_slot[0]:
                                                            if predecessor == elemento_en_time_slot[1]:
                                                                node_place = elemento_en_time_slot[2]
                                                                break
                                                    contador_time_slots += 1
                                            node_place_buffer = node_place
                                            if self.s_prints == 'basic':
                                                print("bug 20 bueno pues el lugar es ", node_place,
                                                      " y el time slot es ",
                                                      contador_time_slots)
                                                if first_time_special or not bandera_anexion_time:
                                                    print(element_buffer[node_place])
                                                else:
                                                    print(element_buffer[contador_time_slots - 1][node_place])

                                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                                print("the node place is ", node_place, "on time slot",
                                                      contador_time_slots)
                                                print(resource, self.sources_DG)
                                            # we check if the if the predecessor is mapped on a sink or it can reach a sink
                                            # print("bug 06")
                                            ## change 12062020 self.list_sinks_connected_to_rc for self.sinks_DG
                                            if node_place in self.list_sinks_connected_to_rc:
                                                nodo_sink = node_place
                                            else:

                                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                                done = True
                                                counter_internal = 0
                                                # copy_list_sinks_connected_to_rc.remove(nodo_sink)
                                                while done:
                                                    if copy_list_sinks_connected_to_rc:
                                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                                      copy_list_sinks_connected_to_rc,
                                                                                                      node_place)
                                                    else:
                                                        counter_internal = counter_internal + 1
                                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                                      copy_list_sinks_connected_to_rc,
                                                                                                      node_place)
                                                    # print(sink_nodo_sink_task,resource)
                                                    if element_buffer[contador_time_slots - 1][sink_nodo_sink_task][0]:
                                                        copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                                        if counter_internal == 5:
                                                            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copia,
                                                                                                          copy_list_sinks_connected_to_rc,
                                                                                                          node_place)
                                                            done = False
                                                            break

                                                    else:
                                                        done = False
                                                        break
                                                nodo_sink = sink_nodo_sink_task

                                                # nodo_sink = sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)
                                            # print("bug 05")
                                            if resource in self.sources_DG:
                                                nodo_source = resource
                                            else:
                                                nodo_source = source_node_from_any_node(self.DG, self.sources_DG,
                                                                                        resource)
                                            for element in self.lista_mapping:
                                                if predecessor == element[1]:
                                                    node_place = element[2]
                                            if self.s_prints == 'debug':
                                                print(" we find the place  ", node_place, resource)
                                            paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                                            # vector_dependency_02 = []
                                            # print("the paths ", paths)
                                            for path_b in paths:
                                                path = list(path_b)
                                                # path.remove(node_place)
                                                path_buffer = list(path)
                                                path_buffer.remove(node_place)
                                                path_buffer.remove(resource)
                                                lista_nodos_copy_01 = lista_nodos_copy_01 + path_buffer

                                                vector_dependency_01 = []
                                                for node in path:
                                                    vector_dependency_01 = vector_dependency_01 + [
                                                        self.lista_mapping[node][0]]
                                                if True in vector_dependency_01:
                                                    vector_dependency_02 = vector_dependency_02 + [False]

                                            ####################se cambiara de indent
                                        if not False in vector_dependency_02 and all(
                                                vector_validacion_parametros) and bandera_source_of_data:
                                            if self.s_prints == 'debug':
                                                print("Map")
                                            elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                print(
                                                    f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                                                print(
                                                    f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                print("------------------------------------------------------------")

                                            resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                resource,
                                                node_AG)

                                            if self.s_prints == 'basic':
                                                print("estamos checando las latencias 01", resultado_latencia_total,
                                                      resultado_latencia)
                                                print(self.lista_mapping)

                                            # we are going to add the copy nodes
                                            if self.s_prints == 'basic' or self.s_prints == 'testexh':
                                                # print(self.lista_nodos_copy)
                                                print(
                                                    "we are going to map something so we need to add the copy nodes stage 2")

                                                print(node_place_buffer, nodo_sink, nodo_source, resource)
                                            # empecemos con los nodos en el time slot anterior

                                            element_buffer, actuator_sink = self.generation_copy_nodes_time_slot(
                                                node_AG,
                                                resource,
                                                first_time_special,
                                                bandera_anexion_time,
                                                nodo_sink,
                                                node_place_buffer,
                                                element_buffer,
                                                nodo_source,
                                                node_place,
                                                contador_time_slots)

                                            info_actuator = self.info_actuator_generator(node_AG)
                                            bandera_no_mapping = False
                                            self.lista_mapping[resource] = [True, node_AG, resource,
                                                                            self.AG.nodes[node_AG]['op'],
                                                                            self.dict_nodes[resource]['ops'][
                                                                                self.AG.nodes[node_AG]['op']][
                                                                                'latency'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.AG.nodes[node_AG]['par'],
                                                                            self.dict_nodes[resource]['ops'][
                                                                                self.AG.nodes[node_AG]['op']]['clk'],
                                                                            resultado_latencia,
                                                                            resultado_latencia_total,
                                                                            info_sensor, info_actuator, actuator_sink]
                                            # todo we need to change this
                                            # self.lista_mapping[resource] = [True, node_AG, resource,self.AG.node[node_AG]['op'],self.DG.node[resource]['lat'],\
                                            #                     self.AG.node[node_AG]['par'][0],self.AG.node[node_AG]['par'][1],self.AG.node[node_AG]['lat']]
                                            dummy_01 = self.update_lists_case_04(element_buffer, bandera_anexion_time)
                                            #
                                            # time.sleep(5)
                                            item_to_append = [True, nodo_sink, nodo_source, len(dummy_01) - 1,
                                                              self.contador_recomputacion]

                                            # the following lines are for the append of the special nodes list
                                            if special_buffer:
                                                # print(len(special_buffer))
                                                dummy_01 = []
                                                dummy_02 = [[] for r in range(0, len(special_buffer) + 1)]
                                                # print("test de algo special")
                                                # print(len(element_buffer))
                                                for t in range(0, len(special_buffer)):
                                                    # print(t)
                                                    dummy_02[t] = special_buffer[t]
                                                dummy_02[len(special_buffer)] = item_to_append
                                                buffer_special_node = dummy_02
                                            else:
                                                buffer_special_node = [item_to_append]
                                            if self.s_prints == 'debug':
                                                print("a special nodes list is going to be store stage 2 step 4")
                                                print(list(buffer_special_node))
                                            self.next_list_special_nodes.append(list(buffer_special_node))
                                            self.contador_recomputacion = self.contador_recomputacion + 1

                                    ###############




                                else:

                                    for resource in (self.DG_copia.nodes):
                                        element_buffer = copy.deepcopy(self.master_elemento_buffer)
                                        # element_buffer = copia_elemento_buffer.copy()
                                        if self.s_prints == 'testexh':
                                            print("por cada resource", resource, counter_error,
                                                  len(self.DG_copia.nodes),
                                                  node_AG, self.AG_copia.nodes[node_AG]['name'])
                                            print("el elemento buffer")
                                            print(element_buffer)
                                            print("elemento copia")
                                            print(copia_elemento_buffer)

                                        # print(resource)

                                        # verify if the types are compatible
                                        d = datetime.now()
                                        if self.AG_copia.nodes[node_AG]['op'] in self.DG_copia.nodes[resource]['op']:
                                            # if self.DG_copia.node[resource]['op'] == self.AG_copia.node[node_AG]['op']:
                                            #######################################################################################
                                            #############this is a change made 20112019
                                            ###########################################################
                                            if self.s_prints == 'basic':
                                                print("EMPEZAREMOS CON LOS CAMBIOS")
                                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                                b = datetime.now()
                                                now = b.strftime("%H:%M:%S.%f")
                                                c = b - d
                                                print(
                                                    f"Verification of type for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                            d = datetime.now()

                                            vector_validacion_parametros = self.verification_of_parameters(node_AG,
                                                                                                           resource)
                                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                                b = datetime.now()
                                                now = b.strftime("%H:%M:%S.%f")
                                                c = b - d
                                                print(
                                                    f"Validation of parameters for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                            d = datetime.now()
                                            bandera_source_of_data, info_sensor = self.verification_of_source(node_AG,
                                                                                                              resource)
                                            if self.s_prints == 'basic':
                                                print("regreso de las funciones de validacion",
                                                      vector_validacion_parametros,
                                                      bandera_source_of_data, info_sensor)
                                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                                b = datetime.now()
                                                now = b.strftime("%H:%M:%S.%f")
                                                c = b - d
                                                print(
                                                    f"Retrieve sensor info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                            # we verify if the data dependency is correct
                                            # TODO increase the comparative, this is not the complete verification
                                            # The task is a source task so we dont need data dependency verification
                                            d = datetime.now()
                                            if node_AG in self.sources_AG:  # and all(vector_validacion_parametros) and bandera_source_of_data:
                                                # because there is no predecessor we can map the task and also we dont need any special node

                                                if all(vector_validacion_parametros) and bandera_source_of_data:
                                                    if self.s_prints == 'debug':
                                                        print("Map")
                                                    elif self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
                                                        print(
                                                            f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                                                        print(
                                                            f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                        print(
                                                            "------------------------------------------------------------")
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Verification if the task is source for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                        resource, node_AG)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    if self.s_prints == 'basic':
                                                        print("estamos checando las latencias 02",
                                                              resultado_latencia_total,
                                                              resultado_latencia)
                                                    d = datetime.now()
                                                    actuator_sink = self.generation_copy_nodes(node_AG, resource)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    info_actuator = self.info_actuator_generator(node_AG)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    bandera_no_mapping = False
                                                    self.lista_mapping[resource] = [True, node_AG, resource,
                                                                                    self.AG.nodes[node_AG]['op'],
                                                                                    self.dict_nodes[resource]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'latency'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.dict_nodes[resource]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'clk'],
                                                                                    resultado_latencia,
                                                                                    resultado_latencia_total,
                                                                                    info_sensor,
                                                                                    info_actuator, actuator_sink]
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    self.update_lists_case_01(element_buffer, bandera_anexion_time)
                                                    if self.s_prints == 'basic':
                                                        print("regreso de procesamiento de listas 00")
                                                        for n_lista in self.next_list:
                                                            print(n_lista)
                                                        print("termino de")
                                                    if self.s_prints == 'debug':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 5")
                                                        print(list(special_buffer))
                                                    self.next_list_special_nodes.append(list(special_buffer))
                                                    if self.debug_info == 'memory':
                                                        print(
                                                            f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                            else:
                                                # because the task is not a source task we verify the data dependency
                                                # this part can use the function of verification, but i havent done it yet

                                                d = datetime.now()
                                                predecessors = list(self.AG.predecessors(node_AG))
                                                if self.s_prints == 'testexh' or self.s_prints == 'basic':
                                                    print("03 - set of predecessors of task ", node_AG, " is ",
                                                          predecessors)
                                                    print("modulo 2 we try to map ", node_AG, " on the resource ",
                                                          resource)
                                                    print(element_buffer)
                                                lista_nodos_copy_01 = []
                                                lista_nodos_copy_02 = []
                                                vector_dependency_02 = []
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Predecessors for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                d = datetime.now()
                                                for predecessor in predecessors:
                                                    # Now, the issue in here is that we need to check de data dependency in the
                                                    # previous time slots
                                                    contador_time_slots = 0
                                                    node_place = None
                                                    if self.s_prints == 'testexh':
                                                        print(
                                                            f"el elemento buffer se imprimira las bandera primera vez {first_time_special} y anexion tiempo {bandera_anexion_time}")
                                                        print(element_buffer)
                                                        # for uno in element_buffer:
                                                        #     print(uno)
                                                    # tenemos que checar si es primera vez, porque si es primera vez solamente tenemos
                                                    # un time slot entonces iteraremos sobre ese mismo time slot
                                                    if first_time_special or not bandera_anexion_time:
                                                        if self.s_prints == 'basic':
                                                            print("estamos en el if de algo rro bug 08")
                                                        for u in element_buffer:
                                                            if self.s_prints == 'debug':
                                                                print("stest", u)
                                                            if u[0]:
                                                                if predecessor == u[1]:
                                                                    node_place = u[2]
                                                                    break
                                                    else:
                                                        # como no es la primera vez tenemos que iterar sobre time slots
                                                        if self.s_prints == 'basic':
                                                            print(f"el predeceso que estamos buscando es {predecessor}")
                                                            print(element_buffer)

                                                        for u in element_buffer:
                                                            for elemento_en_time_slot in u:

                                                                if elemento_en_time_slot[0]:
                                                                    if predecessor == elemento_en_time_slot[1]:
                                                                        node_place = elemento_en_time_slot[2]
                                                                        break
                                                            contador_time_slots += 1

                                                    ######esta parte del codigo es un quick fix para el problema de que no se encuentra el predecesor
                                                    ######basicamente el detalle son las banderas pero mejor se anexa la siguiente parte, donde buscamos
                                                    ######el predecesor
                                                    contador_time_slots = 0
                                                    bandera_salida_test = False
                                                    if node_place == None:
                                                        for u in element_buffer:
                                                            contador_time_slots += 1
                                                            for elemento_en_time_slot in u:
                                                                if elemento_en_time_slot[0]:
                                                                    if predecessor == elemento_en_time_slot[1]:
                                                                        node_place = elemento_en_time_slot[2]
                                                                        bandera_salida_test = True
                                                                        break

                                                    node_place_buffer = node_place
                                                    if self.s_prints == 'basic':
                                                        print("bug 10 bueno pues el lugar es ", node_place,
                                                              " y el time slot es ", contador_time_slots)
                                                        try:
                                                            if first_time_special or not bandera_anexion_time:
                                                                print(element_buffer[node_place])
                                                            else:
                                                                print(
                                                                    element_buffer[contador_time_slots - 1][node_place])
                                                        except:
                                                            pass

                                                    if self.s_prints == 'debug' or self.s_prints == 'basic':
                                                        print("the node place is ", node_place, "on time slot",
                                                              contador_time_slots)
                                                        print(resource, self.sources_DG)
                                                    # we check if the if the predecessor is mapped on a sink or it can reach a sink
                                                    # print("bug 06")

                                                    try:
                                                        # change 12062020 self.list_sinks_connected_to_rc for self.sinks_DG
                                                        if node_place in self.list_sinks_connected_to_rc:
                                                            nodo_sink = node_place
                                                        else:
                                                            ####################
                                                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                                            done = True
                                                            counter_internal = 0
                                                            while done:
                                                                if copy_list_sinks_connected_to_rc:
                                                                    sink_nodo_sink_task = sink_node_from_any_node(
                                                                        self.DG_copia,
                                                                        copy_list_sinks_connected_to_rc,
                                                                        node_place)
                                                                else:
                                                                    counter_internal = counter_internal + 1
                                                                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                                                    sink_nodo_sink_task = sink_node_from_any_node(
                                                                        self.DG_copia,
                                                                        copy_list_sinks_connected_to_rc,
                                                                        node_place)

                                                                if self.lista_mapping[sink_nodo_sink_task][0]:
                                                                    copy_list_sinks_connected_to_rc.remove(
                                                                        sink_nodo_sink_task)
                                                                    if counter_internal == 5:
                                                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc
                                                                        sink_nodo_sink_task = sink_node_from_any_node(
                                                                            self.DG_copia,
                                                                            copy_list_sinks_connected_to_rc,
                                                                            node_place)
                                                                        done = False
                                                                        break

                                                                else:
                                                                    done = False
                                                                    break

                                                            #################"""
                                                            # nodo_sink = sink_node_from_any_node(self.DG_original,self.list_sinks_connected_to_rc,node_place)

                                                            nodo_sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG_original,self.list_sinks_connected_to_rc,node_place)
                                                        # print("bug 05")
                                                        if resource in self.sources_DG:
                                                            nodo_source = resource
                                                        else:
                                                            nodo_source = source_node_from_any_node(self.DG,
                                                                                                    self.sources_DG,
                                                                                                    resource)
                                                        for element in self.lista_mapping:
                                                            if predecessor == element[1]:
                                                                node_place = element[2]
                                                        if self.s_prints == 'debug':
                                                            print(" we find the place  ", node_place, resource)
                                                        paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                                                        # vector_dependency_02 = []
                                                        # print("the paths ", paths)
                                                        for path_b in paths:
                                                            path = list(path_b)
                                                            # path.remove(node_place)
                                                            path_buffer = list(path)
                                                            path_buffer.remove(node_place)
                                                            path_buffer.remove(resource)
                                                            lista_nodos_copy_01 = lista_nodos_copy_01 + path_buffer

                                                            vector_dependency_01 = []
                                                            for node in path:
                                                                vector_dependency_01 = vector_dependency_01 + [
                                                                    self.lista_mapping[node][0]]
                                                            if True in vector_dependency_01:
                                                                vector_dependency_02 = vector_dependency_02 + [False]
                                                    except:
                                                        vector_dependency_02 = vector_dependency_02 + [False]

                                                ##################################esta parte se cambiara de indent a uno menos
                                                # ####ahora aparecio un error de que vectordependecy no se encuentra pero es porque la tarea es source
                                                #
                                                # if node_AG in self.sources_AG:
                                                #     if self.s_prints == 'basic':
                                                #         print("la tarea es un source")
                                                #     vector_dependency_02 = [True]
                                                if self.debug_info == 'remove' or self.debug_info == 'total':
                                                    b = datetime.now()
                                                    now = b.strftime("%H:%M:%S.%f")
                                                    c = b - d
                                                    print(
                                                        f"Validation of parameters and data dependence for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                if not False in vector_dependency_02 and all(
                                                        vector_validacion_parametros) and bandera_source_of_data:
                                                    if self.s_prints == 'debug':
                                                        print("Map")
                                                    elif self.s_prints == 'basic' or self.s_prints == 'testexh' or self.s_prints == 'iter':
                                                        print(
                                                            f"the task {self.dict_nodes_a[node_AG]['name']} is going to be mapped to the resource {self.dict_nodes[resource]['name']}")
                                                        print(
                                                            f"we add this mapping to the next list, which has a length of {len(self.next_list)}")
                                                        print(
                                                            "------------------------------------------------------------")
                                                    d = datetime.now()
                                                    resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                                        resource, node_AG)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Latency information for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    if self.s_prints == 'basic':
                                                        print("estamos checando las latencias 01",
                                                              resultado_latencia_total,
                                                              resultado_latencia)
                                                        print(self.lista_mapping)

                                                    # we are going to add the copy nodes
                                                    if self.s_prints == 'basic' or self.s_prints == 'testexh':
                                                        # print(self.lista_nodos_copy)
                                                        print(
                                                            "we are going to map something so we need to add the copy nodes stage 3")

                                                        print(node_place_buffer, nodo_sink, nodo_source, resource)
                                                    # empecemos con los nodos en el time slot anterior
                                                    d = datetime.now()
                                                    element_buffer, actuator_sink = self.generation_copy_nodes_time_slot(
                                                        node_AG, resource, first_time_special, bandera_anexion_time,
                                                        nodo_sink,
                                                        node_place_buffer, element_buffer, nodo_source, node_place,
                                                        contador_time_slots)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Generation of copy nodes for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    info_actuator = self.info_actuator_generator(node_AG)
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Retrieve actuator info for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    bandera_no_mapping = False
                                                    self.lista_mapping[resource] = [True, node_AG, resource,
                                                                                    self.AG.nodes[node_AG]['op'],
                                                                                    self.dict_nodes[resource]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'latency'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.AG.nodes[node_AG]['par'],
                                                                                    self.dict_nodes[resource]['ops'][
                                                                                        self.AG.nodes[node_AG]['op']][
                                                                                        'clk'],
                                                                                    resultado_latencia,
                                                                                    resultado_latencia_total,
                                                                                    info_sensor,
                                                                                    info_actuator, actuator_sink]
                                                    # todo we need to change this
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Mapping for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                                    d = datetime.now()
                                                    dummy_01 = self.update_lists_case_04(element_buffer,
                                                                                         bandera_anexion_time)
                                                    item_to_append = [True, nodo_sink, nodo_source, len(dummy_01) - 1,
                                                                      self.contador_recomputacion]
                                                    # if node_AG == 1 and resource == 2:
                                                    #     print(self.lista_mapping)
                                                    #     print(element_buffer)
                                                    #     input("input    ddd")

                                                    # the following lines are for the append of the special nodes list
                                                    if special_buffer:
                                                        # print(len(special_buffer))
                                                        dummy_01 = []
                                                        dummy_02 = [[] for r in range(0, len(special_buffer) + 1)]
                                                        # print("test de algo special")
                                                        # print(len(element_buffer))
                                                        for t in range(0, len(special_buffer)):
                                                            # print(t)
                                                            dummy_02[t] = special_buffer[t]
                                                        dummy_02[len(special_buffer)] = item_to_append
                                                        buffer_special_node = dummy_02
                                                    else:
                                                        buffer_special_node = [item_to_append]
                                                    if self.s_prints == 'testexh':
                                                        print(
                                                            "a special nodes list is going to be store stage 2 step 4")
                                                        print(list(buffer_special_node))
                                                        # print(element_buffer)
                                                    self.next_list_special_nodes.append(list(buffer_special_node))
                                                    self.contador_recomputacion = self.contador_recomputacion + 1
                                                    if self.debug_info == 'memory':
                                                        print(
                                                            f"The memory usage of the next list is {asizeof(self.next_list)} bytes")
                                                    if self.debug_info == 'remove' or self.debug_info == 'total':
                                                        b = datetime.now()
                                                        now = b.strftime("%H:%M:%S.%f")
                                                        c = b - d
                                                        print(
                                                            f"Update of list for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                                        #############################################################################################################################
                                        ###we reset the mapping list

                                        if counter_error >= len(self.DG_copia.nodes):
                                            pass
                                            # raise Exception(
                                            #     f"The mapping cycle, please verify your input files, the exception ocurred in the second stage")
                                        counter_error = counter_error + 1
                                        if self.s_prints == 'testexh':
                                            print("ESTAMOS BUSCANDO SOLUCIONAR EL BUG")
                                            print(element_buffer)
                                            print(" ")
                                            print(self.master_elemento_buffer)
                                        self.lista_mapping = [
                                            [False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for n
                                            in range(0, len(self.DG.nodes))]

                            if self.debug_info == 'remove' or self.debug_info == 'total':
                                b = datetime.now()
                                now = b.strftime("%H:%M:%S.%f")
                                c = b - f
                                print(
                                    f"Finish of the second stage for task  {node_AG}, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

                            first_time_special = False
                            if bandera_no_mapping:
                                raise Exception(
                                    f"The mapping cycle, please verify your input files, the exception ocurred in the second stage")
                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we update the lists checando si se hacen los cambios")
                                print("el contenido de la lista next es")
                                for n_lista in self.next_list:
                                    print(n_lista)
                                    # input("Enter to continue...")
                                print("se termino de imprimir la lista")
                                # input("Enter to continue...")

                            if self.s_pause:
                                input("Press Enter to continue...")




                            next_list_total = next_list_total + self.next_list
                            special_nodes_total = special_nodes_total + self.next_list_special_nodes
                            time_slots_total = time_slots_total + self.time_slot_list_01

                    limit_number_list = 1000
                    number_of_lists = len(next_list_total)
                    inicio_lista = len(next_list_total)
                    # print(inicio_lista)
                    no_zero = True

                    while no_zero:
                        if number_of_lists - limit_number_list > 0:
                            name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            # print(lista_total_mapping[0:1])
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(next_list_total[number_of_lists - limit_number_list:number_of_lists], f)

                            name_pickle = 'specialnodes' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(special_nodes_total[number_of_lists - limit_number_list:number_of_lists], f)

                            name_pickle = 'banderaanexion' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(
                                    time_slots_total[number_of_lists - limit_number_list:number_of_lists],
                                    f)

                            number_of_lists = number_of_lists - limit_number_list
                        else:
                            name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(next_list_total[0:number_of_lists], f)

                            name_pickle = 'specialnodes' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(special_nodes_total[0:number_of_lists], f)

                            name_pickle = 'banderaanexion' + '_' + str(node_AG) + '_' + str(n_pickles_next)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(time_slots_total[0:number_of_lists], f)


                            no_zero = False
                        n_pickles_next = n_pickles_next + 1



                    # self.current_list = self.next_list.copy()
                    if self.debug_info == 'remove' or self.debug_info == 'final' or self.debug_info == 'memory':
                        b = datetime.now()
                        now = b.strftime("%H:%M:%S.%f")
                        c = b - a
                        print(
                            f"Mapping of the {node_AG} task, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                        print(f"The memory usage of the next list is {asizeof(self.next_list)} bytes, list of special nodes {asizeof(self.next_list_special_nodes)} bytes and time slot flags {asizeof(self.time_slot_list_01)} bytes ")



                number_of_pickles = n_pickles_next
                bandera_pickle = True
                previous_task = node_AG
                n_pickles_next = 0
            # print(number_of_pickles)
            # for n_pickles in range(0, number_of_pickles):
            #     name_pickle = 'currentlist' + '_' + str(previous_task) + '_' + str(n_pickles)
            #     with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #         current_list_pickle = pickle.load(f)
            #
            #     if bandera_pickle:
            #         name_pickle = 'specialnodes' + '_' + str(previous_task) + '_' + str(n_pickles)
            #         with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #             special_nodes_pickle = pickle.load(f)
            #
            #         name_pickle = 'banderaanexion' + '_' + str(previous_task) + '_' + str(n_pickles)
            #         with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #             bandera_anexion_time_pickle = pickle.load(f)
                # print(current_list_pickle)
                # print(special_nodes_pickle)
                # print(bandera_anexion_time_pickle)
            # if bandera_una_tarea:
            #     for n_pickles in range(0, number_of_pickles):
            #         name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(n_pickles)
            #         with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #             self.lista_total = self.lista_total + pickle.load(f)
            #
            #     # if self.s_prints == 'basic':
            #     #     print("esta es una sola tarea ")
            #     # self.lista_total = list(self.current_list)
            #     self.lista_total_nodes = []
            # else:
            #     if self.s_prints == 'basic':
            #         print("se integraran los mapping entre listas")
            #
            #     for n_pickles in range(0, number_of_pickles):
            #         name_pickle = 'currentlist' + '_' + str(node_AG) + '_' + str(n_pickles)
            #         with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #             self.lista_total = self.lista_total + pickle.load(f)
            #             # self.lista_total = self.lista_total + list(self.current_list)
            #
            #         # linea para corregir el problema de los indices en la evaluacion de desempeno
            #         # self.lista_total_nodes = self.lista_total_nodes + self.current_list_special_nodes.copy()
            #         name_pickle = 'specialnodes' + '_' + str(node_AG) + '_' + str(n_pickles)
            #         with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
            #             # special_nodes_pickle =
            #             self.lista_total_nodes = self.lista_total_nodes + pickle.load(f)

        if self.s_prints == 'testexh':
            print("se acabo todo")
            print(self.lista_total_nodes)
            print("la lista en reversa es ")
            # print(self.lista_total_nodes[::-1])

        # we are going to remove the innecesary files
        for erase in range(0,number_of_pickles):
            name_pickle = 'banderaanexion' + '_' + str(node_AG) + '_' + str(erase)
            os.remove(os.path.join(self.directorio, name_pickle))

        if self.debug_info == 'remove' or self.debug_info == 'total':

            print(
                f"The memory usage of the total list is {asizeof(self.lista_total)} bytes, list of special nodes {asizeof(self.lista_total_nodes)} bytes")

        return  number_of_pickles,node_AG,bandera_una_tarea

    def function_generador_lista_total(self):
        pass

    def function_generador_listas(self, lista):
        """
        in this function we transfor a list of lists into a generator
        :param lista:  list of the preliminary mappings
        :return: a generator with the lists
        """
        copia_lista = lista.copy()
        for elemento in lista:
            # yield elemento
            yield copia_lista.pop()

    # cambiar esta parte while

