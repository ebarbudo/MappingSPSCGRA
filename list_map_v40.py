import networkx as nx
import random
import time
import matplotlib.pyplot as plt
from graphviz import Digraph
from basic_functions import source_node_from_any_node, sink_from_datapath, sink_node_from_any_node, obtencion_sucesores, \
    obtencion_sources, obtencion_sinks, simple_paths_from_two_nodes
# import class_performance_v4
import collections

infinito = 1000000


# misc functions

def generation_datapaths(input_graph):
    """genera los datapaths independientes, el proceso es sobre un grafo de hardware checamos los nodos que tienen
    un recurso con dos output edges y que uno de ellos va hacia un recurso con dos input edges, entonces removemos
    uno de esos edges y con eso podemos generar otro datapath independiente, luego del preprocesamiento del grafo
    iniciamos ya la busqueda de los datapaths"""

    # vamos a cambiar el codigo y poner el grafo total
    lista_paths = []
    lista_nodos_ocupados_sink = []
    lista_nodos_ocupados_source = []
    nodos_ocupados = []
    """"in here we obtain simple datapaths, for the mapping"""
    ####procesamiento previo, aqui removemos ciertos edges
    copia_DG_proceso_previo = input_graph.copy()
    for nodo in copia_DG_proceso_previo.nodes:
        # si el nodo tiene mas de un output edge
        if copia_DG_proceso_previo.out_degree(nodo) > 1:
            # print("el nodo tiene un grado mayor de dos ", nodo)
            # obtenemos sus sucesores
            sucesores = copia_DG_proceso_previo.successors(nodo)
            for suc in sucesores:
                # si el sucesor tiene input degree mayor de uno
                if copia_DG_proceso_previo.in_degree(suc) > 1:
                    # print("estamos por remover un edge")
                    # removemos el edge
                    copia_DG_proceso_previo.remove_edge(nodo, suc)
                    break
    sources_test = obtencion_sources(copia_DG_proceso_previo)
    sinks_test = obtencion_sinks(copia_DG_proceso_previo)
    # aqui ya obtenemos los datapaths independientes de acuerdo al proceso antiguo
    for source in sources_test:
        for sink in sinks_test:
            paths = nx.all_simple_paths(copia_DG_proceso_previo, source=source, target=sink)
            todos_los_paths = list(paths)
            if todos_los_paths:
                # lista_paths.append(todos_los_paths[0])
                vector = []
                if not sink in lista_nodos_ocupados_sink and not source in lista_nodos_ocupados_source:
                    for i in range(len(todos_los_paths)):
                        for nodo in todos_los_paths[i]:
                            if nodo in nodos_ocupados:
                                vector.append(False)
                        if not False in vector:
                            lista_paths.append(todos_los_paths[i])
                            lista_nodos_ocupados_sink.append(sink)
                            lista_nodos_ocupados_source.append(source)
                            nodos_ocupados = nodos_ocupados + todos_los_paths[i]

    # print("checaremos la nueva forma de obtener los datapaths ", lista_paths)
    lista_paths_respaldo = lista_paths.copy()
    return lista_paths_respaldo


def obtencion_critical_path(input_graph):
    """"from an input graph it obtains the critical path in a terms of number of nodes, if the graph is empty it returns a value near to zero"""
    sources = obtencion_sources(input_graph)
    sinks = obtencion_sinks(input_graph)
    lista_distancias = []
    for source in sources:
        for sink in sinks:
            paths = list(nx.all_simple_paths(input_graph, source=source, target=sink))
            for path in paths:
                lista_distancias.append(len(path))

    # print("distnacia dfs",lista_distancias)
    if lista_distancias:
        return max(lista_distancias)
    else:
        if len(input_graph.nodes) >= 1:
            return 1
        else:
            return 0.001


def obtencion_sucesores_de_una_lista(input_graph, lista_nodos):
    """"obtains the entire set of decendents from a list, it obtain for each element of the list its decendents then add all"""

    # print("la lista a checar es ", lista_nodos)
    lista_total_sucesores = []

    for nodo in lista_nodos:
        try:
            lista_sucesores = nx.dfs_successors(input_graph, nodo)
        except:
            # esto quiere decir que no existen sucesores de dicho nodo
            lista_sucesores = []

        # print(lista_sucesores)
        # print("obtencion de sucesores funcion")
        for element in lista_sucesores:

            # print("element",element,lista_sucesores[element])
            if element not in lista_total_sucesores:
                lista_total_sucesores.append(element)
            grupo = lista_sucesores[element]

            # print("grupo",grupo)
            for item in grupo:
                # if item not in lista_total_sucesores:
                lista_total_sucesores.append(item)

        # lista_total_sucesores.append(lista_sucesores[element][0])
        # print("la lista total de sucesores es dentro debdskfksf" ,lista_total_sucesores)
    if lista_total_sucesores:
        for nodo in lista_nodos:
            if nodo in lista_total_sucesores:
                lista_total_sucesores.remove(nodo)
    # print("regresaremos de la funcion ")
    return lista_total_sucesores


