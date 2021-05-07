
# este archivo es un respaldo del 12/01/2021 antes de los cambios del tamano de la lista

from pympler.asizeof import asizeof
from datetime import datetime
import networkx as nx
import time
import math
from graphviz import Digraph
import matplotlib.pyplot as plt
import GraphVisualization
from basic_functions import obtencion_sources,source_node_from_any_node,simple_paths_from_two_nodes,\
    sink_node_from_any_node,obtencion_sinks






class performance_evaluation:

    def __init__(self,mapping_list, hardware_graph, special_nodes, flag_debugging,
                                       name_file, name_file_perfo, s_prints, debug_info, dict_nodes_h,
                                       dict_nodes_a, hardware_graph_total, dict_info_h, dict_total_h, dict_info_a,
                                       debugging, graph_unroll, app_total, method_evaluation,app_graph):

        """this class is in charge of the performance evaluation (timing analysis) of the resulting mapping
        (implementation), it is divided in several stages, and the ouput of it is """

        self.mapping_list = mapping_list
        self.hardware_graph = hardware_graph
        self.special_nodes = special_nodes
        self.flag_debugging = flag_debugging
        self.name_file = name_file
        self.name_file_perfo = name_file_perfo
        self.s_prints = s_prints

        self.debug_info = debug_info
        self.dict_nodes_h = dict_nodes_h
        self.dict_nodes_a = dict_nodes_a
        self.hardware_graph_total = hardware_graph_total
        self.dict_info_h  = dict_info_h
        self.dict_total_h = dict_total_h
        self.dict_info_a = dict_info_a
        self.debugging = debugging
        self.graph_unroll = graph_unroll
        self.app_total = app_total
        self.method_evaluation = method_evaluation
        self.app_graph = app_graph
        self.clock_selection =  None

    def building_implementation_graph(self,graph_enable):

        ## in this function we start the building of the implementation graph.
        ## we start with the mapping and connect that information with the hardware graph


        time_slot_conteo = 0
        contador_instancias = 0

        cuenta_debug = 0
        contador_instancias_ri = 0
        lista_remove_nodes = []
        lista_nodos_total = [[] for g in range(0, len(self.mapping_list))]
        lista_nodos = []
        contador_nodos = 0
        lista_nodos_definitivos = [[] for g in range(0, len(self.mapping_list))]
        config_vector_parallel = []
        configuration_sum = 0
        configuration_temporal = []
        config_vector_sum = []
        lista_tasks_por_time_slot = []
        lista_nodos_removidos_total = []
        lista_nodos_removidos = []


        ## this is the main cycle, we go through each time slot that composes the mapping list

        for instancia in self.mapping_list:

            t0 = datetime.now()
            lista_nodos = []

            if self.s_prints == 'eval' or self.s_prints == 'debug':
                print(f"working instance {instancia}")
                print("we begin the process")
                print(" hw nodes", self.nodos_hw)

            # now we go through each hardware resource of the complete hardware graph

            for nodo in self.hardware_graph_total.nodes:

                if self.s_prints == 'eval' or self.s_prints == 'debug':
                    print("todos los nodos del hardware graph")
                    print(self.hardware_graph_total.nodes[nodo])

                if self.hardware_graph_total.nodes[nodo]['name'] in self.nodos_hw:

                    # first we obtain the basic information to create a node, this node belongs to the hardware graph
                    # with only the processing resources and the multiplexors

                    if self.s_prints == 'eval' or self.s_prints == 'debug':
                        print("we are checking the node ", nodo, self.hardware_graph_total.nodes[nodo]['name'])

                    # we obtain the predecessors and the successors, and also we define the name of the node in the
                    # implementation graph

                    predecesores = self.hardware_graph_total.predecessors(nodo)
                    sucesores = self.hardware_graph_total.successors(nodo)
                    nombre_nodo = nodo + time_slot_conteo


                    if self.s_prints == 'eval':
                        print(f"the name of node {nodo} is {nombre_nodo} ")

                    # we connect the hardware resource with the working time slot of the mapping, we search for the
                    # same name in both graphs, the hardware resources graph and the complete hardware resources graph

                    lugar = None
                    for p in self.hardware_graph.nodes:
                        if self.hardware_graph_total.nodes[nodo]['name'] == self.hardware_graph.nodes[p]['name']:
                            lugar = p
                            break

                    # we verify if the hardware resource is used or disabled

                    if instancia[lugar][0]:

                        # this node is assigned with a task or copy operation
                        if instancia[lugar][1] != None:
                            lista_tasks_por_time_slot.append(instancia[lugar][1])
                        self.hw_total.add_node(nombre_nodo, map=instancia[lugar][0], task=instancia[lugar][1],
                                          op=instancia[lugar][3], lat_input=instancia[lugar][8],
                                          lat_total=instancia[lugar][9], name=self.hardware_graph_total.nodes[nodo]['name'],
                                          s_info=instancia[lugar][10], a_info=instancia[lugar][11],
                                          weight=instancia[lugar][9])


                    else:

                        # this node is disabled
                        self.hw_total.add_node(nombre_nodo, map=False, task=None,
                                          op=None, lat_input=0,
                                          lat_total=0, name=self.hardware_graph_total.nodes[nodo]['name'], s_info=None,
                                          a_info=None, weight=1)

                    lista_nodos.append(nombre_nodo)

                    if self.s_prints == 'eval':
                        print(instancia[lugar])

                    # we create the edges using the list of predecessors and successors obtained before, notice that
                    # the predecessors carry the information of the latency of the head node
                    for pred in predecesores:
                        if instancia[lugar][2] == 'copy':
                            self.hw_total.add_edge(pred + time_slot_conteo, nombre_nodo, weight=self.latencia_copy)

                        else:
                            self.hw_total.add_edge(pred + time_slot_conteo, nombre_nodo, weight=instancia[lugar][8])

                    for suc in sucesores:
                        self.hw_total.add_edge(nombre_nodo, suc + time_slot_conteo)


                    # now we obtain the configuration cost of this node

                    function_config = self.dict_total_h[lugar]['fun_lat']['formula']

                    if self.s_prints == 'eval':
                        print("the configuration cost formula is ", function_config)

                    # we search for the variables used in the configuration cost formula and put them as global
                    # variables
                    # print(self.dict_total_h[nodo])
                    for variable in self.dict_total_h[nodo]['fun_lat']:

                        if variable != 'formula':
                            # print(variable)
                            globals()[variable] = self.dict_total_h[nodo]['fun_lat'][variable]
                            # break

                    # we obtain the configuration cost function and we evaluate
                    if function_config != None:

                        # in principle the function should be in the dictionaries so we only need to retrieve the data,
                        # in there is something wrong we need to raise an error
                        try:
                            formula_config = self.dict_info_h['functions_cfg'][function_config]
                        except:
                            raise Exception(
                            f"The process could not retrieve the information about the configuration function {function_config}")

                    else:
                        formula_config = 0

                    if self.s_prints == 'eval':
                        print(function_config)


                    if contador_instancias == 0:
                        try:
                            parameters = len(instancia[lugar][5])
                        except:
                            parameters = 1
                        operations = 1
                        if isinstance(formula_config, str):
                            latencia_config = int(eval(formula_config))
                        else:
                            latencia_config = formula_config
                        # print(latencia_config)
                        configuration_sum = configuration_sum + latencia_config
                        configuration_temporal.append(latencia_config)


                    else:

                        try:
                            if self.mapping_list[contador_instancias - 1][lugar][0] != instancia[lugar][0]:
                                if instancia[lugar][0]:
                                    parameters = len(instancia[lugar][5])
                                elif self.mapping_list[contador_instancias - 1][lugar][0]:
                                    parameters = len(self.mapping_list[contador_instancias - 1][lugar][5])
                            else:
                                if instancia[lugar][0]:
                                    parameters_1 = self.mapping_list[contador_instancias - 1][lugar][5]
                                    parameters_2 = instancia[lugar][5]
                                    if parameters_1 != parameters_2:
                                        parameters = len(parameters_2)
                                    else:
                                        parameters = 0
                                else:
                                    parameters = 0
                        except:
                            parameters = 1

                        try:
                            operations_1 = self.mapping_list[contador_instancias - 1][lugar][3]
                            operations_2 = instancia[lugar][3]

                            if operations_1 != operations_2:
                                operations = 1
                            else:
                                operations = 0
                        except:
                            operations = 0

                        if isinstance(formula_config, str):
                            latencia_config = int(eval(formula_config))
                        else:
                            latencia_config = formula_config
                        # print(latencia_config)
                        configuration_sum = configuration_sum + latencia_config
                        configuration_temporal.append(latencia_config)
                else:
                    # this is the other branch of the creation of the implementation graph, in here we deal with
                    # the hardware resources that are not processing resources or multiplexers

                    predecesores = self.hardware_graph_total.predecessors(nodo)
                    done = True
                    info_s = []

                    if nodo not in self.nodos_source:
                        source_nodo_temporal = source_node_from_any_node(self.hardware_graph_total, self.nodos_source, nodo)
                    else:
                        source_nodo_temporal = None

                    if source_nodo_temporal != None:
                        path = simple_paths_from_two_nodes(self.hardware_graph_total, source_nodo_temporal, nodo)
                        # print(path)
                        for unique_path in path:
                            for nodo_in_path in unique_path:
                                try:
                                    # print(instancia[nodo_in_path])
                                    if instancia[nodo_in_path][10] != -1 and instancia[nodo_in_path][10] != 0:
                                        info_s = instancia[nodo_in_path][10]
                                        break
                                except:
                                    pass

                    if info_s:

                        resolution = [info_s[1], info_s[2]]
                    else:
                        task_source = obtencion_sources(self.app_total)
                        source_dummy = task_source.pop()

                        resolution = [self.dict_info_a[source_dummy]['param']['height'],
                                      self.dict_info_a[source_dummy]['param']['width']]

                    sucesores = self.hardware_graph_total.successors(nodo)
                    nombre_nodo = nodo + time_slot_conteo

                    if self.s_prints == 'eval':
                        print("the name in here is different ", nombre_nodo,
                              self.hardware_graph_total.nodes[nodo]['op'], self.hardware_graph_total.nodes[nodo])
                    # print(hardware_graph_total.nodes[nodo]['name'], list(hardware_graph_total.predecessors(nodo)))
                    # print(hardware_graph_total.nodes[])
                    operacion = None
                    if self.hardware_graph_total.nodes[nodo]['op'] == 'ri':
                        operacion = self.hardware_graph_total.nodes[nodo]['op']

                        # if data_performance:
                        #     print(operacion,"sdfsdfds")
                    self.hw_total.add_node(nombre_nodo, map=True, task=None,
                                      op=self.hardware_graph_total.nodes[nodo]['op'],
                                      lat_input=self.hardware_graph_total.nodes[nodo]['lat'],
                                      lat_total=int(self.hardware_graph_total.nodes[nodo]['lat']) * resolution[0] *
                                                resolution[1], name=self.hardware_graph_total.nodes[nodo]['name'],
                                      s_info=resolution, operacion=operacion)

                    lista_nodos.append(nombre_nodo)

                    for pred in predecesores:
                        self.hw_total.add_edge(pred + time_slot_conteo, nombre_nodo,
                                          weight=self.hardware_graph_total.nodes[nodo]['lat'])

                    for suc in sucesores:
                        self.hw_total.add_edge(nombre_nodo, suc + time_slot_conteo)
                        # hw_salida.add_edge(nombre_nodo, suc + time_slot_conteo)

                    # print("memoria de ondof",hardware_graph_total.nodes[nodo]['op'])
                    if self.hardware_graph_total.nodes[nodo]['op'] == 'rw' or self.hardware_graph_total.nodes[nodo]['op'] == 'rd':
                        configuration_sum = configuration_sum + 1
                        configuration_temporal.append(1)

            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - t0
                print(
                    f"First stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

            t1 = datetime.now()

            lista_nodos_total[contador_instancias_ri] = lista_nodos






            if graph_enable and self.s_prints == 'eval':
                cuenta_debug = cuenta_debug + 1
                name_debug = 'test_for_time_slot_before_prune' + str(cuenta_debug)
                lista_vacia = []
                Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app', name_debug, [], 'red', 'black',
                                                              'circle')
                Graph_visual_00.f.render(view=False)
                Graph_visual_00.f.render(view=True, format='pdf')


            # now we will remove the interface nodes and the memory nodes where is needed it
            # we will keep a list of the nodes that we are going to remove
            lista_nodos_removidos = []

            # we start with the memory nodes

            bandera_no_remover = False
            bandera_no_remover_sensor = False
            bandera_no_remover_actuator = False
            for tarea_en_lista in lista_tasks_por_time_slot:

                for nodo_debug in self.app_total.nodes:
                    if self.app_total.nodes[nodo_debug]['name'] == self.app_graph.nodes[tarea_en_lista]['name']:
                        tarea_lista_app_total = nodo_debug
                        break

                if contador_instancias_ri == 0:
                    if self.s_prints == 'eval':
                        print("FIRST TIME SLOT")

                    suc = self.app_total.successors(tarea_lista_app_total)
                    for s in suc:
                        # print(app_total.nodes[s])
                        if self.app_total.nodes[s]['op'] == 'interface':
                            bandera_no_remover_actuator = True
                            bandera_no_remover_sensor = True
                            bandera_no_remover = True
                            break
                    break
                else:
                    if self.s_prints == 'eval':
                        print("TEST SUCCESSORS - ACTUATORS")
                    suc = self.app_total.successors(tarea_lista_app_total)

                    for s in suc:
                        if self.app_total.nodes[s]['op'] == 'interface':
                            bandera_no_remover = True
                            bandera_no_remover_actuator = True
                            break
                    if self.s_prints == 'eval':
                        print("TEST PREDECESSORS - SENSORS")
                    pre = self.app_total.predecessors(tarea_lista_app_total)
                    for p in pre:
                        if self.app_total.nodes[p]['op'] == 'interface':
                            bandera_no_remover_sensor = True
                            bandera_no_remover = True
                            break
                    break



            if self.s_prints == 'eval':
                print(
                    f"The flag of remove nodes is {bandera_no_remover} and the individuals flags {bandera_no_remover_sensor} and {bandera_no_remover_actuator}")
            # hw_total_copia.nodes[actuator_dg]['assign']
            #

            if not bandera_no_remover:
                if self.s_prints == 'eval':
                    print("WE ARE DEBUGGING MEMORY PROBLEM")
                hw_buffer = self.hw_total.copy()
                for nodo in hw_buffer.nodes:
                    if self.hw_total.nodes[nodo]['op'] == 'rm':
                        predecesores = list(self.hw_total.predecessors(nodo))
                        sucesores = list(self.hw_total.successors(nodo))
                        lista_sin_input_edge = []
                        lista_sin_output_edge = []
                        lista_normal_pre = []
                        lista_normal_suc = []
                        for pre in predecesores:
                            if self.hw_total.in_degree(pre) == 0:
                                lista_sin_input_edge.append(pre)
                            else:
                                lista_normal_pre.append(pre)
                        for suc in sucesores:
                            if self.hw_total.out_degree(suc) == 0:
                                lista_sin_output_edge.append(suc)
                            else:
                                lista_normal_suc.append(suc)
                        self.hw_total.remove_node(nodo)
                        contador_nodos = contador_nodos + 1
                        lista_nodos_removidos.append(nodo)
                        for el01 in lista_sin_input_edge:
                            for el02 in lista_normal_suc:
                                self.hw_total.add_edge(el01, el02)
                        for el01 in lista_sin_output_edge:
                            for el02 in lista_normal_pre:
                                self.hw_total.add_edge(el02, el01)


                #########################################################
                # next we remove the actuators and sensors that are not required

                hw_buffer = self.hw_total.copy()
                if self.s_prints == 'eval':
                    print("we remove the actuators and sensors that are not required")
                for n in hw_buffer.nodes:
                    if self.s_prints == 'eval':
                        print(" test 01 - inside building function", n, self.hw_total.nodes[n])
                    if self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.out_degree(
                            n) == 0 and contador_instancias_ri < len(self.mapping_list) - 1:
                        self.hw_total.remove_node(n)
                        contador_nodos = contador_nodos + 1
                        lista_nodos_removidos.append(n)


                    elif self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.in_degree(
                            n) == 0 and contador_instancias_ri != 0:
                        if self.s_prints == 'eval':
                            print("test 02  - inside building function")
                        if n not in self.hardware_graph_total.nodes:
                            self.hw_total.remove_node(n)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(n)


            else:

                for tarea_en_lista in lista_tasks_por_time_slot:
                    if self.s_prints == 'eval':
                        print(f"task is {tarea_en_lista}, {self.sources_aplicacion} yyyy {self.sinks_aplicacion} ")
                    ####verification of the sensors
                    if bandera_no_remover_sensor:
                        if tarea_en_lista in self.sources_aplicacion:
                            lugar_en_grafo_sensor = None
                            for nodo_en_grafo in self.hw_total.nodes:
                                if self.s_prints == 'eval':
                                    print(f"nodo es {nodo_en_grafo} and its data is {self.hw_total.nodes[nodo_en_grafo]}")
                                if tarea_en_lista == self.hw_total.nodes[nodo_en_grafo]['task']:
                                    lugar_en_grafo_sensor = nodo_en_grafo
                            sensor_nodo_arq = source_node_from_any_node(self.hw_total, obtencion_sources(self.hw_total),
                                                                        lugar_en_grafo_sensor)
                            if tarea_en_lista in self.sources_aplicacion_total:  # obtencion_sources(app_total):
                                sensor_nodo_app = tarea_en_lista
                            else:
                                sensor_nodo_app = source_node_from_any_node(self.app_total, self.sources_aplicacion_total,
                                                                            tarea_en_lista)
                            # print(f"datos hw {hw_total.nodes[sensor_nodo_arq]} datos de la aplicacion {app_total.nodes[sensor_nodo_app]} y el numero es {lugar_en_grafo_sensor}")
                            self.hw_total.nodes[sensor_nodo_arq]['assign'] = self.app_total.nodes[sensor_nodo_app]['name']


                    else:
                        #################################################################
                        hw_buffer = self.hw_total.copy()
                        for nodo in hw_buffer.nodes:
                            if self.hw_total.nodes[nodo]['op'] == 'rm':
                                predecesores = list(self.hw_total.predecessors(nodo))
                                sucesores = list(self.hw_total.successors(nodo))
                                lista_sin_input_edge = []
                                lista_sin_output_edge = []
                                lista_normal_pre = []
                                lista_normal_suc = []
                                for pre in predecesores:
                                    if self.hw_total.in_degree(pre) == 0:
                                        lista_sin_input_edge.append(pre)
                                    else:
                                        lista_normal_pre.append(pre)
                                for suc in sucesores:
                                    if self.hw_total.out_degree(suc) == 0:
                                        lista_sin_output_edge.append(suc)
                                    else:
                                        lista_normal_suc.append(suc)
                                self.hw_total.remove_node(nodo)
                                contador_nodos = contador_nodos + 1
                                lista_nodos_removidos.append(nodo)
                                for el01 in lista_sin_input_edge:
                                    for el02 in lista_normal_suc:
                                        self.hw_total.add_edge(el01, el02)
                                for el01 in lista_sin_output_edge:
                                    for el02 in lista_normal_pre:
                                        self.hw_total.add_edge(el02, el01)

                        # we remove the actuators
                        hw_buffer = self.hw_total.subgraph(lista_tasks_por_time_slot).copy()
                        if self.s_prints == 'eval':
                            print("test 03 - inside of the building function")
                        for n in hw_buffer.nodes:

                            if self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.in_degree(
                                    n) == 0 and contador_instancias_ri != 0:
                                # if s_prints == 'evalprint':
                                #     print("PORQUE NO ENTRA AQUI")
                                if n not in self.hardware_graph_total.nodes:
                                    self.hw_total.remove_node(n)
                                    contador_nodos = contador_nodos + 1
                                    lista_nodos_removidos.append(n)



                    if bandera_no_remover_actuator:
                        if tarea_en_lista in self.sinks_aplicacion:
                            if self.s_prints == 'eval':
                                print(f"the task {tarea_en_lista} is a sink and we need to check something")
                            lugar_en_grafo_sensor = None
                            for nodo_en_grafo in self.hw_total.nodes:
                                if tarea_en_lista == self.hw_total.nodes[nodo_en_grafo]['task']:
                                    lugar_en_grafo_sensor = nodo_en_grafo
                            if self.s_prints == 'eval':
                                print(f" debug error 100 {lugar_en_grafo_sensor}")
                            actuator_nodo_arq = sink_node_from_any_node(self.hw_total, obtencion_sinks(self.hw_total),
                                                                        lugar_en_grafo_sensor)
                            # if tarea_en_lista in self.sinks_aplicacion_total
                            ####aqui se tiene un error donde se quiere utilizar el nombre de la tarea de la aplicacion
                            # pero se necesita el de la aplicacion total

                            for nodo_debug in self.app_total.nodes:
                                if self.app_total.nodes[nodo_debug]['name'] == self.app_graph.nodes[tarea_en_lista]['name']:
                                    tarea_lista_app_total = nodo_debug
                                    break
                            #     print(nodo_debug,self.app_total.nodes[nodo_debug]['name'])
                            # for nodo_debug in self.app_graph.nodes:
                            #     print(nodo_debug,self.app_graph.nodes[nodo_debug]['name'])

                            actuator_nodo_app = sink_node_from_any_node(self.app_total, self.sinks_aplicacion_total,
                                                                        tarea_lista_app_total)
                            if self.s_prints == 'eval':
                                print(f" debug error 200 {actuator_nodo_arq} application {actuator_nodo_app}")
                            self.hw_total.nodes[actuator_nodo_arq]['assign'] = self.app_total.nodes[actuator_nodo_app]['name']
                    else:
                        hw_buffer = self.hw_total.copy()
                        for nodo in hw_buffer.nodes:
                            if self.hw_total.nodes[nodo]['op'] == 'rm':
                                predecesores = list(self.hw_total.predecessors(nodo))
                                sucesores = list(self.hw_total.successors(nodo))
                                lista_sin_input_edge = []
                                lista_sin_output_edge = []
                                lista_normal_pre = []
                                lista_normal_suc = []
                                for pre in predecesores:
                                    if self.hw_total.in_degree(pre) == 0:
                                        lista_sin_input_edge.append(pre)
                                    else:
                                        lista_normal_pre.append(pre)
                                for suc in sucesores:
                                    if self.hw_total.out_degree(suc) == 0:
                                        lista_sin_output_edge.append(suc)
                                    else:
                                        lista_normal_suc.append(suc)
                                self.hw_total.remove_node(nodo)
                                contador_nodos = contador_nodos + 1
                                lista_nodos_removidos.append(nodo)
                                for el01 in lista_sin_input_edge:
                                    for el02 in lista_normal_suc:
                                        self.hw_total.add_edge(el01, el02)
                                for el01 in lista_sin_output_edge:
                                    for el02 in lista_normal_pre:
                                        self.hw_total.add_edge(el02, el01)

                        # continuaremos con los nodos actuator si existen antes del ultimo time slot y los sensores del time slot mas alla del primer slot
                        hw_buffer = self.hw_total.subgraph(lista_tasks_por_time_slot).copy()
                        if self.s_prints == 'eval':
                            print("test 04 - inside the building function")
                        for n in hw_buffer.nodes:
                            if self.s_prints == 'eval':
                                print("test 05 - inside the building function ", n, self.hw_total.nodes[n])
                            if self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.out_degree(
                                    n) == 0 and contador_instancias_ri < len(self.mapping_list) - 1:
                                self.hw_total.remove_node(n)
                                contador_nodos = contador_nodos + 1
                                lista_nodos_removidos.append(n)


                            elif self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.in_degree(
                                    n) == 0 and contador_instancias_ri != 0:
                                if self.s_prints == 'eval':
                                    print("test 06 - inside the building function")
                                if n not in self.hardware_graph_total.nodes:
                                    self.hw_total.remove_node(n)
                                    contador_nodos = contador_nodos + 1
                                    lista_nodos_removidos.append(n)



            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - t1
                print(
                    f"Second stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            t2 = datetime.now()



            hw_buffer = self.hw_total.copy()
            if self.s_prints == 'eval':
                print("test 07 - inside the building function")
            for n in hw_buffer.nodes:
                try:
                    if self.hw_total.nodes[n]['op'] == 'ri':

                        test = self.hw_total.nodes[n]['assign']
                except:

                    if self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.out_degree(
                            n) == 0 and contador_instancias_ri < len(self.mapping_list) - 1:
                        if self.s_prints == 'eval':
                            print("test 08 - inside the building function ", n, self.hw_total.nodes[n])
                        self.hw_total.remove_node(n)
                        contador_nodos = contador_nodos + 1
                        lista_nodos_removidos.append(n)


                    elif self.hw_total.nodes[n]['op'] == 'ri' and len(self.mapping_list) > 1 and self.hw_total.in_degree(
                            n) == 0 and contador_instancias_ri != 0:

                        if n not in self.hardware_graph_total.nodes:
                            if self.s_prints == 'eval':
                                print("test 09 - inside the building function")
                            self.hw_total.remove_node(n)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(n)



            lista_tasks_por_time_slot = []

            if graph_enable and self.s_prints == 'eval':
                cuenta_debug = cuenta_debug + 1
                name_debug = 'test_for_time_slot_after_prune' + str(cuenta_debug)
                lista_vacia = []
                Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app', name_debug, [], 'red', 'black',
                                                              'circle')
                Graph_visual_00.f.render(view=False)
                Graph_visual_00.f.render(view=True, format='pdf')



            lista_nodos_definitivos[contador_instancias_ri] = list(set(lista_nodos) - set(lista_nodos_removidos))
            lista_nodos_removidos_total = lista_nodos_removidos + lista_nodos_removidos_total
            config_vector_parallel.append(configuration_temporal)
            config_vector_sum.append(configuration_sum)
            configuration_sum = 0
            configuration_temporal = []

            time_slot_conteo = time_slot_conteo + len(self.hardware_graph_total.nodes) + 1
            contador_instancias = contador_instancias + 1
            contador_instancias_ri += 1
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - t2
                print(
                    f"Third stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        return lista_nodos_definitivos,lista_nodos_removidos,contador_nodos,config_vector_sum,config_vector_parallel,lista_nodos_total

    def adition_special_nodes(self,graph_enable,lista_nodos_definitivos,lista_nodos_removidos):
        # print("lista removidos q", lista_nodos_removidos_total)
        a = datetime.now()
        vector_sensor_dg = []
        bandera_falla_time_slots = False
        vector_actuator_dg = []
        for nodo in self.hw_total.nodes:
            if self.hw_total.nodes[nodo]['op'] == 'ri' and self.hw_total.in_degree(nodo) == 0:
                vector_sensor_dg.append(nodo)
            if self.hw_total.nodes[nodo]['op'] == 'ri' and self.hw_total.out_degree(nodo) == 0:
                vector_actuator_dg.append(nodo)

        maximo_numero = max(list(self.hw_total.nodes))

        contador_nodos_especiales = maximo_numero + 1

        time_slot_conteo = 0
        if self.s_prints == 'eval':
            # if True:
            print("inside the special nodes addition function")
            print(self.special_nodes, contador_nodos_especiales)
            # print(lista_nombres_total,lista_nodos_total)
            print(lista_nodos_definitivos)
            print(f"the lenght of the list {len(lista_nodos_definitivos)}")
            for nodo in self.hw_total.nodes:
                print(nodo, self.hw_total.nodes[nodo])
            print("end of the lists before the special nodes addition section")
        # sinks = obtencion_sinks(hardware_graph_total)
        sinks = self.sinks_hw_total
        # print("vamos a checar que es cada uno de los sinks")
        # for s in sinks:
        #     print(s, hardware_graph_total.nodes[s])
        # input("finalizacion de algo")
        hardware_graph_total_copy = self.hardware_graph_total.copy()
        if lista_nodos_removidos:
            for el in lista_nodos_removidos:
                if el in sinks:
                    sinks.remove(el)
                    hardware_graph_total_copy.remove(el)
                    bandera_done = True
                    while bandera_done:
                        prede = list(self.hardware_graph_total.predecessors(el))
                        sinks = sinks + prede
        # print("lista de nodos removidos",lista_nodos_removidos)
        # sources = obtencion_sources(hardware_graph_total)
        sources = self.nodos_source
        # sinks = obtencion_sinks(hardware_graph_total)
        nodos_por_time_slot = len(self.hardware_graph_total.nodes)
        lista_nodos_especiales = []
        # print(special_nodes,sinks)
        if self.s_prints == 'eval':
            print("the special nodes are ", self.special_nodes)
        # print("test de algo")
        # print(special_nodes)
        # print(mapping_list)
        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Miscellaneous operations evaluation graph, current time {now}"
                f" the processing time is {c.seconds} seconds {c.microseconds} microseconds")


        if self.special_nodes:
            # print(special_nodes)
            # the special nodes will connect two time slots, this will mean that there is some data that needs to be
            # tranfered to a following time slot to be processed. when we write the first time slot we mean the source time
            # slot and the second time slot is the sink time slot or the other way around
            lista_nodos_creados = []
            cuenta_debug = 0
            for pareja in self.special_nodes:
                # print(pareja,special_nodes)
                if self.s_prints == 'eval':
                    print("test 01 - inside the addition special nodes function ", pareja)
                if pareja[0]:
                    if self.s_prints == 'eval':
                        print("test 02 - inside the addition special nodes function")
                    lugar_pareja_1 = None
                    lugar_pareja_2 = None
                    # print(lista_nodos_definitivos, len(lista_nodos_definitivos))
                    if self.s_prints == 'eval':
                        print("test 03 - inside the addition special nodes function")
                        print(lista_nodos_definitivos[pareja[3] - 1])

                    grafo_01 = self.hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1])
                    grafo_02 = self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]])
                    for nodo in grafo_01.nodes:
                        if grafo_01.nodes[nodo]['name'] == self.hardware_graph.nodes[pareja[1]]['name']:
                            lugar_pareja_1 = nodo  ####sink of the first time slot
                    for nodo in grafo_02.nodes:
                        if grafo_02.nodes[nodo]['name'] == self.hardware_graph.nodes[pareja[2]]['name']:
                            lugar_pareja_2 = nodo  ####source of the second time slot
                    if self.s_prints == 'eval':
                        print("test 04 - inside the addition special nodes function - places", lugar_pareja_1, lugar_pareja_2)

                    lista_sinks_rw = []
                    for s in obtencion_sinks(grafo_01):
                        if grafo_01.nodes[s]['op'] == 'rw':
                            lista_sinks_rw.append(s)

                    if lugar_pareja_1 in lista_sinks_rw:
                        sink = lugar_pareja_1
                    else:
                        sink = sink_node_from_any_node(self.hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1]),
                                                       lista_sinks_rw,
                                                       lugar_pareja_1)


                    if self.s_prints == 'eval':
                        print("test 05 - inside the addition special nodes function ", sink)
                        print(lista_sinks_rw)
                        # input("test")
                    nombre_busqueda = sink  # + nodos_por_time_slot * (pareja[3] - 1)

                    if nombre_busqueda != None:
                        if self.s_prints == 'eval':
                            print("test 06 - inside the addition special nodes function")
                        self.hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                          name='sp')
                        self.hw_total.add_edge(nombre_busqueda, contador_nodos_especiales)

                        # print(hw_total.nodes[contador_nodos_especiales])
                        #
                        pareja_append = [contador_nodos_especiales, pareja[3] - 1, sink, 'suc']
                        lista_nodos_especiales.append(pareja_append)
                        lista_nodos_creados.append(contador_nodos_especiales)
                        contador_nodos_especiales = contador_nodos_especiales + 1

                    # ahora anexaremos el nodo que debe de ser source
                    # print(nombre_busqueda)
                    # nombre_busqueda = pareja[2] + nodos_por_time_slot * (pareja[3])
                    if graph_enable:
                        for er in self.hw_total:
                            print("test", er, self.hw_total.nodes[er])
                    nombre_busqueda = lugar_pareja_2 + nodos_por_time_slot * (pareja[3])
                    if graph_enable:
                        print(nombre_busqueda, obtencion_sources(self.hw_total))
                    # for bla in hw_total.nodes:
                    #     print("interno ", bla,hw_total.nodes[bla])
                    if lugar_pareja_2 in obtencion_sources(self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]])):
                        source = lugar_pareja_2
                    else:
                        source = source_node_from_any_node(self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]]),
                                                           obtencion_sources(
                                                               self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]])),
                                                           [lugar_pareja_2])

                    # source = source_node_from_any_node(hw_total,obtencion_sources(hw_total), [nombre_busqueda])
                    if graph_enable:
                        print(source)
                    # if source in lista_nodos_creados:
                    #     source = list(hw_total.successors(source))
                    #     source = source[0]
                    if self.s_prints == 'eval' or graph_enable:
                        print("test 07 - inside the addition special nodes function ", source)

                    if source != None:
                        if graph_enable or self.s_prints == 'eval':
                            print("test 08 - inside the addition special nodes function ", contador_nodos_especiales, source, nombre_busqueda, lugar_pareja_2,
                                  nodos_por_time_slot)

                        self.hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                          name='sp')
                        self.hw_total.add_edge(contador_nodos_especiales, source)

                        pareja_append = [contador_nodos_especiales, pareja[3], source, 'pre']
                        lista_nodos_especiales.append(pareja_append)
                        lista_nodos_creados.append(contador_nodos_especiales)
                        contador_nodos_especiales = contador_nodos_especiales + 1


                else:
                    # pass
                    # print("NODO DE RECOMPUTO",pareja)
                    # print(lista_nodos_definitivos)
                    # print(pareja)
                    try:
                        grafo_02 = self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]])

                        for nodo in grafo_02.nodes:
                            if grafo_02.nodes[nodo]['name'] == self.hardware_graph.nodes[pareja[1]]['name']:
                                lugar_pareja_1 = nodo  ####sink of the first time slot
                        for nodo in grafo_02.nodes:
                            if grafo_02.nodes[nodo]['name'] == self.hardware_graph.nodes[pareja[2]]['name']:
                                lugar_pareja_2 = nodo  ####source of the second time slot
                        if self.s_prints == 'eval':
                            print("debugging 01 - special nodes")
                            print(lugar_pareja_1,lugar_pareja_2)
                            # print("vamos a checar algo")
                        # grafo_prueba = hw_total.subgraph(lista_nodos_definitivos[pareja[3]])
                        lista_sinks_rw = []
                        for s in obtencion_sinks(grafo_02):
                            if grafo_02.nodes[s]['op'] == 'rw':
                                lista_sinks_rw.append(s)
                            elif grafo_02.nodes[s]['op'] == 'ri':
                                prede_ri = list(grafo_02.predecessors(s))
                                done = True
                                while done:
                                    prede_ri_buffer = prede_ri.pop()
                                    if grafo_02.nodes[prede_ri_buffer]['op'] == 'rw':
                                        lista_sinks_rw.append(prede_ri_buffer)
                                        done = False
                                        break
                        # print("imprimiremos algo TTTTTEEEESSSSSTTTTTTTT")
                        if graph_enable and self.s_prints == 'eval':
                            cuenta_debug = cuenta_debug + 1
                            name_debug = 'test_addition_special_nodes' + str(cuenta_debug)
                            lista_vacia = []
                            Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app',
                                                                          name_debug, [], 'red', 'black',
                                                                          'circle')
                            Graph_visual_00.f.render(view=False)
                            Graph_visual_00.f.render(view=True, format='pdf')

                        if lugar_pareja_1 in lista_sinks_rw:
                            sink = lugar_pareja_1
                        else:
                            sink = sink_node_from_any_node(grafo_02,
                                                           lista_sinks_rw,
                                                           lugar_pareja_1)
                            if sink == None:
                                sucesores_lugar_pareja_1 = list(grafo_02.successors(lugar_pareja_1))
                                for s in lista_sinks_rw:
                                    if s in sucesores_lugar_pareja_1:
                                        sink = s
                                        break

                        if lugar_pareja_2 in obtencion_sources(self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]])):
                            source = lugar_pareja_2
                        else:
                            source = source_node_from_any_node(self.hw_total.subgraph(lista_nodos_definitivos[pareja[3]]),
                                                               obtencion_sources(
                                                                   self.hw_total.subgraph(
                                                                       lista_nodos_definitivos[pareja[3]])),
                                                               [lugar_pareja_2])
                            if self.hw_total.nodes[source]['op'] == 'ri':
                                sucesores_ri = list(self.hw_total.successors(source))
                                source = sucesores_ri.pop()

                        self.hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                          name='sp')
                        self.hw_total.add_edge(contador_nodos_especiales, source)
                        self.hw_total.add_edge(sink, contador_nodos_especiales)
                        # print(hw_total.nodes[contador_nodos_especiales])
                        #
                        pareja_append = [contador_nodos_especiales, pareja[3] - 1, sink, 'suc']
                        lista_nodos_especiales.append(pareja_append)
                        lista_nodos_creados.append(contador_nodos_especiales)
                        contador_nodos_especiales = contador_nodos_especiales + 1

                    except:
                        bandera_falla_time_slots = True

        return nodos_por_time_slot,lista_nodos_especiales,bandera_falla_time_slots


    def addition_configuration_nodes(self,graph_enable,contador_nodos,config_vector_sum,config_vector_parallel,
                                     nodos_por_time_slot,lista_nodos_total,lista_nodos_especiales):



        #
        type_of_configuration = self.dict_info_h['functions_cfg']['type_cfg']

        if self.s_prints == 'eval':
            for nodo in self.hw_total.nodes:
                print(f"nodes before the addition of configuration nodes {nodo} data {self.hw_total.nodes[nodo]}")

        flag_debugging = False


        maximo_numero = max(list(self.hw_total.nodes))

        contador_nodos_configuracion = maximo_numero + 1 + contador_nodos
        # # vamos a adicionar los nodos de configuracion
        primer_time_slot = True
        if self.s_prints == 'eval':
            print("the number of time slots are ", contador_nodos_configuracion)
            print(len(self.mapping_list))
            print(self.dict_total_h)
            # print(info_nodes_hw)
        configuracion_latencia = 0
        vector_latencies_cfg = []
        configuracion_latencia_total = 0
        for n in range(0, len(self.mapping_list)):
            if self.s_prints == 'eval':
                print("test 1 - inside addition of configuration nodes function ", n, len(self.mapping_list))

            if primer_time_slot:

                if type_of_configuration == 'sequential':
                    self.hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                      lat_total=config_vector_sum[n], name='config')
                elif type_of_configuration == 'parallel':
                    self.hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                      lat_total=max(config_vector_parallel[n]), name='config')
                for source in self.nodos_source:
                    if self.s_prints == 'eval':
                        print("test 2 - inside addition of configuration nodes function - edges 01", contador_nodos_configuracion, source)

                    self.hw_total.add_edge(contador_nodos_configuracion, source)
                # print(max(vector_latencies_cfg))
                contador_nodos_configuracion = contador_nodos_configuracion + 1
                primer_time_slot = False
            else:

                if self.s_prints == 'eval':
                    print("test 3 - inside addition of configuration nodes function ")
                configuracion_latencia = 0
                vector_latencies_cfg = []

                if type_of_configuration == 'sequential':
                    self.hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                      lat_total=config_vector_sum[n], name='config')
                elif type_of_configuration == 'parallel':
                    self.hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                      lat_total=max(config_vector_parallel[n]), name='config')

                # primero conectemos al time slot anterior
                adicion = nodos_por_time_slot * (n - 1)



                # sinks = obtencion_sinks(hardware_graph_total)
                sinks = self.sinks_hw_total

                if self.s_prints == 'eval':
                    print("test 4 - inside addition of configuration nodes function - sinks ", sinks)


                if self.s_prints == 'eval':
                    print("test 4 - inside addition of configuration nodes function - time slot ", n)
                # ahora conectaremos el nodo con el time slot siguiente
                adicion = nodos_por_time_slot * (n - 1)
                if self.s_prints == 'eval':
                    print("test 4 - inside addition of configuration nodes function", adicion, sinks)
                    print(lista_nodos_total[n])
                    print(f"lthe list of nodes is  {lista_nodos_total}")
                    print(lista_nodos_total[n - 1])



                for elemento in lista_nodos_total[n - 1]:

                    if elemento in self.hw_total.nodes:
                        if self.hw_total.out_degree(elemento) == 0:
                            if self.s_prints == 'eval':
                                print(f"edge 01   {elemento} y {contador_nodos_configuracion} ")
                            self.hw_total.add_edge(elemento, contador_nodos_configuracion)
                for elemento in lista_nodos_especiales:
                    if self.s_prints == 'eval':
                        print("element", elemento)
                        print("hw nodes ", self.hw_total.nodes)
                    if elemento[2] in lista_nodos_total[n - 1] and elemento[2] in self.hw_total.nodes:
                        if self.hw_total.out_degree(elemento[0]) == 0:
                            if self.hw_total.nodes[elemento[0]]['op'] != 'config':
                                if self.s_prints == 'eval':
                                    print(f"edge 02   {elemento[0]} y {contador_nodos_configuracion}")
                                self.hw_total.add_edge(elemento[0], contador_nodos_configuracion)

                # sources = obtencion_sources(hardware_graph_total)
                sources = self.nodos_source
                if self.s_prints == 'eval':
                    print("connection of the next time slot", n)
                # ahora conectaremos el nodo con el time slot siguiente
                adicion = nodos_por_time_slot * (n)
                if self.s_prints == 'eval':
                    print("data", adicion, sources)
                    print(lista_nodos_total[n])

                for elemento in lista_nodos_total[n]:

                    if elemento in self.hw_total.nodes:
                        if self.hw_total.in_degree(elemento) == 0:
                            if self.s_prints == 'eval':
                                print(f"edge 04   {contador_nodos_configuracion} y {elemento}")
                            self.hw_total.add_edge(contador_nodos_configuracion, elemento)
                for elemento in lista_nodos_especiales:
                    if self.s_prints == 'eval':
                        print("element", elemento)
                    if elemento[2] in lista_nodos_total[n] and elemento[2] in self.hw_total.nodes:
                        if self.hw_total.in_degree(elemento[0]) == 0:
                            if self.hw_total.nodes[elemento[0]]['op'] != 'config':
                                if self.s_prints == 'eval':
                                    print(f" edge 06   {contador_nodos_configuracion} y {elemento[0]}")
                                self.hw_total.add_edge(contador_nodos_configuracion, elemento[0])

                contador_nodos_configuracion = contador_nodos_configuracion + 1
                configuracion_latencia_total = configuracion_latencia + configuracion_latencia_total

    def disable_nodes_removing(self):

        self.hw_perfo = self.hw_total.copy()
        # s_prints = 'evalprint'
        vector_edges_perfo = []
        detect_edge = False

        for nodo in self.hw_total.nodes:
            # if s_prints == 'basic' or s_prints == 'debug':
            # print("datos del nodo", nodo, hw_total.nodes[nodo])
            if not self.hw_total.nodes[nodo]['map'] or self.hw_total.nodes[nodo]['op'] == 'mem' or self.hw_total.nodes[nodo][
                'op'] == 'rm':
                if self.s_prints == 'eval':
                    print("we will remove the node ", nodo)

                predecesores = list(self.hw_perfo.predecessors(nodo))
                copia_predecesores = []
                valido = True
                if predecesores:
                    while valido:
                        vector_test = []
                        for el in predecesores:
                            if el in self.hw_perfo.nodes:
                                vector_test.append(True)
                        if len(vector_test) >= 1:
                            valido = False
                        else:
                            predecesores_copy = list(predecesores)
                            predecesores = []
                            for el in predecesores_copy:
                                predecesores = predecesores + list(self.hw_perfo.predecessors(el))
                    copia_predecesores = predecesores
                if self.s_prints == 'eval':
                    print("predecessor copy", copia_predecesores)
                sucesores = list(self.hw_perfo.successors(nodo))
                copia_sucesores = []
                valido = True
                if sucesores:
                    while valido:
                        vector_test = []
                        for el in sucesores:
                            if el in self.hw_perfo.nodes:
                                vector_test.append(True)
                        if len(vector_test) >= 1:
                            valido = False
                        else:
                            sucesores_copy = list(sucesores)
                            sucesores = []
                            for el in sucesores_copy:
                                predecesores = predecesores + list(self.hw_perfo.successors(el))
                    copia_sucesores = sucesores

                if self.s_prints == 'eval' :
                    print("the group of predecessors is ", copia_predecesores)
                    print(" the group of succesors is ", copia_sucesores)
                self.hw_perfo.remove_node(nodo)


            elif self.hw_total.nodes[nodo]['op'] == 'special':
                sucesores = self.hw_total.successors(nodo)
                bandera_config = False
                for suc in sucesores:
                    if self.hw_total.nodes[suc]['op'] == 'config':
                        bandera_config = True
                        break
                if bandera_config:
                    lista_edges = []
                    predecesores = self.hw_perfo.predecessors(nodo)
                    sucesores = self.hw_perfo.successors(nodo)
                    self.hw_perfo.remove_node(nodo)
                    for pred in predecesores:
                        for suc in sucesores:
                            if [pred, suc] in lista_edges:
                                self.hw_perfo.add_edge(pred, suc)
                                buffer_dato = [pred, suc]
                                lista_edges.append(buffer_dato)
                            else:
                                self.hw_perfo.add_edge(pred, suc)
                                buffer_dato = [pred, suc]
                                lista_edges.append(buffer_dato)

    def evaluation(self,bandera_falla_time_slots):


        # hw_perfo = hw_total.copy()
        longest = None
        lat_new_version_total = None

        if self.s_prints == 'eval':
            print(f"start of the performance evaluation, the method will be {self.method_evaluation}")
        contador_error_longest = 0
        # print(method_evaluation)
        # input("enter")

        maximum_clock = None
        a = datetime.now()
        if self.method_evaluation == 'longest':
            try:

                vector_relojes = []
                longest = nx.dag_longest_path(self.hw_perfo, weight='weight', default_weight=1)
                if self.s_prints == 'eval':
                    print("longest parth", longest)
                    # input("test")
                name_clk = 0
                clk_info = None
                contador_error_longest += 1  # 1
                # print("test de evaluacion",longest)
                # if len(longest) == 1:

                # in here we are going to put the name of the resource, the computing latency, and maybe the formula
                vector_info = []
                for nodo in longest:
                    # if data_performance:
                    # print(nodo,hw_perfo.nodes[nodo])

                    try:
                        if self.hw_perfo.nodes[nodo]['operacion'] != None:
                            type_task = self.hw_perfo.nodes[nodo]['operacion']
                        else:
                            type_task = self.hw_perfo.nodes[nodo]['op']
                    except:
                        type_task = self.hw_perfo.nodes[nodo]['op']

                    # print("ntest", type_task)
                    name_resource = self.hw_perfo.nodes[nodo]['name']
                    if type_task == 'ri' or type_task == 'rr' or type_task == 'rw':
                        if type_task == 'ri':
                            try:
                                for n, data in self.dict_total_h.items():
                                    if data['name'] == name_resource:
                                        name_clk = data['ops']['actuator']['clk']
                            except:
                                for n, data in self.dict_total_h.items():
                                    if data['name'] == name_resource:
                                        name_clk = data['ops']['sensor']['clk']
                        elif type_task == 'rw':
                            for n, data in self.dict_total_h.items():
                                if data['name'] == name_resource:
                                    name_clk = data['ops']['write']['clk']
                        elif type_task == 'rr':
                            for n, data in self.dict_total_h.items():
                                if data['name'] == name_resource:
                                    name_clk = data['ops']['read']['clk']

                    else:

                        if self.s_prints == 'eval':
                            print("first line ", nodo, name_resource, type_task)

                        for n, data in self.dict_total_h.items():
                            if data['name'] == name_resource:

                                for operacion in data['ops']:
                                    if operacion == type_task:
                                        # print(data['ops'][operacion]['clk'])
                                        name_clk = data['ops'][operacion]['clk']
                    # if data_performance:
                    if self.s_prints == 'eval':
                        print("test", name_clk)
                    # print("dddd", name_clk)
                    for t, data in self.dict_info_h['functions_res'].items():
                        # print(self.hw_total[nodo]['task'])

                        if name_clk == t:
                            if self.s_prints == 'eval':
                                print(data,name_clk)
                            # we need to check if the computing clock is a function or an integer
                            try:
                                if isinstance(data, str):
                                    # if the computing latency is an equation
                                    # print("The computing latency is an equation")
                                    # we call again the variable_separation function
                                    vector_total_parametros = self.variable_separation(data)
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

                                    if self.s_prints == 'eval':
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
                                            for pa in self.dict_nodes_a[self.hw_perfo[nodo]['task']]['param']:
                                                if param_formula == pa:
                                                    globals()[pa] = self.dict_nodes_a[self.hw_perfo[nodo]['task']]['param'][pa]
                                    # now we can evaluate the formula
                                    value_clk = eval(data)
                                    if self.s_prints == 'eval':
                                        print("the final value of the equation is  ", data)
                                    vector_relojes.append(data)
                                    clk_info = data
                                else:
                                    # if the equation is an integer we dont do anything

                                    vector_relojes.append(data)
                                    clk_info = data

                            except:
                                vector_relojes.append(self.latencia_copy)
                                clk_info = self.latencia_copy

                            # vector_relojes.append(data)
                            # clk_info = data
                    #     print("nsdf",data,t,name_clk)
                    #     if name_clk == t:
                    #         print("tetgd")
                    # if flag_debugging:
                    #     print(nodo, name_resource, clk_info, type_task)
                    temporal_info = [nodo, name_resource, clk_info, type_task]
                    vector_info.append(temporal_info)
                # print(vector_relojes)
                contador_error_longest += 1  # 2
                if self.clock_selection == 'perf_clock':
                    maximum_clock = self.dict_info_h['max_clk']
                else:
                    maximum_clock = max(vector_relojes)
                # print("el clock q utilizar ", maximum_clock)
                if self.s_prints == 'eval':
                    print(longest)
                    print(self.hw_perfo.nodes)
                    print("we are going to obtain the latency")
                if self.s_prints =='eval':
                    for nodo in self.hw_perfo.nodes:
                        print("data of the node", nodo, self.hw_perfo.nodes[nodo])
                    for nodo in self.hw_total.nodes:
                        print(nodo, self.hw_total.nodes[nodo])

                contador_error_longest += 1  # 3


                contador_error_longest += 1  # 4
                # print(dict_info_hw)
                # performance evaluation
                lat_new_version_total = 0
                latencia_total = 0
                if self.s_prints == 'eval':
                    print(
                        "We are going to start the performance evaluation method, based on the critical path "
                        "of the evaluation graph, the longest path es", longest)
                bandera_fin_time_slot = False
                contador = 0
                computing_latency_temporal = 0
                primer_nodo = True
                contador_nodos_critical = len(longest)
                contador_error_longest += 1  # 5
                for nodo in longest:
                    # print(nodo)
                    if self.s_prints == 'eval':
                        print("data of the node and vector_info", nodo, vector_info[contador])
                        print(f"the node name is {self.hw_perfo.nodes[nodo]['name']}")
                    successor = list(self.hw_perfo.successors(nodo))
                    contador_error_longest += 1  # 6
                    if successor:
                        for suc in successor:
                            if self.s_prints == 'eval':
                                print("el sucesor es ", suc, self.hw_perfo.nodes[suc])

                            if self.hw_perfo.nodes[suc]['op'] == 'config':  # or contador == contador_nodos_critical - 1:
                                bandera_fin_time_slot = True
                    else:
                        bandera_fin_time_slot = True
                    contador_error_longest += 1  # 7
                    if self.s_prints == 'eval':
                        print("the flag ", bandera_fin_time_slot, successor)
                        print("the node is  ", nodo, " and its name is ", self.hw_perfo.nodes[nodo])
                    if self.hw_perfo.nodes[nodo]['op'] == 'config':

                        lat_new_version_total = lat_new_version_total + int(self.hw_perfo.nodes[nodo]['lat_total'])
                        latencia_total = latencia_total + int(self.hw_perfo.nodes[nodo]['lat_total'])
                        self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                        self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = int(self.hw_perfo.nodes[nodo]['lat_total'])
                        if self.s_prints == 'eval' :
                            print(
                                f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {int(self.hw_perfo.nodes[nodo]['lat_total'])}")
                            print(f"the latency until now is {lat_new_version_total}")
                        # bandera_fin_time_slot = False
                        contador_error_longest += 1  # 8

                    elif bandera_fin_time_slot:
                        if self.s_prints == 'eval':
                            print("test 01 - inside the performance evaluation", self.hw_perfo.nodes[nodo])

                        if len(self.hw_perfo.nodes[nodo]['s_info']) == 3:
                            if self.s_prints == 'eval':
                                print("case 1")
                            lat_new_version_total_temporal = self.hw_perfo.nodes[nodo]['s_info'][1] * \
                                                             self.hw_perfo.nodes[nodo]['s_info'][
                                                                 2] * maximum_clock
                        elif len(self.hw_perfo.nodes[nodo]['s_info']) == 2:
                            if self.s_prints == 'eval':
                                print("case 2")
                            lat_new_version_total_temporal = self.hw_perfo.nodes[nodo]['s_info'][0] * \
                                                             self.hw_perfo.nodes[nodo]['s_info'][
                                                                 1] * maximum_clock
                        # except:
                        contador_error_longest += 1  # 9
                        if self.s_prints == 'eval':
                            print("ojnsdfsds")
                        lat_new_version_total = lat_new_version_total + lat_new_version_total_temporal
                        # print(lat_new_version_total)
                        if self.s_prints == 'eval' :
                            print(
                                f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {lat_new_version_total_temporal}")
                        # print(f"the latency until now is {lat_new_version_total}")
                        self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                        self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = lat_new_version_total_temporal
                        bandera_fin_time_slot = False
                        if self.s_prints == 'eval':
                            print("test 02")
                        contador_error_longest += 1  # 10
                    elif self.hw_perfo.nodes[nodo]['op'] == 'special':
                        # input("enter")
                        self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                        self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = 0
                    else:

                        try:
                            name_resource_lat = self.hw_perfo.nodes[nodo]['name']
                            lugar_recurso = None
                            for n, data in self.dict_nodes_h.items():
                                # print(data['name'])
                                if name_resource_lat == data['name']:
                                    lugar_recurso = n
                            if self.s_prints == 'eval':
                                print("hhdhdhdh", lugar_recurso, name_resource_lat)
                            name_function = self.dict_nodes_h[lugar_recurso]['ops'][self.hw_perfo.nodes[nodo]['op']]['latency']

                            for data in self.dict_info_h['functions_res']:
                                # print(data)
                                if data == name_function:
                                    function_formula = self.dict_info_h['functions_res'][data]
                            # print(function_formula)
                            # ############this is the new way to obtain the latency
                            lugar_nodo = None

                            # print(dict_info_a)
                            # print("entre")
                            # print(info_nodes_app)
                            for n, data in self.dict_info_a.items():
                                if data['name'] == self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['name']:
                                    # print("se encontro")
                                    lugar_nodo = n

                            # for n, data in dict_info_a.items():
                            #     if dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name'] == dict_info_a[n]['name']:
                            # lista_nodos_numeros                #         lugar_nodo = n
                            # lista_sources_ag_total = obtencion_sources(app_total)
                            lista_sources_ag_total = self.sources_aplicacion_total
                            source_total_app = source_node_from_any_node(self.app_total,
                                                                         lista_sources_ag_total,
                                                                         lugar_nodo)
                            #
                            height = self.dict_info_a[source_total_app]['param']['height']
                            width = self.dict_info_a[source_total_app]['param']['width']
                            # print(width)
                            # # we are going to autoasign the values of the parameters
                            # # print(self.dict_nodes_a)
                            # # print(function_formula)
                            if self.s_prints == 'eval':
                                print(f" the function is {function_formula}, the width is {width}, the height is {height}")
                            contador_parametros = 0
                            bandera_primera_vez_letra = True
                            vector_parametro = []
                            vector_total_parametros = []
                            contador_linea = 0
                            if isinstance(function_formula, str):
                                for letra in function_formula:

                                    if bandera_primera_vez_letra:
                                        if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                            pass
                                        else:
                                            vector_parametro.append(letra)
                                            bandera_primera_vez_letra = False
                                    else:
                                        if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ' or contador_linea == len(
                                                function_formula):

                                            vector_total_parametros.append(vector_parametro)
                                            vector_parametro = []
                                        else:
                                            if contador_linea == len(function_formula) - 1:

                                                vector_parametro.append(letra)
                                                vector_total_parametros.append(vector_parametro)
                                            else:
                                                vector_parametro.append(letra)
                                    contador_linea = contador_linea + 1



                            vector_parametro = []
                            # print("bibisbf, ",vector_total_parametros)
                            for it in vector_total_parametros:
                                dummy = "".join(it)
                                if dummy:
                                    try:
                                        int(dummy)
                                    except:
                                        if dummy not in vector_parametro:
                                            vector_parametro.append(dummy)

                            ### we first look for the general values of width and height
                            for param_formula in vector_parametro:
                                if param_formula == 'width':
                                    pass
                                elif param_formula == 'height':
                                    pass
                                else:
                                    # in here we are going to look the value in the dict of the nodes
                                    for pa in self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['param']:

                                        if param_formula == pa:
                                            # print("bugggaaaaaaaa")
                                            # print(pa)
                                            globals()[pa] = self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['param'][pa]
                            if vector_info[contador - 1][1] == 'config':
                                clk_test = 0
                            else:
                                clk_test = vector_info[contador - 1][2]
                            # if self.s_prints == 'eval':
                            #     print("error tracker",clk_test)
                            if computing_latency_temporal >= clk_test:
                                computing_latency_temporal = computing_latency_temporal
                            else:
                                computing_latency_temporal = clk_test

                            if isinstance(function_formula, str):
                                # print("buggzazo",function_formula,computing_latency_temporal,vector_info)
                                # resultado_latencia = (eval(function_formula) ) * maximum_clock + \
                                #                      vector_info[contador][2]

                                resultado_latencia = (eval(function_formula) - 1) * computing_latency_temporal + \
                                                     vector_info[contador][2] + 1
                            else:
                                # resultado_latencia = (function_formula ) * maximum_clock + \
                                #                      vector_info[contador][2]

                                resultado_latencia = (function_formula - 1) * computing_latency_temporal + \
                                                     vector_info[contador][2] + 1
                            # print("buggazoo")
                            # print(maximum_clock)
                            resultado_latencia_total = width * height * maximum_clock

                            # print("resultado input latenci ",resultado_latencia)
                            # print("resultado latenci total",resultado_latencia_total)

                            lat_new_version_total = lat_new_version_total + resultado_latencia
                            if self.s_prints == 'eval' :
                                print(
                                    f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {resultado_latencia}")
                                print(f"the latency until now is {lat_new_version_total}")
                            self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                            self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = resultado_latencia
                            if self.s_prints == 'eval':
                                print(f"the latency of the node is {resultado_latencia} "
                                      f"and the overall latency is {lat_new_version_total}")
                        except:
                            if self.s_prints == 'eval':
                                print("test 03 - enter except")
                            # # if data_performance:
                            # #     print("no se pudo hacer nada")
                            # # pass
                            # # aqui se tomaran en cuenta los recursos de comunicacion y extras
                            # print(vector_info)
                            valor_a_sumar = vector_info[contador][2]
                            if valor_a_sumar != None:
                                lat_new_version_total = lat_new_version_total + vector_info[contador][
                                    2]  # int(hw_perfo.nodes[nodo]['lat_input'])
                            else:
                                lat_new_version_total = 0
                            if self.s_prints == 'eval' or self.s_prints == 'printper':
                                print(
                                    f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {int(self.hw_perfo.nodes[nodo]['lat_input'])}")
                            # print(f"the latency until now is {lat_new_version_total}")
                            self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                            self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = vector_info[contador][
                                2]  # int(hw_perfo.nodes[nodo]['lat_input'])
                            if self.s_prints == 'eval':
                                print(f"the latency of the node is {vector_info[contador][2]} "
                                      f"and the overall latency is {lat_new_version_total}")
                    contador = contador + 1
            except:
                # print("se llego al error")
                # time.sleep(3)
                # print("entrada a error en la evaluacion ",contador_error_longest)
                lat_new_version_total = 1000000000000000
                longest = None

        else:
            #########inicio de procesamiento

            valor_maximo = 0
            debug_prints = False
            sources = obtencion_sources(self.hw_perfo)
            sinks = obtencion_sinks(self.hw_perfo)
            longest_final = []
            if self.s_prints == 'eval':
                print(f"the method selected is simple paths, sources nodes {sources} and the sinks nodes are {sinks}")
            # print("entrada nuevo metedo")
            for source in sources:
                for sink in sinks:
                    for simple in nx.all_simple_paths(self.hw_perfo, source, sink):
                        try:
                            vector_relojes = []
                            longest = simple
                            if debug_prints:
                                print("longest parth", longest)
                            name_clk = 0
                            clk_info = None
                            # in here we are going to put the name of the resource, the computing latency, and maybe the formula
                            vector_info = []
                            for nodo in longest:
                                try:
                                    if self.hw_perfo.nodes[nodo]['operacion'] != None:
                                        type_task = self.hw_perfo.nodes[nodo]['operacion']
                                    else:
                                        type_task = self.hw_perfo.nodes[nodo]['op']
                                except:
                                    type_task = self.hw_perfo.nodes[nodo]['op']
                                name_resource = self.hw_perfo.nodes[nodo]['name']
                                if type_task == 'ri' or type_task == 'rr' or type_task == 'rw':
                                    if type_task == 'ri':
                                        try:
                                            for n, data in self.dict_total_h.items():
                                                if data['name'] == name_resource:
                                                    name_clk = data['ops']['actuator']['clk']
                                        except:
                                            for n, data in self.dict_total_h.items():
                                                if data['name'] == name_resource:
                                                    name_clk = data['ops']['sensor']['clk']
                                    elif type_task == 'rw':
                                        for n, data in self.dict_total_h.items():
                                            if data['name'] == name_resource:
                                                name_clk = data['ops']['write']['clk']
                                    elif type_task == 'rr':
                                        for n, data in self.dict_total_h.items():
                                            if data['name'] == name_resource:
                                                name_clk = data['ops']['read']['clk']

                                else:
                                    if self.s_prints == 'eval':
                                        print("first line ", nodo, name_resource, type_task)

                                    for n, data in self.dict_total_h.items():
                                        if data['name'] == name_resource:

                                            for operacion in data['ops']:
                                                if operacion == type_task:
                                                    # print(data['ops'][operacion]['clk'])
                                                    name_clk = data['ops'][operacion]['clk']
                                # if data_performance:
                                if self.s_prints == 'eval':
                                    print("test 04", name_clk)
                                # print("dddd", name_clk)
                                for t, data in self.dict_info_h['functions_res'].items():

                                    # print(name_clk,t)
                                    if name_clk == t:
                                        vector_relojes.append(data)
                                        clk_info = data

                                temporal_info = [nodo, name_resource, clk_info, type_task]
                                vector_info.append(temporal_info)

                            if self.clock_selection == 'perf_clock':
                                maximum_clock = self.dict_info_h['max_clk']
                            else:
                                maximum_clock = max(vector_relojes)
                            # print("el clock q utilizar ", maximum_clock)
                            if self.s_prints =='eval':
                                print(longest)
                                print(self.hw_perfo.nodes)

                                print(
                                    "We are going to start the performance evaluation method, based on the critical path of the evaluation graph")
                            # performance evaluation
                            lat_new_version_total = 0
                            latencia_total = 0


                            bandera_fin_time_slot = False
                            contador = 0
                            computing_latency_temporal = 0
                            primer_nodo = True
                            contador_nodos_critical = len(longest)
                            for nodo in longest:
                                # print(nodo)
                                if self.s_prints == 'eval':
                                    print("info of node ", nodo, vector_info[contador])
                                    print(f"the node name is {self.hw_perfo.nodes[nodo]['name']}")
                                # print("el nodo es ", nodo, "y su nombre es", hw_perfo.nodes[nodo]['name'])


                                successor = list(self.hw_perfo.successors(nodo))
                                # print(successor)

                                if successor:
                                    for suc in successor:
                                        if debug_prints:
                                            print("el sucesor es ", suc, self.hw_perfo.nodes[suc])

                                        if self.hw_perfo.nodes[suc][
                                            'op'] == 'config':  # or contador == contador_nodos_critical - 1:
                                            bandera_fin_time_slot = True
                                else:
                                    bandera_fin_time_slot = True
                                if self.s_prints == 'eval':
                                    print("flag", bandera_fin_time_slot, successor)
                                    print("el nodo es ", nodo, "y su nombre es", self.hw_perfo.nodes[nodo])
                                if self.hw_perfo.nodes[nodo]['op'] == 'config':
                                    if debug_prints:
                                        print("error search")
                                    lat_new_version_total = lat_new_version_total + int(
                                        self.hw_perfo.nodes[nodo]['lat_total'])
                                    latencia_total = latencia_total + int(self.hw_perfo.nodes[nodo]['lat_total'])
                                    self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                    self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = int(self.hw_perfo.nodes[nodo]['lat_total'])
                                    if self.s_prints == 'eval':
                                        print(
                                            f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {int(self.hw_perfo.nodes[nodo]['lat_total'])}")
                                        print(f"the latency until now is {lat_new_version_total}")
                                    # bandera_fin_time_slot = False
                                elif bandera_fin_time_slot:
                                    if self.s_prints == 'eval':
                                        print("nsdofsdf", self.hw_perfo.nodes[nodo])
                                        print("mas datos")
                                    if len(self.hw_perfo.nodes[nodo]['s_info']) == 3:
                                        if self.s_prints == 'eval':
                                            print("caso 1")
                                        lat_new_version_total_temporal = self.hw_perfo.nodes[nodo]['s_info'][1] * \
                                                                         self.hw_perfo.nodes[nodo]['s_info'][
                                                                             2] * maximum_clock
                                    elif len(self.hw_perfo.nodes[nodo]['s_info']) == 2:
                                        if self.s_prints == 'eval':
                                            print("caso 2")
                                        lat_new_version_total_temporal = self.hw_perfo.nodes[nodo]['s_info'][0] * \
                                                                         self.hw_perfo.nodes[nodo]['s_info'][
                                                                             1] * maximum_clock
                                    # except:


                                    lat_new_version_total = lat_new_version_total + lat_new_version_total_temporal
                                    # print(lat_new_version_total)
                                    if self.s_prints == 'eval':
                                        print(
                                            f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {lat_new_version_total_temporal}")
                                    # print(f"the latency until now is {lat_new_version_total}")
                                    self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                    self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = lat_new_version_total_temporal
                                    bandera_fin_time_slot = False
                                    if debug_prints:
                                        print("teststst")
                                else:

                                    try:
                                        name_resource_lat = self.hw_perfo.nodes[nodo]['name']
                                        lugar_recurso = None
                                        for n, data in self.dict_nodes_h.items():
                                            # print(data['name'])
                                            if name_resource_lat == data['name']:
                                                lugar_recurso = n
                                        if self.s_prints == 'eval':
                                            print("hhdhdhdh", lugar_recurso, name_resource_lat)
                                        name_function = self.dict_nodes_h[lugar_recurso]['ops'][self.hw_perfo.nodes[nodo]['op']][
                                            'latency']

                                        for data in self.dict_info_h['functions_res']:
                                            # print(data)
                                            if data == name_function:
                                                function_formula = self.dict_info_h['functions_res'][data]
                                        # print(function_formula)
                                        # ############this is the new way to obtain the latency
                                        lugar_nodo = None
                                        # print(dict_info_a)
                                        # print("entre")
                                        # print(info_nodes_app)
                                        for n, data in self.dict_info_a.items():
                                            if data['name'] == self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['name']:
                                                # print("se encontro")
                                                lugar_nodo = n

                                        # for n, data in dict_info_a.items():
                                        #     if dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name'] == dict_info_a[n]['name']:
                                        #         lugar_nodo = n
                                        # lista_sources_ag_total = obtencion_sources(app_total)
                                        lista_sources_ag_total = self.sources_aplicacion_total
                                        source_total_app = source_node_from_any_node(self.app_total,
                                                                                     lista_sources_ag_total,
                                                                                     lugar_nodo)
                                        #
                                        height = self.dict_info_a[source_total_app]['param']['height']
                                        width = self.dict_info_a[source_total_app]['param']['width']
                                        # print(width)
                                        # # we are going to autoasign the values of the parameters
                                        # # print(self.dict_nodes_a)
                                        # # print(function_formula)
                                        contador_parametros = 0
                                        bandera_primera_vez_letra = True
                                        vector_parametro = []
                                        vector_total_parametros = []
                                        if isinstance(function_formula, str):
                                            for letra in function_formula:
                                                if bandera_primera_vez_letra:
                                                    if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                                        pass
                                                    else:
                                                        vector_parametro.append(letra)
                                                        bandera_primera_vez_letra = False
                                                else:
                                                    if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                                        vector_total_parametros.append(vector_parametro)
                                                        vector_parametro = []
                                                    else:
                                                        vector_parametro.append(letra)
                                        vector_parametro = []
                                        for it in vector_total_parametros:
                                            dummy = "".join(it)
                                            if dummy:
                                                try:
                                                    int(dummy)
                                                except:
                                                    if dummy not in vector_parametro:
                                                        vector_parametro.append(dummy)

                                        ### we first look for the general values of width and height
                                        for param_formula in vector_parametro:
                                            if param_formula == 'width':
                                                pass
                                            elif param_formula == 'height':
                                                pass
                                            else:
                                                # in here we are going to look the value in the dict of the nodes
                                                for pa in self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['param']:

                                                    if param_formula == pa:
                                                        globals()[pa] = \
                                                        self.dict_nodes_a[self.hw_perfo.nodes[nodo]['task']]['param'][
                                                            pa]
                                        if vector_info[contador - 1][1] == 'config':
                                            clk_test = 0
                                        else:
                                            clk_test = vector_info[contador - 1][2]

                                        if computing_latency_temporal >= clk_test:
                                            computing_latency_temporal = computing_latency_temporal
                                        else:
                                            computing_latency_temporal = clk_test

                                        if isinstance(function_formula, str):

                                            resultado_latencia = (eval(function_formula)) * maximum_clock + \
                                                                 vector_info[contador][2]

                                            # resultado_latencia = (eval(function_formula) - 1) * computing_latency_temporal + \
                                            #                      vector_info[contador][2] + 1
                                        else:
                                            resultado_latencia = (function_formula) * maximum_clock + \
                                                                 vector_info[contador][2]

                                            # resultado_latencia = (function_formula - 1) * computing_latency_temporal + \
                                            #                      vector_info[contador][2] + 1
                                        resultado_latencia_total = width * height * maximum_clock

                                        # print("resultado input latenci ",resultado_latencia)
                                        # print("resultado latenci total",resultado_latencia_total)

                                        lat_new_version_total = lat_new_version_total + resultado_latencia
                                        if self.s_prints == 'eval':
                                            print(
                                                f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {resultado_latencia}")
                                            print(f"the latency until now is {lat_new_version_total}")
                                        self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                        self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = resultado_latencia

                                    except:
                                        if self.s_prints == 'eval':
                                            print("enter to except for the simple path method")
                                        # # if data_performance:
                                        # #     print("no se pudo hacer nada")
                                        # # pass
                                        # # aqui se tomaran en cuenta los recursos de comunicacion y extras
                                        # print(vector_info)
                                        valor_a_sumar = vector_info[contador][2]
                                        if valor_a_sumar != None:
                                            lat_new_version_total = lat_new_version_total + vector_info[contador][
                                                2]  # int(hw_perfo.nodes[nodo]['lat_input'])
                                        else:
                                            lat_new_version_total = 0
                                        if self.s_prints == 'eval':
                                            print(
                                                f"the node is {self.hw_perfo.nodes[nodo]['name']} and its latency is {int(self.hw_perfo.nodes[nodo]['lat_input'])}")
                                        # print(f"the latency until now is {lat_new_version_total}")
                                        self.hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                        self.hw_perfo.nodes[nodo]['latencia_de_nodo'] = vector_info[contador][
                                            2]  # int(hw_perfo.nodes[nodo]['lat_input'])

                                contador = contador + 1
                        except:
                            # print("se llego al error")
                            # time.sleep(3)
                            maximum_clock = None
                            lat_new_version_total = 'no_valid'
                            longest = None
                        # print(longest,lat_new_version_total)
                        if lat_new_version_total != 'no_valid':
                            # print("entreamos aqui")
                            if valor_maximo < lat_new_version_total:
                                # print("asignamos el valor")
                                valor_maximo = lat_new_version_total
                                longest_final = simple

        if bandera_falla_time_slots:
            lat_new_version_total = 1000000000000000
            longest = None

        if self.s_prints == 'eval':
            print(longest,lat_new_version_total, maximum_clock)
            print("end of the performance evaluation")

        # lista_nombres_critical = []
        # for l in longest:
        #     lista_nombres_critical.append(hw_perfo.nodes[l]['name'])
        # print(f"el path critico es {longest} y los nombres de este path son {lista_nombres_critical} y el numero de elementos son {len(longest)} y {len(lista_nombres_critical)}")
        if self.method_evaluation == 'simple':
            longest = longest_final
            lat_new_version_total = valor_maximo
        return longest,lat_new_version_total,maximum_clock

    def building_unroll_graph(self,lista_nodos_total,hw_total_copia,lista_especial,lista_nodos_especiales,contador_extra):

        for nodo_unroll in self.graph_unroll:
            # print(nodo_unroll,graph_unroll.nodes[nodo_unroll])

            if self.graph_unroll.nodes[nodo_unroll]['op'] == 'rm':
                # print(contador_extra)
                predecesores = self.graph_unroll.predecessors(nodo_unroll)
                sucesores = self.graph_unroll.successors(nodo_unroll)
                lista_names_predecesores = []
                lista_names_sucesores = []

                if self.s_prints == 'eval':
                    print("test 01 - graph unroll", list(self.graph_unroll.predecessors(nodo_unroll)),
                          list(self.graph_unroll.successors(nodo_unroll)))

                for pre in predecesores:
                    # print("lista",pre)
                    lista_names_predecesores.append(self.graph_unroll.nodes[pre]['name'])
                for suc in sucesores:
                    # print("suc",suc)
                    lista_names_sucesores.append(self.graph_unroll.nodes[suc]['name'])

                # print(lista_names_sucesores,lista_names_predecesores)
                if self.s_prints == 'eval':
                    print("list of nodes  -  ", lista_nodos_total)
                primer_time_slot_final = True
                contador_time_slots = 0
                for time_slot in lista_nodos_total:
                    # print(time_slot)
                    esta_el_nodo = False
                    lista_nombres = []
                    for elemento in time_slot:
                        # print(elemento)
                        # print(f"el elemento is {hw_total_copia.nodes[elemento]}")
                        # print(f"el nombre del elemento es {hw_total_copia.nodes[elemento]['name']}")
                        try:
                            lista_nombres.append(hw_total_copia.nodes[elemento]['name'])
                        except:
                            pass
                    if self.graph_unroll.nodes[nodo_unroll]['name'] not in lista_nombres:

                        hw_total_copia.add_node(contador_extra, name=self.graph_unroll.nodes[nodo_unroll]['name'],
                                                op=self.graph_unroll.nodes[nodo_unroll]['op'], lat=0, task='mem01',
                                                map=False,
                                                label='mem')

                        for nodo in time_slot:
                            if nodo in self.hw_total.nodes:

                                if self.hw_total.nodes[nodo]['name'] in lista_names_sucesores:

                                    if nodo in lista_especial:

                                        # print("estamos checando esto 01", nodo)
                                        lugar = None
                                        for elemento in lista_nodos_especiales:
                                            if elemento[2] == nodo:
                                                lugar = elemento[0]
                                        if self.s_prints == 'eval':
                                            print("arco 072", lugar, contador_extra,
                                                              self.hw_total.nodes[lugar]['name'])
                                        sucesores_arco = list(hw_total_copia.predecessors(lugar))
                                        for suc_ar in sucesores_arco:
                                            hw_total_copia.remove_edge(suc_ar, lugar)
                                            hw_total_copia.add_edge(suc_ar, contador_extra)
                                        # print("succesores arco", sucesores_arco)

                                        hw_total_copia.add_edge(contador_extra, lugar)


                                    else:

                                        if self.s_prints == 'eval':
                                            print("arco 01", contador_extra, nodo,
                                                            self.hw_total.nodes[nodo]['name'])
                                        predecesores_arco = list(hw_total_copia.predecessors(nodo))
                                        # print("predecesores arco", predecesores_arco)
                                        for pre_arco in predecesores_arco:
                                            hw_total_copia.remove_edge(pre_arco, nodo)
                                        hw_total_copia.add_edge(contador_extra, nodo)
                                        hw_total_copia.add_edge(pre_arco, contador_extra)

                                if self.hw_total.nodes[nodo]['name'] in lista_names_predecesores:
                                    if nodo in lista_especial:
                                        # print("estamos checando esto 01",nodo)
                                        lugar = None
                                        for elemento in lista_nodos_especiales:
                                            if elemento[2] == nodo:
                                                lugar = elemento[0]
                                        if self.s_prints == 'eval':   print("arco 042", lugar, contador_extra,
                                                              self.hw_total.nodes[lugar]['name'])
                                        sucesores_arco = list(hw_total_copia.successors(lugar))
                                        for suc_ar in sucesores_arco:
                                            hw_total_copia.remove_edge(lugar, suc_ar)
                                            hw_total_copia.add_edge(contador_extra, suc_ar)
                                        # print("succesores arco", sucesores_arco)

                                        hw_total_copia.add_edge(lugar, contador_extra)



                                    else:
                                        if self.s_prints == 'eval':
                                            print("arco 0jjj2", nodo, contador_extra, self.hw_total.nodes[nodo]['name'])
                                        sucesores_arco = list(hw_total_copia.successors(nodo))
                                        for suc_ar in sucesores_arco:
                                            hw_total_copia.remove_edge(nodo, suc_ar)
                                            hw_total_copia.add_edge(contador_extra, suc_ar)
                                        if self.s_prints == 'eval':   print("succesores arco", sucesores_arco)
                                        hw_total_copia.add_edge(nodo, contador_extra)

                        # if s_prints == 'evalprint':
                        #     print("PRIMERA VISITA A ESTE MODULO",contador_extra)
                        # if primer_time_slot_final == True:
                        #     primer_time_slot_final = False
                        # else:
                        #
                        #     grafo_para_sinks = hw_total_copia.subgraph(lista_nodos_total[contador_time_slots - 1])
                        #     sinks_lista = obtencion_sinks(grafo_para_sinks)
                        #     grafo_para_sources = hw_total_copia.subgraph(time_slot)
                        #     sources_lista = obtencion_sources(grafo_para_sources)
                        #     for si in sinks_lista:
                        #         for so in sources_lista:
                        #             hw_total_copia.add_edge(si,so)
                        # contador_time_slots = contador_time_slots + 1
                        contador_extra = contador_extra + 1

        vector_sensor_ag = []
        # vector_sensor_dg = []
        vector_actuator_ag = []
        # vector_actuator_dg = []
        for nodo in self.app_total:
            if self.app_total.nodes[nodo]['op'] == 'interface' and self.app_total.in_degree(nodo) == 0:
                vector_sensor_ag.append(nodo)
            if self.app_total.nodes[nodo]['op'] == 'interface' and self.app_total.out_degree(nodo) == 0:
                vector_actuator_ag.append(nodo)

        for nodo in hw_total_copia.nodes:
            if hw_total_copia.nodes[nodo]['op'] == 'special':
                hw_total_copia.nodes[nodo]['map'] = False
        return  hw_total_copia

    def perf_eval(self):


        a = datetime.now()
        if self.s_prints == 'basic':
            print("we enter the perfomance evaluation function ")
            print(self.hardware_graph_total.nodes)
            print("the mapping that we are going to evaluate is")
            print(self.mapping_list)
            print("we are going to print the info of the nodes ")
            print(self.dict_info_h)
            print("between dictionaries application nodes")
            print(self.dict_nodes_a)
            print("between dictionaries hardware nodes")
            print(self.dict_nodes_h)
            print("between dictionaries total nodes")
            print(self.dict_total_h)


        ####### data that is recurrent of all processes
        self.nodos_source = obtencion_sources(self.hardware_graph_total)
        self.sources_aplicacion = obtencion_sources(self.app_graph)
        self.sources_aplicacion_total = obtencion_sources(self.app_total)
        self.sinks_aplicacion = obtencion_sinks(self.app_graph)
        self.sinks_hw_total = obtencion_sinks(self.hardware_graph_total)
        self.sinks_aplicacion_total = obtencion_sinks(self.app_total)
        self.nodos_hw = []
        for node in self.hardware_graph.nodes:
            self.nodos_hw.append(self.hardware_graph.nodes[node]['name'])
        self.maximum_clock = self.dict_info_h['max_clk']


        ## we verify if the copy nodes have latency if not we put zero
        try:
            self.latencia_copy = self.dict_info_h['functions_res']['lat_copy']
        except:
            self.latencia_copy = 0


        # implementation graph
        self.hw_total = nx.DiGraph()


        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Beginning of the performance evaluation, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            # print(
            #     f"The memory usage of the next list is {asizeof(self.next_list)} bytes, list of special nodes {asizeof(self.next_list_special_nodes)} bytes and time slot flags {asizeof(self.time_slot_list_01)} bytes ")
        a = datetime.now()

        ######debug with graphs
        GRAPH_ENABLE_DEBUG = False
        lista_nodos_definitivos,lista_nodos_removidos,contador_nodos,config_vector_sum,config_vector_parallel,\
            lista_nodos_total= self.building_implementation_graph(GRAPH_ENABLE_DEBUG)


        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Build of the basic structure of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

        if self.s_prints == 'eval' and self.debugging:
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app', 'implementationgraph_firststage', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')

        a = datetime.now()

        nodos_por_time_slot,lista_nodos_especiales,bandera_falla_time_slots = \
            self.adition_special_nodes(False, lista_nodos_definitivos, lista_nodos_removidos)

        if self.s_prints == 'eval' and self.debugging:
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app', 'implementationgraph_afterspecialnodes', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Addition to the special nodes of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        a = datetime.now()

        self.addition_configuration_nodes( False, contador_nodos, config_vector_sum, config_vector_parallel,
                                     nodos_por_time_slot, lista_nodos_total, lista_nodos_especiales)

        if self.s_prints == 'eval' and self.debugging:
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_total, lista_vacia, 'app',
                                                          'implementationgraph_afterconfignodes', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')

        if self.s_prints == 'eval':
            for nodo in self.hw_total.nodes:
                print(f"nodes after addition of config {nodo} data {self.hw_total.nodes[nodo]}  test ")

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Addition to the config nodes of the evaluation graph, current time {now} the processing time "
                f"is {c.seconds} seconds {c.microseconds} microseconds")

        # up until here we have the complete graph, in this stage we remove the nodes that are disable or the memory
        # nodes, we create a new implementation graph which is going to help us obtain the computing time of processing
        # an image

        a = datetime.now()

        self.disable_nodes_removing()


        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Remove of the disable nodes of the evaluation graph, current time {now} the processing time "
                f"is {c.seconds} seconds {c.microseconds} microseconds")



        if self.s_prints == 'eval' and self.debugging:
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.hw_perfo, lista_vacia, 'app', 'evaluationgraph', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')
            # time.sleep(2)
        if self.s_prints == 'eval':
            print("before the evaluation")
            for nodo in self.hw_perfo.nodes:
                print(nodo, self.hw_perfo.nodes[nodo])

        a = datetime.now()

        longest,lat_new_version_total,maximum_clock =  self.evaluation(bandera_falla_time_slots)

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Perfomance evaluation, current time {now} the processing time "
                f"is {c.seconds} seconds {c.microseconds} microseconds")



        contador_extra = max(self.hw_total.nodes) + 1
        hw_total_copia = self.hw_total.copy()

        lista_especial = []
        for elem in lista_nodos_especiales:
            lista_especial.append(elem[2])



        if self.s_prints == 'eval':
            print("Building of the last graph")
            for nodo in hw_total_copia.nodes:
                print(f" node {nodo} and data {hw_total_copia.nodes[nodo]}")

        a = datetime.now()

        hw_total_copia = self.building_unroll_graph(lista_nodos_total,hw_total_copia,
                                                    lista_especial,lista_nodos_especiales,contador_extra)

        if self.s_prints == 'eval':
            print('End of the processing')
            print(longest)
            # time.sleep(5)

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Final operations, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

        return longest, self.hw_perfo, hw_total_copia, lat_new_version_total, maximum_clock



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


def performance_evaluation_function_v2(mapping_list, hardware_graph, special_nodes, flag_debugging,
                                       name_file, name_file_perfo, s_prints, debug_info, dict_nodes_h,
                                       dict_nodes_a, hardware_graph_total, dict_info_h, dict_total_h, dict_info_a,
                                       debugging, graph_unroll, app_total, method_evaluation,app_graph):
    a = datetime.now()
    if s_prints == 'evalprint':
        print("ESTAMOS EN LA FUNCION DE EVALUACION DE DESEMPENO")
        print(hardware_graph_total.nodes)

    name_file = name_file




    time_slot_conteo = 0

    #####inicializacion del grafo (networkx)

    contador_instancias = 0
    bandera_falla_time_slots = False


    if s_prints == 'evalprint' or s_prints == 'debug':
        print("enter the function that transforms the list into a graph")
    if s_prints == 'debug' or s_prints == 'evalprint':
        print(mapping_list)
        print("we are going to print the info of the nodes ")
        print(dict_info_h)
        print("between dictionaries application nodes")
        print(dict_nodes_a)
        print("between dictionaries hardware nodes")
        print(dict_nodes_h)
        print("between dictionaries total nodes")
        print(dict_total_h)


    hw_total = nx.DiGraph()

    contador_instancias_ri = 0
    lista_remove_nodes = []
    lista_nodos_total = [[] for g in range(0, len(mapping_list))]
    lista_nodos = []
    # lista_nodos_nombres = []
    # lista_nombres_total = [[] for g in range(0, len(mapping_list))]
    contador_nodos = 0
    lista_nodos_definitivos = [[] for g in range(0, len(mapping_list))]


    config_vector_parallel = []
    configuration_sum = 0
    configuration_temporal  = []
    config_vector_sum = []

    # this is the worst clock of the entire hardware
    maximum_clock = dict_info_h['max_clk']

    cuenta_debug = 0
    ## we verify if the copy nodes have latency if not we put zero
    try:
        latencia_copy = dict_info_h['functions_res']['lat_copy']
    except:
        latencia_copy = 0
    lista_tasks_por_time_slot = []
    # lista_tasks_implementacion = []
    # in the follow loop we will obtain two graphs, one for the performance evaluation and another for the visualization
    # the idea for the first one is to create a similar graph of the unrolling one, but without the sensor and actuator
    # between time slots, and also without the mem nodes, the input edges will have the input latency plus the
    # computing latency of one pixel of each resource so this
    # will help us at the end to get a correct critical path. The other graph will only have the sensors and actuators
    # removed so it will help to create the implementation graph. For both graphs we will have weighted edges with the
    # value of the input latency. Another thing is that we obtain the configuration cost, for both parallel and
    # sequential methods
    lista_nodos_removidos_total = []
    lista_nodos_removidos = []
    # print("EL SDLKNSLDNFS",len(mapping_list))

    # print(f"el mapping list es {mapping_list}")

    # for tarea in app_total.nodes:
    #     print(f"la tarea {tarea} jjd {app_total.nodes[tarea]}")

    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Beginning of the performance evaluation, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        # print(
        #     f"The memory usage of the next list is {asizeof(self.next_list)} bytes, list of special nodes {asizeof(self.next_list_special_nodes)} bytes and time slot flags {asizeof(self.time_slot_list_01)} bytes ")
    a = datetime.now()
    nodos_source = obtencion_sources(hardware_graph_total)
    sources_aplicacion = obtencion_sources(app_graph)
    sources_aplicacion_total = obtencion_sources(app_total)
    sinks_aplicacion = obtencion_sinks(app_graph)
    sinks_hw_total = obtencion_sinks(hardware_graph_total)
    sinks_aplicacion_total = obtencion_sinks(app_total)
    nodos_hw = []
    for node in hardware_graph.nodes:
        nodos_hw.append(hardware_graph.nodes[node]['name'])


    for instancia in mapping_list:
        t0 = datetime.now()
        lista_nodos = []
        # lista_nodos_nombres = []
        if s_prints == 'evalprint' or s_prints == 'debug':
            print(f"la instancia a trabajar es {instancia}")
            print("iniciaremos el proceso")
        # creamos dos grafos, uno nos servira para la evaluacion el otro para la visualizacion


        # nodos_hw_total = []
        # for node in hardware_graph_total.nodes:
        #     nodos_hw_total.append(hardware_graph_total.nodes[node]['name'])

        if s_prints == 'evalprint' or s_prints == 'debug':
            print(" nodos hw", nodos_hw)

        for nodo in hardware_graph_total.nodes:

            if s_prints == 'evalprint' or s_prints == 'debug':
                print("todos los nodos del hardware graph")
                print(hardware_graph_total.nodes[nodo])
            if hardware_graph_total.nodes[nodo]['name'] in nodos_hw:
                # first we obtain the basic information to create a node, this node belongs to the hardware graph
                # with only the processing resources and the multiplexors
                if s_prints == 'evalprint' or s_prints == 'debug':
                    print("el nodo que estamos checando es ", nodo, hardware_graph_total.nodes[nodo]['name'])

                predecesores = hardware_graph_total.predecessors(nodo)
                sucesores = hardware_graph_total.successors(nodo)
                nombre_nodo = nodo + time_slot_conteo

                # print(f"EL NOMBRE DEL NODO ES {nombre_nodo}")
                if s_prints == 'evalprint':
                    print("el nombre que utilizaremos es ", nombre_nodo)
                lugar = None
                for p in hardware_graph.nodes:
                    if hardware_graph_total.nodes[nodo]['name'] == hardware_graph.nodes[p]['name']:
                        lugar = p
                        break
                # print(instancia[lugar])
                if instancia[lugar][0]:
                    # este nodo tiene asignada una operacion ya sea copy o una tarea
                    if instancia[lugar][1] != None:
                        lista_tasks_por_time_slot.append(instancia[lugar][1])
                    hw_total.add_node(nombre_nodo, map=instancia[lugar][0], task=    instancia[lugar][1],
                                      op=instancia[lugar][3], lat_input=instancia[lugar][8],
                                      lat_total=instancia[lugar][9], name=hardware_graph_total.nodes[nodo]['name'],
                                      s_info=instancia[lugar][10], a_info=instancia[lugar][11], weight=instancia[lugar][9])
                    # hw_salida.add_node(nombre_nodo, map=instancia[lugar][0], task=instancia[lugar][1],
                    #                   op=instancia[lugar][3], lat_input=instancia[lugar][8],
                    #                   lat_total=instancia[lugar][9], name=hardware_graph_total.nodes[nodo]['name'],
                    #                   s_info=instancia[lugar][10], a_info=instancia[lugar][11],weight=1)


                else:
                    #este nodo no tiene asignada ninguna operacion
                    hw_total.add_node(nombre_nodo, map=False, task=None,
                                      op=None, lat_input=0,
                                      lat_total=0, name=hardware_graph_total.nodes[nodo]['name'], s_info=None,
                                      a_info=None,weight=1)
                    # hw_salida.add_node(nombre_nodo, map=False, task=None,
                    #                   op=None, lat_input=0,
                    #                   lat_total=0, name=hardware_graph_total.nodes[nodo]['name'], s_info=None,
                    #                   a_info=None,weight=1)
                lista_nodos.append(nombre_nodo)
                # lista_nodos_nombres.append(nodo)
                if s_prints == 'evalprint':
                    print(instancia[lugar])
                for pred in predecesores:
                    if instancia[lugar][2] == 'copy':
                        hw_total.add_edge(pred + time_slot_conteo, nombre_nodo , weight=latencia_copy)
                        # hw_salida.add_edge(pred + time_slot_conteo, nombre_nodo, weight=latencia_copy)
                    else:
                        hw_total.add_edge(pred + time_slot_conteo, nombre_nodo, weight=instancia[lugar][8])
                        # hw_salida.add_edge(pred + time_slot_conteo, nombre_nodo, weight=instancia[lugar][8])



                for suc in sucesores:
                    hw_total.add_edge(nombre_nodo, suc + time_slot_conteo)
                    # hw_salida.add_edge(nombre_nodo, suc + time_slot_conteo)

                    # if instancia[lugar][2] == 'copy':
                    #     hw_total.add_edge(nombre_nodo, suc + time_slot_conteo, weight=latencia_copy)
                    #     hw_salida.add_edge(nombre_nodo, suc + time_slot_conteo, weight=latencia_copy)
                    # else:
                    #     hw_total.add_edge(nombre_nodo, suc + time_slot_conteo, weight=instancia[lugar][8])
                    #     hw_salida.add_edge(nombre_nodo, suc + time_slot_conteo, weight=instancia[lugar][8])

                 ###########################################
                #now we obtain the configuration cost of this node
                function_config = dict_total_h[lugar]['fun_lat']['formula']
                # print("the configuration cost formula is ", function_config)
                ###aqui haremos conexion con las variables
                for variable in dict_total_h[nodo]['fun_lat']:
                    if variable != 'formula':
                        globals()[variable] = dict_total_h[nodo]['fun_lat'][variable]
                        break


                if s_prints == 'evalprint': print("funcion de configuracion", function_config)

                if function_config != None:
                    for data in dict_info_h['functions_cfg']:
                        # print(data,function_config)
                        if s_prints == 'evalprint':
                            print("extracto del dict_info", data, function_config)
                            print(len(data), (function_config))
                            # print(dict_info_h)
                            # print(dict_total_h)
                            print("funcion de configuracion", function_config)
                        if data == function_config:
                            if s_prints == 'evalprint': print("entramos")
                            formula_config = dict_info_h['functions_cfg'][data]
                            # print(formula_config)
                            break
                else:
                    formula_config = 0
                # print("la formula config", formula_config)
                if s_prints == 'evalprint':
                    print(function_config)
                    # print("la formula es ", formula_config)
                    # print("los parametros son ", cfg_cost_par,cfg_cost_op)


                # print(instancia[lugar])

                if contador_instancias == 0:
                    try:
                        parameters = len(instancia[lugar][5])
                    except:
                        parameters = 1
                    operations = 1
                    # if s_prints == 'basic':
                    # print("vamos a evaluar la funcion con los siguientes numeros", parameters, operations)
                    if isinstance(formula_config, str):
                        latencia_config = int(eval(formula_config))
                    else:
                        latencia_config = formula_config

                    # print("la latencia de configuracion",latencia_config)
                    configuration_sum = configuration_sum + latencia_config
                    configuration_temporal.append(latencia_config)


                else:
                    # print("test de configuracion")
                    # # print(mapping_list[contador_instancias - 1])
                    # # print("entre test")
                    # print(mapping_list[contador_instancias - 1][lugar])
                    # print(instancia[lugar])
                    try:
                        if mapping_list[contador_instancias - 1][lugar][0] != instancia[lugar][0]:
                            if instancia[lugar][0]:
                                parameters = len(instancia[lugar][5])
                            elif mapping_list[contador_instancias - 1][lugar][0]:
                                parameters = len(mapping_list[contador_instancias - 1][lugar][5])
                        else:
                            if instancia[lugar][0]:
                                parameters_1 = mapping_list[contador_instancias - 1][lugar][5]
                                parameters_2 = instancia[lugar][5]
                                if parameters_1 != parameters_2:
                                    parameters = len(parameters_2)
                                else:
                                    parameters = 0
                            else:
                                parameters = 0
                    except:
                            parameters = 1

                    try:
                        operations_1 = mapping_list[contador_instancias - 1][lugar][3]
                        operations_2 = instancia[lugar][3]

                        if operations_1 != operations_2:
                            operations = 1
                        else:
                            operations = 0
                    except:
                        operations = 0

                    if isinstance(formula_config, str):
                        latencia_config = int(eval(formula_config))
                    else:
                        latencia_config = formula_config


                    # print("dfsdfs", parameters ,operations)
                    configuration_sum = configuration_sum + latencia_config
                    configuration_temporal.append(latencia_config)
            else:
                # el nodo no esta en la lista de recursos de procesamiento o multiplexores,
                # por lo tanto debe de ser una interfaz o memoria

                # print(nodo, hardware_graph_total.nodes[nodo])
                predecesores = hardware_graph_total.predecessors(nodo)
                done = True
                info_s = []
                # nodo_temporal = nodo
                #
                if nodo not in nodos_source:
                    source_nodo_temporal = source_node_from_any_node(hardware_graph_total, nodos_source, nodo)
                else:
                    source_nodo_temporal = None
                # copia_nodos_source = nodos_source.copy()
                # for nodo_s in nodos_source:
                #     print(simple_paths_from_two_nodes(hardware_graph_total,nodo_s,nodo))

                if source_nodo_temporal != None:
                    path = simple_paths_from_two_nodes(hardware_graph_total, source_nodo_temporal, nodo)
                    # print(path)
                    for unique_path in path:
                        for nodo_in_path in unique_path:
                            try:
                                # print(instancia[nodo_in_path])
                                if instancia[nodo_in_path][10] != -1 and instancia[nodo_in_path][10] != 0:
                                    info_s = instancia[nodo_in_path][10]
                                    break
                            except:
                                pass
                # source_nodo_temporal = source_from_any_node(hardware_graph_total,nodo)

                # print(source_nodo_temporal)
                # for prede_res in predecesores:
                #     if hardware_graph_total.nodes[prede_res]['name'] in nodos_hw:
                # print(info_s)
                if info_s:
                    # print(f"info_s    {info_s}")
                    resolution = [info_s[1], info_s[2]]
                else:
                    task_source = obtencion_sources(app_total)
                    source_dummy = task_source.pop()

                    resolution = [dict_info_a[source_dummy]['param']['height'],
                                  dict_info_a[source_dummy]['param']['width']]
                    # print(f"la resolucion es {resolution} the source es {source_dummy} ")
                    # height =
                    # width =

                    # print(int(hardware_graph_total.nodes[nodo]['lat']) * resolution[0] *
                    #                         resolution[1])
                sucesores = hardware_graph_total.successors(nodo)
                nombre_nodo = nodo + time_slot_conteo
                # print(f"EL NOMBRE DEL NODO ES {nombre_nodo} y su operacion es {hardware_graph_total.nodes[nodo]['op']} y su nombre {hardware_graph_total.nodes[nodo]['name']}")
                if s_prints == 'evalprint':
                    print("el nombre de aqui es diferente ", nombre_nodo,
                          hardware_graph_total.nodes[nodo]['op'], hardware_graph_total.nodes[nodo])
                # print(hardware_graph_total.nodes[nodo]['name'], list(hardware_graph_total.predecessors(nodo)))
                # print(hardware_graph_total.nodes[])
                operacion = None
                if hardware_graph_total.nodes[nodo]['op'] == 'ri':
                    operacion = hardware_graph_total.nodes[nodo]['op']

                    # if data_performance:
                    #     print(operacion,"sdfsdfds")
                hw_total.add_node(nombre_nodo, map=True, task=None,
                                  op=hardware_graph_total.nodes[nodo]['op'],
                                  lat_input=hardware_graph_total.nodes[nodo]['lat'],
                                  lat_total=int(hardware_graph_total.nodes[nodo]['lat']) * resolution[0] *
                                            resolution[1], name=hardware_graph_total.nodes[nodo]['name'],
                                  s_info=resolution, operacion=operacion)
                # hw_salida.add_node(nombre_nodo, map=True, task=None,
                #                   op=hardware_graph_total.nodes[nodo]['op'],
                #                   lat_input=hardware_graph_total.nodes[nodo]['lat'],
                #                   lat_total=int(hardware_graph_total.nodes[nodo]['lat']) * resolution[0] *
                #                             resolution[1], name=hardware_graph_total.nodes[nodo]['name'],
                #                   s_info=resolution, operacion=operacion)
                lista_nodos.append(nombre_nodo)
                # lista_nodos_nombres.append(nodo)
                for pred in predecesores:
                    hw_total.add_edge(pred + time_slot_conteo,  nombre_nodo, weight=hardware_graph_total.nodes[nodo]['lat'])
                    # hw_salida.add_edge(pred + time_slot_conteo, nombre_nodo, weight=hardware_graph_total.nodes[nodo]['lat'])
                    # print(hardware_graph_total.nodes[pred])
                # print("la latencia va para el peso del edge",hardware_graph_total.nodes[nodo]['lat'],hardware_graph_total.nodes[nodo]['op'])
                for suc in sucesores:
                    hw_total.add_edge(nombre_nodo, suc + time_slot_conteo)
                    # hw_salida.add_edge(nombre_nodo, suc + time_slot_conteo)



                # print("memoria de ondof",hardware_graph_total.nodes[nodo]['op'])
                if hardware_graph_total.nodes[nodo]['op'] == 'rw' or hardware_graph_total.nodes[nodo]['op'] == 'rd':
                    configuration_sum = configuration_sum + 1
                    configuration_temporal.append(1)

        if debug_info == 'remove' or debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - t0
            print(
                f"First stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

        t1 = datetime.now()
        # aqui se procesa las cosas por time slot, porque ya pasamos por el for
        # donde se atraviesa todos los recursos del grafo de arquitectura

        # lista_tasks_implementacion.append(lista_tasks_por_time_slot)


        # time_slot_conteo = time_slot_conteo + len(hardware_graph_total.nodes)
        # #     contador_instancias_ri += 1

        # for nodo in hw_total.nodes:
        #     print(nodo,hw_total.nodes[nodo])
        lista_nodos_total[contador_instancias_ri] = lista_nodos
        # lista_nombres_total[contador_instancias_ri] = lista_nodos_nombres

        # cuenta_debug = cuenta_debug + 1
        # name_debug = 'test' + str(cuenta_debug)
        # lista_vacia = []
        # Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', name_debug, [], 'red', 'black',
        #                                               'circle')
        # Graph_visual_00.f.render(view=False)
        # Graph_visual_00.f.render(view=True, format='pdf')

        # if s_prints == 'evalprint':
        #     print(f"LA LISTA DE TAREAS CREO AUE POR TIME SLOT ES {lista_tasks_por_time_slot} y la total es {lista_tasks_implementacion} y el contado isntancias {contador_instancias_ri}")

        # depuraremos el grafo eliminando los nodos de interfaz y el nodo de memoria
        lista_nodos_removidos = []
        # iniciaremos con el nodo de memoria

        bandera_no_remover = False
        bandera_no_remover_sensor = False
        bandera_no_remover_actuator = False
        for tarea_en_lista in lista_tasks_por_time_slot:
            if contador_instancias_ri == 0:
                if s_prints == 'evalprint':
                    print("PRIMER TIME SLOT")
                suc = app_total.successors(tarea_en_lista)
                for s in suc:
                    # print(app_total.nodes[s])
                    if app_total.nodes[s]['op'] == 'interface':
                        bandera_no_remover_actuator = True
                        bandera_no_remover_sensor = True
                        bandera_no_remover = True
                        break
                break
            else:
                if s_prints == 'evalprint':
                    print("TEST DE SUCESORES - ACTUADORES")
                suc = app_total.successors(tarea_en_lista)

                for s in suc:
                    if app_total.nodes[s]['op'] == 'interface':
                        bandera_no_remover = True
                        bandera_no_remover_actuator = True
                        break
                if s_prints == 'evalprint':
                    print("TEST DE PREDECESORES - SENSORES")
                pre = app_total.predecessors(tarea_en_lista)
                for p in pre:
                    if app_total.nodes[p]['op'] == 'interface':
                        bandera_no_remover_sensor = True
                        bandera_no_remover = True
                        break
                break

        # print(f"la bandera es {bandera_no_remover} la lista de {lista_tasks_por_time_slot}")

        if s_prints == 'evalprint':
            print(f"BUENO LA BANDERA DE REMOVER NODOS ES {bandera_no_remover} de forma individual {bandera_no_remover_sensor} y {bandera_no_remover_actuator}")
        # hw_total_copia.nodes[actuator_dg]['assign']
        #

        if not bandera_no_remover:
            hw_buffer = hw_total.copy()
            for nodo in hw_buffer.nodes:
                if hw_total.nodes[nodo]['op'] == 'rm':
                    predecesores = list(hw_total.predecessors(nodo))
                    sucesores = list(hw_total.successors(nodo))
                    lista_sin_input_edge = []
                    lista_sin_output_edge = []
                    lista_normal_pre = []
                    lista_normal_suc = []
                    for pre in predecesores:
                        if hw_total.in_degree(pre) == 0:
                            lista_sin_input_edge.append(pre)
                        else:
                            lista_normal_pre.append(pre)
                    for suc in sucesores:
                        if hw_total.out_degree(suc) == 0:
                            lista_sin_output_edge.append(suc)
                        else:
                            lista_normal_suc.append(suc)
                    hw_total.remove_node(nodo)
                    contador_nodos = contador_nodos + 1
                    lista_nodos_removidos.append(nodo)
                    for el01 in lista_sin_input_edge:
                        for el02 in lista_normal_suc:
                            hw_total.add_edge(el01, el02)
                    for el01 in lista_sin_output_edge:
                        for el02 in lista_normal_pre:
                            hw_total.add_edge(el02, el01)

                # if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.out_degree(
                #         n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                #     hw_total.remove_node(n)
                #     contador_nodos = contador_nodos + 1
                #     lista_nodos_removidos.append(n)
                #
                #
                # elif hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.in_degree(
                #         n) == 0 and contador_instancias_ri != 0:
                #     if s_prints == 'evalprint':
                #         print("PORQUE NO ENTRA AQUI")
                #     if n not in hardware_graph_total.nodes:
                #         hw_total.remove_node(n)
                #         contador_nodos = contador_nodos + 1
                #         lista_nodos_removidos.append(n)

            #########################################################
            # continuaremos con los nodos actuator si existen antes del ultimo time slot y los sensores del time slot mas alla del primer slot
            hw_buffer = hw_total.copy()
            if s_prints == 'evalprint':
                print("VAMOS A CONTAR")
            for n in hw_buffer.nodes:
                if s_prints == 'evalprint':
                    print("ALGO RARO ", n, hw_total.nodes[n])
                if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.out_degree(
                        n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                    hw_total.remove_node(n)
                    contador_nodos = contador_nodos + 1
                    lista_nodos_removidos.append(n)


                elif hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.in_degree(
                        n) == 0 and contador_instancias_ri != 0:
                    if s_prints == 'evalprint':
                        print("PORQUE NO ENTRA AQUI")
                    if n not in hardware_graph_total.nodes:
                        hw_total.remove_node(n)
                        contador_nodos = contador_nodos + 1
                        lista_nodos_removidos.append(n)

            # hw_buffer = hw_salida.copy()
            # if s_prints == 'evalprint':
            #     print("VAMOS A CONTAR")
            # for n in hw_buffer:
            #     if s_prints == 'evalprint':
            #         print("ALGO RARO ", n, hw_salida.nodes[n])
            #     if hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.out_degree(
            #             n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
            #         hw_salida.remove_node(n)
            #         contador_nodos = contador_nodos + 1
            #         lista_nodos_removidos.append(n)
            #
            #
            #     elif hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.in_degree(
            #             n) == 0 and contador_instancias_ri != 0:
            #         if s_prints == 'evalprint':
            #             print("PORQUE NO ENTRA AQUI")
            #         if n not in hardware_graph_total.nodes:
            #             hw_salida.remove_node(n)
            #             contador_nodos = contador_nodos + 1
            #             lista_nodos_removidos.append(n)

        else:
            # lo unico que se tiene que hacer es asignar los datos a loa sensores
            for tarea_en_lista in lista_tasks_por_time_slot:
                if s_prints == 'evalprint':
                    print(f"tarea es {tarea_en_lista}, {sources_aplicacion} yyyy {sinks_aplicacion} ")
                ####ahora chequemos el sensor
                if bandera_no_remover_sensor :
                    if tarea_en_lista in sources_aplicacion:
                        lugar_en_grafo_sensor = None
                        for nodo_en_grafo in hw_total.nodes:
                            if s_prints == 'evalprint':
                                print(f"nodo es {nodo_en_grafo} y sus datos son {hw_total.nodes[nodo_en_grafo]}")
                            if tarea_en_lista == hw_total.nodes[nodo_en_grafo]['task']:
                                lugar_en_grafo_sensor = nodo_en_grafo
                        sensor_nodo_arq = source_node_from_any_node(hw_total,obtencion_sources(hw_total),lugar_en_grafo_sensor)
                        if tarea_en_lista in   sources_aplicacion_total:#   obtencion_sources(app_total):
                            sensor_nodo_app = tarea_en_lista
                        else:
                            sensor_nodo_app = source_node_from_any_node(app_total,sources_aplicacion_total,tarea_en_lista)
                        # print(f"datos hw {hw_total.nodes[sensor_nodo_arq]} datos de la aplicacion {app_total.nodes[sensor_nodo_app]} y el numero es {lugar_en_grafo_sensor}")
                        hw_total.nodes[sensor_nodo_arq]['assign'] = app_total.nodes[sensor_nodo_app]['name']


                else:
                    #################################################################
                    hw_buffer = hw_total.copy()
                    for nodo in hw_buffer.nodes:
                        if hw_total.nodes[nodo]['op'] == 'rm':
                            predecesores = list(hw_total.predecessors(nodo))
                            sucesores = list(hw_total.successors(nodo))
                            lista_sin_input_edge = []
                            lista_sin_output_edge = []
                            lista_normal_pre = []
                            lista_normal_suc = []
                            for pre in predecesores:
                                if hw_total.in_degree(pre) == 0:
                                    lista_sin_input_edge.append(pre)
                                else:
                                    lista_normal_pre.append(pre)
                            for suc in sucesores:
                                if hw_total.out_degree(suc) == 0:
                                    lista_sin_output_edge.append(suc)
                                else:
                                    lista_normal_suc.append(suc)
                            hw_total.remove_node(nodo)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(nodo)
                            for el01 in lista_sin_input_edge:
                                for el02 in lista_normal_suc:
                                    hw_total.add_edge(el01, el02)
                            for el01 in lista_sin_output_edge:
                                for el02 in lista_normal_pre:
                                    hw_total.add_edge(el02, el01)

                    # continuaremos con los nodos actuator si existen antes del ultimo time slot y los sensores del time slot mas alla del primer slot
                    hw_buffer = hw_total.subgraph(lista_tasks_por_time_slot).copy()
                    if s_prints == 'evalprint':
                        print("VAMOS A CONTAR")
                    for n in hw_buffer.nodes:
                        # if s_prints == 'evalprint':
                        #     print("ALGO RARO ", n, hw_total.nodes[n])
                        # if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.out_degree(
                        #         n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                        #     hw_total.remove_node(n)
                        #     contador_nodos = contador_nodos + 1
                        #     lista_nodos_removidos.append(n)


                        if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.in_degree(
                                n) == 0 and contador_instancias_ri != 0:
                            # if s_prints == 'evalprint':
                            #     print("PORQUE NO ENTRA AQUI")
                            if n not in hardware_graph_total.nodes:
                                hw_total.remove_node(n)
                                contador_nodos = contador_nodos + 1
                                lista_nodos_removidos.append(n)

                    # hw_buffer = hw_salida.copy()
                    # if s_prints == 'evalprint':
                    #     print("VAMOS A CONTAR")
                    # for n in hw_buffer:
                    #     # if s_prints == 'evalprint':
                    #     #     print("ALGO RARO ", n, hw_salida.nodes[n])
                    #     # if hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.out_degree(
                    #     #         n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                    #     #     hw_salida.remove_node(n)
                    #     #     contador_nodos = contador_nodos + 1
                    #     #     lista_nodos_removidos.append(n)
                    #
                    #
                    #     if hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.in_degree(
                    #             n) == 0 and contador_instancias_ri != 0:
                    #         # if s_prints == 'evalprint':
                    #         #     print("PORQUE NO ENTRA AQUI")
                    #         if n not in hardware_graph_total.nodes:
                    #             hw_salida.remove_node(n)
                    #             contador_nodos = contador_nodos + 1
                    #             lista_nodos_removidos.append(n)




                        #################################################






                if bandera_no_remover_actuator :
                    if tarea_en_lista in sinks_aplicacion:
                        lugar_en_grafo_sensor = None
                        for nodo_en_grafo in hw_total.nodes:
                            if tarea_en_lista == hw_total.nodes[nodo_en_grafo]['task']:
                                lugar_en_grafo_sensor = nodo_en_grafo
                        actuator_nodo_arq = sink_node_from_any_node(hw_total,obtencion_sinks(hw_total),lugar_en_grafo_sensor)
                        actuator_nodo_app = sink_node_from_any_node(app_total,sinks_aplicacion_total,tarea_en_lista)
                        hw_total.nodes[actuator_nodo_arq]['assign'] = app_total.nodes[actuator_nodo_app]['name']
                else:
                    hw_buffer = hw_total.copy()
                    for nodo in hw_buffer.nodes:
                        if hw_total.nodes[nodo]['op'] == 'rm':
                            predecesores = list(hw_total.predecessors(nodo))
                            sucesores = list(hw_total.successors(nodo))
                            lista_sin_input_edge = []
                            lista_sin_output_edge = []
                            lista_normal_pre = []
                            lista_normal_suc = []
                            for pre in predecesores:
                                if hw_total.in_degree(pre) == 0:
                                    lista_sin_input_edge.append(pre)
                                else:
                                    lista_normal_pre.append(pre)
                            for suc in sucesores:
                                if hw_total.out_degree(suc) == 0:
                                    lista_sin_output_edge.append(suc)
                                else:
                                    lista_normal_suc.append(suc)
                            hw_total.remove_node(nodo)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(nodo)
                            for el01 in lista_sin_input_edge:
                                for el02 in lista_normal_suc:
                                    hw_total.add_edge(el01, el02)
                            for el01 in lista_sin_output_edge:
                                for el02 in lista_normal_pre:
                                    hw_total.add_edge(el02, el01)

                    # continuaremos con los nodos actuator si existen antes del ultimo time slot y los sensores del time slot mas alla del primer slot
                    hw_buffer = hw_total.subgraph(lista_tasks_por_time_slot).copy()
                    if s_prints == 'evalprint':
                        print("VAMOS A CONTAR")
                    for n in hw_buffer.nodes:
                        if s_prints == 'evalprint':
                            print("ALGO RARO ", n, hw_total.nodes[n])
                        if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.out_degree(
                                n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                            hw_total.remove_node(n)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(n)


                        elif hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.in_degree(
                                n) == 0 and contador_instancias_ri != 0:
                            if s_prints == 'evalprint':
                                print("PORQUE NO ENTRA AQUI")
                            if n not in hardware_graph_total.nodes:
                                hw_total.remove_node(n)
                                contador_nodos = contador_nodos + 1
                                lista_nodos_removidos.append(n)

                    # hw_buffer = hw_salida.copy()
                    # if s_prints == 'evalprint':
                    #     print("VAMOS A CONTAR")
                    # for n in hw_buffer:
                    #     if s_prints == 'evalprint':
                    #         print("ALGO RARO ", n, hw_salida.nodes[n])
                    #     if hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.out_degree(
                    #             n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                    #         hw_salida.remove_node(n)
                    #         contador_nodos = contador_nodos + 1
                    #         lista_nodos_removidos.append(n)
                    #
                    #
                    #     elif hw_salida.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_salida.in_degree(
                    #             n) == 0 and contador_instancias_ri != 0:
                    #         if s_prints == 'evalprint':
                    #             print("PORQUE NO ENTRA AQUI")
                    #         if n not in hardware_graph_total.nodes:
                    #             hw_salida.remove_node(n)
                    #             contador_nodos = contador_nodos + 1
                    #             lista_nodos_removidos.append(n)

        if debug_info == 'remove' or debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - t1
            print(
                f"Second stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        t2 = datetime.now()
        ##########ultimo paso, remover los nodos de interface que no tengan nada asignado
        # continuaremos con los nodos actuator si existen antes del ultimo time slot y los sensores del time slot mas alla del primer slot

        hw_buffer = hw_total.copy()
        if s_prints == 'evalprint':
            print("VAMOS A CONTAR 77777")
        for n in hw_buffer.nodes:
            try:
                if hw_total.nodes[n]['op'] == 'ri':
                    # print("usduonfsODNSNDF")
                    test = hw_total.nodes[n]['assign']
            except:
                    # print("usduonfsSSSSSSSSSODNSNDF")
                    if hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.out_degree(
                            n) == 0 and contador_instancias_ri < len(mapping_list) - 1:
                        if s_prints == 'evalprint':
                            print("ALGO RARO   tetetet ", n, hw_total.nodes[n])
                        hw_total.remove_node(n)
                        contador_nodos = contador_nodos + 1
                        lista_nodos_removidos.append(n)


                    elif hw_total.nodes[n]['op'] == 'ri' and len(mapping_list) > 1 and hw_total.in_degree(
                            n) == 0 and contador_instancias_ri != 0:

                        if n not in hardware_graph_total.nodes:
                            if s_prints == 'evalprint':
                                print("PORQUE NO ENTRA AQUI")
                            hw_total.remove_node(n)
                            contador_nodos = contador_nodos + 1
                            lista_nodos_removidos.append(n)

        ######################"


        lista_tasks_por_time_slot = []

        # cuenta_debug = cuenta_debug + 1
        # name_debug = 'testpost' + str(cuenta_debug)
        # lista_vacia = []
        # Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', name_debug, [], 'red', 'black',
        #                                               'circle')
        # Graph_visual_00.f.render(view=False)
        # Graph_visual_00.f.render(view=True, format='pdf')


        lista_nodos_definitivos[contador_instancias_ri] = list(set(lista_nodos)-set(lista_nodos_removidos))
        lista_nodos_removidos_total = lista_nodos_removidos + lista_nodos_removidos_total
        config_vector_parallel.append(configuration_temporal)
        config_vector_sum.append(configuration_sum)
        configuration_sum = 0
        configuration_temporal = []

        time_slot_conteo = time_slot_conteo + len(hardware_graph_total.nodes) + 1
        contador_instancias = contador_instancias + 1
        contador_instancias_ri += 1
        if debug_info == 'remove' or debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - t2
            print(
                f"Third stage of the building of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    # for n  in hw_total.nodes:
    #     print("luego de la generacion",n,hw_total.nodes[n])

    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Build of the basic structure of the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    if s_prints == 'evalprint':
        lista_vacia = []
        Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', 'testtest', [], 'red', 'black',
                                                      'circle')
        Graph_visual_00.f.render(view=False)
        Graph_visual_00.f.render(view=True, format='pdf')

    a = datetime.now()

    # print("lista removidos q", lista_nodos_removidos_total)
    vector_sensor_dg = []
    vector_actuator_dg = []
    for nodo in hw_total.nodes:
        if hw_total.nodes[nodo]['op'] == 'ri' and hw_total.in_degree(nodo) == 0:
            vector_sensor_dg.append(nodo)
        if hw_total.nodes[nodo]['op'] == 'ri' and hw_total.out_degree(nodo) == 0:
            vector_actuator_dg.append(nodo)

    # lista_nodos_removidos = lista_nodos_removidos_total
    # print("latencias", config_vector_parallel)
    # print(config_vector_sum)
    # for nodo in hw_total.nodes:
    #     print(nodo, hw_total.nodes[nodo])

    # for nnnn in hw_total.nodes:
    #     print("jdsjfsd",nnnn, hw_total.nodes[nnnn])
    # lista_nodos_numeros = []
    # for nodo in hw_total.nodes:
    #     lista_nodos_numeros.append(nodo)
    #
    # maximo_numero = max(lista_nodos_numeros)
    maximo_numero = max(list(hw_total.nodes))

    contador_nodos_especiales = maximo_numero + 1


    # contador_nodos_especiales = len(hw_total.nodes) + contador_nodos
    # contador_nodos_especiales_total = lista_sin_input_edge(hw_salida.nodes) + contador_nodos
    time_slot_conteo = 0
    if s_prints == 'evalprint':
    # if True:
        print("NODOS ESPECIALES")
        print(special_nodes, contador_nodos_especiales)
        # print(lista_nombres_total,lista_nodos_total)
        print(lista_nodos_definitivos)
        print(f"la longitud de la lista {len(lista_nodos_definitivos)}")
        for nodo in hw_total.nodes:
            print(nodo, hw_total.nodes[nodo])
        print("TERMINO DE LISTAS ANTES DE NODOS ESPECIALES")
    # sinks = obtencion_sinks(hardware_graph_total)
    sinks = sinks_hw_total
    # print("vamos a checar que es cada uno de los sinks")
    # for s in sinks:
    #     print(s, hardware_graph_total.nodes[s])
    # input("finalizacion de algo")
    hardware_graph_total_copy = hardware_graph_total.copy()
    if lista_nodos_removidos:
        for el in lista_nodos_removidos:
            if el in sinks:
                sinks.remove(el)
                hardware_graph_total_copy.remove(el)
                bandera_done = True
                while bandera_done:
                    prede = list(hardware_graph_total.predecessors(el))
                    sinks = sinks + prede
    # print("lista de nodos removidos",lista_nodos_removidos)
    # sources = obtencion_sources(hardware_graph_total)
    sources = nodos_source
    # sinks = obtencion_sinks(hardware_graph_total)
    nodos_por_time_slot = len(hardware_graph_total.nodes)
    lista_nodos_especiales = []
    # print(special_nodes,sinks)
    if s_prints == 'evalprint':
        print("SE IMPRIMIRAN NODOS ESPECIALES", special_nodes)
    # print("test de algo")
    # print(special_nodes)
    # print(mapping_list)
    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Miscellaneous operations evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    a = datetime.now()
    if special_nodes:
        # print(special_nodes)
        # the special nodes will connect two time slots, this will mean that there is some data that needs to be
        # tranfered to a following time slot to be processed. when we write the first time slot we mean the source time
        # slot and the second time slot is the sink time slot or the other way around
        lista_nodos_creados = []
        for pareja in special_nodes:
            # print(pareja,special_nodes)
            if s_prints == 'evalprint':
                print("pareja", pareja)
            if pareja[0]:
                if s_prints == 'evalprint':
                    print("tenemos un nodo especial doble")
                lugar_pareja_1 = None
                lugar_pareja_2 = None
                # print(lista_nodos_definitivos, len(lista_nodos_definitivos))
                if s_prints == 'evalprint':
                    print("IBIJDSFSF")
                    print(lista_nodos_definitivos[pareja[3] - 1])

                grafo_01 = hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1])
                grafo_02 = hw_total.subgraph(lista_nodos_definitivos[pareja[3]])
                for nodo in grafo_01.nodes:
                    if grafo_01.nodes[nodo]['name'] == hardware_graph.nodes[pareja[1]]['name']:
                        lugar_pareja_1 = nodo ####sink of the first time slot
                for nodo in grafo_02.nodes:
                    if grafo_02.nodes[nodo]['name'] == hardware_graph.nodes[pareja[2]]['name']:
                        lugar_pareja_2 = nodo ####source of the second time slot
                if s_prints == 'evalprint':
                    print("lugares ", lugar_pareja_1,lugar_pareja_2)
                # tomamos el lado donde el nodo especial tiene que ser un sink
                # nombre_busqueda = pareja[1]  + nodos_por_time_slot*(pareja[3] - 1)

                # print("el nombre del nodo es",nombre_busqueda)

                # print("los sinks son ",pareja)
                lista_sinks_rw = []
                for s in obtencion_sinks(grafo_01):
                    if grafo_01.nodes[s]['op'] == 'rw':
                        lista_sinks_rw.append(s)

                if lugar_pareja_1 in lista_sinks_rw:
                    sink = lugar_pareja_1
                else:
                    sink = sink_node_from_any_node(hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1]),
                                                   lista_sinks_rw,
                                                   lugar_pareja_1)

                # if lugar_pareja_1 in obtencion_sinks(hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1])):
                #     sink = lugar_pareja_1
                # else:
                #     sink = sink_node_from_any_node(hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1]),
                #                                obtencion_sinks(hw_total.subgraph(lista_nodos_definitivos[pareja[3] - 1])),
                #                                lugar_pareja_1)

                # sink = sink_node_from_any_node(hw_total,obtencion_sinks(hw_total),lugar_pareja_1)
                # print("el sink es ", sink)
                # if sink in lista_nodos_creados:
                #     sink = list(hw_total.predecessors(sink))
                #     sink = sink[0]
                if s_prints == 'evalprint':
                    print("EL NOMBRE DEL SINK ES ", sink)
                    print(lista_sinks_rw)
                    # input("test")
                nombre_busqueda = sink # + nodos_por_time_slot * (pareja[3] - 1)
                # print(nombre_busqueda,contador_nodos_especiales)
                # # if nombre_busqueda in sinks:
                # #     sink = nombre_busqueda
                # # else:
                # #     sink = sink_node_from_any_node(hw_total,obtencion_sinks(hw_total), [nombre_busqueda])
                # print("adicion 1", contador_nodos_especiales,nombre_busqueda)
                if nombre_busqueda != None:
                    if s_prints == 'evalprint':
                        print("SE CREARA UN NODO ESPECIAL SINK")
                    hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                      name='sp')
                    hw_total.add_edge(nombre_busqueda, contador_nodos_especiales)

                    # print(hw_total.nodes[contador_nodos_especiales])
                    #
                    pareja_append = [contador_nodos_especiales, pareja[3] - 1, sink, 'suc']
                    lista_nodos_especiales.append(pareja_append)
                    lista_nodos_creados.append(contador_nodos_especiales)
                    contador_nodos_especiales = contador_nodos_especiales + 1

                # ahora anexaremos el nodo que debe de ser source
                # print(nombre_busqueda)
                # nombre_busqueda = pareja[2] + nodos_por_time_slot * (pareja[3])
                if flag_debugging:
                    for er in hw_total:
                        print("test", er, hw_total.nodes[er])
                nombre_busqueda = lugar_pareja_2 + nodos_por_time_slot * (pareja[3])
                if flag_debugging:
                    print(nombre_busqueda,obtencion_sources(hw_total))
                # for bla in hw_total.nodes:
                #     print("interno ", bla,hw_total.nodes[bla])
                if lugar_pareja_2 in obtencion_sources(hw_total.subgraph(lista_nodos_definitivos[pareja[3]])):
                    source = lugar_pareja_2
                else:
                    source = source_node_from_any_node(hw_total.subgraph(lista_nodos_definitivos[pareja[3] ]),
                                                   obtencion_sources(hw_total.subgraph(lista_nodos_definitivos[pareja[3]])),
                                                   [lugar_pareja_2])

                # source = source_node_from_any_node(hw_total,obtencion_sources(hw_total), [nombre_busqueda])
                if flag_debugging:
                    print(source)
                # if source in lista_nodos_creados:
                #     source = list(hw_total.successors(source))
                #     source = source[0]
                if s_prints == 'evalprint':
                    print("EL NOMBRE DEL SOURCE ES ", source)
                if flag_debugging:
                    print("el source es",source)
                if source != None:
                    if flag_debugging:
                        print("adicion 2 ",contador_nodos_especiales,source,nombre_busqueda,lugar_pareja_2,nodos_por_time_slot)
                    if s_prints == 'evalprint':
                        print("SE CREARA UN NODO ESPECIAL SOURCE")
                    hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                      name='sp')
                    hw_total.add_edge(contador_nodos_especiales, source)

                    pareja_append = [contador_nodos_especiales, pareja[3], source, 'pre']
                    lista_nodos_especiales.append(pareja_append)
                    lista_nodos_creados.append(contador_nodos_especiales)
                    contador_nodos_especiales = contador_nodos_especiales + 1


            else:
                # pass
                # print("NODO DE RECOMPUTO",pareja)
                # print(lista_nodos_definitivos)
                # print(pareja)
                try:
                    grafo_02 = hw_total.subgraph(lista_nodos_definitivos[pareja[3]])

                    for nodo in grafo_02.nodes:
                        if grafo_02.nodes[nodo]['name'] == hardware_graph.nodes[pareja[1]]['name']:
                            lugar_pareja_1 = nodo ####sink of the first time slot
                    for nodo in grafo_02.nodes:
                        if grafo_02.nodes[nodo]['name'] == hardware_graph.nodes[pareja[2]]['name']:
                            lugar_pareja_2 = nodo ####source of the second time slot
                    # print(lugar_pareja_1,lugar_pareja_2)
                    # print("vamos a checar algo")
                    # grafo_prueba = hw_total.subgraph(lista_nodos_definitivos[pareja[3]])
                    lista_sinks_rw = []
                    for s in obtencion_sinks(grafo_02):
                        if grafo_02.nodes[s]['op'] == 'rw':
                            lista_sinks_rw.append(s)
                        elif grafo_02.nodes[s]['op'] == 'ri':
                            prede_ri = list(grafo_02.predecessors(s))
                            done = True
                            while done:
                                prede_ri_buffer = prede_ri.pop()
                                if grafo_02.nodes[prede_ri_buffer]['op'] == 'rw':
                                    lista_sinks_rw.append(prede_ri_buffer)
                                    done = False
                                    break
                    # print("imprimiremos algo ")
                    # lista_vacia = []
                    # Graph_visual_00 = GraphVisualization.GraphRep([], grafo_02, lista_vacia, 'app', 'testtest', [], 'red',
                    #                                               'black',
                    #                                               'circle')
                    # Graph_visual_00.f.render(view=False)
                    # Graph_visual_00.f.render(view=True, format='pdf')
                    # print(obtencion_sinks(grafo_02))
                    # for nodo in grafo_02.nodes:
                    #     print(nodo,grafo_02.nodes[nodo])
                    # print(lugar_pareja_2,lugar_pareja_1,lista_sinks_rw)
                    if lugar_pareja_1 in lista_sinks_rw:
                        sink = lugar_pareja_1
                    else:
                        sink = sink_node_from_any_node(grafo_02,
                                                       lista_sinks_rw,
                                                       lugar_pareja_1)
                        if sink == None:
                            sucesores_lugar_pareja_1 = list(grafo_02.successors(lugar_pareja_1))
                            for s in lista_sinks_rw:
                                if s in sucesores_lugar_pareja_1:
                                    sink = s
                                    break
                    # print(sink,lista_sinks_rw)
                    # if lugar_pareja_1 in obtencion_sinks(hw_total.subgraph(lista_nodos_definitivos[pareja[3]])):
                    #     sink = lugar_pareja_1
                    # else:
                    #     sink = sink_node_from_any_node(hw_total.subgraph(lista_nodos_definitivos[pareja[3]]),
                    #                                    obtencion_sinks(
                    #                                        hw_total.subgraph(lista_nodos_definitivos[pareja[3] ])),
                    #                                    lugar_pareja_1)

                    # sources_buffer = obtencion_sources(hw_total.subgraph(lista_nodos_definitivos[pareja[3]]))
                    # sources_sin_ri = []
                    # for s in sources_buffer:
                    #     if grafo_02.nodes[s]['op'] == 'ri':
                    #         sucesor_ri = list(grafo_02.successors(s))
                    #         sources_sin_ri = sources_sin_ri + sucesor_ri
                    #     else:
                    #         sources_sin_ri = sources_sin_ri + [s]
                    # print("SUCESODERSSDFSDF", sources_sin_ri,sources_buffer)
                    if lugar_pareja_2 in obtencion_sources(hw_total.subgraph(lista_nodos_definitivos[pareja[3]])):
                        source = lugar_pareja_2
                    else:
                        source = source_node_from_any_node(hw_total.subgraph(lista_nodos_definitivos[pareja[3]]),
                                                           obtencion_sources(
                                                               hw_total.subgraph(lista_nodos_definitivos[pareja[3]])),
                                                              [lugar_pareja_2])
                        if hw_total.nodes[source]['op'] == 'ri':
                            sucesores_ri = list(hw_total.successors(source))
                            source = sucesores_ri.pop()



                    hw_total.add_node(contador_nodos_especiales, map=True, op='special', lat_input=0, lat_total=0,
                                      name='sp')
                    hw_total.add_edge(contador_nodos_especiales, source)
                    hw_total.add_edge(sink, contador_nodos_especiales)
                    # print(hw_total.nodes[contador_nodos_especiales])
                    #
                    pareja_append = [contador_nodos_especiales, pareja[3] - 1, sink, 'suc']
                    lista_nodos_especiales.append(pareja_append)
                    lista_nodos_creados.append(contador_nodos_especiales)
                    contador_nodos_especiales = contador_nodos_especiales + 1

                except:
                    bandera_falla_time_slots = True

                # input("Enter to continue...")

    ##############################################luego de la adicion de nodos especiales
    # cuenta_debug = cuenta_debug + 1
    # name_debug = 'test' + str(cuenta_debug)
    if s_prints == 'evalprint':
        lista_vacia = []
        Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', 'despuesnodosespeciales', [], 'red', 'black',
                                                      'circle')
        Graph_visual_00.f.render(view=False)
        Graph_visual_00.f.render(view=True, format='pdf')
    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Addition of the special nodes to the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    a = datetime.now()
    #
    type_of_configuration = dict_info_h['functions_cfg']['type_cfg']
    # print(type_of_configuration)
    # #
    # vector_latencies_cfg = []
    # if debugging:
    #     for nodo in hw_total.nodes:
    #         print("antes de config", nodo, hw_total.nodes[nodo])
    #
    if flag_debugging:
        lista_vacia = []
        Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', 'testddddest', [], 'red', 'black',
                                                      'circle')
        Graph_visual_00.f.render(view=False)
        Graph_visual_00.f.render(view=True, format='pdf')

    if s_prints == 'evalprint':
        for nodo in hw_total.nodes:
            print(f"PUES TENEMOS QUE CHECAR EL NODO {nodo} que trae {hw_total.nodes[nodo]}")

    flag_debugging = False

    # lista_nodos_numeros = []
    # for nodo in hw_total.nodes:
    #     # if nodo != None:
    #     lista_nodos_numeros.append(nodo)
    #     # print(nodo,hw_total.nodes[nodo])
    maximo_numero = max(list(hw_total.nodes))

    contador_nodos_configuracion = maximo_numero + 1 + contador_nodos
    # # vamos a adicionar los nodos de configuracion
    primer_time_slot = True
    if s_prints == 'evalprint':
        print("the number of time slots are ", contador_nodos_configuracion)
        print(len(mapping_list))
        print(dict_total_h)
        # print(info_nodes_hw)
    configuracion_latencia = 0
    vector_latencies_cfg = []
    configuracion_latencia_total = 0
    for n in range(0, len(mapping_list)):
        if s_prints == 'evalprint':
            print("nsdnsdnfsd", n)
        if debugging:
            print("ENTRA AQUI", len(mapping_list))
        if primer_time_slot:

            if type_of_configuration == 'sequential':
                hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                  lat_total=config_vector_sum[n], name='config')
            elif type_of_configuration == 'parallel':
                hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                  lat_total=max(config_vector_parallel[n]), name='config')
            for source in sources:
                if debugging:
                    print("edges 01", contador_nodos_configuracion, source)

                hw_total.add_edge(contador_nodos_configuracion, source)
            # print(max(vector_latencies_cfg))
            contador_nodos_configuracion = contador_nodos_configuracion + 1
            primer_time_slot = False
        else:
            if debugging:
                print("BIGGAZO")
            if s_prints == 'evalprint':
                print("INICIAREMOS CON UNA NUEVA INSTANCIA")
            configuracion_latencia = 0
            vector_latencies_cfg = []

            if type_of_configuration == 'sequential':
                hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                  lat_total=config_vector_sum[n], name='config')
            elif type_of_configuration == 'parallel':
                hw_total.add_node(contador_nodos_configuracion, map=True, op='config', lat_input=0,
                                  lat_total=max(config_vector_parallel[n]), name='config')

            # primero conectemos al time slot anterior
            adicion = nodos_por_time_slot * (n - 1)
            if s_prints == 'evalprint':
                print(" se incluira el nodo de configuracion", sinks)

            # sinks = obtencion_sinks(hardware_graph_total)
            sinks = sinks_hw_total
            if s_prints == 'evalprint':
                print("conectaremos al nodo de configuracion al siguiente time slot", n)
            # ahora conectaremos el nodo con el time slot siguiente
            adicion = nodos_por_time_slot * (n - 1)
            if s_prints == 'evalprint':
                print("datos", adicion, sinks)
                print(lista_nodos_total[n])
            if debugging:
                print(f"la lsita de nodos total es {lista_nodos_total}")
                print(lista_nodos_total[n - 1])
            for elemento in lista_nodos_total[n - 1]:
                if debugging: print(elemento)
                if elemento in hw_total.nodes:
                    if hw_total.out_degree(elemento) == 0:
                        if debugging:
                            print(f"edge 01   {elemento} y {contador_nodos_configuracion} ")
                        hw_total.add_edge(elemento, contador_nodos_configuracion)
            for elemento in lista_nodos_especiales:
                if s_prints == 'evalprint':
                    print("elemento", elemento)
                    print("nodos en hw", hw_total.nodes)
                if elemento[2] in lista_nodos_total[n - 1] and elemento[2] in hw_total.nodes:
                    if hw_total.out_degree(elemento[0]) == 0:
                        if hw_total.nodes[elemento[0]]['op'] != 'config':
                            if debugging:
                                print(f"edge 02   {elemento[0]} y {contador_nodos_configuracion}")
                            hw_total.add_edge(elemento[0], contador_nodos_configuracion)

            # sources = obtencion_sources(hardware_graph_total)
            sources = nodos_source
            if s_prints == 'evalprint':
                print("conectaremos al nodo de configuracion al siguiente time slot", n)
            # ahora conectaremos el nodo con el time slot siguiente
            adicion = nodos_por_time_slot * (n)
            if s_prints == 'evalprint':
                print("datos", adicion, sources)
                print(lista_nodos_total[n])

            for elemento in lista_nodos_total[n]:
                if debugging: print(elemento)
                if elemento in hw_total.nodes:
                    if hw_total.in_degree(elemento) == 0:
                        if debugging:
                            print(f"edge 04   {contador_nodos_configuracion} y {elemento}")
                        hw_total.add_edge(contador_nodos_configuracion, elemento)
            for elemento in lista_nodos_especiales:
                if s_prints == 'evalprint':
                    print("elemento", elemento)
                if elemento[2] in lista_nodos_total[n] and elemento[2] in hw_total.nodes:
                    if hw_total.in_degree(elemento[0]) == 0:
                        if hw_total.nodes[elemento[0]]['op'] != 'config':
                            if debugging:
                                print(f" edge 06   {contador_nodos_configuracion} y {elemento[0]}")
                            hw_total.add_edge(contador_nodos_configuracion, elemento[0])

            contador_nodos_configuracion = contador_nodos_configuracion + 1
            configuracion_latencia_total = configuracion_latencia + configuracion_latencia_total

    if s_prints == 'evalprint':
        for nodo in hw_total.nodes:
            print(f"PUES TENEMOS QUE CHECAR EL NODO {nodo} que trae {hw_total.nodes[nodo]} ESTO LUEGO DEL RELAJO")
    # lista_vacia = []
    # Graph_visual_00 = GraphVisualization.GraphRep([], hw_total, lista_vacia, 'app', 'testconfig', [], 'red', 'black',
    #                                               'circle')
    # Graph_visual_00.f.render(view=False)
    # Graph_visual_00.f.render(view=True, format='pdf')
    # # time.sleep(5)
    # for nodo in hw_total.nodes:
    #     print(f"PUES TENEMOS QUE CHECAR EL NODO {nodo} que trae {hw_total.nodes[nodo]} ESTO LUEGO DEL RELAJO")

    # up until here we have the complete graph, in this stage we remove the nodes that are disable or the memory
    # nodes, we create a new implementation graph which is going to help us obtain the computing time of processing
    # an image
    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Addition of the configuration nodes to the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    a = datetime.now()
    hw_perfo = hw_total.copy()
    # s_prints = 'evalprint'
    vector_edges_perfo = []
    detect_edge = False
    for nodo in hw_total.nodes:
        # if s_prints == 'basic' or s_prints == 'debug':
        # print("datos del nodo", nodo, hw_total.nodes[nodo])
        if not hw_total.nodes[nodo]['map'] or hw_total.nodes[nodo]['op'] == 'mem' or hw_total.nodes[nodo][
            'op'] == 'rm':
            if s_prints == 'evalprint':
                print("el nodo se removera", nodo)
            if debugging:
                print("el nodo se removera", nodo)
            predecesores = list(hw_perfo.predecessors(nodo))
            copia_predecesores = []
            valido = True
            if predecesores:
                while valido:
                    vector_test = []
                    for el in predecesores:
                        if el in hw_perfo.nodes:
                            vector_test.append(True)
                    if len(vector_test) >= 1:
                        valido = False
                    else:
                        predecesores_copy = list(predecesores)
                        predecesores = []
                        for el in predecesores_copy:
                            predecesores = predecesores + list(hw_perfo.predecessors(el))
                copia_predecesores = predecesores
            if debugging:
                print("copia de predecesores", copia_predecesores)
            sucesores = list(hw_perfo.successors(nodo))
            copia_sucesores = []
            valido = True
            if sucesores:
                while valido:
                    vector_test = []
                    for el in sucesores:
                        if el in hw_perfo.nodes:
                            vector_test.append(True)
                    if len(vector_test) >= 1:
                        valido = False
                    else:
                        sucesores_copy = list(sucesores)
                        sucesores = []
                        for el in sucesores_copy:
                            predecesores = predecesores + list(hw_perfo.successors(el))
                copia_sucesores = sucesores

            if s_prints == 'evalprint' or debugging:
                print("el grupo de predecesores es ", copia_predecesores)
                print(" el grupo de sucesores es ", copia_sucesores)
            hw_perfo.remove_node(nodo)
            # if copia_sucesores and copia_predecesores:
            #     for pred in copia_predecesores:
            #         for suc in copia_sucesores:
            #             if s_prints == 'evalprint':
            #                 print("dentro de ciclo", pred, suc)
            #             if flag_debugging:
            #                 print("dentro del ciclo", pred, suc)
            #
            #             if (pred, suc) not in vector_edges_perfo and (suc, pred) not in vector_edges_perfo:
            #                 if pred != suc:
            #                     try:
            #
            #                         weight_temporal = hw_total.edges[pred, nodo]['weight']
            #                         # no podemos tener latencias cero, debido a que la funcion longest path elimina esos
            #                         # nodos, ponemos una cantidad pequena para eliminar este problema, tenemos que verificar
            #                         # si no afecta a la evaluacion final
            #                         if weight_temporal == 0:
            #                             weight_temporal = 0.00001
            #                         if s_prints == 'evalprint':
            #                             print(
            #                                 f"bueno aqui hay un problema, vamos a remover nodo {nodo} y unir {pred} con {suc}, pero queremos meterle de peso {weight_temporal}")
            #                         hw_perfo.add_edge(pred, suc, weight=weight_temporal)
            #                         buffer_dummy = (pred, suc)
            #                         vector_edges_perfo.append(buffer_dummy)
            #                     except:
            #                         if s_prints == 'evalprint':
            #                             print("error dentro de la funcion de remocion de nodos")
            #                         hw_perfo.add_edge(pred, suc)
            #                         buffer_dummy = (pred, suc)
            #                         vector_edges_perfo.append(buffer_dummy)

        elif hw_total.nodes[nodo]['op'] == 'special':
            sucesores = hw_total.successors(nodo)
            bandera_config = False
            for suc in sucesores:
                if hw_total.nodes[suc]['op'] == 'config':
                    bandera_config = True
                    break
            if bandera_config:
                lista_edges = []
                predecesores = hw_perfo.predecessors(nodo)
                sucesores = hw_perfo.successors(nodo)
                hw_perfo.remove_node(nodo)
                for pred in predecesores:
                    for suc in sucesores:
                        if [pred,suc] in lista_edges:
                            hw_perfo.add_edge(pred, suc)
                            buffer_dato = [pred, suc]
                            lista_edges.append(buffer_dato)
                        else:
                            hw_perfo.add_edge(pred,suc)
                            buffer_dato = [pred,suc]
                            lista_edges.append(buffer_dato)

        # elif hw_total.nodes[nodo]['op'] == 'rm':
        #
        #     print("NO SE QUE ES ESTO")
        #     hw_perfo.remove_node(nodo)
    # print(f"TEST DE LONGEST PATHS {nx.dag_longest_path(hw_perfo)}")

    # s_prints = 'noprint'
    if s_prints == 'evalprint':
        lista_vacia = []
        Graph_visual_00 = GraphVisualization.GraphRep([], hw_perfo, lista_vacia, 'app', 'tetttekkjsksst', [], 'red', 'black',
                                                      'circle')
        Graph_visual_00.f.render(view=False)
        Graph_visual_00.f.render(view=True, format='pdf')
        time.sleep(2)
        for nodo in hw_perfo.nodes:
            print(nodo,hw_perfo.nodes[nodo])
    # hw_perfo = hw_total.copy()
    longest = None
    lat_new_version_total = None
   #### now we have the perfo graph, we need to decide what to do, if we perform a evaluation using all simple
    # paths or we use the longest path
    # hw_perfo.add_edge(16,17)
    # lista_vacia = []
    # Graph_visual_00 = GraphVisualization.GraphRep([], hw_perfo, lista_vacia, 'app', 'hwperfo120', [], 'red', 'black',
    #                                               'circle')
    # Graph_visual_00.f.render(view=False)
    # Graph_visual_00.f.render(view=True, format='pdf')
    # for nodo in hw_perfo.nodes:
    #     print( f"bla el grafo de evaluacion es   {nodo}  y {hw_perfo.nodes[nodo]}   "    )
    # print(f"aqui hay un buggazo {hw_perfo.nodes[17]}   eee  {list(hw_perfo.successors(17))} este {list(hw_perfo.predecessors(17))} el path critico es {nx.dag_longest_path(hw_perfo)}")
    # print(f" la longitud de {nx.dag_longest_path_length(hw_perfo)}")
    if s_prints == 'evalprint':
        print("INICIO DE LA EVALUACION DE DESEMPENO")
    contador_error_longest = 0
    # print(method_evaluation)
    # input("enter")
    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Final evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    a = datetime.now()
    if method_evaluation == 'longest':
        try:

            vector_relojes = []
            longest = nx.dag_longest_path(hw_perfo, weight='weight', default_weight=1)
            if s_prints == 'evalprint':
                print("longest parth" , longest)
                # input("test")
            name_clk = 0
            clk_info = None
            contador_error_longest += 1 #1
            # print("test de evaluacion",longest)
            # if len(longest) == 1:

            # in here we are going to put the name of the resource, the computing latency, and maybe the formula
            vector_info = []
            for nodo in longest:
                # if data_performance:
                # print(nodo,hw_perfo.nodes[nodo])



                try:
                    if hw_perfo.nodes[nodo]['operacion'] != None:
                        type_task = hw_perfo.nodes[nodo]['operacion']
                    else:
                        type_task = hw_perfo.nodes[nodo]['op']
                except:
                    type_task = hw_perfo.nodes[nodo]['op']


                # print("ntest", type_task)
                name_resource = hw_perfo.nodes[nodo]['name']
                if type_task == 'ri' or type_task == 'rr' or type_task == 'rw':
                    if type_task == 'ri':
                        try:
                            for n,data in dict_total_h.items():
                                if data['name'] == name_resource:
                                    name_clk = data['ops']['actuator']['clk']
                        except:
                            for n,data in dict_total_h.items():
                                if data['name'] == name_resource:
                                    name_clk = data['ops']['sensor']['clk']
                    elif type_task == 'rw':
                        for n, data in dict_total_h.items():
                            if data['name'] == name_resource:
                                name_clk = data['ops']['write']['clk']
                    elif type_task == 'rr':
                        for n, data in dict_total_h.items():
                            if data['name'] == name_resource:
                                name_clk = data['ops']['read']['clk']

                else:


                    if flag_debugging:
                        print("primeralinea " ,nodo,name_resource,type_task)

                    for n, data in dict_total_h.items():
                        if data['name'] == name_resource:

                            for operacion in data['ops']:
                                if operacion == type_task:

                                    # print(data['ops'][operacion]['clk'])
                                    name_clk = data['ops'][operacion]['clk']
                # if data_performance:
                if flag_debugging:
                    print("test",name_clk)
                # print("dddd", name_clk)
                for t, data in dict_info_h['functions_res'].items():

                    # print(name_clk,t)
                    if name_clk == t:
                        vector_relojes.append(data)
                        clk_info = data
                #     print("nsdf",data,t,name_clk)
                #     if name_clk == t:
                #         print("tetgd")
                # if flag_debugging:
                #     print(nodo, name_resource, clk_info, type_task)
                temporal_info = [nodo, name_resource, clk_info, type_task]
                vector_info.append(temporal_info)

            contador_error_longest += 1 #2
            if flag_debugging == 'perf_clock':
                maximum_clock = dict_info_h['max_clk']
            else:
                maximum_clock = max(vector_relojes)
            # print("el clock q utilizar ", maximum_clock)
            if s_prints == 'evalprint':
                print(longest)
                print(hw_perfo.nodes)
                print("inicio de obtencio de latencia total")
            if debugging:
                for nodo in hw_perfo.nodes:
                    print("datos del nodo", nodo, hw_perfo.nodes[nodo])
                for nodo in hw_total.nodes:
                    print(nodo, hw_total.nodes[nodo])

            contador_error_longest += 1 #3
            if s_prints == 'evalprint':
                lista_vacia = []
                Graph_visual_00 = GraphVisualization.GraphRep([], hw_perfo, lista_vacia, 'app', name_file, [], 'red', 'black',
                                                              'circle')
                Graph_visual_00.f.render(view=False)
                Graph_visual_00.f.render(view=True, format='pdf')
                    # for nodo in hw_perfo.nodes:
                    #     print("estamos checando algo", nodo, hw_perfo.nodes[nodo])

            contador_error_longest += 1 #4
            # print(dict_info_hw)
            # performance evaluation
            lat_new_version_total = 0
            latencia_total = 0
            if s_prints == 'evalprint':
                print(
                    "We are going to start the performance evaluation method, based on the critical path "
                    "of the evaluation graph, the longest path es", longest)
            bandera_fin_time_slot = False
            contador = 0
            computing_latency_temporal = 0
            primer_nodo = True
            contador_nodos_critical = len(longest)
            contador_error_longest += 1 #5
            for nodo in longest:
                # print(nodo)
                if flag_debugging:
                    print("infor de nodo y algo mas",nodo, vector_info[contador])
                # print("el nodo es ", nodo, "y su nombre es", hw_perfo.nodes[nodo]['name'])
                if s_prints == 'debug' or s_prints == 'evalprint':
                    print(f"the node name is {hw_perfo.nodes[nodo]['name']}")
                successor = list(hw_perfo.successors(nodo))
                contador_error_longest += 1  # 6
                # print(successor)
                if s_prints == 'evalprint':
                    print("datos del nodo", nodo, hw_perfo.nodes[nodo])
                if successor:
                    for suc in successor:
                        if debugging:
                            print("el sucesor es ", suc, hw_perfo.nodes[suc])
                        if flag_debugging:
                            print("el sucesor es ", hw_perfo.nodes[suc])
                        if hw_perfo.nodes[suc]['op'] == 'config':# or contador == contador_nodos_critical - 1:
                            bandera_fin_time_slot = True
                else:
                    bandera_fin_time_slot = True
                contador_error_longest += 1  # 7
                if flag_debugging:
                    print("bandera",bandera_fin_time_slot,successor)
                    print("el nodo es ", nodo, "y su nombre es", hw_perfo.nodes[nodo])
                if hw_perfo.nodes[nodo]['op'] == 'config':
                    if flag_debugging:
                        print("error search")
                    lat_new_version_total = lat_new_version_total + int(hw_perfo.nodes[nodo]['lat_total'])
                    latencia_total = latencia_total + int(hw_perfo.nodes[nodo]['lat_total'])
                    hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                    hw_perfo.nodes[nodo]['latencia_de_nodo'] = int(hw_perfo.nodes[nodo]['lat_total'])
                    if s_prints == 'evalprint' or s_prints == 'printper':
                        print(
                            f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {int(hw_perfo.nodes[nodo]['lat_total'])}")
                        print(f"the latency until now is {lat_new_version_total}")
                    # bandera_fin_time_slot = False
                    contador_error_longest += 1  # 8

                elif bandera_fin_time_slot:
                    if s_prints == 'evalprint':
                        print("nsdofsdf",hw_perfo.nodes[nodo])
                        print("mas datos")
                    if len(hw_perfo.nodes[nodo]['s_info']) == 3:
                        if s_prints == 'evalprint':
                            print("caso 1")
                        lat_new_version_total_temporal = hw_perfo.nodes[nodo]['s_info'][1] * hw_perfo.nodes[nodo]['s_info'][
                            2] * maximum_clock
                    elif len(hw_perfo.nodes[nodo]['s_info']) == 2:
                        if s_prints == 'evalprint':
                            print("caso 2")
                        lat_new_version_total_temporal = hw_perfo.nodes[nodo]['s_info'][0] * hw_perfo.nodes[nodo]['s_info'][
                            1] * maximum_clock
                    # except:
                    contador_error_longest += 1  # 9
                    if s_prints == 'evalprint':
                        print("ojnsdfsds")
                    lat_new_version_total = lat_new_version_total + lat_new_version_total_temporal
                    # print(lat_new_version_total)
                    if s_prints == 'evalprint' or s_prints == 'printper':
                        print(
                            f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {lat_new_version_total_temporal}")
                    # print(f"the latency until now is {lat_new_version_total}")
                    hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                    hw_perfo.nodes[nodo]['latencia_de_nodo'] = lat_new_version_total_temporal
                    bandera_fin_time_slot = False
                    if s_prints == 'evalprint':
                        print("teststst")
                    contador_error_longest += 1  # 10
                elif hw_perfo.nodes[nodo]['op'] == 'special':
                    # input("enter")
                    hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                    hw_perfo.nodes[nodo]['latencia_de_nodo'] = 0
                else:

                    try:
                        name_resource_lat = hw_perfo.nodes[nodo]['name']
                        lugar_recurso = None
                        for n, data in dict_nodes_h.items():
                            # print(data['name'])
                            if name_resource_lat == data['name']:
                                lugar_recurso = n
                        if s_prints == 'testheu':
                            print("hhdhdhdh",lugar_recurso,name_resource_lat)
                        name_function = dict_nodes_h[lugar_recurso]['ops'][hw_perfo.nodes[nodo]['op']]['latency']


                        for data in dict_info_h['functions_res']:
                            # print(data)
                            if data == name_function:
                                function_formula = dict_info_h['functions_res'][data]
                        # print(function_formula)
                        # ############this is the new way to obtain the latency
                        lugar_nodo = None
                        # print(dict_info_a)
                        # print("entre")
                        # print(info_nodes_app)
                        for n, data in dict_info_a.items():
                            if data['name'] == dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name']:
                                # print("se encontro")
                                lugar_nodo = n

                        # for n, data in dict_info_a.items():
                        #     if dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name'] == dict_info_a[n]['name']:
        # lista_nodos_numeros                #         lugar_nodo = n
                        # lista_sources_ag_total = obtencion_sources(app_total)
                        lista_sources_ag_total = sources_aplicacion_total
                        source_total_app = source_node_from_any_node(app_total,
                                                                     lista_sources_ag_total,
                                                                     lugar_nodo)
                        #
                        height = dict_info_a[source_total_app]['param']['height']
                        width = dict_info_a[source_total_app]['param']['width']
                        # print(width)
                        # # we are going to autoasign the values of the parameters
                        # # print(self.dict_nodes_a)
                        # # print(function_formula)
                        contador_parametros = 0
                        bandera_primera_vez_letra = True
                        vector_parametro = []
                        vector_total_parametros = []
                        if isinstance(function_formula, str):
                            for letra in function_formula:
                                if bandera_primera_vez_letra:
                                    if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                        pass
                                    else:
                                        vector_parametro.append(letra)
                                        bandera_primera_vez_letra = False
                                else:
                                    if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                        vector_total_parametros.append(vector_parametro)
                                        vector_parametro = []
                                    else:
                                        vector_parametro.append(letra)
                        vector_parametro = []
                        for it in vector_total_parametros:
                            dummy = "".join(it)
                            if dummy:
                                try:
                                    int(dummy)
                                except:
                                    if dummy not in vector_parametro:
                                        vector_parametro.append(dummy)

                        ### we first look for the general values of width and height
                        for param_formula in vector_parametro:
                            if param_formula == 'width':
                                pass
                            elif param_formula == 'height':
                                pass
                            else:
                                # in here we are going to look the value in the dict of the nodes
                                for pa in dict_nodes_a[hw_perfo.nodes[nodo]['task']]['param']:

                                    if param_formula == pa:
                                        globals()[pa] = dict_nodes_a[hw_perfo.nodes[nodo]['task']]['param'][pa]
                        if vector_info[contador - 1][1] == 'config':
                            clk_test = 0
                        else:
                            clk_test = vector_info[contador - 1][2]

                        if computing_latency_temporal >= clk_test:
                            computing_latency_temporal = computing_latency_temporal
                        else:
                            computing_latency_temporal = clk_test

                        if isinstance(function_formula, str):

                            # resultado_latencia = (eval(function_formula) ) * maximum_clock + \
                            #                      vector_info[contador][2]

                            resultado_latencia = (eval(function_formula) - 1) * computing_latency_temporal + \
                                                 vector_info[contador][2] + 1
                        else:
                            # resultado_latencia = (function_formula ) * maximum_clock + \
                            #                      vector_info[contador][2]


                            resultado_latencia = (function_formula - 1) * computing_latency_temporal + \
                                                 vector_info[contador][2] + 1
                        resultado_latencia_total = width * height * maximum_clock

                        # print("resultado input latenci ",resultado_latencia)
                        # print("resultado latenci total",resultado_latencia_total)

                        lat_new_version_total = lat_new_version_total + resultado_latencia
                        if s_prints == 'evalprint' or s_prints == 'printper':
                            print(
                                f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {resultado_latencia}")
                            print(f"the latency until now is {lat_new_version_total}")
                        hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                        hw_perfo.nodes[nodo]['latencia_de_nodo'] = resultado_latencia

                    except:
                        if s_prints == 'evalprint':
                            print("entra aqui")
                        # # if data_performance:
                        # #     print("no se pudo hacer nada")
                        # # pass
                        # # aqui se tomaran en cuenta los recursos de comunicacion y extras
                        # print(vector_info)
                        valor_a_sumar = vector_info[contador][2]
                        if valor_a_sumar != None:
                            lat_new_version_total = lat_new_version_total + vector_info[contador][
                                2]  # int(hw_perfo.nodes[nodo]['lat_input'])
                        else:
                            lat_new_version_total = 0
                        if s_prints == 'evalprint' or s_prints == 'printper':
                            print(
                                f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {int(hw_perfo.nodes[nodo]['lat_input'])}")
                        # print(f"the latency until now is {lat_new_version_total}")
                        hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                        hw_perfo.nodes[nodo]['latencia_de_nodo'] = vector_info[contador][
                            2]  # int(hw_perfo.nodes[nodo]['lat_input'])

                contador = contador + 1
        except:
            # print("se llego al error")
            # time.sleep(3)
            # print("entrada a error en la evaluacion ",contador_error_longest)
            lat_new_version_total = 1000000000000000
            longest = None

    else:
        #########inicio de procesamiento

        valor_maximo = 0
        debug_prints = False
        sources = obtencion_sources(hw_perfo)
        sinks = obtencion_sinks(hw_perfo)
        longest_final = []
        if s_prints == 'evalprint':
            print(f"el metodo seleccionado es simple paths, los sources son {sources} y los sinks son {sinks}")
        # print("entrada nuevo metedo")
        for source in sources:
            for sink in sinks:
                for simple in nx.all_simple_paths(hw_perfo,source,sink):
                    try:
                        vector_relojes = []
                        longest = simple
                        if debug_prints:
                            print("longest parth", longest)
                        name_clk = 0
                        clk_info = None
                        # in here we are going to put the name of the resource, the computing latency, and maybe the formula
                        vector_info = []
                        for nodo in longest:
                            try:
                                if hw_perfo.nodes[nodo]['operacion'] != None:
                                    type_task = hw_perfo.nodes[nodo]['operacion']
                                else:
                                    type_task = hw_perfo.nodes[nodo]['op']
                            except:
                                type_task = hw_perfo.nodes[nodo]['op']
                            name_resource = hw_perfo.nodes[nodo]['name']
                            if type_task == 'ri' or type_task == 'rr' or type_task == 'rw':
                                if type_task == 'ri':
                                    try:
                                        for n, data in dict_total_h.items():
                                            if data['name'] == name_resource:
                                                name_clk = data['ops']['actuator']['clk']
                                    except:
                                        for n, data in dict_total_h.items():
                                            if data['name'] == name_resource:
                                                name_clk = data['ops']['sensor']['clk']
                                elif type_task == 'rw':
                                    for n, data in dict_total_h.items():
                                        if data['name'] == name_resource:
                                            name_clk = data['ops']['write']['clk']
                                elif type_task == 'rr':
                                    for n, data in dict_total_h.items():
                                        if data['name'] == name_resource:
                                            name_clk = data['ops']['read']['clk']

                            else:
                                if debug_prints:
                                    print("primeralinea ", nodo, name_resource, type_task)

                                for n, data in dict_total_h.items():
                                    if data['name'] == name_resource:

                                        for operacion in data['ops']:
                                            if operacion == type_task:
                                                # print(data['ops'][operacion]['clk'])
                                                name_clk = data['ops'][operacion]['clk']
                            # if data_performance:
                            if debug_prints:
                                print("test", name_clk)
                            # print("dddd", name_clk)
                            for t, data in dict_info_h['functions_res'].items():

                                # print(name_clk,t)
                                if name_clk == t:
                                    vector_relojes.append(data)
                                    clk_info = data

                            temporal_info = [nodo, name_resource, clk_info, type_task]
                            vector_info.append(temporal_info)

                        if flag_debugging == 'perf_clock':
                            maximum_clock = dict_info_h['max_clk']
                        else:
                            maximum_clock = max(vector_relojes)
                        # print("el clock q utilizar ", maximum_clock)
                        if debug_prints:
                            print(longest)
                            print(hw_perfo.nodes)
                            print("inicio de obtencio de latencia total")
                        # performance evaluation
                        lat_new_version_total = 0
                        latencia_total = 0
                        if debug_prints:
                            print(
                                "We are going to start the performance evaluation method, based on the critical path of the evaluation graph")
                        bandera_fin_time_slot = False
                        contador = 0
                        computing_latency_temporal = 0
                        primer_nodo = True
                        contador_nodos_critical = len(longest)
                        for nodo in longest:
                            # print(nodo)
                            if debug_prints:
                                print("infor de nodo y algo mas", nodo, vector_info[contador])
                            # print("el nodo es ", nodo, "y su nombre es", hw_perfo.nodes[nodo]['name'])
                            if debug_prints:
                                print(f"the node name is {hw_perfo.nodes[nodo]['name']}")
                            successor = list(hw_perfo.successors(nodo))
                            # print(successor)
                            if debug_prints:
                                print("datos del nodo", nodo, hw_perfo.nodes[nodo])
                            if successor:
                                for suc in successor:
                                    if debug_prints:
                                        print("el sucesor es ", suc, hw_perfo.nodes[suc])

                                    if hw_perfo.nodes[suc][
                                        'op'] == 'config':  # or contador == contador_nodos_critical - 1:
                                        bandera_fin_time_slot = True
                            else:
                                bandera_fin_time_slot = True
                            if debug_prints:
                                print("bandera", bandera_fin_time_slot, successor)
                                print("el nodo es ", nodo, "y su nombre es", hw_perfo.nodes[nodo])
                            if hw_perfo.nodes[nodo]['op'] == 'config':
                                if debug_prints:
                                    print("error search")
                                lat_new_version_total = lat_new_version_total + int(hw_perfo.nodes[nodo]['lat_total'])
                                latencia_total = latencia_total + int(hw_perfo.nodes[nodo]['lat_total'])
                                hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                hw_perfo.nodes[nodo]['latencia_de_nodo'] = int(hw_perfo.nodes[nodo]['lat_total'])
                                if debug_prints:
                                    print(
                                        f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {int(hw_perfo.nodes[nodo]['lat_total'])}")
                                    print(f"the latency until now is {lat_new_version_total}")
                                # bandera_fin_time_slot = False
                            elif bandera_fin_time_slot:
                                if debug_prints:
                                    print("nsdofsdf", hw_perfo.nodes[nodo])
                                    print("mas datos")
                                if len(hw_perfo.nodes[nodo]['s_info']) == 3:
                                    if debug_prints:
                                        print("caso 1")
                                    lat_new_version_total_temporal = hw_perfo.nodes[nodo]['s_info'][1] * \
                                                                     hw_perfo.nodes[nodo]['s_info'][
                                                                         2] * maximum_clock
                                elif len(hw_perfo.nodes[nodo]['s_info']) == 2:
                                    if debug_prints:
                                        print("caso 2")
                                    lat_new_version_total_temporal = hw_perfo.nodes[nodo]['s_info'][0] * \
                                                                     hw_perfo.nodes[nodo]['s_info'][
                                                                         1] * maximum_clock
                                # except:

                                if debug_prints:
                                    print("ojnsdfsds")
                                lat_new_version_total = lat_new_version_total + lat_new_version_total_temporal
                                # print(lat_new_version_total)
                                if debug_prints:
                                    print(
                                        f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {lat_new_version_total_temporal}")
                                # print(f"the latency until now is {lat_new_version_total}")
                                hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                hw_perfo.nodes[nodo]['latencia_de_nodo'] = lat_new_version_total_temporal
                                bandera_fin_time_slot = False
                                if debug_prints:
                                    print("teststst")
                            else:

                                try:
                                    name_resource_lat = hw_perfo.nodes[nodo]['name']
                                    lugar_recurso = None
                                    for n, data in dict_nodes_h.items():
                                        # print(data['name'])
                                        if name_resource_lat == data['name']:
                                            lugar_recurso = n
                                    if debug_prints:
                                        print("hhdhdhdh", lugar_recurso, name_resource_lat)
                                    name_function = dict_nodes_h[lugar_recurso]['ops'][hw_perfo.nodes[nodo]['op']][
                                        'latency']

                                    for data in dict_info_h['functions_res']:
                                        # print(data)
                                        if data == name_function:
                                            function_formula = dict_info_h['functions_res'][data]
                                    # print(function_formula)
                                    # ############this is the new way to obtain the latency
                                    lugar_nodo = None
                                    # print(dict_info_a)
                                    # print("entre")
                                    # print(info_nodes_app)
                                    for n, data in dict_info_a.items():
                                        if data['name'] == dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name']:
                                            # print("se encontro")
                                            lugar_nodo = n

                                    # for n, data in dict_info_a.items():
                                    #     if dict_nodes_a[hw_perfo.nodes[nodo]['task']]['name'] == dict_info_a[n]['name']:
                                    #         lugar_nodo = n
                                    # lista_sources_ag_total = obtencion_sources(app_total)
                                    lista_sources_ag_total = sources_aplicacion_total
                                    source_total_app = source_node_from_any_node(app_total,
                                                                                 lista_sources_ag_total,
                                                                                 lugar_nodo)
                                    #
                                    height = dict_info_a[source_total_app]['param']['height']
                                    width = dict_info_a[source_total_app]['param']['width']
                                    # print(width)
                                    # # we are going to autoasign the values of the parameters
                                    # # print(self.dict_nodes_a)
                                    # # print(function_formula)
                                    contador_parametros = 0
                                    bandera_primera_vez_letra = True
                                    vector_parametro = []
                                    vector_total_parametros = []
                                    if isinstance(function_formula, str):
                                        for letra in function_formula:
                                            if bandera_primera_vez_letra:
                                                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                                    pass
                                                else:
                                                    vector_parametro.append(letra)
                                                    bandera_primera_vez_letra = False
                                            else:
                                                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                                                    vector_total_parametros.append(vector_parametro)
                                                    vector_parametro = []
                                                else:
                                                    vector_parametro.append(letra)
                                    vector_parametro = []
                                    for it in vector_total_parametros:
                                        dummy = "".join(it)
                                        if dummy:
                                            try:
                                                int(dummy)
                                            except:
                                                if dummy not in vector_parametro:
                                                    vector_parametro.append(dummy)

                                    ### we first look for the general values of width and height
                                    for param_formula in vector_parametro:
                                        if param_formula == 'width':
                                            pass
                                        elif param_formula == 'height':
                                            pass
                                        else:
                                            # in here we are going to look the value in the dict of the nodes
                                            for pa in dict_nodes_a[hw_perfo.nodes[nodo]['task']]['param']:

                                                if param_formula == pa:
                                                    globals()[pa] = dict_nodes_a[hw_perfo.nodes[nodo]['task']]['param'][
                                                        pa]
                                    if vector_info[contador - 1][1] == 'config':
                                        clk_test = 0
                                    else:
                                        clk_test = vector_info[contador - 1][2]

                                    if computing_latency_temporal >= clk_test:
                                        computing_latency_temporal = computing_latency_temporal
                                    else:
                                        computing_latency_temporal = clk_test

                                    if isinstance(function_formula, str):

                                        resultado_latencia = (eval(function_formula)) * maximum_clock + \
                                                             vector_info[contador][2]

                                        # resultado_latencia = (eval(function_formula) - 1) * computing_latency_temporal + \
                                        #                      vector_info[contador][2] + 1
                                    else:
                                        resultado_latencia = (function_formula) * maximum_clock + \
                                                             vector_info[contador][2]

                                        # resultado_latencia = (function_formula - 1) * computing_latency_temporal + \
                                        #                      vector_info[contador][2] + 1
                                    resultado_latencia_total = width * height * maximum_clock

                                    # print("resultado input latenci ",resultado_latencia)
                                    # print("resultado latenci total",resultado_latencia_total)

                                    lat_new_version_total = lat_new_version_total + resultado_latencia
                                    if debug_prints:
                                        print(
                                            f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {resultado_latencia}")
                                        print(f"the latency until now is {lat_new_version_total}")
                                    hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                    hw_perfo.nodes[nodo]['latencia_de_nodo'] = resultado_latencia

                                except:
                                    if debug_prints:
                                        print("entra aqui")
                                    # # if data_performance:
                                    # #     print("no se pudo hacer nada")
                                    # # pass
                                    # # aqui se tomaran en cuenta los recursos de comunicacion y extras
                                    # print(vector_info)
                                    valor_a_sumar = vector_info[contador][2]
                                    if valor_a_sumar != None:
                                        lat_new_version_total = lat_new_version_total + vector_info[contador][
                                            2]  # int(hw_perfo.nodes[nodo]['lat_input'])
                                    else:
                                        lat_new_version_total = 0
                                    if debug_prints:
                                        print(
                                            f"the node is {hw_perfo.nodes[nodo]['name']} and its latency is {int(hw_perfo.nodes[nodo]['lat_input'])}")
                                    # print(f"the latency until now is {lat_new_version_total}")
                                    hw_perfo.nodes[nodo]['latencia_resultante'] = lat_new_version_total
                                    hw_perfo.nodes[nodo]['latencia_de_nodo'] = vector_info[contador][
                                        2]  # int(hw_perfo.nodes[nodo]['lat_input'])

                            contador = contador + 1
                    except:
                        # print("se llego al error")
                        # time.sleep(3)
                        lat_new_version_total = 'no_valid'
                        longest = None
                    # print(longest,lat_new_version_total)
                    if lat_new_version_total != 'no_valid':
                        # print("entreamos aqui")
                        if valor_maximo < lat_new_version_total:
                            # print("asignamos el valor")
                            valor_maximo = lat_new_version_total
                            longest_final = simple




    if bandera_falla_time_slots:
        lat_new_version_total = 1000000000000000
        longest = None



    if s_prints == 'evalprint':
        print(longest)
        # input("tetsFFDFDDFFDFDst")

    # lista_nombres_critical = []
    # for l in longest:
    #     lista_nombres_critical.append(hw_perfo.nodes[l]['name'])
    # print(f"el path critico es {longest} y los nombres de este path son {lista_nombres_critical} y el numero de elementos son {len(longest)} y {len(lista_nombres_critical)}")
    if method_evaluation == 'simple':
        longest = longest_final
        lat_new_version_total = valor_maximo

    # for nodo in hw_total.nodes:
    #     print(nodo,hw_total.nodes[nodo])
    contador_extra = max(hw_total.nodes) + 1
    hw_total_copia = hw_total.copy()
    # for nodo in hw_total_copia:
    #     print(nodo, hw_total_copia.nodes[nodo], list(hw_total_copia.successors(nodo)))

    # print(lista_nodos,lista_nodos_total,lista_nombres_total)

    # print("vamos a integrar los nodos de memoria seccionados",len(mapping_list),contador_extra)
    # print(hw_total.nodes)
    # print("lista de nodos especiales", lista_nodos_especiales)
    lista_especial = []
    for elem in lista_nodos_especiales:
        lista_especial.append(elem[2])
    # print("estos nodos tenemos que verificar",lista_especial)
    # for nodo in graph_unroll:
    #     print(nodo,graph_unroll.nodes[nodo])
    if s_prints == 'evalprint':

        lista_vacia = []
        Graph_visual_00 = GraphVisualization.GraphRep([], hw_perfo, lista_vacia, 'app', name_file_perfo, [], 'red', 'black',
                                                      'circle')
        Graph_visual_00.f.render(view=False)
        Graph_visual_00.f.render(view=True, format='pdf')


    if s_prints == 'evalprint':
        print("INICIO DE LO DEL GRAFO RARO")
        for nodo in hw_total_copia.nodes:
            print(f" nodo {nodo} y sus datos {hw_total_copia.nodes[nodo]}")
    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Performance evaluation over the evaluation graph, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    a = datetime.now()
    for nodo_unroll in graph_unroll:
        # print(nodo_unroll,graph_unroll.nodes[nodo_unroll])



        if graph_unroll.nodes[nodo_unroll]['op'] == 'rm':
            # print(contador_extra)
            predecesores = graph_unroll.predecessors(nodo_unroll)
            sucesores = graph_unroll.successors(nodo_unroll)
            lista_names_predecesores = []
            lista_names_sucesores = []

            if s_prints == 'evalprint':
                print( "bjsdnnsfds",  list(graph_unroll.predecessors(nodo_unroll)),list(graph_unroll.successors(nodo_unroll)))

            for pre in predecesores:
                # print("lista",pre)
                lista_names_predecesores.append(graph_unroll.nodes[pre]['name'])
            for suc in sucesores:
                # print("suc",suc)
                lista_names_sucesores.append(graph_unroll.nodes[suc]['name'])

            # print(lista_names_sucesores,lista_names_predecesores)
            if s_prints == 'evalprint':
                print("la lista de nodos total es ", lista_nodos_total)
            primer_time_slot_final = True
            contador_time_slots = 0
            for time_slot in lista_nodos_total:
                # print(time_slot)
                esta_el_nodo = False
                lista_nombres = []
                for elemento in time_slot:
                    # print(elemento)
                    # print(f"el elemento is {hw_total_copia.nodes[elemento]}")
                    # print(f"el nombre del elemento es {hw_total_copia.nodes[elemento]['name']}")
                    try:
                        lista_nombres.append(hw_total_copia.nodes[elemento]['name'])
                    except:
                        pass
                if graph_unroll.nodes[nodo_unroll]['name'] not in lista_nombres:


                    hw_total_copia.add_node(contador_extra, name=graph_unroll.nodes[nodo_unroll]['name'],
                                            op=graph_unroll.nodes[nodo_unroll]['op'], lat=0, task='mem01', map=False,
                                            label='mem')

                    for nodo in time_slot:
                        if nodo in hw_total.nodes:

                            if hw_total.nodes[nodo]['name'] in lista_names_sucesores:

                                if nodo in lista_especial:
                                    if debugging:   print("estamos checando esto", nodo)
                                    # print("estamos checando esto 01", nodo)
                                    lugar = None
                                    for elemento in lista_nodos_especiales:
                                        if elemento[2] == nodo:
                                            lugar = elemento[0]
                                    if debugging:   print("arco 072", lugar, contador_extra, hw_total.nodes[lugar]['name'])
                                    sucesores_arco = list(hw_total_copia.predecessors(lugar))
                                    for suc_ar in sucesores_arco:
                                        hw_total_copia.remove_edge(suc_ar, lugar)
                                        hw_total_copia.add_edge(suc_ar, contador_extra)
                                    # print("succesores arco", sucesores_arco)

                                    hw_total_copia.add_edge(contador_extra, lugar)


                                else:

                                    if debugging: print("arco 01", contador_extra, nodo, hw_total.nodes[nodo]['name'])
                                    predecesores_arco = list(hw_total_copia.predecessors(nodo))
                                    # print("predecesores arco", predecesores_arco)
                                    for pre_arco in predecesores_arco:
                                        hw_total_copia.remove_edge(pre_arco, nodo)
                                    hw_total_copia.add_edge(contador_extra, nodo)
                                    hw_total_copia.add_edge(pre_arco,contador_extra)

                            if hw_total.nodes[nodo]['name'] in lista_names_predecesores:
                                if nodo in lista_especial:
                                    # print("estamos checando esto 01",nodo)
                                    lugar = None
                                    for elemento in lista_nodos_especiales:
                                        if elemento[2] == nodo:
                                            lugar = elemento[0]
                                    if debugging:   print("arco 042", lugar, contador_extra, hw_total.nodes[lugar]['name'])
                                    sucesores_arco = list(hw_total_copia.successors(lugar))
                                    for suc_ar in sucesores_arco:
                                        hw_total_copia.remove_edge(lugar, suc_ar)
                                        hw_total_copia.add_edge(contador_extra, suc_ar)
                                    # print("succesores arco", sucesores_arco)

                                    hw_total_copia.add_edge(lugar, contador_extra)



                                else:
                                    if debugging:
                                        print("arco 0jjj2", nodo, contador_extra, hw_total.nodes[nodo]['name'])
                                    sucesores_arco = list(hw_total_copia.successors(nodo))
                                    for suc_ar in sucesores_arco:
                                        hw_total_copia.remove_edge(nodo, suc_ar)
                                        hw_total_copia.add_edge(contador_extra, suc_ar)
                                    if debugging:   print("succesores arco", sucesores_arco)
                                    hw_total_copia.add_edge(nodo, contador_extra)

                    # if s_prints == 'evalprint':
                    #     print("PRIMERA VISITA A ESTE MODULO",contador_extra)
                    # if primer_time_slot_final == True:
                    #     primer_time_slot_final = False
                    # else:
                    #
                    #     grafo_para_sinks = hw_total_copia.subgraph(lista_nodos_total[contador_time_slots - 1])
                    #     sinks_lista = obtencion_sinks(grafo_para_sinks)
                    #     grafo_para_sources = hw_total_copia.subgraph(time_slot)
                    #     sources_lista = obtencion_sources(grafo_para_sources)
                    #     for si in sinks_lista:
                    #         for so in sources_lista:
                    #             hw_total_copia.add_edge(si,so)
                    # contador_time_slots = contador_time_slots + 1
                    contador_extra = contador_extra + 1

    if s_prints == 'evalprint':
        print("performance evaluation total es de ", 0)
        nx.draw(hw_total, with_labels=True, font_weight='bold')

        # plt.savefig("testgraph.png")
    vector_sensor_ag = []
    # vector_sensor_dg = []
    vector_actuator_ag = []
    # vector_actuator_dg = []
    for nodo in app_total:
        if app_total.nodes[nodo]['op'] == 'interface' and app_total.in_degree(nodo) == 0:
            vector_sensor_ag.append(nodo)
        if app_total.nodes[nodo]['op'] == 'interface' and app_total.out_degree(nodo) == 0:
            vector_actuator_ag.append(nodo)


    for nodo in hw_total_copia.nodes:
        if hw_total_copia.nodes[nodo]['op'] == 'special':
            hw_total_copia.nodes[nodo]['map'] = False

    if s_prints == 'evalprint':
        print('hemos terminado el analisis')
        print(longest)

    if debug_info == 'remove' or debug_info == 'total':
        b = datetime.now()
        now = b.strftime("%H:%M:%S.%f")
        c = b - a
        print(
            f"Final operations, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

    return longest, hw_perfo, hw_total_copia, lat_new_version_total, maximum_clock