class ListBasedMapping:

    def __init__(self, DG, AG, datapaths_independientes, dict_nodes,
                 dict_info, selection_prints, dict_nodes_a, selection_pause, dict_info_a, DG_total, AG_total,
                 dict_total, debugging_options, lista_constraints, lista_tareas_constrains, all_topological,
                 topological_app, topological_hw, list_selection, recomputation_enable):

        # FLOW DIAGRAM 1
        self.AG_total = AG_total.copy()
        self.dict_total = dict_total
        self.debugging_options = debugging_options
        self.s_pause = selection_pause
        self.AG = AG.copy()
        self.DG = DG.copy()
        self.DG_total = DG_total
        self.dict_nodes = dict_nodes
        self.dict_info = dict_info
        self.dict_nodes_a = dict_nodes_a
        self.dict_info_a = dict_info_a
        self.lista_constraints = lista_constraints
        self.lista_tareas_constrains = lista_tareas_constrains
        self.all_topological = all_topological
        self.list_selection = list_selection
        self.recomputation_enable = recomputation_enable
        if all_topological:
            self.topological_app = topological_app
            self.topological_hw = topological_hw

        self.s_prints = selection_prints
        self.DG_copy = DG.copy()
        self.DG_original = DG.copy()
        self.AG_original = AG.copy()
        self.list_sinks_connected_to_rc = self.sinks_connected_to_rc()
        self.AG_copy = AG.copy()
        self.AG_copia = AG.copy()

        # FLOW DIAGRAM 2
        self.datapaths_independientes = datapaths_independientes
        # print(self.datapaths_independientes)
        self.datapaths_independientes = self.generation_datapaths(self.DG_original)

        # FLOW DIAGRAM 3
        self.lista_final, self.vector_config_01, self.vector_config_02 = self.Mapping()

        if self.s_prints == 'debug' or self.s_prints == 'list' or self.s_prints == 'basic':
            print(self.lista_final)
            print(self.lista_nodos_especiales_final)
            # print(self.lista_nodos_especiales)
            print("end of mapping")

    def generation_datapaths(self, input_graph):
        """genera los datapaths independientes, el proceso es sobre un grafo de hardware checamos los nodos que tienen
        un recurso con dos output edges y que uno de ellos va hacia un recurso con dos input edges, entonces removemos
        uno de esos edges y con eso podemos generar otro datapath independiente, luego del preprocesamiento del grafo
        iniciamos ya la busqueda de los datapaths"""

        # vamos a cambiar el codigo y poner el grafo total
        lista_paths = []
        lista_nodos_ocupados_sink = []
        lista_nodos_ocupados_source = []
        nodos_ocupados = []
        """"in here we obtain simple datapaths, for the mapping"""
        ####procesamiento previo, aqui removemos ciertos edges
        copia_DG_proceso_previo = input_graph.copy()
        for nodo in copia_DG_proceso_previo.nodes:
            # si el nodo tiene mas de un output edge
            if copia_DG_proceso_previo.out_degree(nodo) > 1:
                # print("el nodo tiene un grado mayor de dos ", nodo)
                # obtenemos sus sucesores
                sucesores = copia_DG_proceso_previo.successors(nodo)
                for suc in sucesores:
                    # si el sucesor tiene input degree mayor de uno
                    if copia_DG_proceso_previo.in_degree(suc) > 1:
                        # print("estamos por remover un edge")
                        # removemos el edge
                        copia_DG_proceso_previo.remove_edge(nodo, suc)
                        break
        sources_test = obtencion_sources(copia_DG_proceso_previo)
        sinks_test = self.list_sinks_connected_to_rc
        # sinks_test = obtencion_sinks(copia_DG_proceso_previo)
        # aqui ya obtenemos los datapaths independientes de acuerdo al proceso antiguo
        for source in sources_test:
            for sink in sinks_test:
                paths = nx.all_simple_paths(copia_DG_proceso_previo, source=source, target=sink)
                todos_los_paths = list(paths)
                if todos_los_paths:
                    # lista_paths.append(todos_los_paths[0])
                    vector = []
                    if not sink in lista_nodos_ocupados_sink and not source in lista_nodos_ocupados_source:
                        for i in range(len(todos_los_paths)):
                            for nodo in todos_los_paths[i]:
                                if nodo in nodos_ocupados:
                                    vector.append(False)
                            if not False in vector:
                                lista_paths.append(todos_los_paths[i])
                                lista_nodos_ocupados_sink.append(sink)
                                lista_nodos_ocupados_source.append(source)
                                nodos_ocupados = nodos_ocupados + todos_los_paths[i]

        # print("checaremos la nueva forma de obtener los datapaths ", lista_paths)
        lista_paths_respaldo = lista_paths.copy()
        return lista_paths_respaldo

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
        return list_sinks_connected_to_rc

    def degree_verification(self, nodo_AG, selected_resource, lista_salida_memoria):
        # caso de input degree
        if self.s_prints == 'list':
            print(("we are going to check the degree of the resource"))
        input_degree_flag = False
        if self.DG_original.in_degree(selected_resource) == self.AG.in_degree(nodo_AG):
            input_degree_flag = True
        elif self.DG_original.in_degree(selected_resource) > self.AG.in_degree(nodo_AG):
            predecesores_tarea = self.AG.predecessors(nodo_AG)
            predecesores_recurso = self.DG_original.predecessors(selected_resource)
            for pr in predecesores_recurso:

                if lista_salida_memoria[pr][0] and lista_salida_memoria[pr][
                    1] not in predecesores_tarea:
                    input_degree_flag = False
                    break
                else:
                    input_degree_flag = True
        elif self.DG_original.in_degree(selected_resource) == 0:
            input_degree_flag = True
        # caso de output degree
        output_degree_flag = False
        if self.DG_original.out_degree(selected_resource) >= self.AG.out_degree(nodo_AG):
            if self.s_prints == 'list':
                print("test modificacion de grados 1")
            output_degree_flag = True
        else:
            sucesor_degree = self.DG_original.successors(selected_resource)
            conteo_sucesores = self.DG_original.out_degree(selected_resource)
            for su in sucesor_degree:
                conteo_sucesores = conteo_sucesores + self.DG_original.out_degree(su)
            conteo_predecesores = self.DG_original.in_degree(
                selected_resource)
            predecesor_degree = self.DG_original.predecessors(selected_resource)
            for pr in predecesor_degree:
                conteo_predecesores = conteo_predecesores + self.DG_original.in_degree(pr)
            if conteo_sucesores >= self.AG.out_degree(
                    nodo_AG) and conteo_predecesores >= self.AG.in_degree(nodo_AG):
                output_degree_flag = True
            else:
                if self.DG_original.out_degree(selected_resource) == 0:
                    output_degree_flag = True
                else:
                    output_degree_flag = False
            if self.s_prints == 'list':
                print("test modificacion de grados 2", conteo_sucesores, conteo_predecesores,
                      output_degree_flag)
        test_degree = output_degree_flag and input_degree_flag
        if self.s_prints == 'basic' or self.s_prints == 'list':
            print(
                f"degree flag {test_degree},  "
                f"input degree flag {input_degree_flag} and the ouput degree flag {output_degree_flag}")
        return test_degree

    def verification_of_parameters_succcesors(self, node_AG, resource):

        # print("entering the verificacation of parameters")
        successors_application = list(self.AG.successors(node_AG))
        successors_hardware = obtencion_sucesores_de_una_lista(self.DG, [resource])
        if self.s_prints == 'list':
            print(successors_application, successors_hardware)
        validation_total = []
        if len(successors_hardware) > 1:
            for suc_task in successors_application:
                validation_per_task = []
                for des_resource in successors_hardware:
                    try:
                        validation_resource = self.verification_of_parameters(suc_task, des_resource)
                        if all(validation_resource):
                            validation_per_task.append(True)
                        else:
                            validation_per_task.append(False)
                    except:
                        validation_per_task.append(False)
                if any(validation_per_task):
                    validation_total.append(True)
                else:
                    validation_total.append(False)
        else:
            validation_total.append(True)

        # print(validation_total)
        if all(validation_total):
            return True
        else:
            ###### there is an error that happens when the resources does not have a lot of descendants so if the
            # resource has a path to a sink node we still return True
            return False

    def verification_of_parameters(self, node_AG, resource):

        try:
            test_01 = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']
        except:
            if self.s_prints == 'list':
                print(f"A possible error in the constrain file occurred, as this part is verified otherwise")
            raise ValueError(
                f"The task name is {self.AG_copia.nodes[node_AG]['name']}, please verify the constrains file")

        if self.s_prints == 'basic':
            print("ENTRADA A VERIFICAFION DE PARAMETROS FOR ", resource)
        new_validacion_parameters = []
        # for each parameter of the task, we check if the values are correct
        if self.s_prints == 'basic':
            print(self.AG_copia.nodes[node_AG])
            print(self.dict_nodes[resource]['name'], self.dict_nodes[resource]['ops'])
        try:
            if self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'] == None:
                new_validacion_parameters.append(True)
            else:

                for param in self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']:
                    if self.s_prints == 'basic':
                        print(param)
                    # we check if the parameters values are a range of values of a set of fixed values
                    if isinstance(
                            self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0],
                            str):
                        # for this case the parameters are a set of fixed values
                        # first we grab all the values
                        vector_param_values = []
                        if len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                   param]) != 0:
                            if self.s_prints == 'basic':
                                print("solo un elemento",
                                      self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                          param])
                                if self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                    param] == "down":
                                    print(" es dozn")

                                print(
                                    len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']))
                                print(len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                              param]))
                        es_integer = False
                        try:
                            dummy_variable = int(
                                self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0])
                            es_integer = True
                        except:
                            pass

                        if len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][
                                   0]) == 1 and not es_integer:
                            vector_buffer = [
                                self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]]
                        else:
                            vector_buffer = \
                            self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]
                        for param_value in vector_buffer:  # self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]:
                            try:
                                vector_param_values.append(int(param_value))
                            except:
                                vector_param_values.append(param_value)
                        if vector_param_values == ['boolean']:
                            vector_param_values = ['False', 'True']
                            if self.s_prints == 'basic':
                                print("imrpresion de algo enononfsd", vector_param_values)
                                print(self.dict_nodes_a)
                        # we got the values, so we check if the value that we want to assign to this resource is valid
                        if self.s_prints == 'basic':
                            if vector_param_values == ['boolean']:
                                print("OJNDSJFNSDNFOSD", param, self.dict_nodes_a[node_AG]['param'])
                        if param in self.dict_nodes_a[node_AG]['param']:
                            if self.s_prints == 'basic':
                                print("entrada a ciclo de algo", self.dict_nodes_a[node_AG]['param'][param],
                                      vector_param_values)
                            if self.dict_nodes_a[node_AG]['param'][param] in vector_param_values:
                                new_validacion_parameters.append(True)
                                if self.s_prints == 'basic':
                                    print("the value is valid")
                            else:
                                new_validacion_parameters.append(False)
                                if self.s_prints == 'basic':
                                    print("the value is not valid")
                        else:
                            raise UnboundLocalError(
                                f"parameter {param} is not described in the parameters of task {self.dict_nodes_a[node_AG]['name']}")
                    else:
                        if self.s_prints == 'basic':
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
        except:
            new_validacion_parameters.append(False)

        if self.s_prints == 'basic':
            print("la validacion de parametros ha terminado", new_validacion_parameters)
        return new_validacion_parameters

    def verification_of_source(self, node_AG, resource):
        bandera_source_of_data = False
        info_sensor = []
        if self.s_prints == 'basic':
            print("ANOTHER CHANGE 01")
            print(self.lista_sources_AG)
        if node_AG in self.lista_sources_AG:
            if self.s_prints == 'basic':
                print("it is a source node")
                # print(self.dict_nodes_a)
                # print(self.dict_info_a)
                # print(self.dict_total)
                # print(self.dict_nodes)
            lugar_nodo = None
            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         lugar_nodo)
            # print("verificacion de datos", self.AG_total.nodes[source_total_app]['par']['height'])
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
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
        else:
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            if node_AG in lista_sources_ag_total:
                source_total_app = node_AG
            else:
                source_total_app = source_node_from_any_node(self.AG_total,
                                                             lista_sources_ag_total,
                                                             node_AG)

            # print(self.AG_total.nodes[source_total_app])
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
            bandera_source_of_data = True
        # print(info_sensor)
        return bandera_source_of_data, info_sensor

    def variable_separation(self, function_formula):
        contador_linea = 0
        bandera_primera_vez_letra = True
        vector_parametro = []
        vector_total_parametros = []
        for letra in function_formula:
            # print(letra,contador_linea,len(function_formula))
            if bandera_primera_vez_letra:
                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
                    pass
                else:
                    vector_parametro.append(letra)
                    bandera_primera_vez_letra = False
            else:
                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ' or contador_linea == len(
                        function_formula):
                    # print(vector_parametro)
                    vector_total_parametros.append(vector_parametro)
                    vector_parametro = []
                else:
                    if contador_linea == len(function_formula) - 1:

                        vector_parametro.append(letra)
                        vector_total_parametros.append(vector_parametro)
                    else:
                        vector_parametro.append(letra)
            contador_linea = contador_linea + 1
        return vector_total_parametros

    def verificacion_path_a_sink(self, lista_salida_memoria, nodo_AG, resource):
        if self.s_prints == 'list':
            print("estamos en la verificacion de path a sink")
        bandera_sink = False
        for sink in self.list_sinks_connected_to_rc:

            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                      resource,
                                                      sink)
            # if simple_path
            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
            vector_verificacion_no_mapeo_02 = []  ######por cada path
            # print("dentro de funcion",sink,simple_path)
            # time.sleep(5)
            if self.s_prints == 'list':
                print(simple_path)
            if simple_path:
                while simple_path:
                    path_b = min(simple_path, key=len)
                    paths_copy = simple_path.copy()
                    for i in range(0, len(paths_copy)):
                        if paths_copy[i] == path_b:
                            dummy = simple_path.pop(i)
                    path = list(path_b)
                    if resource in path:
                        path.remove(resource)
                    bandera_salida = False
                    vector_verificacion_no_mapeo_01 = []
                    # esto es para indicar los nodos copy
                    path_buffer = list(path)
                    # if recurso_elegido in path_buffer:
                    #     path_buffer.remove(recurso_elegido)
                    vector_dependency_01 = []
                    if self.s_prints == 'list':
                        print("verificaremos el path ", path)
                    for node in path:
                        if self.s_prints == 'list':
                            print(lista_salida_memoria[node])
                        if lista_salida_memoria[node][0]:  # and self.lista_mapping[node][2] != 'copy':#

                            vector_dependency_01 = vector_dependency_01 + [
                                lista_salida_memoria[node][0]]
                    if self.s_prints == 'list':
                        print(vector_dependency_01)
                    if True in vector_dependency_01:
                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                    else:  #
                        return True

        return False

    def obtention_latency(self, resource, node_AG):
        """This function obtain both the input latency and the computing latency of a resource,
        and also we obtain the overall latency for a entire frame"""

        # we retrieve the name of the function of input latency, but because we may be using the constraints file
        # we can have an error if we are placing a task into a wrong resource, thats the purpose of the following
        # try, to catch that error and raise an error
        try:
            name_function = \
                self.dict_nodes[resource]['ops'][self.AG.nodes[node_AG]['op']]['latency']
        except:
            # print(f"the task is {self.AG.nodes[node_AG]['name']} and the resource is {self.dict_nodes[resource]['name']}")
            raise ValueError(
                f"An error occurred, possibly in the constraints file, as normally we verify this condition previously but not during the constraints mapping, the task is {self.AG.nodes[node_AG]['name']} and the resource is {self.dict_nodes[resource]['name']}")
        # print(name_function)

        # now, as we have the name of the function, we look for the equation itself, this search is in the dict_info which
        # is the one with all the functions
        for data in self.dict_info['functions_res']:
            # print(data)
            if data == name_function:
                function_formula = self.dict_info['functions_res'][data]
            # print(n)

        # now we have the name and the formula, we obtain the input data from the application
        if self.s_prints == 'basic':
            print(f"el nombre de la ecuacion es {name_function} y la ecuacion es {function_formula}")
        # another change, because we need the resolution we are going to obtain the resolution from
        # the interface sensor
        # first we obtain the interface node
        # for nodo in self.AG.nodes:
        #     print(self.AG.nodes[nodo])
        lugar_nodo = None
        for n, data in self.dict_info_a.items():
            if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                lugar_nodo = n
        lista_sources_ag_total = obtencion_sources(self.AG_total)
        source_total_app = source_node_from_any_node(self.AG_total, lista_sources_ag_total,
                                                     lugar_nodo)

        height = self.dict_info_a[source_total_app]['param']['height']
        width = self.dict_info_a[source_total_app]['param']['width']
        # we are going to autoasign the values of the parameters
        # print(self.dict_nodes_a)
        # print(function_formula)
        contador_parametros = 0
        bandera_primera_vez_letra = True
        vector_parametro = []
        vector_total_parametros = []
        # print(function_formula)
        contador_linea = 0
        # print(contador_linea)
        if isinstance(function_formula, str):
            vector_total_parametros = self.variable_separation(function_formula)
            # for letra in function_formula:
            #     # print(letra,contador_linea,len(function_formula))
            #     if bandera_primera_vez_letra:
            #         if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ':
            #             pass
            #         else:
            #             vector_parametro.append(letra)
            #             bandera_primera_vez_letra = False
            #     else:
            #         if letra == '(' or letra == ')' or letra == '*' or letra == '+' or letra == '/' or letra == '-' or letra == ' ' or contador_linea == len(function_formula) :
            #             # print(vector_parametro)
            #             vector_total_parametros.append(vector_parametro)
            #             vector_parametro = []
            #         else:
            #             if contador_linea == len(function_formula) - 1:
            #
            #                 vector_parametro.append(letra)
            #                 vector_total_parametros.append(vector_parametro)
            #             else:
            #                 vector_parametro.append(letra)
            #     contador_linea = contador_linea + 1
        vector_parametro = []
        # print(vector_total_parametros)
        for it in vector_total_parametros:
            dummy = "".join(it)
            if dummy:
                try:
                    int(dummy)
                except:
                    if dummy not in vector_parametro:
                        vector_parametro.append(dummy)

        ### we first look for the general values of width and height
        # print(f"el vector parametro es {vector_parametro}")
        for param_formula in vector_parametro:
            # print("debug de algun error",param_formula)
            if param_formula == 'width':
                pass
            elif param_formula == 'height':
                pass
            else:
                # in here we are going to look the value in the dict of the nodes
                for pa in self.dict_nodes_a[node_AG]['param']:
                    # print(pa)
                    if param_formula == pa:
                        globals()[pa] = self.dict_nodes_a[node_AG]['param'][pa]
        # finally we evaluate the formula with the input and store the result in the results list
        name_clk = self.dict_nodes[resource][
            'ops'][
            self.AG.nodes[node_AG]['op']][
            'clk']
        if self.s_prints == 'basic':
            print("we are going to print the dict info")
            print(self.dict_info)
            print("the print of the dict info is finished")
            print("now we are going to print the dict total")
            print(self.dict_total)
            print("we finished printing the dict total")
        value_clk = None
        for el in self.dict_info['functions_res']:
            if el == name_clk:
                value_clk = self.dict_info['functions_res'][el]

        # print(self.dict_info)
        # value_clk = self.dict_info['max_clk']
        if value_clk == None:
            raise UnboundLocalError(
                f"Parameter {name_clk} is not described in the functions section")

        # if self.debugging_options == 'perf_clock':
        #     value_clk = self.dict_info['max_clk']
        # else:
        value_clk = value_clk

        if self.s_prints == 'basic':
            print("vamos a evaluar la funcion de latencia")
            print(value_clk)
            print(self.dict_nodes)
            # print(self.dict_info)
            try:
                print(eval(value_clk))
            except:
                pass

        ######ahora obtendremos el valor de la latencia de computo, debido a que puede ser una ecuacion o una
        # constante necesitamos hacer una verificacion previa y tambien sacar los valores
        # normalmente ya tenemos la ecuacion, entonces es separarla y asignar valores
        if isinstance(value_clk, str):
            # si la latencia de computacion es una ecuacion
            print("LA LATENCIA DE COMPUTO ES UNA ECUACION")
            vector_total_parametros = self.variable_separation(value_clk)
            vector_parametro = []
            # print(vector_total_parametros)
            for it in vector_total_parametros:
                dummy = "".join(it)
                if dummy:
                    try:
                        int(dummy)
                    except:
                        if dummy not in vector_parametro:
                            vector_parametro.append(dummy)

            ### we first look for the general values of width and height
            print(f"el vector parametro es {vector_parametro}")
            for param_formula in vector_parametro:
                # print("debug de algun error",param_formula)
                if param_formula == 'width':
                    pass
                elif param_formula == 'height':
                    pass
                else:
                    # in here we are going to look the value in the dict of the nodes
                    for pa in self.dict_nodes_a[node_AG]['param']:
                        # print(pa)
                        if param_formula == pa:
                            globals()[pa] = self.dict_nodes_a[node_AG]['param'][pa]
            value_clk = eval(value_clk)
            print("EL VALOR DE LA ECUACION ES ", value_clk)
        else:
            value_clk = value_clk

        if isinstance(function_formula, str):
            resultado_latencia = eval(function_formula) * self.dict_info['max_clk'] + value_clk
        else:
            resultado_latencia = function_formula * self.dict_info['max_clk'] + value_clk
        resultado_latencia_total = width * height * self.dict_info['max_clk']

        return resultado_latencia, resultado_latencia_total

    def Mapping(self):

        # FLOW DIAGRAM 3.1
        # we verify if we are using all topological sortings we use the input sorting if not we use one that we obtain
        if self.all_topological:
            lista_DG = self.topological_hw
            lista_AG = self.topological_app
        else:
            lista_DG = list(nx.topological_sort(self.DG_copy))
            lista_AG = list(nx.topological_sort(self.AG_copy))

        if self.s_prints == 'basic' or self.s_prints == 'list':
            print("hardware info")
            for nodo in self.DG_copy.nodes:
                print(nodo, self.DG_copy.nodes[nodo])
            print("app info")
            for nodo in self.AG_copy.nodes:
                print(nodo, self.AG_copy.nodes[nodo])
            print(f"topological sorting hw {lista_DG}")
            print(f"topological sorting app {lista_AG}")
            print(f"datapaths {self.datapaths_independientes}")
            dummy_print_dg = []
            for nd in lista_DG:
                dummy_print_dg.append(self.dict_nodes[nd]['name'])
            dummy_print_ag = []
            for nd in lista_AG:
                dummy_print_ag.append(self.dict_nodes_a[nd]['name'])
            print(f"We obtain the topological sorting of GAPP which is {dummy_print_ag} ")
            print(f"We obtain the topological sorting of GHW which is {dummy_print_dg} ")
            # input("test")
        #####important variable, we use it throughout the algorithm, from this list we select the resources
        self.lista_topo_DG_copy = lista_DG.copy()

        # list of variables misc
        # FLOW DIAGRAM 3.2
        self.contador_time_slots = 0
        _lista_posible = None
        self.lista_en_time_slots = False
        self.lista_nodos_copy = []
        self.lista_nodos_ocupados_source = []
        self.lista_nodos_ocupados_sinks = []
        self.lista_AG_copy = list(lista_AG)

        bandera_recomputo = False
        self.counter = 0
        self.lista_nodos_ya_mapeados = []

        copia_DG = self.DG_copy.copy()
        self.vector_de_parejas_memoria = []
        bandera_reinicio = False
        bandera_primer_nodo = True
        bandera_solo_un_nodo = False
        mapping = True
        vector_nodos_especiales = []
        bandera_nodo_especial = False
        lista_nodos_especiales = []
        contador_reinicios = 0
        bandera_source = False
        bandera_caso_no_probabilidad = False
        vector_buffer_especiales = []
        vector_nodo_especial_predecesor = []
        lista_final = []
        self.contador_instancias = 0
        self.lista_predecesores_01 = []
        self.lista_nodos_especiales = []
        self.lista_nodos_especiales_final = []
        self.contador_recomputacion = 0
        self.sinks_para_asignar = obtencion_sinks(self.AG_total)
        # changes 20112019
        backtrack_flag = True
        bandera_no_match_parameters = False
        #######################
        self.lista_nodos_time_slot_anterior = []

        # important variable where the preliminary mapping will be stored
        lista_salida_memoria = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                range(0, len(self.DG_copy))]

        # listas of sinks and sources, we are going to need them during the mapping
        self.lista_sinks_DG = obtencion_sinks(self.DG_copy)
        self.lista_sources_DG = obtencion_sources(self.DG_copy)
        self.lista_sinks_AG = obtencion_sinks(self.AG_copy)
        self.lista_sources_AG = obtencion_sources(self.AG_copy)
        # datos del grafo total
        self.lista_sinks_DG_total = obtencion_sinks(self.DG_total)
        self.lista_sources_DG_total = obtencion_sources(self.DG_total)

        # this is part of the heuristic mapping todo try to chance this part
        primer_grupo = self.lista_sources_DG.copy()  # obtencion_sources(self.DG_copy)
        primer_grupo_buffer = primer_grupo.copy()
        # print(self.lista_sources_DG,primer_grupo_buffer)
        # input(" debug error heterogenous")
        primer_grupo = primer_grupo.pop()
        # primer_grupo_buffer.remove(primer_grupo)
        #################changes of 19/04/2021, we are going to change how we select the resource to use, previously
        # it was like the heuristic, now we try to use the same approach as the old list-based
        primer_grupo = self.lista_topo_DG_copy.pop(0)
        primer_grupo_buffer = primer_grupo


        primera_vez = True
        if self.s_prints == 'basic' or self.s_prints == 'list':
            print(
                f"The first set of possible candidates are {self.dict_nodes[primer_grupo]['name']} , {primer_grupo_buffer}")
        elif self.s_prints == 'debug':
            print("the first set of possible candidates are ", primer_grupo, primer_grupo_buffer)
        # input("debug error")
        # Start of the mapping
        if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter':
            print("------------------------------------------------------------")
            print("list-based algorithm")
            print("We are going to start the mapping")
            print("------------------------------------------------------------")
        if self.s_pause:
            input("Press Enter to continue...")

        counter_iter = 0
        # FLOW DIAGRAM 3.3
        while self.lista_AG_copy:
            contador_datapaths = 0
            # we select the task to map

            # FLOW DIAGRAM 3.3.1
            nodo_AG = self.lista_AG_copy.pop(0)
            #############if we want to debug the previous mapping
            # if self.s_prints == 'list':
            #     if nodo_AG == 5:
            #         input("debug of the previous mapping")
            self.tarea_a_mapear_global = nodo_AG
            bandera_no_conexion = False
            # obtention of the operation of the task
            task_AG = self.AG_copy.nodes[nodo_AG]['op']
            # obtention of the successors of the task
            sucesores_nodo_AG = list(self.AG_copy.successors(nodo_AG))
            mapping = True
            self.counter = 0
            name_task = self.dict_nodes_a[nodo_AG]['name']

            if self.s_prints == 'basic' or self.s_prints == 'list':
                print("BEGIN OF A NEW TASK MAPPING ", nodo_AG, name_task)
                # input("Enter to continue ...")
            # FLOW DIAGRAM 3.3.2
            # if we have any constrains we enter this cycle
            if name_task in self.lista_tareas_constrains:

                ###### FLOW DIAGRAM 3.3.2.1
                if self.s_prints == 'basic':
                    print("inicio de constrains")
                    print(f"las constrains son {self.lista_tareas_constrains}")
                # we search for the info of the resource and the task
                name_resource = None
                for parejas in self.lista_constraints:
                    if parejas[0] == name_task:
                        name_resource = parejas[1]
                resource = None
                for n, data in self.dict_nodes.items():
                    if name_resource == data['name']:
                        resource = n
                if self.s_prints == 'basic':
                    print(resource, name_task)
                # we need to improve this part
                # ya tenemos toda la informacion del recurso y de la tarea
                # print("iniciaremos otra iteracion")
                # print(resource,name_resource,nodo_AG,name_task)

                # FLOW DIAGRAM 3.3.2.2
                # this section defines if we starting a new time slot, if so we can go back to the previous time
                # slot and try to see if we can use it
                bandera_posible_reuso = False
                vector_todos_mapeados = []
                for nodo_map in lista_salida_memoria:
                    if nodo_map[0] and nodo_map[2] != 'copy':
                        vector_todos_mapeados.append(False)
                    else:
                        vector_todos_mapeados.append(True)
                if resource in self.lista_nodos_time_slot_anterior and all(vector_todos_mapeados):
                    # esto quiere decir que el nuevo time slot esta vacio y que podemos utilizar el anterior time slot
                    if self.s_prints == 'basic':
                        print("VEREMOS LAS PAREJAS", self.vector_de_parejas_memoria)
                    numero_parejas = len(self.vector_de_parejas_memoria)
                    for elemento in range(0, numero_parejas):
                        if nodo_AG == self.vector_de_parejas_memoria[elemento][0]:
                            self.vector_de_parejas_memoria.pop(elemento)
                    lista_salida_memoria = lista_final.pop()

                # now that we have check which time slot we can use we continue to the mapping of the task
                # FLOW DIAGRAM 3.3.2.3
                if nodo_AG in self.lista_sources_AG:
                    # print("la tarea es un source node")

                    # FLOW DIAGRAM 3.3.2.3.1
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':

                        # FLOW DIAGRAM 3.3.2.3.1.1
                        if self.s_prints == 'list':
                            print("lk,lkncncxx no more resource")
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, \
                        lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, \
                        bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)

                        # FLOW DIAGRAM 3.3.2.3.1.2
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("we are at stage 1 step 1 x")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'basic' or self.s_prints == 'iter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'basic':
                            print("modulo 01 - debug")

                        # FLOW DIAGRAM 3.3.2.3.1.3
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'basic' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes
                        # FLOW DIAGRAM 3.3.2.3.1.4
                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)
                        # FLOW DIAGRAM 3.3.2.3.1.5
                        info_actuator = self.info_actuator_generator(nodo_AG)
                        # FLOW DIAGRAM 3.3.2.3.1.6
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # print("mapearemos algo")
                        # FLOW DIAGRAM 3.3.2.3.1.7
                        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                          self.AG.nodes[nodo_AG]['op'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'latency'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'clk'], resultado_latencia,
                                                          resultado_latencia_total, info_sensor, info_actuator,
                                                          actuator_sink
                                                          ]

                        # we keep track of the tasks that we map

                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                        if self.s_prints == 'basic' or self.s_prints == 'list':
                            print(self.DG_copy.nodes)
                            print("jndsijfsd", self.lista_predecesores_01)
                            print("la lista de salida es ", lista_salida_memoria)
                        # self.generation_special_nodes(nodo_AG, resource, lista_final)

                        # FLOW DIAGRAM 3.3.2.3.1.8
                        if len(self.lista_AG_copy) > 0:
                            if self.s_prints == 'debug':
                                print("there is more tasks to map ")

                            if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                bandera_no_conexion = False
                            else:
                                if self.s_prints == 'basic' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 02")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'basic':
                            input("Press Enter to continue...")

                        # FLOW DIAGRAM 3.3.2.3.1.9
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # FLOW DIAGRAM 3.3.2.3.1.10
                        nueva_lista_primer_grupo = []
                        if self.lista_AG_copy:
                            ###obtenemos los predecesores de la siguiente tarea:
                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                            nueva_lista_primer_grupo = []
                            for predecesor in predecesores:
                                lugar_mapeado = None
                                for lugar in lista_salida_memoria:
                                    if lugar[1] == predecesor:
                                        lugar_mapeado = lugar[2]
                                if lugar_mapeado != None:
                                    nueva_lista_primer_grupo = list(set(
                                        nueva_lista_primer_grupo + (list(self.DG_original.successors(lugar_mapeado)))))
                            lista_final_primer_grupo = []
                            for posible in nueva_lista_primer_grupo:
                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                    2] != 'copy':
                                    pass
                                else:
                                    lista_final_primer_grupo.append(posible)
                        if self.s_prints == 'basic':
                            print("LA NUEVA LISTA DE CANDIDATOS ES 01", lista_final_primer_grupo)

                        primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                        # FLOW DIAGRAM 3.3.2.3.1.11
                        if not primer_grupo:
                            # we call the function that verifies the datapaths
                            if self.s_prints == 'list':
                                print("odjfosdf no more resources")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                            primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                            vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths \
                                = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                        primer_grupo_buffer = primer_grupo.copy()
                    else:

                        # FLOW DIAGRAM 3.3.2.3.1.2
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("we are at stage 1 step 1 l")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'basic' or self.s_prints == 'iter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'basic':
                            print("modulo 02 - debug")
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'basic' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # print("mapearemos algo")
                        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                          self.AG.nodes[nodo_AG]['op'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'latency'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'clk'], resultado_latencia,
                                                          resultado_latencia_total, info_sensor, info_actuator,
                                                          actuator_sink
                                                          ]

                        # we keep track of the tasks that we map
                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                        if self.s_prints == 'basic':
                            print(self.DG_copy.nodes)
                            print("jndsijfsd", self.lista_predecesores_01)
                            print("la lista de salida es ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        # self.generation_special_nodes(nodo_AG, resource, lista_final)
                        # now we check if there are still tasks to map
                        # and if the following task is a successor of the newly mapped task
                        if len(self.lista_AG_copy) > 0:
                            if self.s_prints == 'debug':
                                print("there is more tasks to map ")
                            # verification of the conexion between the following task and the newly mapped one
                            # bandera_no_conexion activated (True) means that there is no connection, but False
                            # means that there is a connection
                            if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                bandera_no_conexion = False
                            else:
                                if self.s_prints == 'basic' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 03")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'basic':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        nueva_lista_primer_grupo = []
                        if self.lista_AG_copy:
                            ###obtenemos los predecesores de la siguiente tarea:
                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                            nueva_lista_primer_grupo = []
                            for predecesor in predecesores:
                                lugar_mapeado = None
                                for lugar in lista_salida_memoria:
                                    if lugar[1] == predecesor:
                                        lugar_mapeado = lugar[2]
                                if lugar_mapeado != None:
                                    nueva_lista_primer_grupo = list(set(
                                        nueva_lista_primer_grupo + (list(self.DG_original.successors(lugar_mapeado)))))
                            lista_final_primer_grupo = []
                            for posible in nueva_lista_primer_grupo:
                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                    2] != 'copy':
                                    pass
                                else:
                                    lista_final_primer_grupo.append(posible)
                            lista_final_primer_grupo = []
                            for posible in nueva_lista_primer_grupo:
                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                    2] != 'copy':
                                    pass
                                else:
                                    lista_final_primer_grupo.append(posible)
                        if self.s_prints == 'basic':
                            print("LA NUEVA LISTA DE CANDIDATOS ES 02", lista_final_primer_grupo)

                        primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))

                        if not primer_grupo:
                            # we call the function that verifies the datapaths
                            if self.s_prints == 'list':
                                print("aaeaezaz no more resources")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False

                elif nodo_AG in self.lista_sinks_AG:
                    # print("la tarea es un sink node")
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':
                        if self.s_prints == 'list':
                            print("sjfjdf no more resources qqaaaq")
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("we are at stage 1 step 1 t")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'basic' or self.s_prints == 'iter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'basic':
                            print("modulo 03 - debug")
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'basic' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # print("mapearemos algo")
                        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                          self.AG.nodes[nodo_AG]['op'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'latency'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'clk'], resultado_latencia,
                                                          resultado_latencia_total, info_sensor, info_actuator,
                                                          actuator_sink
                                                          ]

                        # we keep track of the tasks that we map
                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                        if self.s_prints == 'basic':
                            print(self.DG_copy.nodes)
                            print("jndsijfsd", self.lista_predecesores_01)
                            print("la lista de salida es ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final, lista_salida_memoria)

                        bandera_no_conexion = False
                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'basic':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task

                        elif not sucesores_nodo_AG or bandera_no_conexion:
                            # print("ciclo elif de algo")
                            if self.s_prints == 'list':
                                print("odlfojdsjdf e,ntrada no more resources")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                        else:
                            # in this part we only update the first group of candidates, because there are still
                            # resources and tasks
                            # print("ciclo else de algo")
                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)

                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                ###obtenemos los predecesores de la siguiente tarea:
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = list(set(nueva_lista_primer_grupo + (
                                            list(self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'basic':
                                print("LA NUEVA LISTA DE CANDIDATOS ES 03", lista_final_primer_grupo)

                            primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            if self.s_prints == 'list':
                                print("BUGG Nbbbbbbbbbb")
                                print(primer_grupo)
                            if not primer_grupo:
                                # we call the function that verifies the datapaths
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                    else:

                        # print("bugg 01", self.DG_copy.nodes)
                        self.DG_copy = self.DG_original.copy()
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("we are at stage 1 step 1 h")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'basic' or self.s_prints == 'iter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'basic':
                            print("modulo 04 - debug")
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'basic' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # print("mapearemos algo")
                        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                          self.AG.nodes[nodo_AG]['op'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'latency'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'clk'], resultado_latencia,
                                                          resultado_latencia_total, info_sensor, info_actuator,
                                                          actuator_sink
                                                          ]

                        # we keep track of the tasks that we map
                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                        if self.s_prints == 'basic':
                            print(self.DG_copy.nodes)
                            print("jndsijfsd", self.lista_predecesores_01)
                            print("la lista de salida es ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final, lista_salida_memoria)

                        bandera_no_conexion = False
                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'basic':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task

                        elif not sucesores_nodo_AG and bandera_no_conexion:
                            # print("ciclo elif de algo")
                            if self.s_prints == 'list':
                                print("vamos a entrar a no more resources 78545521")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                            bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                            contador_datapaths = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)



                        else:
                            # in this part we only update the first group of candidates, because there are still
                            # resources and tasks
                            # print("ciclo else de algo")
                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)

                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                ###obtenemos los predecesores de la siguiente tarea:
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = \
                                            list(set(nueva_lista_primer_grupo +
                                                     (list(self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'basic':
                                print("LA NUEVA LISTA DE CANDIDATOS ES 04", lista_final_primer_grupo)

                            primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            if self.s_prints == 'list':
                                print("BUGG uuuuN")
                                print(primer_grupo)
                            if not primer_grupo:
                                # we call the function that verifies the datapaths
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                else:
                    # print("otro tipo de nodo")
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':
                        # print("no espacio")
                        if self.s_prints == 'list':
                            print("vamos a entrar a no more resources 7856")
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, \
                        bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)
                        # print("es otro tipo de nodo luego del reinicio")
                        if resource not in self.DG_copy.nodes:
                            bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad \
                                = self.reinicio_time_slot(
                                lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                                vector_nodos_especiales, bandera_caso_no_probabilidad)
                            bandera_recomputo = False

                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("we are at stage 1 step 1 f")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'basic' or self.s_prints == 'iter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'basic':
                            print("modulo 05 - debug")
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'basic' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes

                        # print("bandera_recomputo", bandera_recomputo)
                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)
                        # print(bandera_mapping_valido,self.lista_en_time_slots)
                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # print("mapearemos algo", lista_salida_memoria)
                        # print(lista_final)
                        # print(self.lista_en_time_slots)
                        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                          self.AG.nodes[nodo_AG]['op'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'latency'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.AG.nodes[nodo_AG]['par'],
                                                          self.dict_nodes[
                                                              resource][
                                                              'ops'][
                                                              self.AG.nodes[nodo_AG]['op']][
                                                              'clk'], resultado_latencia,
                                                          resultado_latencia_total, info_sensor, info_actuator,
                                                          actuator_sink
                                                          ]

                        # we keep track of the tasks that we map
                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                        if self.s_prints == 'basic':
                            print(self.DG_copy.nodes)
                            print("jndsijfsd", self.lista_predecesores_01)
                            print("la lista de salida es ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final, lista_salida_memoria)
                        # now we check if there are still tasks to map
                        # and if the following task is a successor of the newly mapped task
                        if len(self.lista_AG_copy) > 0:
                            if self.s_prints == 'debug':
                                print("there is more tasks to map ")
                            # verification of the conexion between the following task and the newly mapped one
                            # bandera_no_conexion activated (True) means that there is no connection, but False
                            # means that there is a connection
                            if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                bandera_no_conexion = False
                            else:
                                if self.s_prints == 'basic' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 05")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'basic':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task
                        elif not sucesores_nodo_AG or bandera_no_conexion:
                            print("ciclo elif de algo 8554")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                            primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                            vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)
                        else:
                            # in this part we only update the first group of candidates, because there are still
                            # resources and tasks
                            # print("ciclo else de algo")
                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)

                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                ###obtenemos los predecesores de la siguiente tarea:
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = list(set(nueva_lista_primer_grupo
                                                                            + (list(
                                            self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'basic':
                                print("LA NUEVA LISTA DE CANDIDATOS ES 05", lista_final_primer_grupo)

                            primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            if self.s_prints == 'list':
                                print("BUGG Nllllll")
                                print(primer_grupo)
                            if not primer_grupo:
                                # we call the function that verifies the datapaths
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                    self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False



                    else:
                        if self.s_prints == 'basic':
                            print("es otro tipo de nodo")

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        if bandera_mapping_valido:
                            bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                            if self.s_prints == 'basic':
                                print("verificacion de sources ", bandera_source_of_data, info_sensor)

                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we are at stage 1 step 1 n")
                                print("we are going to map task ", nodo_AG, " to resource ", resource)
                            elif self.s_prints == 'basic' or self.s_prints == 'iter':
                                print(
                                    f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                                print("------------------------------------------------------------")
                            if self.s_pause:
                                input("Press Enter to continue...")
                            if self.s_prints == 'basic':
                                print("modulo 06 - debug")
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                # print(self.lista_nodos_copy)
                                # print(self.lista_nodos_copy_time)
                                print("we are going to map something so we need to add the copy nodes 03")
                                print(lista_final)

                            ######## aqui integramos todos los copy nodes

                            bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                       nodo_AG,
                                                                                       lista_salida_memoria,
                                                                                       lista_final, copia_DG,
                                                                                       bandera_recomputo)

                            info_actuator = self.info_actuator_generator(nodo_AG)
                            actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                          lista_salida_memoria,
                                                                                                          nodo_AG,
                                                                                                          resource)
                            # print("mapearemos algo")
                            lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                              self.AG.nodes[nodo_AG]['op'],
                                                              self.dict_nodes[
                                                                  resource][
                                                                  'ops'][
                                                                  self.AG.nodes[nodo_AG]['op']][
                                                                  'latency'],
                                                              self.AG.nodes[nodo_AG]['par'],
                                                              self.AG.nodes[nodo_AG]['par'],
                                                              self.dict_nodes[
                                                                  resource][
                                                                  'ops'][
                                                                  self.AG.nodes[nodo_AG]['op']][
                                                                  'clk'], resultado_latencia,
                                                              resultado_latencia_total, info_sensor, info_actuator,
                                                              actuator_sink
                                                              ]

                            # we keep track of the tasks that we map
                            self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                            if self.s_prints == 'basic':
                                print(self.DG_copy.nodes)
                                print("jndsijfsd", self.lista_predecesores_01)
                                print("la lista de salida es ", lista_salida_memoria)
                            # we proceed to create the special nodes, if necessary

                            self.generation_special_nodes(nodo_AG, resource, lista_final, lista_salida_memoria)
                            # now we check if there are still tasks to map
                            # and if the following task is a successor of the newly mapped task
                            if len(self.lista_AG_copy) > 0:
                                if self.s_prints == 'debug':
                                    print("there is more tasks to map ")
                                # verification of the conexion between the following task and the newly mapped one
                                # bandera_no_conexion activated (True) means that there is no connection, but False
                                # means that there is a connection
                                if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                    bandera_no_conexion = False
                                else:
                                    if self.s_prints == 'basic' or self.s_prints == 'debug':
                                        print(
                                            "there is no connection between the current mapped task and the next task 06")
                                    bandera_no_conexion = True
                                # deactivation of the recomputation flag
                                bandera_recomputo = False

                            # if there are no more tasks to map we end the mapping here
                            if self.s_pause and self.s_prints == 'basic':
                                input("Press Enter to continue...")
                            if not self.lista_AG_copy:
                                lista_final.append(lista_salida_memoria)

                            # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                            # is no more successors of the current task
                            elif not sucesores_nodo_AG or bandera_no_conexion:
                                if self.s_prints == 'list':
                                    print("ciclo elif de algo 785")
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                    self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)
                            else:
                                # in this part we only update the first group of candidates, because there are still
                                # resources and tasks
                                # print("ciclo else de algo")
                                if self.s_prints == 'debug' or self.s_prints == 'basic':
                                    print("we end a cycle in stage 1b")
                                    print("the current mapping list is")
                                    print(lista_salida_memoria)
                                    print(self.DG_copy.nodes)

                                nueva_lista_primer_grupo = []
                                if self.lista_AG_copy:
                                    ###obtenemos los predecesores de la siguiente tarea:
                                    predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                    nueva_lista_primer_grupo = []
                                    for predecesor in predecesores:
                                        lugar_mapeado = None
                                        for lugar in lista_salida_memoria:
                                            if lugar[1] == predecesor:
                                                lugar_mapeado = lugar[2]
                                        if lugar_mapeado != None:
                                            nueva_lista_primer_grupo = list(set(
                                                nueva_lista_primer_grupo +
                                                (list(self.DG_original.successors(lugar_mapeado)))))
                                    lista_final_primer_grupo = []
                                    for posible in nueva_lista_primer_grupo:
                                        if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                            2] != 'copy':
                                            pass
                                        else:
                                            lista_final_primer_grupo.append(posible)
                                if self.s_prints == 'basic':
                                    print("LA NUEVA LISTA DE CANDIDATOS ES 06", lista_final_primer_grupo)

                                primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                                # print(primer_grupo)
                                if self.s_prints == 'list':
                                    print("BUGG Nooo")
                                    print(primer_grupo)
                                if not primer_grupo:
                                    # we call the function that verifies the datapaths
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                    primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                    vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                        self.no_more_resources(
                                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                            vector_buffer_especiales, vector_nodos_especiales,
                                            bandera_caso_no_probabilidad,
                                            copia_DG, bandera_nodo_especial)

                                if self.s_prints == 'basic' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the new possible candidates are {dummy_print_dg}")
                            bandera_primer_nodo = False
                            mapping = False
                        else:
                            if self.s_prints == 'list':
                                print("vamos a entrar a la funcion no more resources 01")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, \
                            lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, \
                            bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                            bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                            if self.s_prints == 'basic':
                                print("verificacion de sources ", bandera_source_of_data, info_sensor)

                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("we are at stage 1 step 1 b")
                                print("we are going to map task ", nodo_AG, " to resource ", resource)
                            elif self.s_prints == 'basic' or self.s_prints == 'iter':
                                print(
                                    f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
                                print("------------------------------------------------------------")
                            if self.s_pause:
                                input("Press Enter to continue...")
                            if self.s_prints == 'basic':
                                print("modulo 07 - debug")
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                            if self.s_prints == 'basic' or self.s_prints == 'debug':
                                # print(self.lista_nodos_copy)
                                # print(self.lista_nodos_copy_time)
                                print("we are going to map something so we need to add the copy nodes 03")
                                print(lista_final)

                            ######## aqui integramos todos los copy nodes

                            bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                       nodo_AG,
                                                                                       lista_salida_memoria,
                                                                                       lista_final, copia_DG,
                                                                                       bandera_recomputo)

                            info_actuator = self.info_actuator_generator(nodo_AG)
                            actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                          lista_salida_memoria,
                                                                                                          nodo_AG,
                                                                                                          resource)
                            # print("mapearemos algo")
                            lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                                              self.AG.nodes[nodo_AG]['op'],
                                                              self.dict_nodes[
                                                                  resource][
                                                                  'ops'][
                                                                  self.AG.nodes[nodo_AG]['op']][
                                                                  'latency'],
                                                              self.AG.nodes[nodo_AG]['par'],
                                                              self.AG.nodes[nodo_AG]['par'],
                                                              self.dict_nodes[
                                                                  resource][
                                                                  'ops'][
                                                                  self.AG.nodes[nodo_AG]['op']][
                                                                  'clk'], resultado_latencia,
                                                              resultado_latencia_total, info_sensor, info_actuator,
                                                              actuator_sink
                                                              ]

                            # we keep track of the tasks that we map
                            self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                            if self.s_prints == 'basic':
                                print(self.DG_copy.nodes)
                                print("jndsijfsd", self.lista_predecesores_01)
                                print("la lista de salida es ", lista_salida_memoria)
                            # we proceed to create the special nodes, if necessary

                            self.generation_special_nodes(nodo_AG, resource, lista_final, lista_salida_memoria)
                            # now we check if there are still tasks to map
                            # and if the following task is a successor of the newly mapped task
                            if len(self.lista_AG_copy) > 0:
                                if self.s_prints == 'debug':
                                    print("there is more tasks to map ")
                                # verification of the conexion between the following task and the newly mapped one
                                # bandera_no_conexion activated (True) means that there is no connection, but False
                                # means that there is a connection
                                if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                    bandera_no_conexion = False
                                else:
                                    if self.s_prints == 'basic' or self.s_prints == 'debug':
                                        print(
                                            "there is no connection between the current mapped task and the next task 07")
                                    bandera_no_conexion = True
                                # deactivation of the recomputation flag
                                bandera_recomputo = False

                            # if there are no more tasks to map we end the mapping here
                            if self.s_pause and self.s_prints == 'basic':
                                input("Press Enter to continue...")
                            if not self.lista_AG_copy:
                                lista_final.append(lista_salida_memoria)

                            # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                            # is no more successors of the current task
                            elif not sucesores_nodo_AG or bandera_no_conexion:
                                if self.s_prints == 'list':
                                    print("ciclo elif de algo")
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                    self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)
                                if self.s_prints == 'list':
                                    print("bandera recomputo", bandera_recomputo)
                            else:
                                # in this part we only update the first group of candidates, because there are still
                                # resources and tasks
                                # print("ciclo else de algo")
                                if self.s_prints == 'debug' or self.s_prints == 'basic':
                                    print("we end a cycle in stage 1b")
                                    print("the current mapping list is")
                                    print(lista_salida_memoria)
                                    print(self.DG_copy.nodes)

                                nueva_lista_primer_grupo = []
                                if self.lista_AG_copy:
                                    ###obtenemos los predecesores de la siguiente tarea:
                                    predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                    nueva_lista_primer_grupo = []
                                    for predecesor in predecesores:
                                        lugar_mapeado = None
                                        for lugar in lista_salida_memoria:
                                            if lugar[1] == predecesor:
                                                lugar_mapeado = lugar[2]
                                        if lugar_mapeado != None:
                                            nueva_lista_primer_grupo = list(set(
                                                nueva_lista_primer_grupo +
                                                (list(self.DG_original.successors(lugar_mapeado)))))
                                    lista_final_primer_grupo = []
                                    for posible in nueva_lista_primer_grupo:
                                        if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                            2] != 'copy':
                                            pass
                                        else:
                                            lista_final_primer_grupo.append(posible)
                                if self.s_prints == 'basic':
                                    print("LA NUEVA LISTA DE CANDIDATOS ES 07", lista_final_primer_grupo)

                                primer_grupo = lista_final_primer_grupo  # list(self.DG_original.successors(resource))
                                # print(primer_grupo)
                                if self.s_prints == 'list':
                                    print("BUGG N")
                                    print(primer_grupo)
                                if not primer_grupo:
                                    # we call the function that verifies the datapaths
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                    bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                    contador_datapaths = self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)

                                if self.s_prints == 'list' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the new possible candidates are {dummy_print_dg}")
                                    print("bandera recomputo", bandera_recomputo)
                            bandera_primer_nodo = False
                            mapping = False

                ##################@@@@@@@@@@@@@@@@@@@@@@@@@@@

            else:

                bandera_reinicio = False
                if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'iter' or self.s_prints == 'list':
                    print("------------------------------------------------------------")
                    counter_iter += 1
                    print(f"iteration {counter_iter} ")
                    print(
                        f"we are going to try to map the task {self.dict_nodes_a[nodo_AG]['name']}"
                        f" which has the type {self.dict_nodes_a[nodo_AG]['op']}")
                    dummy_print_ag = []
                    for nd in sucesores_nodo_AG:
                        dummy_print_ag.append(self.dict_nodes_a[nd]['name'])

                    print(f"the sucessors of the task are {dummy_print_ag}")

                bandera_not_used = False
                bandera_extraccion_de_topo = False
                set_resources_not_used = []
                # time.sleep(2)
                contador_ciclo = 0
                while mapping:
                    # we start the iteration, we print some information that we use to debug

                    if self.s_prints == 'debug' or self.s_prints == 'list':
                        dummy_print_dg = []
                        for nd in lista_DG:
                            dummy_print_dg.append(self.dict_nodes[nd]['name'])
                        print(f"the remaining resources are {dummy_print_dg}")
                        print(f"the candidates are {primer_grupo}")
                        print(f"the candidates buffer is {primer_grupo_buffer}")
                        print("the remaining resources are ", self.lista_topo_DG_copy)
                        print("until now the final mapping list is ", lista_final)
                        print("until now the mapping list is ", lista_salida_memoria)
                        print("bandera recomputo ", bandera_recomputo)
                        # input("test ")

                    # this counter helps us to exit from a infinite loop
                    self.counter = self.counter + 1
                    if self.s_prints == 'basic' or self.s_prints == 'list':
                        print(f"EL CONTADOR DE INTENTOS O ALGO ASI ES {self.counter}")
                    if self.counter > len(self.DG_original) * 2 or self.contador_time_slots > 2:
                        #####backtracking
                        # de integrar la funcion de backtracking

                        raise Exception(f"The mapping cycle, please verify your input files")

                    # in here we select the resource
                    if self.s_prints == 'list':
                        print("el primer grupo es ", primer_grupo, "el buffer es ", primer_grupo_buffer)



                    # input("test")
                    if primera_vez:
                        selected_resource = primer_grupo
                        primer_grupo = []
                        primera_vez = False
                    else:
                        if primer_grupo:
                            if self.s_prints == 'list':
                                print("the candidates list is not empty")
                                print(f"")
                            try:
                                selected_resource = primer_grupo.pop(0)
                                # self.lista_topo_DG_copy.remove(selected_resource)
                            except:
                                selected_resource = primer_grupo
                                # self.lista_topo_DG_copy.remove(selected_resource)
                            try:
                                self.lista_topo_DG_copy.remove(selected_resource)
                            except:
                                pass
                        else:

                            if self.lista_topo_DG_copy:
                                selected_resource = self.lista_topo_DG_copy.pop(0)

                            else:
                                if self.s_prints == 'list':
                                    print("bug 01 seleccion de candidato, no hay sucesores, ", self.DG_copy.nodes)
                                    # input("testsss")
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)
                                # print(primer_grupo)
                                if self.s_prints == 'list':
                                    print("DEBUG ERROR SOMETHING",bandera_recomputo,"bandera recomputo")
                                self.lista_topo_DG_copy = lista_DG.copy()
                                # input("gdgdggd")
                                contador_ciclo = contador_ciclo + 1
                                if contador_ciclo > 5:
                                    selected_resource = self.lista_topo_DG_copy.pop(0)
                                    primer_grupo = selected_resource
                                    # primer_grupo_buffer = selected_resource
                                else:
                                    selected_resource = self.lista_topo_DG_copy.pop(0)
                                    # selected_resource = primer_grupo.pop(0)
                                    # primer_grupo_buffer = primer_grupo.copy()
                                    # try:
                                    #     self.lista_topo_DG_copy.remove(selected_resource)
                                    # except:
                                    #     if self.s_prints == 'list':
                                    #         print("error de la lista de topo 01")



                    if self.s_prints == 'list':
                        print(f" the selected resource is {selected_resource}, the reamining resource "
                              f"{self.lista_topo_DG_copy} and the remaining elements in the list of "
                              f"candidates {primer_grupo}")
                        print(f"we want to map {task_AG} which is of node {nodo_AG}")
                        print(self.DG_copy.nodes)
                        # input("kkdkkdkd")
                    if selected_resource in self.DG_copy:
                        if task_AG in self.DG_copy.nodes[selected_resource]['op']:
                            if self.s_prints == 'list':
                                print("New list-based process test 01 ")

                            bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG,
                                                                                              selected_resource)

                            bandera_mapping_valido = self.verificacion_data_dependence(selected_resource,
                                                                                       nodo_AG,
                                                                                       lista_salida_memoria,
                                                                                       lista_final, copia_DG,
                                                                                       bandera_recomputo)

                            vector_validacion_parametros = self.verification_of_parameters(nodo_AG, selected_resource)

                            if self.s_prints == 'list':
                                print("regreso de verificacion de parametros ,", vector_validacion_parametros)
                            vector_validacion_parametros_successors = \
                                self.verification_of_parameters_succcesors(nodo_AG, selected_resource)
                            if self.s_prints == 'list':
                                print("regreso de la verificacion de todos los sucesores creo, "
                                      " ", vector_validacion_parametros_successors)
                            if not vector_validacion_parametros_successors:
                                vector_validacion_parametros_successors = \
                                    self.verificacion_path_a_sink(lista_salida_memoria, nodo_AG, selected_resource)
                            test_degree = self.degree_verification(nodo_AG, selected_resource, lista_salida_memoria)
                            if self.s_prints == 'list':
                                print(test_degree, vector_validacion_parametros_successors, bandera_mapping_valido,
                                      vector_validacion_parametros, bandera_source_of_data)

                            if all(vector_validacion_parametros) and bandera_mapping_valido and \
                                    bandera_source_of_data and test_degree and vector_validacion_parametros_successors:

                                if self.s_prints == 'list':
                                    print("first stage cleared test 02")
                                    print(f" the app sources are {self.lista_sources_AG}",bandera_recomputo)

                                bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG,
                                                                                                  selected_resource)
                                bandera_mapping_valido = self.verificacion_data_dependence(selected_resource,
                                                                                           nodo_AG,
                                                                                           lista_salida_memoria,
                                                                                           lista_final, copia_DG,
                                                                                           bandera_recomputo)
                                if self.s_prints == 'list':
                                    print(
                                        f"the list of nodes that need to have copy function are {self.lista_nodos_copy} ")
                                    print("the list until now is")
                                    print(lista_salida_memoria)
                                    print(bandera_recomputo)

                                # if there is no problem we follow the process and map the task
                                if bandera_mapping_valido and bandera_source_of_data:
                                    # this is the mapping rutine, maybe we can put it into a function

                                    if self.s_prints == 'debug' or self.s_prints == 'basic' or self.s_prints == 'list':
                                        print("we are at stage 1 step 1 y")
                                        print("we are going to map task ", nodo_AG, " to resource ", selected_resource)
                                    elif self.s_prints == 'basic' or self.s_prints == 'iter':
                                        print(
                                            f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} "
                                            f"to the resource {self.dict_nodes[selected_resource]['name']} ")
                                        print("------------------------------------------------------------")
                                    if self.s_pause:
                                        input("Press Enter to continue...")
                                    if self.s_prints == 'basic':
                                        print("modulo 08 - debug")

                                    resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                        selected_resource, nodo_AG)

                                    if self.s_prints == 'basic' or self.s_prints == 'debug' or self.s_prints == 'list':
                                        print("section before the acgtuator generator test 01")
                                        print(self.lista_nodos_copy)
                                        print(self.lista_nodos_copy_time)
                                        print("we are going to map something so we need to add the copy nodes 03")
                                        print(lista_final)
                                        print("end debug test 01")

                                    info_actuator = self.info_actuator_generator(nodo_AG)
                                    actuator_sink, lista_final, lista_salida_memoria = \
                                        self.generation_copy_nodes(lista_final, lista_salida_memoria,
                                                                   nodo_AG, selected_resource)

                                    lista_salida_memoria[selected_resource] = [True, nodo_AG, selected_resource,
                                                                               self.AG.nodes[nodo_AG]['op'],
                                                                               self.dict_nodes[
                                                                                   selected_resource][
                                                                                   'ops'][
                                                                                   self.AG.nodes[nodo_AG]['op']][
                                                                                   'latency'],
                                                                               self.AG.nodes[nodo_AG]['par'],
                                                                               self.AG.nodes[nodo_AG]['par'],
                                                                               self.dict_nodes[
                                                                                   selected_resource][
                                                                                   'ops'][
                                                                                   self.AG.nodes[nodo_AG]['op']][
                                                                                   'clk'], resultado_latencia,
                                                                               resultado_latencia_total, info_sensor,
                                                                               info_actuator, actuator_sink
                                                                               ]
                                    # we keep track of the tasks that we map
                                    # reset of values
                                    mapping = False
                                    contador_ciclo = 0
                                    self.counter = 0
                                    if self.s_prints == 'basic' or self.s_prints == 'list':
                                        print("la lista de salida es ", lista_salida_memoria)
                                        print(f" the mapping flag is {mapping}")

                                    # we store the mapped task
                                    self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                                    # creation of special nodes

                                    self.generation_special_nodes(nodo_AG, selected_resource, lista_final,
                                                                  lista_salida_memoria)

                                    # we check if there are still tasks to map
                                    if len(self.lista_AG_copy) > 0:
                                        # verification of the successors of the current task
                                        if self.s_prints == 'list':
                                            print("entro en el ciclo paleta ")
                                        if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):

                                            bandera_no_conexion = False
                                        else:

                                            bandera_no_conexion = True
                                    # we verify is there are still resources, datapaths availables or if we need to create
                                    # a new time slot, this part maybe can be put it in a function
                                    bandera_no_conexion = False
                                    if not bandera_no_conexion:

                                        if self.s_prints == 'list':
                                            print("debug - ", selected_resource)
                                        # print(primer_grupo[max_index])
                                        # print(list(self.DG_copy.successors(primer_grupo[max_index])))

                                        nueva_lista_primer_grupo = []
                                        if self.lista_AG_copy:
                                            ###obtenemos los predecesores de la siguiente tarea:
                                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                            numero_predecesores = len(
                                                list(self.AG_copy.predecessors(self.lista_AG_copy[0])))
                                            if self.s_prints == 'list':
                                                print(" la siguiente tarea es ", (self.lista_AG_copy[0]),
                                                      "the predecessors son ",
                                                      list(self.AG_copy.predecessors(self.lista_AG_copy[0])))
                                                print("the mapping list is ", lista_salida_memoria)
                                            nueva_lista_primer_grupo = []
                                            primera_vez_nuevos = True
                                            lista_candidatos_final = []
                                            for predecesor in predecesores:
                                                lugar_mapeado = None
                                                for lugar in lista_salida_memoria:
                                                    if lugar[1] == predecesor:
                                                        lugar_mapeado = lugar[2]
                                                if lugar_mapeado != None:
                                                    nueva_lista_primer_grupo = list(set(nueva_lista_primer_grupo + (
                                                        list(self.DG_original.successors(lugar_mapeado)))))

                                                if primera_vez_nuevos:
                                                    lista_candidatos_primer_grupo = nueva_lista_primer_grupo
                                                    primera_vez_nuevos = False
                                                else:
                                                    for elemento_en_nueva_lista in nueva_lista_primer_grupo:
                                                        if elemento_en_nueva_lista in lista_candidatos_primer_grupo:
                                                            lista_candidatos_final.append(elemento_en_nueva_lista)
                                                if numero_predecesores == 1:
                                                    lista_candidatos_final = nueva_lista_primer_grupo
                                            lista_final_primer_grupo = []
                                            for posible in lista_candidatos_final:

                                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                                    2] != 'copy':
                                                    pass
                                                else:
                                                    lista_final_primer_grupo.append(posible)
                                            if self.s_prints == 'list':
                                                print("LA NUEVA LISTA DE CANDIDATOS ES 10", lista_final_primer_grupo)

                                            primer_grupo = list(set(
                                                lista_final_primer_grupo))  # list(self.DG_original.successors(primer_grupo[max_index]))
                                            if self.s_prints == 'list' or self.s_prints == 'debug':
                                                dummy_print_dg = []
                                                for nd in primer_grupo:
                                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                                try:
                                                    print(
                                                        f"the new list of possible candidates is {dummy_print_dg} "
                                                        f"for the task {self.lista_AG_copy[0]} section 01")
                                                except:
                                                    pass
                                            if primer_grupo:
                                                pass
                                            else:
                                                if self.lista_topo_DG_copy:
                                                    if self.s_prints == 'list':
                                                        print("no hay primer grupo pero si hay elementos en la lista topo")
                                                    primer_grupo = self.lista_topo_DG_copy.pop(0)
                                                else:
                                                    if self.s_prints == 'list':
                                                        print("we are going to enter the no more resource function - 05")
                                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                                    bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                                    contador_datapaths = self.no_more_resources(
                                                        lista_salida_memoria, contador_datapaths, bandera_reinicio,
                                                        lista_final,
                                                        vector_buffer_especiales, vector_nodos_especiales,
                                                        bandera_caso_no_probabilidad,
                                                        copia_DG, bandera_nodo_especial)
                                                    self.lista_topo_DG_copy = lista_DG.copy()
                                                    primer_grupo = self.lista_topo_DG_copy.pop(0)

                                            primer_grupo_buffer = primer_grupo

                                    bandera_nodo_especial = False
                                    # bandera_recomputo = False
                                    if self.s_pause and self.s_prints == 'basic':
                                        input("Press Enter to continue...")
                                    if not self.lista_AG_copy:
                                        lista_final.append(lista_salida_memoria)
                                        if self.s_prints == 'debug' or self.s_prints == 'basic' or self.s_prints == 'list':
                                            print("thre are no more tasks to map stage 2")



                                else:
                                    primer_grupo = []

                                    # # we reset the mapping list
                                    # bandera_primer_nodo = False
                                    # mapping = True
                                    # bandera_solo_un_nodo = False
                                    # if self.s_pause and self.s_prints == 'basic':
                                    #     input("Press Enter to continue...")
                                    # if self.s_prints == 'debug':
                                    #     print("Append module stage 2 - debug -", lista_final)
                                    # if not self.lista_AG_copy:
                                    #     lista_final.append(lista_salida_memoria)
                                    #     # self.lista_nodos_especiales_final.append()
                                    #     lista_salida_memoria = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                                    #                             for g in range(len(copia_DG))]
                                    # else:
                                    #
                                    #     bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                    #     primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                    #     vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                    #         self.no_more_resources(
                                    #             lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    #             vector_buffer_especiales, vector_nodos_especiales,
                                    #             bandera_caso_no_probabilidad,
                                    #             copia_DG, bandera_nodo_especial)
                                    #     primer_grupo_buffer = primer_grupo.copy()
                            else:
                                primer_grupo = []
                        else:
                            primer_grupo = []
                    else:
                        primer_grupo = []

        if self.s_prints == 'debug' or self.s_prints == 'basic' or self.s_prints == 'list':
            print("end of the mapping debug - ", vector_nodos_especiales, len(lista_final), vector_buffer_especiales)
            print(f"los nodos especiales son {self.lista_nodos_especiales_final} o esta {self.lista_nodos_especiales}")
            print("the final mapping list inside the mapping function")
            print(lista_final)
            print("  por time slots ")
            for timeslot in lista_final:
                print("   ")
                print(timeslot)
            print("se termino")

        vector_config = []
        vector_config_v2 = []

        # FLOW DIAGRAM 3.4
        return lista_final, vector_config, vector_config_v2

    def no_more_resources(self, lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                          vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, copia_DG,
                          bandera_nodo_especial):
        bandera_recomputo = False
        if self.s_prints == 'list':
            print(
                f"ENTRAMOS EN LA FUNCION DE NO MORE RESOURCES, la lista de datapaths son {bandera_recomputo}")
        lista_datapaths_disponibles = []
        if self.recomputation_enable:
            lista_datapaths_disponibles, bandera_recomputo = self.datapaths_available(
                lista_salida_memoria)

        if lista_datapaths_disponibles:
            self.DG_copy = self.remove_nodes_DG(lista_datapaths_disponibles)
            bandera_nodo_especial = True
            primer_grupo = obtencion_sources(self.DG_copy)
            bandera_primer_nodo = True
            bandera_recomputo = True
            # if self.s_prints == 'basic' or self.s_prints == 'debug':
            #     dummy_print_dg = []
            #     for nd in primer_grupo:
            #         dummy_print_dg.append(self.dict_nodes[nd]['name'])
            #     print(f"the next group of candidates is {dummy_print_dg} ")
            contador_datapaths = contador_datapaths + 1
            if contador_datapaths > len(self.datapaths_independientes) + 1:
                bandera_reinicio = True
        else:
            # if self.s_prints == 'debug':
            #     print("we dont have more resources - debug - mapping list ", lista_final)
            #     print("we are going to create a time slot")
            if self.s_prints == 'list':
                print("we are going to create a new time slot")
            bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad = self.reinicio_time_slot(
                lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                vector_nodos_especiales, bandera_caso_no_probabilidad)
        return bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths

    def generation_special_nodes(self, nodo_AG, resource, lista_final, lista_salida_memoria):
        ### tenemos que checar bien esta funcion
        # print("lista de nodos especiales inicio",self.lista_nodos_especiales)
        copy_nodos_conectados_rc = self.list_sinks_connected_to_rc.copy()
        if self.lista_predecesores_01:
            if self.s_prints == 'debug' or self.s_prints == 'list':
                print("creation of a special node")
                print(self.lista_predecesores_01)
                print(lista_final)
            for nodo_especial in self.lista_predecesores_01:
                if nodo_especial[0] == nodo_AG:

                    datapaths = self.generation_datapaths(self.DG)
                    datapath_buffer = []
                    for path in datapaths:
                        if nodo_especial[2] \
                                in path:
                            datapath_buffer = path
                            break
                    if self.s_prints == 'list':
                        print(f"el datapath del predecessor es {datapath_buffer}")
                        print(nodo_especial)
                        print(lista_salida_memoria)
                    copy_nodos_conectados_rc = self.list_sinks_connected_to_rc.copy()
                    if nodo_especial[2] in copy_nodos_conectados_rc:
                        lugar_sink = nodo_especial[2]
                        try:
                            copy_nodos_conectados_rc.remove(lugar_sink)
                        except:
                            copy_nodos_conectados_rc = self.list_sinks_connected_to_rc.copy()
                            copy_nodos_conectados_rc.remove(lugar_sink)
                    else:

                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0

                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              nodo_especial[2])
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              nodo_especial[2])
                            # print(sink_nodo_sink_task,resource)
                            if (lista_salida_memoria[sink_nodo_sink_task][
                                    0] and lista_salida_memoria[sink_nodo_sink_task][
                                    2] != 'copy') or sink_nodo_sink_task not in datapath_buffer:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  nodo_especial[2])
                                    done = False
                                    break

                            else:
                                done = False
                                break
                        if self.s_prints == 'list':
                            print("nada")
                        lugar_sink = sink_nodo_sink_task
                        # sink_node_from_any_node(self.DG_original, self.list_sinks_connected_to_rc,
                        #                                      nodo_especial[2])
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                 resource)

                    buffer_nodo_especial = [nodo_especial[3], lugar_sink, lugar_source,
                                            len(lista_final), self.contador_recomputacion]
                    # print("buffer nodo especial", buffer_nodo_especial)
                    if self.s_prints == 'list':
                        print(
                            f" se anexara un nodo especial 01-a {buffer_nodo_especial} y la lista es {self.lista_nodos_especiales}")
                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    self.lista_predecesores_01.remove(nodo_especial)
        # we add the special nodes corresponding to the nodes mapped in the previous time slot
        elementos_to_remove = []
        if self.s_prints == 'list':
            print("las parejas son ", self.vector_de_parejas_memoria)
        if self.vector_de_parejas_memoria:
            if self.s_prints == 'basic':
                print("jbdsfds")
            for pareja in self.vector_de_parejas_memoria:
                if nodo_AG == pareja[0]:
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                 resource)
                    if self.s_prints == 'basic':
                        print(self.lista_nodos_ocupados_source, lugar_source)
                    if lugar_source in self.lista_nodos_ocupados_source:
                        copy_lista_sources = self.lista_sources_DG.copy()
                        copy_lista_sources.remove(lugar_source)

                        lugar_source_copia = source_node_from_any_node(self.DG_original, copy_lista_sources, resource)
                        if lugar_source_copia != None:
                            lugar_source = lugar_source_copia

                    if self.s_prints == 'list':
                        print(" buffer nodo especial", pareja[1], lugar_source, len(lista_final),
                              self.contador_recomputacion)
                    buffer_nodo_especial = [True, pareja[1], lugar_source, len(lista_final),
                                            self.contador_recomputacion]
                    self.lista_nodos_ocupados_source.append(lugar_source)
                    if self.s_prints == 'list':
                        print(
                            f" se anexara un nodo especial 03 {buffer_nodo_especial} y la lista es {self.lista_nodos_especiales}")
                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    elementos_to_remove.append(pareja)
            for el in elementos_to_remove:
                self.vector_de_parejas_memoria.remove(el)
        # print(self.vector_de_parejas_memoria)
        # print(self.lista_nodos_especiales)
        # print(self.lista_nodos_especiales_final)
        return

    def info_actuator_generator(self, nodo_AG):
        lugar_n = None
        if nodo_AG in self.lista_sinks_AG:
            for nodo_total in self.AG_total.nodes:
                # print(nodo_total)
                if self.AG_original.nodes[nodo_AG]['name'] == self.AG_total.nodes[nodo_total]['name']:
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

    def generation_copy_nodes(self, lista_final, lista_salida_memoria, nodo_AG, resource):

        if self.s_prints == 'list':
            print("inside the generation copy nodes function")
        # print(self.dict_nodes[resource])
        latency_variable = self.dict_nodes[resource]['ops']['copy']['clk']
        # print(self.dict_info)
        latency = None
        for n in self.dict_info['functions_res']:
            if n == latency_variable:
                latency = self.dict_info['functions_res'][n]
        # if latency == None:
        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)

        if self.lista_en_time_slots:
            if self.s_prints == 'basic' or self.s_prints == 'list':
                print("test 01 - copy nodes function")
                print(lista_final[self.lugar_time_slot - 1])
            for copy_node in self.lista_nodos_copy_time:
                if self.s_prints == 'basic' or self.s_prints == 'list':
                    print(f"test 02 - copy nodes function {copy_node}")
                if lista_final[self.lugar_time_slot][copy_node][0]:
                    pass
                else:
                    lista_final[self.lugar_time_slot][copy_node] = [True, None, 'copy', 'copy', copy_node, nodo_AG,
                                                                    's8', 0, latency, latency, info_sensor, 0, 0]
            for copy_node in self.lista_nodos_copy:
                if self.s_prints == 'basic' or self.s_prints == 'list':
                    print(f"test 03 - copy nodes function {copy_node}")
                if lista_salida_memoria[copy_node][0]:
                    pass
                else:
                    lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', copy_node, nodo_AG,
                                                       's7', 0, latency, latency, info_sensor, 0, 0]

        else:
            for copy_node in self.lista_nodos_copy:
                if self.s_prints == 'basic' or self.s_prints == 'list':
                    print(f"test 04 - copy nodes function {copy_node}")
                if lista_salida_memoria[copy_node][0]:
                    pass
                else:
                    lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', copy_node, nodo_AG,
                                                       's6', 0, latency, latency, info_sensor, 0, 0]
        if self.s_prints == 'basic' or self.s_prints == 'list':
            print("test 05 - copy nodes function")
            print(lista_final)
            print(lista_salida_memoria)
            print(" end debug")

            # we already add the nodes between tasks but we need to add the copy nodes from the sink tasks
            # to the sinks of the hardware
        actuator_sink = None
        copia_nodos_conectados_a_rc = self.list_sinks_connected_to_rc.copy()
        #####aqui se cambiara toda el ciclo

        if nodo_AG in self.lista_sinks_AG and resource not in self.list_sinks_connected_to_rc:
            if self.s_prints == 'basic' or self.s_prints == 'list':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
                print(self.list_sinks_connected_to_rc)

            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
            done = True
            counter_internal = 0

            datapaths = self.generation_datapaths(self.DG)
            datapath_buffer = []
            for path in datapaths:
                if resource \
                        in path:
                    datapath_buffer = path
                    break
            if self.s_prints == 'list':
                print(f"el datapath del predecessor es {datapath_buffer}")
                # input("ttt")

            while done:
                if copy_list_sinks_connected_to_rc:
                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                  copy_list_sinks_connected_to_rc,
                                                                  resource)
                    if sink_nodo_sink_task == None:
                        counter_internal = counter_internal + 1
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                    if self.s_prints == 'list':
                        print("error 78", sink_nodo_sink_task)
                else:
                    counter_internal = counter_internal + 1
                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                  copy_list_sinks_connected_to_rc,
                                                                  resource)
                    if self.s_prints == 'list':
                        print("error 79", sink_nodo_sink_task)
                # print(sink_nodo_sink_task,resource,self.list_sinks_connected_to_rc)
                if lista_salida_memoria[sink_nodo_sink_task][0] or sink_nodo_sink_task not in datapath_buffer:
                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                    if counter_internal == 5:
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                        done = False
                        break

                else:
                    done = False
                    break

            if self.s_prints == 'list':
                print("we are checking a problem with the sinks ")
                print(sink_nodo_sink_task, resource)

            # sink_nodo_sink_task = sink_node_from_any_node(self.DG_original, self.list_sinks_connected_to_rc,
            #                                               resource)
            path_sink_node = simple_paths_from_two_nodes(self.DG_original, resource, sink_nodo_sink_task)
            if self.s_prints == 'basic':
                print("the paths between the sink task and the sink hardware", path_sink_node)
                print(f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            # single_path = path_sink_node.pop()
            single_path = min(path_sink_node, key=len)
            single_path.remove(resource)
            for nodo_a_sink in single_path:
                if lista_salida_memoria[nodo_a_sink][0]:
                    pass
                else:
                    lista_salida_memoria[nodo_a_sink] = [True, None, 'copy', 'copy', nodo_a_sink, nodo_AG,
                                                         's5', 0, latency, latency, info_sensor, 0, 0]
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == self.DG_original.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            ###################esto tenemos que checarlo con calma
            if not self.lista_sinks_DG_total:
                self.lista_sinks_DG_total = obtencion_sinks(self.DG_total)
            copia_sinks = self.lista_sinks_DG_total.copy()
            contador_pasos = 0
            while done:
                if copia_sinks:
                    sink_test = copia_sinks.pop()
                    if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t, sink_test):
                        actuator_sink = sink_test
                        done = False
                        break
                else:
                    if contador_pasos > 3:
                        copia_sinks = self.lista_sinks_DG_total.copy()
                        actuator_sink = copia_sinks.pop()
                        done = False
                        break
                    else:
                        copia_sinks = self.lista_sinks_DG_total.copy()
            self.lista_sinks_DG_total = self.lista_sinks_DG_total.remove(actuator_sink)

        if nodo_AG in self.lista_sources_AG and resource not in self.lista_sources_DG:
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            source_nodo_sink_task = source_node_from_any_node(self.DG_original,
                                                              self.lista_sources_DG,
                                                              resource)
            path_source_node = simple_paths_from_two_nodes(self.DG_original, source_nodo_sink_task,
                                                           resource)
            if self.s_prints == 'basic':
                print("the paths between the source task and the osusdofsdf hardware",
                      path_source_node)
                print(
                    f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            single_path = path_source_node.pop()
            single_path.remove(resource)
            for nodo_a_source in single_path:
                lista_salida_memoria[nodo_a_source] = [True, None, 'copy', 'copy', nodo_a_source, nodo_AG,
                                                       's4', 0, latency, latency, info_sensor, 0, 0]

        return actuator_sink, lista_final, lista_salida_memoria

    def remove_nodes_AG(self, lista_nodos):
        #######funcion que de un grafo y una lista de nodos, remueve los nodos extra y regresa un grafo que solo tiene
        #######los nodos de la lista y sus conexiones
        copy_graph = self.AG_original.copy()
        copy_graph.remove_nodes_from(lista_nodos)
        copy_graph_buffer = self.AG_original.copy()
        copy_graph.remove_nodes_from(list(copy_graph.nodes))
        return copy_graph_buffer

    def remove_nodes_DG(self, lista_nodos):
        #######funcion que de un grafo y una lista de nodos, remueve los nodos extra y regresa un grafo que solo tiene
        #######los nodos de la lista y sus conexiones
        # print("Entry node removal ",self.DG_original.nodes,lista_nodos)
        copy_graph = self.DG_original.copy()
        # print("la lista copia es ",copy_graph.nodes)
        copy_graph.remove_nodes_from(lista_nodos)
        # print("la lista que auedo luego de remover los nodos es",copy_graph.nodes)
        copy_graph_buffer = self.DG_original.copy()
        copy_graph_buffer.remove_nodes_from(list(copy_graph.nodes))
        # print("el grafo final es ", copy_graph_buffer.nodes)
        return copy_graph_buffer

    def verificacion_data_dependence(self, recurso_elegido, nodo_AG, lista_salida_memoria, lista_final, copia_DG,
                                     bandera_recomputo):
        # recurso_elegido = primer_grupo[max_index]
        bandera_mapping_valido = False
        bandera_source = False
        bandera_no_esta_en_el_mismo_time_slot = False
        # print("verificacion de dependencia",recurso_elegido,nodo_AG)
        # print("los recursos son ",copia_DG.nodes)
        ######obtenemos los predecesores de la tarea a asignar
        set_predecesores = list(self.AG_copy.predecessors(nodo_AG))
        if self.s_prints == 'debug' or self.s_prints == 'list':
            print("estamos en la funcion de verificacion de data dependence")
            print("el set de predecesores es ", set_predecesores)
            print("EL SET DE PREDECESORES", set_predecesores)
            print("lista mapping ", lista_salida_memoria)
            print("time slots ", lista_final)
        # if self.dict_nodes_a[nodo_AG]['name']=='t3': time.sleep(5)
        self.lista_nodos_copy = []
        self.lista_nodos_copy_time = []
        self.lista_en_time_slots = False
        self.lugar_time_slot = None
        vector_predecesores_verificacion = []
        ######si existen predecesores
        if set_predecesores:
            ####checamos por cada predecesor, donde esta mapeado y si existe una conexion directa hacia
            ####donde se mapeara la tarea a asignar
            lugar_nodo = None
            if self.s_prints == 'list':
                print("entro en este modulo", set_predecesores)
            vector_predecesores_verificacion = []
            bandera_no_esta_en_el_mismo_time_slot = False
            for predecesor in set_predecesores:
                if self.s_prints == 'list':
                    print(f"el predecesor que vamos a checar es {predecesor}")
                # print(predecesor)
                lugar_nodo = None
                # print(lista_salida_memoria)
                for elemento_lista in range(0, len(lista_salida_memoria)):
                    if predecesor == lista_salida_memoria[elemento_lista][1]:
                        lugar_nodo = elemento_lista
                #####si no se encontro el lugar del nodo esto quiere decir que fue mapeado en un diferente
                #####time slot por lo que se busca en la lista final
                numero_time_slot = 0
                # print("predecesor",predecesor,lugar_nodo)
                # print(lista_final)
                if lugar_nodo == None:
                    for time_slot in range(0, len(lista_final)):
                        lista_final_buffer = lista_final[time_slot]
                        # print(lista_final_buffer)
                        for elemento_interno in range(0, len(lista_final_buffer)):
                            # print(lista_final_buffer[elemento_interno])
                            if predecesor == lista_final_buffer[elemento_interno][1]:
                                lugar_nodo = elemento_interno
                                numero_time_slot = time_slot
                                bandera_no_esta_en_el_mismo_time_slot = True

                # print(len(lista_final))
                if lugar_nodo == None:
                    if len(lista_final) >= 1:
                        if self.s_prints == 'debug' or self.s_prints == 'list':
                            print("we have to look in the time slots")
                            print("testslknfsdf")
                if self.s_prints == 'list':
                    print("EL LUGAR DEL PREDECESOR ES ", lugar_nodo, bandera_recomputo)
                #####ya encontramos el donde esta mapeado el predecesor de la tarea, ahora
                #####validaremos que existe un simple path entre el recurso candidato y donde esta
                #####mapeado el predecesor, tenemos dos casos, si esta en el mismo time slot o no
                vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                vector_verificacion_no_mapeo_02 = []  ######por cada path
                if not bandera_no_esta_en_el_mismo_time_slot and not bandera_recomputo:
                    simple_path = simple_paths_from_two_nodes(copia_DG,
                                                              lugar_nodo,
                                                              recurso_elegido)

                    # print("antes de la verificacion ",simple_path)
                    if simple_path:
                        # print("test")
                        while simple_path:
                            path_b = min(simple_path, key=len)
                            paths_copy = simple_path.copy()
                            for i in range(0, len(paths_copy)):
                                if paths_copy[i] == path_b:
                                    dummy = simple_path.pop(i)
                            path = list(path_b)
                            if lugar_nodo in path:
                                path.remove(lugar_nodo)
                            bandera_salida = False
                            vector_verificacion_no_mapeo_01 = []
                            # esto es para indicar los nodos copy
                            path_buffer = list(path)
                            if recurso_elegido in path_buffer:
                                path_buffer.remove(recurso_elegido)
                            vector_dependency_01 = []
                            for node in path:

                                if lista_salida_memoria[node][0]:  # and self.lista_mapping[node][2] != 'copy':#

                                    vector_dependency_01 = vector_dependency_01 + [lista_salida_memoria[node][0]]
                            if True in vector_dependency_01:
                                vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                            else:  #
                                vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [True]
                                self.lista_nodos_copy = self.lista_nodos_copy + path_buffer  #
                                bandera_salida = True
                            if bandera_salida:
                                break

                        # for unique_path in simple_path:
                        #     if self.s_prints== 'basic':
                        #         print("impresion de path dentro de verificacion de dependencia", unique_path)
                        #     # print(unique_path)
                        #     unique_path_buffer = list(unique_path)
                        #     unique_path_buffer.remove(lugar_nodo)
                        #     vector_verificacion_no_mapeo_01 = []
                        #     list_copy_function = list(unique_path_buffer)
                        #     list_copy_function.remove(recurso_elegido)
                        #     # self.lista_nodos_copy = self.lista_nodos_copy + list_copy_function
                        #     # self.lista_nodos_copy.append(list_copy_function)
                        #     for nodo_in_unique in unique_path_buffer:
                        #         if lista_salida_memoria[nodo_in_unique][0] and lista_salida_memoria[nodo_in_unique][2] != 'copy':
                        #             vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                        #             lista_salida_memoria[nodo_in_unique][0]]
                        #     if not True in vector_verificacion_no_mapeo_01:
                        #         if self.s_prints == 'basic':
                        #             print(f"los nodos se que se van a adicionar son {list_copy_function} y los nodos ya dentro de la lista son {self.lista_nodos_copy}")
                        #         self.lista_nodos_copy = self.lista_nodos_copy + list_copy_function
                        #         vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                        #             True]
                        if self.s_prints == 'list':
                            print(vector_verificacion_no_mapeo_02)
                        if True in vector_verificacion_no_mapeo_02:
                            # bandera_mapping_valido = True
                            vector_predecesores_verificacion.append(True)
                    else:
                        if self.s_prints == 'list':
                            print("tenemos un buggazo aqui", simple_path)
                        vector_predecesores_verificacion.append(False)

                else:
                    if self.s_prints == 'debug' or self.s_prints == 'list':
                        print("caso raro , la bandera recomputo", bandera_recomputo)
                    if self.s_prints == 'basic':
                        print(
                            "estamos en la verificacion de dependencia en los time slots, se utilizaba la bandera de recomputo "
                            "pero se sustiyo por un True, hay que checar si esta bien")
                    # bandera_recomputo = False
                    if bandera_recomputo:
                        # print("aqui en algo raro")
                        datapaths = self.generation_datapaths(self.DG)
                        datapath_buffer = []
                        for path in datapaths:
                            if lugar_nodo \
                                    in path:
                                datapath_buffer = path
                                break
                        if self.s_prints == 'list':
                            print(f"el datapath del predecessor es {datapath_buffer}")

                        bandera_es_sink = False
                        bandera_es_source = False
                        if lugar_nodo in self.list_sinks_connected_to_rc:
                            bandera_es_sink = True
                        else:
                            # print("buscaremos el sink")

                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                            done = True
                            counter_internal = 0

                            while done:
                                if copy_list_sinks_connected_to_rc:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  lugar_nodo)
                                    if sink_nodo_sink_task == None:
                                        counter_internal = counter_internal + 1
                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      lugar_nodo)
                                else:
                                    counter_internal = counter_internal + 1
                                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  lugar_nodo)

                                # print(sink_nodo_sink_task,lugar_nodo,self.list_sinks_connected_to_rc.copy())
                                if lista_salida_memoria[sink_nodo_sink_task][
                                    0] or sink_nodo_sink_task not in datapath_buffer:
                                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                    if counter_internal == 5:
                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      lugar_nodo)
                                        done = False
                                        break

                                else:
                                    done = False
                                    break

                            sink = sink_nodo_sink_task
                            # sink = sink_node_from_any_node(self.DG_original,
                            #                                self.lista_sinks_DG,
                            #                                lugar_nodo)
                            # print("buscaremos el path",lugar_nodo,sink)

                            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                                      lugar_nodo,
                                                                      sink)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            # print("dentro de funcion",sink,simple_path)
                            # time.sleep(5)
                            if simple_path:
                                while simple_path:
                                    path_b = min(simple_path, key=len)
                                    paths_copy = simple_path.copy()
                                    for i in range(0, len(paths_copy)):
                                        if paths_copy[i] == path_b:
                                            dummy = simple_path.pop(i)
                                    path = list(path_b)
                                    if lugar_nodo in path:
                                        path.remove(lugar_nodo)
                                    bandera_salida = False
                                    vector_verificacion_no_mapeo_01 = []
                                    # esto es para indicar los nodos copy
                                    path_buffer = list(path)
                                    if recurso_elegido in path_buffer:
                                        path_buffer.remove(recurso_elegido)
                                    vector_dependency_01 = []
                                    for node in path:

                                        if lista_salida_memoria[node][0]:  # and self.lista_mapping[node][2] != 'copy':#

                                            vector_dependency_01 = vector_dependency_01 + [
                                                lista_salida_memoria[node][0]]
                                    if True in vector_dependency_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                                    else:  #
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [True]
                                        self.lista_nodos_copy = self.lista_nodos_copy + path_buffer  #
                                        bandera_salida = True
                                    if bandera_salida:
                                        break

                                # for unique_path_b in simple_path:
                                #
                                #     unique_path = list(unique_path_b)
                                #     unique_path.remove(lugar_nodo)
                                #
                                #     list_copy_function = list(unique_path)
                                #     if recurso_elegido in list_copy_function:
                                #         list_copy_function.remove(recurso_elegido)
                                #
                                #     # self.lista_nodos_copy.append(list_copy_function)
                                #
                                #     vector_verificacion_no_mapeo_01 = []
                                #     for nodo_in_unique in unique_path:
                                #         vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                #             lista_salida_memoria[nodo_in_unique][0]]
                                #     if not True in vector_verificacion_no_mapeo_01:
                                #         self.lista_nodos_copy = self.lista_nodos_copy + list_copy_function
                                #         vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                #             True]
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_sink = True

                        if recurso_elegido in self.lista_sources_DG:
                            bandera_es_source = True
                        else:
                            source = source_node_from_any_node(copia_DG,
                                                               self.lista_sources_DG,
                                                               recurso_elegido)
                            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                                      source,
                                                                      recurso_elegido)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            if simple_path:
                                for unique_path in simple_path:
                                    vector_verificacion_no_mapeo_01 = []
                                    for nodo_in_unique in unique_path:
                                        vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                            lista_salida_memoria[nodo_in_unique][0]]
                                    if not True in vector_verificacion_no_mapeo_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                            True]
                                        unique_path_copia = unique_path
                                        unique_path_copia = unique_path_copia.remove(recurso_elegido)
                                        if unique_path:
                                            self.lista_nodos_copy = self.lista_nodos_copy + unique_path
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_source = True
                        if self.s_prints == 'debug' or self.s_prints == 'basic':
                            print("las banderas son ", bandera_es_source, bandera_es_sink, recurso_elegido)

                        if bandera_es_source and bandera_es_sink:
                            # bandera_mapping_valido = True
                            vector_predecesores_verificacion.append(True)




                    else:

                        if self.s_prints == 'debug' or self.s_prints == 'list':
                            print("otro time slot", numero_time_slot)
                        self.lista_en_time_slots = True
                        self.lugar_time_slot = numero_time_slot
                        # print("la tarea se mapeo en otro time slot",numero_time_slot)
                        time_slot_buffer = lista_final[numero_time_slot]
                        if self.s_prints == 'list':
                            print("el mapping en el time slot ", numero_time_slot, " es ", time_slot_buffer)
                        #####checaremos primero si el predecesor tiene acceso a un sink
                        bandera_es_sink = False
                        bandera_es_source = False
                        if self.s_prints == 'debug' or self.s_prints == 'list':
                            # if self.dict_nodes_a[nodo_AG]['name'] == 't3': time.sleep(5)
                            print("los elementos que se checaran son ", lugar_nodo, recurso_elegido)

                        datapaths = self.generation_datapaths(self.DG)
                        datapath_buffer = []
                        for path in datapaths:
                            if lugar_nodo \
                                    in path:
                                datapath_buffer = path
                                break
                        if self.s_prints == 'list':
                            print(f"el datapath del predecessor es {datapath_buffer}")

                        # aqui buscaremos en el time slot anterior, en el sentido de que el predecesor esta en un
                        # sink o tenemos que buscar un sink que este conectado al predecesor
                        if lugar_nodo in self.list_sinks_connected_to_rc:
                            bandera_es_sink = True
                        else:
                            # print("buscaremos el sink")

                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                            done = True
                            counter_internal = 0

                            while done:
                                if copy_list_sinks_connected_to_rc:
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  lugar_nodo)
                                    if sink_nodo_sink_task == None:
                                        counter_internal = counter_internal + 1
                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      lugar_nodo)
                                else:
                                    counter_internal = counter_internal + 1
                                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  lugar_nodo)
                                # print(sink_nodo_sink_task,resource)
                                if (time_slot_buffer[sink_nodo_sink_task][
                                    0] and time_slot_buffer[sink_nodo_sink_task][
                                    2] != 'copy')  or sink_nodo_sink_task not in datapath_buffer:
                                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                    if counter_internal == 5:
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      lugar_nodo)
                                        done = False
                                        break

                                else:
                                    done = False
                                    break

                            sink = sink_nodo_sink_task
                            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                                      lugar_nodo,
                                                                      sink)
                            if self.s_prints == 'list':
                                print("el sink es ", sink, " los paths son ", simple_path)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            # print("dentro de funcion",sink,simple_path)
                            # time.sleep(5)
                            if simple_path:
                                while simple_path:
                                    path_b = min(simple_path, key=len)
                                    paths_copy = simple_path.copy()
                                    for i in range(0, len(paths_copy)):
                                        if paths_copy[i] == path_b:
                                            dummy = simple_path.pop(i)
                                    path = list(path_b)
                                    if lugar_nodo in path:
                                        path.remove(lugar_nodo)
                                    bandera_salida = False
                                    vector_verificacion_no_mapeo_01 = []
                                    # esto es para indicar los nodos copy
                                    path_buffer = list(path)
                                    # if recurso_elegido in path_buffer:
                                    #     path_buffer.remove(recurso_elegido)
                                    vector_dependency_01 = []
                                    if self.s_prints == 'list':
                                        print("verificaremos el path ", path)
                                    for node in path:

                                        if time_slot_buffer[node][0]:# and time_slot_buffer[node][2] != 'copy':#

                                            vector_dependency_01 = vector_dependency_01 + [
                                                time_slot_buffer[node][0]]
                                    if True in vector_dependency_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                                    else:  #
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [True]
                                        self.lista_nodos_copy_time = self.lista_nodos_copy_time + path_buffer  #
                                        bandera_salida = True
                                    if bandera_salida:
                                        break

                                # if lugar_nodo in self.lista_sinks_DG:
                                #     if self.s_prints == 'debug' or self.s_prints == 'basic':
                                #         print("not a sink")
                                #     bandera_es_sink = True
                                # else:
                                #     if self.s_prints == 'debug' or self.s_prints == 'basic':
                                #         print("verification of data dependence")
                                #
                                #     if self.s_prints == 'debug' or self.s_prints == 'basic':
                                #         print("esto cambio bastante por el bug del ejemplo checar si esta bien todo")
                                #     sink = sink_node_from_any_node(self.DG_original,
                                #                                    self.lista_sinks_DG,
                                #                                    lugar_nodo)
                                #     simple_path = []
                                #     for sink in self.lista_sinks_DG:
                                #         buffer_dummy = simple_paths_from_two_nodes(self.DG_original,
                                #                                                    lugar_nodo,
                                #                                                    sink)
                                #         if buffer_dummy:
                                #             for ni in buffer_dummy:
                                #                 simple_path.append(ni)

                                # simple_path.append( simple_paths_from_two_nodes(self.DG_original,
                                #                                                     lugar_nodo,
                                #                                                     sink))
                                # print(simple_path)
                                # if self.s_prints == 'debug' or self.s_prints == 'basic':
                                #     print("the simple paths are ", simple_path, recurso_elegido)
                                # vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                                # vector_verificacion_no_mapeo_02 = []  ######por cada path
                                # if simple_path:
                                #     for unique_path_b in simple_path:
                                #         unique_path = list(unique_path_b)
                                #         unique_path.remove(lugar_nodo)
                                #         list_copy_function = list(unique_path)
                                #
                                #         # todo checar si este cambio es correcto
                                #         # if recurso_elegido in list_copy_function:
                                #         #     list_copy_function.remove(recurso_elegido)
                                #         list_copy_copia = list(list_copy_function)
                                #         # print("el path para verificar ", list_copy_copia,lugar_nodo,
                                #         #                                        sink,recurso_elegido)
                                #         for el in list_copy_copia:
                                #             if time_slot_buffer[el][0]:
                                #                 list_copy_function.remove(el)
                                #
                                #         self.lista_nodos_copy_time = self.lista_nodos_copy_time + list_copy_function
                                #         # self.lista_nodos_copy.append(list_copy_function)
                                #
                                #
                                #         if self.s_prints == 'debug':
                                #             print("path to check ", unique_path)
                                #         vector_verificacion_no_mapeo_01 = []
                                #         for nodo_in_unique in unique_path:
                                #             vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                #                 time_slot_buffer[nodo_in_unique][0]]
                                #         if self.s_prints == 'debug':
                                #             print("debug - verification vector ", vector_verificacion_no_mapeo_01)
                                #         if not True in vector_verificacion_no_mapeo_01:
                                #             vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                #                 True]
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_sink = True
                        ### esto es la parte del source, entonces debe de estar en la parte actual,
                        # en realidad estamos buscando si el lugar del resource es source o si no es asi buscamos un source
                        if recurso_elegido in self.lista_sources_DG:
                            bandera_es_source = True
                        else:
                            source = source_node_from_any_node(copia_DG,
                                                               self.lista_sources_DG,
                                                               recurso_elegido)
                            simple_path = simple_paths_from_two_nodes(self.DG_copy,
                                                                      source,
                                                                      recurso_elegido)
                            if self.s_prints == 'debug' or self.s_prints == 'basic':
                                print("simple paths ", simple_path)
                                print(time_slot_buffer)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            if simple_path:
                                for unique_path in simple_path:

                                    unique_path_buffer = list(unique_path)
                                    unique_path_buffer.remove(recurso_elegido)
                                    if self.s_prints == 'list':
                                        print(f"ESTAMOS ANEXANDO ALGO {unique_path_buffer} a {self.lista_nodos_copy}")

                                    vector_verificacion_no_mapeo_01 = []
                                    for nodo_in_unique in unique_path:
                                        vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                            lista_salida_memoria[nodo_in_unique][0]]
                                    if not True in vector_verificacion_no_mapeo_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                            True]
                                        self.lista_nodos_copy = unique_path_buffer + self.lista_nodos_copy
                                        self.lista_en_time_slots = True

                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_source = True
                        # print(f"las banderas sink {bandera_es_sink} source {bandera_es_source}")
                        if self.s_prints == 'debug' or self.s_prints == 'list':
                            print("las banderas en el caso raro son(sink,source) ", bandera_es_sink, bandera_es_source)
                        if bandera_es_source and bandera_es_sink:
                            # bandera_mapping_valido = True
                            vector_predecesores_verificacion.append(True)

            if False in vector_predecesores_verificacion:
                bandera_mapping_valido = False
            else:
                bandera_mapping_valido = True



        else:
            if recurso_elegido in self.lista_sources_DG:
                bandera_mapping_valido = True
            else:

                source_nodo = source_node_from_any_node(copia_DG, self.lista_sources_DG, recurso_elegido)
                simple_path = simple_paths_from_two_nodes(copia_DG, source_nodo, recurso_elegido)
                # print("estamos en la verificacion de paths", source_nodo,simple_path)
                vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                vector_verificacion_no_mapeo_02 = []  ######por cada path
                if simple_path:
                    for unique_path in simple_path:
                        vector_verificacion_no_mapeo_01 = []
                        for nodo_in_unique in unique_path:
                            vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                lista_salida_memoria[nodo_in_unique][0]]
                        if not True in vector_verificacion_no_mapeo_01:
                            vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                True]
                    # print(vector_verificacion_no_mapeo_02)
                    if True in vector_verificacion_no_mapeo_02:
                        bandera_mapping_valido = True
        if self.s_prints == 'list':
            if bandera_mapping_valido:
                print("there is a chance that it can not be mapped", vector_predecesores_verificacion)
            else:
                print("the node can not be mapped", vector_predecesores_verificacion)
        return bandera_mapping_valido

    def reinicio_time_slot(self, lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                           vector_nodos_especiales, bandera_caso_no_probabilidad):

        if self.s_prints == 'iter' or self.s_prints == 'basic':
            print("------------------------------------------------------------")
            print("Creation of a time slot")
            print("------------------------------------------------------------")

        if self.s_pause and self.s_prints == 'basic':
            input("Press Enter to continue...")
        self.counter = 0
        if self.s_prints == 'debug':
            print(vector_nodos_especiales)
        lista_nodos_mapeados = []
        for elemento in lista_salida_memoria:
            if elemento[0]:
                if elemento[1] != None:
                    lista_nodos_mapeados.append(elemento[1])
        if self.s_prints == 'debug':
            print("mapped nodes", lista_nodos_mapeados)
        lista_parejas = []
        lista_nodos_ag = list(self.AG_copy.nodes)
        if self.s_prints == 'debug' or self.s_prints == 'basic':
            print(lista_nodos_ag)
            print(lista_nodos_mapeados)
        for elemento in lista_nodos_mapeados:
            if elemento == None:
                pass
            else:
                lista_nodos_ag.remove(elemento)
        if self.s_prints == 'basic':
            print("la lista de nodos que auedan es ", lista_nodos_ag)
        for nodo in lista_nodos_mapeados:
            if nodo == None:
                pass
            else:
                for elemento in lista_nodos_ag:

                    path_time = list(nx.all_simple_paths(self.AG_copy, source=nodo, target=elemento, cutoff=1))
                    if path_time:
                        lista_parejas.append([nodo, elemento])
        nuevo_vector_parejas = []
        contador = 0
        vector_buffer_pareja = []
        if self.s_prints == 'debug' or self.s_prints == 'list':
            print("test 01 debug de problema de sinks QQQQQQQQQQQQ", lista_parejas, self.datapaths_independientes)
            print(lista_parejas, self.datapaths_independientes)
        for parejas in lista_parejas:
            if self.s_prints == 'list': print(parejas)
            for elemento in range(0, len(lista_salida_memoria)):
                if parejas[0] == lista_salida_memoria[elemento][1]:
                    if self.s_prints == 'list':
                        print(f"sinks list  {self.lista_sinks_DG_total} ")

                    ############aqui se realizaran muchos cambios poraue en si la funcion es extrana

                    copy_lista_sinks_rc = self.list_sinks_connected_to_rc.copy()
                    copy_lista_sinks_rc.reverse()



                    if elemento in copy_lista_sinks_rc:
                        sink = elemento
                        vector_buffer_pareja.append([parejas[1], sink, False])
                    else:
                        bandera_break = False
                        for path_independiente in self.datapaths_independientes:
                            if elemento in path_independiente:
                                for copy_lista_sinks_rc_elemento in copy_lista_sinks_rc:
                                    if copy_lista_sinks_rc_elemento in path_independiente:
                                        sink = copy_lista_sinks_rc_elemento
                                        bandera_break = True
                                        break
                            if bandera_break:
                                break

                        if bandera_break:
                            vector_buffer_pareja.append([parejas[1], sink, False])
                        else:
                            sink = sink_node_from_any_node(self.DG_original, copy_lista_sinks_rc, elemento)
                            vector_buffer_pareja.append([parejas[1], sink, False])



                    # if elemento in self.lista_sinks_DG:
                    #     sink = elemento
                    #     vector_buffer_pareja.append([parejas[1], sink, False])
                    # else:
                    #     if self.s_prints == 'debug':
                    #         print("verification test")
                    #     for path in self.datapaths_independientes:
                    #         if elemento in path:
                    #             if self.s_prints == 'debug':
                    #                 print(elemento)
                    #             if len([elemento]) > 1:
                    #                 sink = sink_from_datapath(self.DG, path)
                    #             else:
                    #                 if self.s_prints == 'debug':
                    #                     print("se hicieron muchos cambios aqui")
                    #                     print("no entiendo esto")
                    #
                    #                 sink = sink_node_from_any_node(self.DG, self.lista_sinks_DG, elemento)
                    #                 # print(lista_salida_memoria)
                    #                 simple_path = []
                    #                 for sink in self.lista_sinks_DG:
                    #                     buffer_dummy = simple_paths_from_two_nodes(self.DG,
                    #                                                                elemento,
                    #                                                                sink)
                    #                     if buffer_dummy:
                    #                         for ni in buffer_dummy:
                    #                             simple_path.append(ni)
                    #
                    #                 # print(simple_path)
                    #                 if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                     print("the simple paths are ", simple_path)
                    #                 vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                    #                 vector_verificacion_no_mapeo_02 = []  ######por cada path
                    #                 path_limpio = []
                    #                 if simple_path:
                    #                     for unique_path_b in simple_path:
                    #                         unique_path = list(unique_path_b)
                    #                         unique_path.remove(elemento)
                    #                         if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                             print("path to check ", unique_path)
                    #                         vector_verificacion_no_mapeo_01 = []
                    #                         for nodo_in_unique in unique_path:
                    #                             vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                    #                                 lista_salida_memoria[nodo_in_unique][0]]
                    #                         if self.s_prints == 'debug' or self.s_prints == 'basic':
                    #                             print("debug - verification vector ", vector_verificacion_no_mapeo_01)
                    #                         if not True in vector_verificacion_no_mapeo_01:
                    #                             vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                    #                                 True]
                    #                             if self.s_prints == 'basic':
                    #                                 print("el path elegido es ",unique_path_b)
                    #                             path_limpio = unique_path_b
                    #                 if self.s_prints== "basic":
                    #                     print("test de algo ",path_limpio,self.lista_sinks_DG_total)
                    #                 for hi in path_limpio:
                    #
                    #                     copy_lista_sinks_rc = self.list_sinks_connected_to_rc.copy()
                    #                     if hi in self.lista_sinks_DG:
                    #
                    #                         sink = hi
                    #
                    #
                    #             if self.s_prints == 'debug':
                    #                 print(sink)
                    #             if self.s_prints == 'basic':
                    #                 print("hfofd",sink)
                    #             vector_buffer_pareja.append([parejas[1], sink, False])
        if self.s_prints == 'debug' or self.s_prints == 'basic':
            print("old version test", vector_buffer_pareja)
            print("la parajera", vector_buffer_pareja)
        self.vector_de_parejas_memoria = vector_buffer_pareja
        if self.s_prints == 'debug' or self.s_prints == 'basic':
            print(self.vector_de_parejas_memoria)
            print("la lista hasta ahorita es", lista_salida_memoria)
        lista_final.append(lista_salida_memoria)
        if self.s_prints == 'basic':
            print("los recursos son ", list(copia_DG.nodes))
        self.lista_nodos_time_slot_anterior = []
        for nodo in range(0, len(lista_salida_memoria)):
            if not lista_salida_memoria[nodo][0]:
                self.lista_nodos_time_slot_anterior.append(nodo)
            elif lista_salida_memoria[nodo][0] and lista_salida_memoria[nodo][2] == 'copy':
                self.lista_nodos_time_slot_anterior.append(nodo)

        lista_salida_memoria = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                range(len(copia_DG))]
        self.DG_copy = copia_DG.copy()
        primer_grupo = obtencion_sources(self.DG_copy)
        bandera_primer_nodo = True
        # vector_nodos_especiales.extend(vector_buffer_pareja)
        # if vector_nodos_especiales:
        vector_buffer_especiales.append(vector_nodos_especiales)
        vector_nodos_especiales = []
        bandera_reinicio = True
        self.contador_instancias = self.contador_instancias + len(self.DG_copy.nodes)
        if self.s_prints == 'basic':
            print("new time slot")
            print("el nuevo primer grupoi es", primer_grupo)
        bandera_caso_no_probabilidad = False
        return bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad

    def datapaths_available_v1(self, lista):

        print("nueva funcion")
        # print(lista)
        vector = []
        lista_vector = []
        lista_provisional = [False for n in range(0, len(lista))]
        # print(self.datapaths_independientes)
        for path in self.datapaths_independientes:
            vector = []
            for nodo in path:
                vector.append(lista[nodo][0])
            if True in vector:
                for nodo in path:
                    lista_provisional[nodo] = True

        # print(lista_provisional)
        # print(lista)
        return lista_provisional

    def datapaths_available(self, lista_salida_memoria):
        if self.s_prints == 'list':
            print("verification of datapaths")
        vector_01 = []
        bandera_recomputo = False
        datapath_available = []
        for simple_path in self.datapaths_independientes:
            # print(simple_path)
            vector_01 = []
            for nodo in simple_path:
                # print(lista_salida_memoria[nodo][0])
                vector_01 = vector_01 + [lista_salida_memoria[nodo][0]]
            # print(vector_01)
            if not True in vector_01:
                datapath_available = datapath_available + simple_path
        if self.s_prints == 'debug' or self.s_prints == 'list':
            print("test inside the verification of datapaths")
            print(self.lista_AG_copy + [self.tarea_a_mapear_global])
            print(self.lista_nodos_ya_mapeados)
        # lista_predecesores_01 = []
        for nodos_restante in self.lista_AG_copy + [self.tarea_a_mapear_global]:
            predecesores = self.AG_original.predecessors(nodos_restante)

            if list(predecesores):
                if self.s_prints == 'list':
                    print(
                        f"los precesores de {nodos_restante} son {list(self.AG_original.predecessors(nodos_restante))}")
                for predecesor in self.AG_original.predecessors(nodos_restante):
                    # print("kjdkfnskfsdfsd")
                    if predecesor in self.lista_nodos_ya_mapeados:
                        for elemento in range(0, len(lista_salida_memoria)):
                            if lista_salida_memoria[elemento][1] == predecesor:
                                lugar_nodo = elemento

                        ####nodo restante es el nodo que no se ha mapeado, predecesor es su predecesor que ya se mapeo
                        #### y el lugar_nodo es donde se mapeo, con respecto al grafo de hardware, el ultimo elemento es
                        ####para identificar si es nodo de recomputo (False) o nodo entre time slots (True)
                        if datapath_available:
                            buffer_predecesor = [nodos_restante, predecesor, lugar_nodo, False]
                            # else:
                            #     buffer_predecesor = [nodos_restante, predecesor, lugar_nodo, True]
                            self.lista_predecesores_01.append(buffer_predecesor)
        if self.s_prints == 'debug' or self.s_prints == 'list':
            print("las predecesores son")
            print(self.lista_predecesores_01)

        if datapath_available:
            if self.s_prints == 'debug' or self.s_prints == 'list':
                print(f"we still have datapaths {datapath_available}")
            bandera_recomputo = True
        # print("se esta checando si existen datapaths")
        # input("se esta checando si existen datapaths")
        return (datapath_available, bandera_recomputo)

    def mapping_for_constrains(self, nodo_AG, resource, lista_final, lista_salida_memoria, copia_DG, bandera_recomputo,
                               sucesores_nodo_AG, vector_buffer_especiales,
                               vector_nodos_especiales, bandera_caso_no_probabilidad):

        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
        print("verificacion de sources ", bandera_source_of_data, info_sensor)

        if self.s_prints == 'basic' or self.s_prints == 'iter':
            print(
                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to the resource {self.dict_nodes[resource]['name']} ")
            print("------------------------------------------------------------")
        if self.s_pause:
            input("Press Enter to continue...")
        if self.s_prints == 'basic':
            print("modulo 11 - debug")
        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

        if self.s_prints == 'basic' or self.s_prints == 'debug':
            # print(self.lista_nodos_copy)
            # print(self.lista_nodos_copy_time)
            print("we are going to map something so we need to add the copy nodes 03")
            print(lista_final)

        ######## aqui integramos todos los copy nodes

        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                   nodo_AG,
                                                                   lista_salida_memoria,
                                                                   lista_final, copia_DG,
                                                                   bandera_recomputo)

        if self.lista_en_time_slots:
            if self.s_prints == 'basic':
                print("estamos en algo extrano")
                print(lista_final[self.lugar_time_slot - 1])
            for copy_node in self.lista_nodos_copy_time:
                if self.s_prints == 'basic':
                    print(f"esto esta bien raro y se pone mas raro {copy_node}")
                lista_final[self.lugar_time_slot - 1][copy_node] = [True, None, 'copy', 'copy', copy_node,
                                                                    nodo_AG, 's3', 0, 0, 0, 0, 0, 0, 0]
            for copy_node in self.lista_nodos_copy:
                if self.s_prints == 'basic':
                    print(f"todavia mas raro vamos a ver que onda {copy_node}")
                lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', copy_node, nodo_AG, 's2', 0, 0, 0, 0, 0,
                                                   0]

        else:
            for copy_node in self.lista_nodos_copy:
                if self.s_prints == 'basic':
                    print(f"todavia mas raro vamos a ver que onda {copy_node}")
                lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', copy_node, nodo_AG, 's1', 0, 0, 0, 0, 0,
                                                   0]

        # # we already add the nodes between tasks but we need to add the copy nodes from the sink tasks
        # # to the sinks of the hardware
        actuator_sink = None
        if nodo_AG in self.lista_sinks_AG and resource not in self.lista_sinks_DG:
            print(" si la tarea es un sink y el recurso no es sink")
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")

            sink_nodo_sink_task = sink_node_from_any_node(self.DG_original, self.lista_sinks_DG,
                                                          resource)
            # print(resource,sink_nodo_sink_task,self.lista_sinks_DG)
            path_sink_node = simple_paths_from_two_nodes(self.DG_original, resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'basic':
                print("the paths between the sink task and the sink hardware", path_sink_node)
                print(
                    f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            single_path = path_sink_node.pop()
            single_path.remove(resource)
            for nodo_a_sink in single_path:
                lista_salida_memoria[nodo_a_sink] = [True, None, 'copy', 'copy', nodo_a_sink, nodo_AG, 's0', 0, 0, 0, 0,
                                                     0, 0]
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == self.DG_original.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.lista_sinks_DG_total.copy()
            while done:
                sink_test = copia_sinks.pop()
                if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t, sink_test):
                    actuator_sink = sink_test
                    done = False
                    break
            self.lista_sinks_DG_total = self.lista_sinks_DG_total.remove(actuator_sink)

        if nodo_AG in self.lista_sources_AG and resource not in self.lista_sources_DG:
            print("el recurso no es un source y la tarea  es un source")
            if self.s_prints == 'basic':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            source_nodo_sink_task = source_node_from_any_node(self.DG_original,
                                                              self.lista_sources_DG,
                                                              resource)
            path_source_node = simple_paths_from_two_nodes(self.DG_original, source_nodo_sink_task,
                                                           resource)
            if self.s_prints == 'basic':
                print("the paths between the source task and the osusdofsdf hardware",
                      path_source_node)
                print(
                    f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            single_path = path_source_node.pop()
            single_path.remove(resource)
            for nodo_a_source in single_path:
                lista_salida_memoria[nodo_a_source] = [True, None, 'copy', 'copy', nodo_a_source, nodo_AG,
                                                       's9', 0, 0, 0, 0, 0, 0]

        # aqui obtenemos informacion sobre el actuator, si la tarea es un sink
        if nodo_AG in self.lista_sinks_AG:

            lugar_n = None
            for nodo_total in self.AG_total.nodes:
                # print(nodo_total)
                if self.AG_original.nodes[nodo_AG]['name'] == self.AG_total.nodes[nodo_total]['name']:
                    # print("encontrado")
                    lugar_n = nodo_total
            sinks_ag_total = obtencion_sinks(self.AG_total)
            actuator_info = sink_node_from_any_node(self.AG_total, sinks_ag_total, lugar_n)
            info_actuator = [self.AG_total.nodes[actuator_info]['name'],
                             self.AG_total.nodes[actuator_info]['par']['height'],
                             self.AG_total.nodes[actuator_info]['par']['width']]
        else:
            info_actuator = [None, None, None]

        lista_salida_memoria[resource] = [True, nodo_AG, resource,
                                          self.AG.nodes[nodo_AG]['op'],
                                          self.dict_nodes[
                                              resource][
                                              'ops'][
                                              self.AG.nodes[nodo_AG]['op']][
                                              'latency'],
                                          self.AG.nodes[nodo_AG]['par'],
                                          self.AG.nodes[nodo_AG]['par'],
                                          self.dict_nodes[
                                              resource][
                                              'ops'][
                                              self.AG.nodes[nodo_AG]['op']][
                                              'clk'], resultado_latencia,
                                          resultado_latencia_total, info_sensor, info_actuator,
                                          actuator_sink
                                          ]

        # we keep track of the tasks that we map
        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
        if self.s_prints == 'basic':
            print(self.DG_copy.nodes)
            print("jndsijfsd", self.lista_predecesores_01)
            print("la lista de salida es ", lista_salida_memoria)
        # we proceed to create the special nodes, if necessary

        if self.lista_predecesores_01:
            if self.s_prints == 'debug' or 'basic':
                print("creation of a special node")
                print(self.lista_predecesores_01)
            # input("Continue ...")
            for nodo_especial in self.lista_predecesores_01:
                if nodo_especial[0] == nodo_AG:

                    # todo cambiar esta parte tambien

                    if nodo_especial[2] in self.lista_sinks_DG:
                        lugar_sink = nodo_especial[2]
                    else:
                        lugar_sink = sink_node_from_any_node(self.DG_original, self.lista_sinks_DG,
                                                             nodo_especial[2])
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                 resource)

                    buffer_nodo_especial = [nodo_especial[3], lugar_sink, lugar_source,
                                            len(lista_final), self.contador_recomputacion]
                    if self.s_prints == 'basic':
                        print(
                            f" se anexara un nodo especial 01-b {buffer_nodo_especial} y la lista es {self.lista_nodos_especiales}")

                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    self.lista_predecesores_01.remove(nodo_especial)
        # we add the special nodes corresponding to the nodes mapped in the previous time slot
        elementos_to_remove = []
        if self.s_prints == 'basic':
            print("las parejas son ", self.vector_de_parejas_memoria)
        if self.vector_de_parejas_memoria:
            if self.s_prints == 'basic':
                print("jbdsfds")
            for pareja in self.vector_de_parejas_memoria:
                if nodo_AG == pareja[0]:
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                 resource)

                    buffer_nodo_especial = [True, pareja[1], lugar_source, len(lista_final),
                                            self.contador_recomputacion]
                    if self.s_prints == 'basic':
                        print(
                            f" se anexara un nodo especial 02 {buffer_nodo_especial} y la lista es {self.lista_nodos_especiales}")
                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    elementos_to_remove.append(pareja)
            for el in elementos_to_remove:
                self.vector_de_parejas_memoria.remove(el)

        # now we check if there are still tasks to map
        # and if the following task is a successor of the newly mapped task
        if len(self.lista_AG_copy) > 0:
            if self.s_prints == 'debug':
                print("there is more tasks to map ")
            # verification of the conexion between the following task and the newly mapped one
            # bandera_no_conexion activated (True) means that there is no connection, but False
            # means that there is a connection
            if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                bandera_no_conexion = False
            else:
                if self.s_prints == 'basic' or self.s_prints == 'debug':
                    print(
                        "there is no connection between the current mapped task and the next task 01")
                bandera_no_conexion = True
            # deactivation of the recomputation flag
            bandera_recomputo = False

        # if there are no more tasks to map we end the mapping here
        if self.s_pause and self.s_prints == 'basic':
            input("Press Enter to continue...")
        if not self.lista_AG_copy:
            lista_final.append(lista_salida_memoria)

        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
        # is no more successors of the current task
        elif not sucesores_nodo_AG or bandera_no_conexion:
            print("ciclo elif de algo")
            # in here we are going to check if there are datapaths available
            if self.s_prints == 'debug':
                print("verification of available datapaths")
                print("for debugging we are going to print the current mapping list")
                print(lista_salida_memoria)

            # we call the function that verifies the datapaths
            lista_datapaths_disponibles, bandera_recomputo = self.datapaths_available(
                lista_salida_memoria)
            if self.s_prints == 'debug':
                print("we return from the verification of datapaths")
            cuenta = 0
            # if we have datapaths available we return their nodes to the resources list
            print(lista_datapaths_disponibles)
            if lista_datapaths_disponibles:
                if self.s_prints == 'debug':
                    print("there are datapaths available so we reintegrate their resources")
                self.DG_copy = self.remove_nodes_DG(lista_datapaths_disponibles)

                primer_grupo = obtencion_sources(self.DG_copy)
                bandera_primer_nodo = True
            else:
                print("thehe")
                # if we dont have any available datapath we create a time slot
                if self.s_prints == 'basic' or self.s_prints == 'debug':
                    print("creation of time slot in stage 1")
                bandera_reinicio_dummy, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad = self.reinicio_time_slot(
                    lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                    vector_nodos_especiales, bandera_caso_no_probabilidad)


        else:
            # in this part we only update the first group of candidates, because there are still
            # resources and tasks
            print("ciclo else de algo")
            if self.s_prints == 'debug' or self.s_prints == 'basic':
                print("we end a cycle in stage 1b")
                print("the current mapping list is")
                print(lista_salida_memoria)
                print(self.DG_copy.nodes)

            primer_grupo = list(self.DG_original.successors(resource))
            # print(primer_grupo)
            if self.s_prints == 'basic':
                print("BUGG N")
                print(primer_grupo)
            if not primer_grupo:
                # we call the function that verifies the datapaths
                lista_datapaths_disponibles, bandera_recomputo = self.datapaths_available(
                    lista_salida_memoria)
                if self.s_prints == 'debug':
                    print("we return from the verification of datapaths")
                cuenta = 0
                # if we have datapaths available we return their nodes to the resources list
                if lista_datapaths_disponibles:
                    if self.s_prints == 'debug':
                        print("there are datapaths available so we reintegrate their resources")
                    self.DG_copy = self.remove_nodes_DG(lista_datapaths_disponibles)
                    primer_grupo = obtencion_sources(self.DG_copy)
                    # print(primer_grupo)
                    bandera_primer_nodo = True
                else:
                    # print("debeeria de entra aqui")
                    # if we dont have any available datapath we create a time slot
                    if self.s_prints == 'basic' or self.s_prints == 'debug':
                        print("creation of time slot in stage 1")
                    bandera_reinicio_dummy, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad = self.reinicio_time_slot(
                        lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                        vector_nodos_especiales, bandera_caso_no_probabilidad)

            if self.s_prints == 'basic' or self.s_prints == 'debug':
                dummy_print_dg = []
                for nd in primer_grupo:
                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                print(f"the new possible candidates are {dummy_print_dg}")
        bandera_primer_nodo = False
        mapping = False
        if self.s_prints == 'basic':
            print("finalizacion del modulo de constrains")
        return lista_final, lista_salida_memoria, copia_DG, bandera_recomputo, sucesores_nodo_AG, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad