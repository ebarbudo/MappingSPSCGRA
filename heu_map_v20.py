import networkx as nx
import random
import time
import matplotlib.pyplot as plt
from graphviz import Digraph
from basic_functions import source_node_from_any_node,sink_from_datapath,sink_node_from_any_node,obtencion_sucesores,\
    obtencion_sources,obtencion_sinks,simple_paths_from_two_nodes
# import class_performance_v4
import collections
infinito = 1000000


# misc functions




def obtencion_critical_path(input_graph):
    """"from an input graph it obtains the critical path in  terms of number of nodes, if the
    graph is empty it returns a value near to zero"""
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

    """"obtains the entire set of descendants from a list, it obtain for each element of the
     list its decendents then add all"""

    # print("la lista a checar es ", lista_nodos)
    lista_total_sucesores = []

    for nodo in lista_nodos:
        try:
            lista_sucesores = nx.dfs_successors(input_graph, nodo)
        except:
            #esto quiere decir que no existen sucesores de dicho nodo
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




class HeuristicMethod:

    def __init__(self, DG, AG, dict_nodes,
                 dict_info, selection_prints, dict_nodes_a, selection_pause, dict_info_a,DG_total,AG_total,
                 dict_total,debugging_options,lista_constraints,lista_tareas_constrains):


        #### global variables

        ####application related
        self.AG_total = AG_total.copy()
        self.AG = AG.copy()
        self.AG_original = AG.copy()
        self.dict_nodes_a = dict_nodes_a
        self.dict_info_a = dict_info_a
        self.AG_copy = AG.copy()
        self.AG_copia = AG.copy()
        ####hardware related
        self.DG_total = DG_total
        self.DG = DG.copy()
        self.DG_copy = DG.copy()
        self.DG_original = DG.copy()
        self.dict_total = dict_total
        self.dict_nodes = dict_nodes
        ####general information
        self.dict_info = dict_info
        ####constrains
        self.lista_constraints = lista_constraints
        self.lista_tareas_constrains = lista_tareas_constrains
        ####general arguments
        self.s_prints = selection_prints
        self.debugging_options = debugging_options
        self.s_pause = selection_pause

        ####function to get the resources that are connected to a rw resource, this is important to get in order to
        # define if the hardware allows recomputation
        self.list_sinks_connected_to_rc = self.sinks_connected_to_rc()
        # we obtain the independent datapaths of the hardware graph
        self.datapaths_independientes = self.generation_datapaths(self.DG_original)
        if self.s_prints == 'heudebug':
            print("we are going to start the process of the hueristic mapping")

        #####main mapping function
        self.lista_final, self.vector_config_01, self.vector_config_02 = self.Mapping()

        if self.s_prints == 'heudebug':
            print(f"the final list is {self.lista_final}")
            print(f"the special nodes are {self.lista_nodos_especiales}")
            print("end of mapping")

    def generation_datapaths(self,input_graph):
        """his function defines the independent datapaths, the process is over an hardware graph
        we verify the resources that have an output degree of two and if one of those edges is connected to a resource
        with input degree of two, then we remove one of those edges, next after this transformation we define the
        independent datapaths, the input parameter is
        :parameter hardware graph without the communication nodes (basic structure)"""

        # vamos a cambiar el codigo y poner el grafo total
        lista_paths = []
        lista_nodos_ocupados_sink = []
        lista_nodos_ocupados_source = []
        nodos_ocupados = []
        ####tranformation of the input graph, we remove certain edges
        copia_DG_proceso_previo = input_graph.copy()
        for nodo in copia_DG_proceso_previo.nodes:
            # if the resource has more than one output edge
            if copia_DG_proceso_previo.out_degree(nodo) > 1:
                # we obtain its successors
                sucesores = copia_DG_proceso_previo.successors(nodo)
                for suc in sucesores:
                   # if the successor has a input degree greater than 1
                    if copia_DG_proceso_previo.in_degree(suc) > 1:
                        # we remove the edge
                        copia_DG_proceso_previo.remove_edge(nodo, suc)
                        break
        # we obtain the source nodes of the resulting graph
        sources_test = obtencion_sources(copia_DG_proceso_previo)
        # we make a copy of the nodes that allows to output data
        sinks_test = self.list_sinks_connected_to_rc
        # print(sinks_test)
        # input("test")
        # in here we produce the independent datapaths
        for source in sources_test:
            for sink in sinks_test:
                paths = nx.all_simple_paths(copia_DG_proceso_previo, source=source, target=sink)
                todos_los_paths = list(paths)
                if todos_los_paths:
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
        if self.s_prints == 'heudebug':
            print(f"the independent datapaths are {lista_paths}")
            # input("")
        lista_paths_respaldo = lista_paths.copy()
        return lista_paths_respaldo





    def sinks_connected_to_rc(self):
        """this functions allow us to define the resources that are able to output data, the ones that are connected
        to a rw or a ri resource"""
        # todo verify if we need the DG_original or we can use another and remove that copy
        list_sinks_connected_to_rc = []
        bandera_salida = True
        # we traverse the hardware graph
        for nodo in self.DG_original.nodes:
            # we find the successors
            edges_nodo = self.dict_nodes[nodo]['edges']
            bandera_salida = True
            # for each successor
            for i in edges_nodo:
                if i:
                    # we gather the information about the successor
                    for n, data in self.dict_total.items():
                        if data['name'] == i:
                            # if the successor is a rw or a ri we added it to the list
                            if data['type'] == 'rw' or  data['type'] == 'ri':
                                list_sinks_connected_to_rc.append(nodo)
                                bandera_salida = False
                                break
                if not bandera_salida:
                    break
        if self.s_prints == 'huedebug':
            print(f"we return from the sinks connected to rc function, the result is {list_sinks_connected_to_rc}")
        return list_sinks_connected_to_rc



    def evaluation_degree(self,elemento,task,lista_salida_memoria):
        """this function verify the compability of degree between a task and a resource
        the idea is to compare the input and output degree of both elements and see if the following relations hold:
        input degree
            if the input degree of both elements are the same
            if the input and output degree of the task are zero and the output degree of the resource is zero
            if the input degree of the resource is greater than the input degree of the task, we verify that the
            predecessors of the resource dont have any task mapped other than the predecessors of the task in process
            otherwise the input degree condition is not valid
        output degree
            if the output degree of the resource is equal to the output degree of the task
            if the output degree of the resource is zero
        :parameter elemento is the resource to verify
        :parameter task is the task to verify
        :parameter lista_salida_memoria is the current mapping list
        """
        #########################################################################
        # input degree case
        input_degree_flag = False
        # if the input degree of both the resource and the task are the same
        if self.DG_original.in_degree(elemento) == self.AG.in_degree(task):
            input_degree_flag = True
        # if the input and output degree of the task is zero and also the output degree of the resource is zero
        elif self.AG.in_degree(task) == 0 and self.AG.out_degree(task) == 0 and self.DG_original.out_degree(
                elemento) == 0:
            input_degree_flag = True
        # if the input degree of the resource is greater than the task
        elif self.DG_original.in_degree(elemento) > self.AG.in_degree(task):
            # we obtain the predecessors of both of the task and the resource
            predecesores_tarea = self.AG.predecessors(task)
            predecesores_recurso = self.DG_original.predecessors(elemento)
            # we verify for each resource's predecessors
            for pr in predecesores_recurso:
                # if self.s_prints == 'heudebug':
                #     print(lista_salida_memoria[pr])
                # if we find another task mapped onto the predecessor and it is not a predecessor of the task the
                # condition is not valid, otherwise the condition is valid
                if lista_salida_memoria[pr][0] and lista_salida_memoria[pr][1] not in predecesores_tarea:
                    input_degree_flag = False
                    break
                else:
                    input_degree_flag = True

        # output degree case
        output_degree_flag = False
        # if the output degree of the resource is greater than the output degree of the task or if the output degree
        # of the resource is zero
        if self.DG_original.out_degree(elemento) >= self.AG.out_degree(task) or self.DG_original.out_degree(
                elemento) == 0:
            # if self.s_prints == 'heudebug':
            #     print("test modification degree 1")
            output_degree_flag = True
        # otherwise we need to check another condition, which is that the sum of the output degree of the resource plus
        # the output degree of his sucessors does exceed the output degree of the task, and that the sum of input degree
        # of the resource and the input degree of the predecessors does exceed the input degree of the task
        else:
            # first we verify the case of the output degree, we obtain the list of successors of the resource and its
            # output degre
            sucesor_degree = self.DG_original.successors(elemento)
            conteo_sucesores = self.DG_original.out_degree(elemento)
            # next, for each successor we add its output degree to the output degree of the resource
            for su in sucesor_degree:
                conteo_sucesores = conteo_sucesores + self.DG_original.out_degree(su)

            # second, we verify the case of the input degree, we obtain the list of predecessors of the resource and
            # its input degree
            conteo_predecesores = self.DG_original.in_degree(
                elemento)
            predecesor_degree = self.DG_original.predecessors(elemento)
            # next, we add the input degree of each predecessor to the input degree of the resource
            for pr in predecesor_degree:
                conteo_predecesores = conteo_predecesores + self.DG_original.in_degree(pr)

            # finally we validate the condition
            if conteo_sucesores >= self.AG.out_degree(
                    task) and conteo_predecesores >= self.AG.in_degree(task):
                output_degree_flag = True
            else:
                output_degree_flag = False

            # if self.s_prints == 'heudebug':
            #     print("Test 2 degree modification", conteo_sucesores, conteo_predecesores,
            #           output_degree_flag)
        if self.s_prints == 'heudebug':
            print(f"we are going to return from the evaluation of degree, the result is "
                  f"{input_degree_flag,output_degree_flag}")
        # if both conditions are valid we return True
        if output_degree_flag and input_degree_flag:
            return True
        else:
            return False





    def obtencion_probabilidad(self, app_graph, successors_task, nodo_hw, DG,
                                       total_nodes, lista_salida_memoria):
        """In this function we obtain the probability of mapping success,
         :parameter app_graph is the application graph
         :parameter successors_task is the set of tasks successors
         :parameter nodo_hw is the resource
         :parameter DG is the hardware graph
         :parameter total_nodes is the set of descendants of all the possible candidates
         :parameter lista_salida_memoria is the current mapping list"""
        # todo we need to improve the description of the function depending of the final definition of this equation
        # if self.s_prints == 'heudebug':
        #     print("we are in the probability function")
        #     print( "the successors of the task", successors_task)
        #     print("the descendants and the resource",total_nodes, nodo_hw)
        #     print("values to use:")
        #     dummy_print_ag = []
        #     for nd in successors_task:
        #         dummy_print_ag.append(self.dict_nodes_a[nd]['name'])
        #     dummy_print_dg = []
        #
        #     print(f"the successors of the current task are {dummy_print_ag}")
        #     print(f"the successors of the resource candidate {self.dict_nodes[nodo_hw]['name']} are {dummy_print_dg}")
        #     dummy_print_dg = []
        #     for nd in total_nodes:
        #         dummy_print_dg.append(self.dict_nodes[nd]['name'])
        #     print(f"all the descendants of the candidates {dummy_print_dg}")

        minimo_valor_distancias = 0
        # first from the resource we find its successors
        try:
            set_sucesores_nodo = obtencion_sucesores(DG, nodo_hw)
        except:
            set_sucesores_nodo = []

        if self.s_prints == 'heudebug':
            print("the successors of the resource are ", set_sucesores_nodo)

        # obtention of the critical path of the set of all the descendants of the list of candidates
        # todo this can be a function itself
        # we create a copy of the hardware graph to create a subgraph of only the descendants
        copia_DG = DG.copy()
        # if there is descendants
        if len(total_nodes) >= 1:
            # if self.s_prints == 'heudebug':
            #     print("it seems like there is a set of successors")
            # if the number of descendants is only one we will not be able to create a subgraph so we assign a 1 to
            # the critical path
            if len(total_nodes) == 1:
                critical_path = 1
            else:
                # if the number of descendants is more than 1 then we can create a subgraph where we can find a critical
                # path based on the number of nodes in a path (upward rank)
                CPGraph = copia_DG.subgraph(total_nodes)
                critical_path = obtencion_critical_path(CPGraph)
        else:
            # if there is no descendants we assign a 1 to the critical path
            # if self.s_prints == 'heudebug':
            #     print("there is no set of descendants we assign a value of 1")
            critical_path = 1

        probabilidad = 0
        cuenta = 0
        computing_latency_list = []

        # we start the compute of the equation
        # for each task in the set of tasks successors
        for task in successors_task:  #####for each task of the succesor of the application node
            # we gather the type of task
            operacion = app_graph.nodes[task]['op']
            # we obtain the worse computing latency of this type of task
            # we assign a default value of the worse computing latency todo we maybe need to define better this value
            worse_computing_latency = -1
            # for this purpose we traverse the set of descendants
            for descendant in total_nodes:
                # we try to obtain the computing latency of the task of the descendant, we put this process into a
                # try/except because maybe the resource does not have this task so an exception will raise
                try:
                    # we gather the equation of the computing latency
                    worse_function = self.dict_info['functions_res'][
                        self.dict_nodes[descendant]['ops'][operacion]['clk']]
                    # if the computing latency is an equation
                    if isinstance(worse_function, str):
                        # we call the separation of variable function
                        vector_total_parametros = self.variable_separation(worse_function)
                        vector_parametro = []
                        # this is the basic process to separate the parameters and put them in a list
                        for it in vector_total_parametros:
                            dummy = "".join(it)
                            if dummy:
                                try:
                                    int(dummy)
                                except:
                                    if dummy not in vector_parametro:
                                        vector_parametro.append(dummy)
                        # we now make a cross relation with the name of parameters with its values
                        # we first look for the general values of width and height
                        for param_formula in vector_parametro:
                            if param_formula == 'width':
                                pass
                            elif param_formula == 'height':
                                pass
                            else:
                                # in here we are going to look the value in the dict of the nodes
                                for pa in self.dict_nodes_a[task]['param']:
                                    # print(pa)
                                    if param_formula == pa:
                                        globals()[pa] = self.dict_nodes_a[task]['param'][pa]
                        # after the cross relation we evaluate the equation
                        value_clk = eval(worse_function)
                    else:
                        # if the equation is a constant we assign it to the temporal variable
                        value_clk = worse_function
                    # if self.s_prints == 'heudebug':
                    #     print("the computing latency is ",value_clk)
                    # we evaluate if the computing latency is worse than default value or the previous worse computing
                    # latency
                    if value_clk > worse_computing_latency:
                        worse_computing_latency = value_clk
                except:
                    # if the resource does not has this task we catch the error
                    pass

            # now we have the worse latency of the type of task and we need to find the number of possible allocations
            # in the set of successors of the resource
            # we initialize the variables
            cuenta = 0
            vector_distancias_entre_nodos = []
            lista_latencias = []
            # if self.s_prints == 'heudebug':
            #     print(set_sucesores_nodo)
            # if there is a set of successors
            if set_sucesores_nodo:
                # for each sucessor we verify that it can be used for this type of task
                for elemento in set_sucesores_nodo:
                    # we verify the degree condition
                    test_degree = self.evaluation_degree(elemento,task,lista_salida_memoria)
                    # if self.s_prints == 'heudebug':
                    #     print("inside the probability function test 01 ", DG.nodes[elemento], operacion)
                    # we verify that the type of task is compatible with the resource
                    if operacion in DG.nodes[elemento]['op'] and not lista_salida_memoria[elemento][0]:
                        # we add a try/except process to catch any error
                        # todo verify if this is needed it
                        try:
                            # we verify the parameters to validate that the resource is capable of allocate the task
                            validacion_parametros = self.verification_of_parameters(task, elemento)
                            # if the validation of the parameters and degree is valid
                            if all(validacion_parametros) and test_degree:
                                # we count the resource
                                cuenta = cuenta + 1
                                # next we need to find the computing latency of this resource when allocate this
                                # particular task
                                computing_latency_preliminar = 0
                                # we put this compute into a try/except to catch any error
                                # todo verify if this is needed it
                                try:
                                    # we gather the data of the computing latency equation
                                    worse_function = self.dict_info['functions_res'][
                                        self.dict_nodes[elemento]['ops'][operacion]['clk']]
                                    # print(worse_function)
                                    # if the computing latency is an equation
                                    if isinstance(worse_function, str):
                                        # we make the same process as always in order to evaluate the equation
                                        # todo maybe we can put this to a function itself
                                        vector_total_parametros = self.variable_separation(worse_function)
                                        vector_parametro = []
                                        for it in vector_total_parametros:
                                            dummy = "".join(it)
                                            if dummy:
                                                try:
                                                    int(dummy)
                                                except:
                                                    if dummy not in vector_parametro:
                                                        vector_parametro.append(dummy)
                                        for param_formula in vector_parametro:
                                            if param_formula == 'width':
                                                pass
                                            elif param_formula == 'height':
                                                pass
                                            else:
                                                # in here we are going to look the value in the dict of the nodes
                                                for pa in self.dict_nodes_a[task]['param']:
                                                    # print(pa)
                                                    if param_formula == pa:
                                                        globals()[pa] = self.dict_nodes_a[task]['param'][pa]
                                        # we evaluate the equation
                                        computing_latency_preliminar = eval(worse_function)

                                    else:
                                        # because the computing latency is a constant we assign it to the variable
                                        # directly
                                        computing_latency_preliminar = worse_function
                                    # if self.s_prints == 'heudebug':
                                    #     print(f"inside the cycle of the sucessors,"
                                    #           f"the computing latency of the sucessor is ",computing_latency_preliminar)
                                except:
                                    # we catch the error
                                    pass

                                # we add the the computing latency that we obtain to a list, because we will use only
                                # the best one
                                lista_latencias.append(computing_latency_preliminar)

                                # if self.s_prints == 'heudebug':
                                #     print("test 01")
                                #     print(nodo_hw, elemento)
                                #     print(self.dict_distancias.item((nodo_hw, elemento)))
                        except:
                            pass
                        # we obtain the distance between the resource and its successor that can be used to allocate
                        # the successor task
                        # todo this maybe needs to be inside the previuos cycle
                        # we check if there is a connection or not, if there is not we assign the infinite value
                        if self.dict_distancias.item((self.orden_matriz_distancia.index(nodo_hw),
                                                      self.orden_matriz_distancia.index(elemento))) == float('inf'):
                            # if self.s_prints == 'heudebug':
                            #     print("bug infinity")
                            vector_distancias_entre_nodos.append(infinito)
                        else:
                            # if self.s_prints == 'heudebug':
                            #     print("bug infinity else")
                            vector_distancias_entre_nodos.append(int(self.dict_distancias.item(
                                (self.orden_matriz_distancia.index(nodo_hw), self.orden_matriz_distancia.index(elemento)))))

            else:
                # if there is no set of successors we assign a value of 1 to be able to compute the equation
                lista_latencias = [1]

            # if self.s_prints == 'heudebug':
            #     print("the distance between nodes is ", vector_distancias_entre_nodos)

            # if we are able to obtain the distances we select the minimum distance
            if vector_distancias_entre_nodos:
                minimo_valor_distancias = min(vector_distancias_entre_nodos)

            # if self.s_prints == 'heudebug':
            #     print("debug -  ", minimo_valor_distancias, critical_path, cuenta, len(total_nodes))

            # now we need to compute the denominator and numerator separately
            # if self.s_prints == 'heudebug':
            #     print(lista_latencias)
            numerator = worse_computing_latency*critical_path*cuenta
            if lista_latencias:
                denominator = (sum(lista_latencias) / len(lista_latencias) )*int(minimo_valor_distancias)*len(total_nodes)
            else:
                denominator = 0

            # if the denominator is zero we can not compute the equation because we will get an error so we test
            # this and if we need we use a zero to add to the probability, this probability will be the probability of
            # this resource, it will be computed over all the successors of the task
            if denominator == 0:
                probabilidad = probabilidad + 0
            else:
                probabilidad = probabilidad + (numerator/denominator)

            # if self.s_prints == 'heudebug':
            #     print(f"probability of {self.dict_nodes[nodo_hw]['name']} related with {task}  is {probabilidad} ")

        if self.s_prints == 'heudebug' or self.s_prints == 'basic':
            print(
                f"the probability of {self.dict_nodes[nodo_hw]['name']} is "
                f"{probabilidad}, value before normalization")

        return probabilidad




    def verification_of_parameters(self,node_AG,resource):
        """in this function we try to verify that a task can be allocated onto a resource, it verify all the parameters
        of the resource and task
        :parameter node_AG is the task
        :parameter resource is the resource"""

        # we make a first verification, if the type of task can be allocated onto the resource, without the parameters
        # verification, this is done after, this verification is because maybe the constrains file if wrong
        try:
            test_01 = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']
        except:
            print(f"A possible error in the constrain file occurred, as this part is verified otherwise")
            raise  ValueError(f"The task name is {self.AG_copia.nodes[node_AG]['name']}, please verify the constrains file")

        if self.s_prints == 'heudebug':
            print("We enter to the parameters verification function for the ", resource)

        # we initialize the vector of validation
        new_validacion_parameters = []

        # for each parameter of the task, we check if the values are correct
        # if self.s_prints == 'heudebug':
        #     print(self.AG_copia.nodes[node_AG])
        #     print(self.dict_nodes[resource]['name'],self.dict_nodes[resource]['ops'])
        # we wrap this process into a try/except to catch any error
        try:
            # we verify if the task has values or not, if not we only append a valid signal (True)
            if self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'] == None:
                new_validacion_parameters.append(True)
            else:
                # if the task has parameters we need to verify each parameter
                for param in self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']:

                    # if self.s_prints == 'heudebug':
                    #     print(param)

                    # we check if the parameters values are a range of values of a set of fixed values
                    if isinstance(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0], str):
                        # for this case the parameters are a set of fixed values
                        # first we grab all the values
                        vector_param_values = []
                        # this is only to debug
                        # if len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]) != 0:
                        #     if self.s_prints == 'heudebug':
                        #         print("only one element",self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param])
                        #         if self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param] == "down":
                        #             print("its down")
                        #         print(len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']))
                        #         print(len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]))

                        # we verify if the value of the parameter is an integer
                        es_integer = False
                        try:
                            dummy_variable = int(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0])
                            es_integer = True
                        except:
                            pass

                        # we gather the values of the parameter, with a division between the type of parameters
                        if len(self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param][0]) == 1 \
                                and not es_integer:
                            vector_buffer = [self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]]
                        else:
                            vector_buffer = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]

                        # in here we make the change to integer if it is possible and needed
                        for param_value in vector_buffer: #self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]:
                            try:
                                vector_param_values.append(int(param_value))
                            except:
                                vector_param_values.append(param_value)

                        # if the parameters are boolean
                        if vector_param_values == ['boolean']:
                            vector_param_values = ['False', 'True']
                            # if self.s_prints == 'heudebug':
                            #     print("we print the vector values",vector_param_values)
                            #     print(self.dict_nodes_a)


                        # if self.s_prints == 'heudebug':
                        #     if vector_param_values == ['boolean']:
                        #         print("OJNDSJFNSDNFOSD",param,self.dict_nodes_a[node_AG]['param'])

                        # we got the values, so we check if the value that we want to assign to this resource is valid
                        if param in self.dict_nodes_a[node_AG]['param']:
                            # if self.s_prints == 'heudebug':
                            #     print("entry to the cycle",self.dict_nodes_a[node_AG]['param'][param],vector_param_values)
                            if self.dict_nodes_a[node_AG]['param'][param] in vector_param_values:
                                new_validacion_parameters.append(True)
                                # if self.s_prints == 'heudebug':
                                #     print("the value is valid")
                            else:
                                new_validacion_parameters.append(False)
                                # if self.s_prints == 'heudebug':
                                #     print("the value is not valid")
                        else:
                            raise UnboundLocalError(
                                f"parameter {param} is not described in the parameters of task {self.dict_nodes_a[node_AG]['name']}")
                    else:
                        # if self.s_prints == 'heudebug':
                        #     print(param)
                        # in here the value is in a range, in the parsing we put only two values the lower and upper limit
                        # first we check if the parameter in part of the parameters of the task, if not we can either put false and
                        # not use the resource or if the resource has default values we can go with it, this feature needs to be added
                        try:
                            if self.dict_nodes_a[node_AG]['param'][param] >= \
                                    self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                        param][0] and self.dict_nodes_a[node_AG]['param'][param] <= \
                                    self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][
                                        param][1]:
                                # if self.s_prints == 'heudebug':
                                #     print("the value is valid 01")
                                new_validacion_parameters.append(True)
                            else:
                                # if self.s_prints == 'heudebug':
                                #     print("the value is not valid 01")
                                new_validacion_parameters.append(False)
                        except:
                            raise UnboundLocalError(
                                f"parameter {param} is not described in the parameters of task {self.dict_nodes_a[node_AG]['name']}")
        except:
            new_validacion_parameters.append(False)
        if self.s_prints== 'heudebug':
            print("the parameters validation is finished, ", new_validacion_parameters)
        return new_validacion_parameters



    def verification_of_source(self,node_AG,resource):
        """in this function we verify the source of data, in the model we consider two types, a sensor and a memory,
        in this sense we check that the source of the task is compatible with the source of the resource
        :parameter node_AG is the task to check
        :parameter resource is the resource to check"""

        # initialization of the flag
        bandera_source_of_data = False
        info_sensor = []

        # if self.s_prints == 'heudebug':
        #     print("ANOTHER CHANGE 01")
        #     print(self.lista_sources_AG)
        # we make a distintion between source tasks of the basic structure and other tasks, this is because the source
        # node is the only one that is directly connected to the source of data, so this is the one that needs to be
        # validate, the other side of the process, if the task is not a source node we only gather the information of
        # the sensor in order to use it to evaluate the latency
        if node_AG in self.lista_sources_AG:
            # if self.s_prints == 'heudebug':
            #     print("it is a source node")

            # because is a source node of the basic structure we only need to find the source node on the complete
            # structure
            lugar_nodo = None
            # we gather the name of the task in order to make a cross relation to the complete structure (total graph)
            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            # we obtain the source nodes of the complete structure todo verify if this can be done at the beggining
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            # we obtain the source node from the complete structure related to the task in question
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         lugar_nodo)

            # the following step is to obtain the source node related to the hardware
            lugar_nodo = None
            for n, data in self.dict_total.items():
                if self.dict_nodes[resource]['name'] == self.dict_total[n][
                    'name']:
                    lugar_nodo = n
            # we obtain the source nodes of the complete structure of the hardware todo verify if this can be done
            #  at the beggining
            lista_sources_dg_total = obtencion_sources(self.DG_total)
            # we obtain the source node in the complete structure related to the resource in question
            source_total_hw = source_node_from_any_node(self.DG_total,
                                                        lista_sources_dg_total,
                                                        lugar_nodo)

            # now we need to obtain the type of the source node and verify if it is compatible with the source node
            # of the task, we make the distintion between sensor and memory in both graphs because there is differente
            # label for each one
            if self.dict_total[source_total_hw]['type'] == 'ri' and \
                    self.dict_info_a[source_total_app][
                        'op'] == 'interface':
                bandera_source_of_data = True
            elif self.dict_total[source_total_hw]['type'] == 'rm' and \
                    self.dict_info_a[source_total_app]['op'] == 'memory':
                bandera_source_of_data = True
            else:
                bandera_source_of_data = False
            # we obtain the parameters of the sensor to use for the evaluation of the latency both computing and input
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],self.AG_total.nodes[source_total_app]['par']['height'],self.AG_total.nodes[source_total_app]['par']['width']]
        else:
            # if the task is not a source node we only gather the information of the parameters of the sensor
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            if node_AG in lista_sources_ag_total:
                source_total_app = node_AG
            else:
                source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         node_AG)

            # print(self.AG_total.nodes[source_total_app])
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],self.AG_total.nodes[source_total_app]['par']['height'],self.AG_total.nodes[source_total_app]['par']['width']]
            bandera_source_of_data = True
        if self.s_prints == 'heudebug':
            print("we ended the verification of source, ",bandera_source_of_data,info_sensor)

        return bandera_source_of_data,info_sensor


    def variable_separation(self,function_formula):
        """this function separate the variables of an equation, we search for mathematical symbols (*,+,/,-) so we can
        separate the parameters of the equation
        :parameter function_formula is the equation to separate"""
        # if self.s_prints == 'heudebug':
        #     print("we enter the variable separation function for ", function_formula)
        contador_linea = 0
        bandera_primera_vez_letra = True
        vector_parametro = []
        vector_total_parametros = []
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

        if self.s_prints == 'heudebug':
            print(f"we end the process of separation, the result is {vector_total_parametros}")

        return vector_total_parametros

    def obtention_latency(self, resource, node_AG):
        """This function obtain both the input latency and the computing latency of a resource,
        and also we obtain the overall latency for a entire frame
        :parameter resource is the resource which is going to be evaluated
        :parameter node_AG is the task to evaluate"""

        # we retrieve the name of the function of input latency, but because we may be using the constraints file
        # we can have an error if we are placing a task into a wrong resource, thats the purpose of the following
        # try, to catch that error and raise an error
        try:
            name_function = \
                self.dict_nodes[resource]['ops'][self.AG.nodes[node_AG]['op']]['latency']
        except:
            # print(f"the task is {self.AG.nodes[node_AG]['name']} and the resource is {self.dict_nodes[resource]['name']}")
            raise ValueError(f"An error occurred, possibly in the constraints file, as normally we verify this condition previously but not during the constraints mapping, the task is {self.AG.nodes[node_AG]['name']} and the resource is {self.dict_nodes[resource]['name']}")
        # print(name_function)

        # now, as we have the name of the function, we look for the equation itself, this search is in the dict_info which
        # is the one with all the functions
        for data in self.dict_info['functions_res']:
            # print(data)
            if data == name_function:
                function_formula = self.dict_info['functions_res'][data]
            # print(n)

        # now we have the name and the formula, we obtain the input data from the application
        # if self.s_prints == 'heudebug':
        #     print(f"the name of the equation is {name_function} and the equation is {function_formula}")
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
        # we verify is the equation is a string, in this case we need to call the variable separation function
        if isinstance(function_formula, str):
            vector_total_parametros = self.variable_separation(function_formula)

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
        # todo this need to also accept amount of input samples
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
        # if self.s_prints == 'heudebug':
        #     print("we are going to print the dict info")
        #     print(self.dict_info)
        #     print("the print of the dict info is finished")
        #     print("now we are going to print the dict total")
        #     print(self.dict_total)
        #     print("we finished printing the dict total")
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

        # if self.s_prints == 'heudebug':
        #     print("we are going  to evaluate the latency equation")
        #     print(value_clk)
        #     print(self.dict_nodes)
        #     # print(self.dict_info)
        #     try:
        #         print(eval(value_clk))
        #     except:
        #         pass


        ######ahora obtendremos el valor de la latencia de computo, debido a que puede ser una ecuacion o una
        # constante necesitamos hacer una verificacion previa y tambien sacar los valores
        # normalmente ya tenemos la ecuacion, entonces es separarla y asignar valores
        if isinstance(value_clk, str):
            # si la latencia de computacion es una ecuacion
            # if self.s_prints == 'heudebug':
            #     print("the computing latency is an equation")
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
            # if self.s_prints == 'heudebug':
            #     print(f"the parameter vector is  {vector_parametro}")
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
            # if self.s_prints == 'heudebug':
            #     print("the value of the equation is  ", value_clk)
        else:
            value_clk = value_clk
        # now we can evaluate both the input and computing latency
        # print(function_formula,self.dict_info['max_clk'])
        # if isinstance(function_formula, str):
        #     resultado_latencia = eval(function_formula) * self.dict_info['max_clk'] + value_clk
        # else:
        #     resultado_latencia = function_formula * self.dict_info['max_clk'] + value_clk
        # resultado_latencia_total = width * height * self.dict_info['max_clk']

        if isinstance(function_formula, str):
            resultado_latencia = eval(function_formula) * value_clk + value_clk
        else:
            resultado_latencia = function_formula * value_clk + value_clk
        resultado_latencia_total = width * height * value_clk

        if self.s_prints == 'heudebug':
            print(f"we finished the obtention of latency, the results are {resultado_latencia,resultado_latencia_total}")
        return resultado_latencia, resultado_latencia_total





    def Mapping(self):
        """this is the main function, in here we call the other functions and we actually map the tasks to the
        resources"""

        # dummy variables just to be used in the generation of the graph


        # we perform a topological sorting, just to have a list to start with
        lista_DG = list(nx.topological_sort(self.DG_copy))
        lista_AG = list(nx.topological_sort(self.AG_copy))

        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
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


        # list of variables misc

        self.contador_time_slots =  0
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

        bandera_no_match_parameters = False
        #######################
        self.lista_nodos_time_slot_anterior = []


        #important variable where the preliminary mapping will be stored
        lista_salida_memoria = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                range(0, len(self.DG_copy))]

        # lists of sinks and sources, we are going to need them during the mapping
        self.lista_sinks_DG = obtencion_sinks(self.DG_copy)
        self.lista_sources_DG = obtencion_sources(self.DG_copy)
        self.lista_sinks_AG = obtencion_sinks(self.AG_copy)
        self.lista_sources_AG = obtencion_sources(self.AG_copy)
        # datos del grafo total
        self.lista_sinks_DG_total = obtencion_sinks(self.DG_total)
        self.lista_sources_DG_total = obtencion_sources(self.DG_total)

        # distance matrix process
        self.orden_matriz_distancia = list(self.DG_copy.nodes)

        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
            print("Generation of the hardware graph distance matrix")
            dummy_print_dg = []
            for nd in self.orden_matriz_distancia:
                dummy_print_dg.append(self.dict_nodes[nd]['name'])
            print(f"the order of the columns/rows is {dummy_print_dg}")

        self.dict_distancias = nx.floyd_warshall_numpy(self.DG_copy)

        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
            print(f"the distance matrix is ")
            print(self.dict_distancias)





        # We obtain the first group of candidates, the nodes with zero input degree
        primer_grupo = self.lista_sources_DG.copy() #obtencion_sources(self.DG_copy)


        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
            dummy_print_dg = []
            for nd in primer_grupo:
                dummy_print_dg.append(self.dict_nodes[nd]['name'])
            print(f"The first set of possible candidates are {dummy_print_dg}")


        # Start of the mapping
        if self.s_prints == 'heudebug' or self.s_prints == 'debug' or self.s_prints == 'heuiter':
            print("------------------------------------------------------------")
            print("Heuristic algorithm")
            print("We are going to start the mapping")
            print("------------------------------------------------------------")
        if self.s_pause:
            input("Press Enter to continue...")

        counter_iter = 0

        while self.lista_AG_copy:
            # we enter to the main cycle
            contador_datapaths = 0
            # we select the task to map, which is the one that occupied the first position of the topological sorting,
            # after the pop operation the following one will take its place
            nodo_AG = self.lista_AG_copy.pop(0)
            self.tarea_a_mapear_global = nodo_AG
            bandera_no_conexion = False
            # obtention of the operation of the task
            task_AG = self.AG_copy.nodes[nodo_AG]['op']
            # obtention of the successors of the task
            sucesores_nodo_AG = list(self.AG_copy.successors(nodo_AG))
            mapping = True
            self.counter = 0
            name_task = self.dict_nodes_a[nodo_AG]['name']

            if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                print("Begin of mapping of a task ", nodo_AG,name_task)


            # for each task there is two main options, if the task is part of the list of constrains we map it as that,
            # there will be no mapping cycle and we only ensure that all the conditions are met to allocate the task to
            # the assigned resource according to the list of constrains. Otherwise we enter the mapping cycle where
            # we need to find the best allocation for it

           # if we have any constrains we enter this cycle
            if name_task in self.lista_tareas_constrains:
                if self.s_prints == 'heudebug':
                    print("beginning of the mapping in the constrains cycle")
                    print(f"the constrains are  {self.lista_tareas_constrains}")
                # we search for the info of the resource and the task
                name_resource = None
                for parejas in self.lista_constraints:
                    if parejas[0] == name_task:
                        name_resource = parejas[1]
                resource = None
                for n,data in self.dict_nodes.items():
                    if name_resource == data['name']:
                        resource = n
                if self.s_prints == 'heudebug':
                    print("the resource and the name is ",resource,name_task)
                # we need to improve this part
                # we now have the information of the task and the resource

                # first we need to check if we can reuse a previous time slot

                bandera_posible_reuso = False
                vector_todos_mapeados = []
                for nodo_map in lista_salida_memoria:
                    if nodo_map[0] and nodo_map[2] != 'copy':
                        vector_todos_mapeados.append(False)
                    else:
                        vector_todos_mapeados.append(True)
                if resource in self.lista_nodos_time_slot_anterior and all(vector_todos_mapeados):
                    # this means that the new time slot esta vacio and we can use the previous time slot
                    if self.s_prints == 'heudebug':
                        print("The dependency couples are ", self.vector_de_parejas_memoria)
                    numero_parejas = len(self.vector_de_parejas_memoria)
                    for elemento in range(0,numero_parejas):
                        if nodo_AG == self.vector_de_parejas_memoria[elemento][0]:
                            self.vector_de_parejas_memoria.pop(elemento)
                    lista_salida_memoria = lista_final.pop()

                # next we will map the task to the resource, but we make a distintion if the task is a source, a sink
                # or an internal node, this is because the processes are not the same, mainly the verifications and the
                # generation of copy and special nodes
                if nodo_AG in self.lista_sources_AG:
                    # the task is a source task, in this case we will omit the dependency verification, but we first
                    # need to check if the resource is available
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':
                        # because the resource is not available we need to create a new time slot, we call the function
                        # no more resources to do that
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                        vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                            self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)

                        # now we've return from the no more resources function and we should have a new time slot, and
                        # we are sure that the resource is available, so we start the verifications with the
                        # verification of source which will be the only one needed
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("we are at stage 1 step 1 x constrains stage")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to "
                                f"the resource {self.dict_nodes[resource]['name']} in the constrains stage ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'heudebug':
                            print("modulo 01 - debug constrains stage")

                        # the following step is to gather the information about the latency
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03"
                                  ", the current final mapping is ")
                            print(lista_final)

                        ######## aqui integramos todos los copy nodes
                        # in here we use this function to obtain the copy nodes
                        # todo verify if this function is needed
                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        # next the information about the actuator and we generate the copy nodes, in this case the copy
                        # nodes are required if the task does not have any successors, because we first check if the
                        # task is a source and then if it is a sink we may end up with a task that is both, so we need
                        # to generate the copy nodes
                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = \
                            self.generation_copy_nodes(lista_final,lista_salida_memoria,nodo_AG,resource)
                        # print("mapearemos algo")
                        # finally we map the task to the resource
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
                        if self.s_prints == 'heudebug':
                            print("we are at the constrains stage level 1")
                            print(self.DG_copy.nodes)
                            print("the current list of dependency predecesssors", self.lista_predecesores_01)
                            print("the current mapping list is  ", lista_salida_memoria)
                        # self.generation_special_nodes(nodo_AG, resource, lista_final)

                        # after the mapping we check if we got to the end of the list of tasks or if we need to
                        # continue the mapping and get the following list of candidates
                        if len(self.lista_AG_copy) > 0:
                            # in here we check if the current task has any successors that are not mapped, this is
                            # because there was an error that occured in that case, but i think that we no longer need
                            # this part
                            if self.s_prints == 'heudebug':
                                print("there is more tasks to map ")
                            if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):
                                bandera_no_conexion = False
                            else:
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 02")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'heudebug':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # because there are still more tasks to map
                        nueva_lista_primer_grupo = []
                        if self.lista_AG_copy:
                            # we get the predecessors of the next task to map
                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                            nueva_lista_primer_grupo = []
                            # we find where there are mapped and collect those places, the idea is that the next set of
                            # possible candidates should be the successors of the resources that allocate the
                            # predecessors of the next task to map
                            for predecesor in predecesores:
                                lugar_mapeado = None
                                for lugar in lista_salida_memoria:
                                    if lugar[1] == predecesor:
                                        lugar_mapeado = lugar[2]
                                if lugar_mapeado != None:
                                    nueva_lista_primer_grupo = list(set( nueva_lista_primer_grupo +
                                                                         (list(self.DG_original.successors(lugar_mapeado)))))
                            # we prune the previous list and remove the resources that already occupied
                            lista_final_primer_grupo = []
                            for posible in nueva_lista_primer_grupo:
                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                    2] != 'copy':
                                    pass
                                else:
                                    lista_final_primer_grupo.append(posible)
                        if self.s_prints == 'heudebug':
                            print("The new list of possible candidates, place 01 constrains stage", lista_final_primer_grupo)

                        # now we assign the list to the global list of possible candidates
                        primer_grupo =    lista_final_primer_grupo# list(self.DG_original.successors(resource))

                        # if we dont have any possible candidate, we need to verify the datapaths or create a new time
                        # slot
                        if not primer_grupo:
                            # we call the function that verifies the datapaths and creates time slots
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                            primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                            vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                            # now we do have a list of possible candidates and we can end this cycle
                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                    else:
                        # because the resource is available we enter directly to here, where we will only gather the
                        # data that we need to map the task to the resource, we start with the source of data
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("we are at stage 1 step 1 l constrains stage")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to "
                                f"the resource {self.dict_nodes[resource]['name']} in the constrains stage ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'heudebug':
                            print("modulo 02 - debug constrains stage")

                        # we gather the information about the latency
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        # we gather the data about the copy nodes

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)

                        # the data about the actuator and add the copy nodes
                        info_actuator = self.info_actuator_generator(nodo_AG)
                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                      lista_salida_memoria,
                                                                                                      nodo_AG,
                                                                                                      resource)
                        # now we map the task to the resource
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
                        if self.s_prints == 'heudebug':
                            print(self.DG_copy.nodes)
                            print("the list of dependency predecessors", self.lista_predecesores_01)
                            print("the current mapping list, place 04 ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary
                        # todo the generation of special nodes is commented in here, we need to verify it
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
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 03")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'heudebug':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)
                        # because there are more tasks to map we need to get the list of possible candidates
                        nueva_lista_primer_grupo = []
                        if self.lista_AG_copy:
                            # so, we first get the predecxessors of the next task to map
                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                            nueva_lista_primer_grupo = []
                            # we find the places where those predecessors are mapped
                            for predecesor in predecesores:
                                lugar_mapeado = None
                                for lugar in lista_salida_memoria:
                                    if lugar[1] == predecesor:
                                        lugar_mapeado = lugar[2]
                                if lugar_mapeado != None:
                                    nueva_lista_primer_grupo = list(set( nueva_lista_primer_grupo +
                                                                         (list(self.DG_original.successors(lugar_mapeado)))))
                            lista_final_primer_grupo = []
                            # then we prune the list of the locations by removing the ones that are already occupied
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
                        if self.s_prints == 'heudebug':
                            print("The new list of possible candidates is, place 08", lista_final_primer_grupo)


                        # we assign the pruned list to the global variable
                        primer_grupo =  lista_final_primer_grupo #list(self.DG_original.successors(resource))
                        # before we end the cycle we need to be sure that we return something, so we check if the list
                        # of possible candidates is not empty
                        if not primer_grupo:
                            # because there are no possible candidates we need to check datapaths or create a new time
                            # slot in order to get a list of possible candidates
                            # we call the function that verifies the datapaths
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                            primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                            vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                            # now we are sure that there are possible candidates and we can end this cycle
                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False

                elif nodo_AG in self.lista_sinks_AG:
                    # the task is a sink, as the previous cycle, we make a distintion if the resource is available
                    # or not
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':
                        # because the resource is not available, we need to call the function to verify the datapaths
                        # or create a new time slot
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                        vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths =\
                            self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)

                        # now we are sure that the resource is available, we start the mapping of the task by
                        # gathering the required data, we start with the data of the source
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("we are at stage 1 step 1 t constrains stage")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} "
                                f"to the resource {self.dict_nodes[resource]['name']} in the constrains stage ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'heudebug':
                            print("modulo 03 - debug")

                        # next we gather the latency data
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        # in here we gather the data of the copy nodes, the actuator and we end up with the inclusion
                        # of the copy nodes to the mapping list

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
                        # now we map the task to the resource
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
                        if self.s_prints == 'heudebug':
                            print(self.DG_copy.nodes)
                            print("the list of dependency predecessors", self.lista_predecesores_01)
                            print("the current mapping list is  ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final)

                        bandera_no_conexion = False
                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'heudebug':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task

                        elif not sucesores_nodo_AG or bandera_no_conexion:
                            # print("ciclo elif de algo")
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
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)
                            # now the following code is to get the possible candidates
                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                # the first part is to get the predecessors of the next task to map
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                # next we get the location of the predecessors
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = \
                                            list(set( nueva_lista_primer_grupo +
                                                      (list(self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                # then we prune the list by removing the resources that are occupied
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'heudebug':
                                print("The new list of possible candidates is ", lista_final_primer_grupo)


                            # we assing the list of possible candidates to the global variable
                            primer_grupo = lista_final_primer_grupo #list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            # if self.s_prints == 'heudebug':
                            #     print("BUGG N")
                            #     print(primer_grupo)
                            # before we end the cycle we check if there is at least one possible candidate
                            if not primer_grupo:
                                # because the list of possible candidates is empty we call the function that checks
                                # the datapaths or create time slots
                                # we call the function that verifies the datapaths
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)
                            # now we are sure that we have a list of possible candidates, and we can end the cycle
                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                    else:
                        # because the resource is available we can use it directly to map the task, we start by
                        # gathering the required data
                        # print("bugg 01", self.DG_copy.nodes)
                        self.DG_copy = self.DG_original.copy()
                        # we gather the data of the source
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("we are at stage 1 step 1 h")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to "
                                f"the resource {self.dict_nodes[resource]['name']} in the constrains stage ")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'heudebug':
                            print("modulo 04 - debug")
                        # we gather the data of the latency
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        # we get the data of the copy nodes, the actuator and we add such copy nodes to the mapping list

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
                        # we map the task to the resource
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
                        if self.s_prints == 'heudebug':
                            print(self.DG_copy.nodes)
                            print("the current list of dependency predecessors", self.lista_predecesores_01)
                            print("the current mapping list  ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final)

                        bandera_no_conexion = False
                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'heudebug':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task

                        elif not sucesores_nodo_AG and bandera_no_conexion:
                            # print("ciclo elif de algo")
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
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)
                            # in here we will get the list of possiblle candidates
                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                # we get the predecessors of the next task to map
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                # next we proceed to obtain the location of the predecessors and then we prune the
                                # list by removing the resources that are occupied
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = \
                                            list(set( nueva_lista_primer_grupo +
                                                      (list(self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'heudebug':
                                print("the new list of possible candidates place 09", lista_final_primer_grupo)


                            # we assign the list to the global variable
                            primer_grupo = lista_final_primer_grupo #list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            if self.s_prints == 'heudebug':
                                print("BUGG N")
                                print(primer_grupo)
                            # before we return to the main cycle we check if there are possible candidates
                            if not primer_grupo:
                                # we call the function that verifies the datapaths because there are no candidates
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio,\
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, \
                                lista_final, vector_buffer_especiales, vector_nodos_especiales,\
                                bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False
                else:
                    # if the task is an internal node of the application graph we enter here
                    # print("otro tipo de nodo")
                    # as the previous cycles we check if the reosurce is available or not
                    if lista_salida_memoria[resource][0] and lista_salida_memoria[resource][2] != 'copy':
                        # print("no espacio")
                        # because the resource is not available we call the function that verifies the datapaths
                        # or create a new time slot
                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                        vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                            copia_DG, bandera_nodo_especial)
                        # print("es otro tipo de nodo luego del reinicio")

                        # the problem of the previous function is that it first check if there are independ datapaths
                        # and sometimes the resource is not there, so we need to check that, if the resource is not
                        # there we call directly the a function to add a new time slot
                        if resource not in self.DG_copy.nodes:
                            bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, \
                            lista_final, vector_buffer_especiales, vector_nodos_especiales, \
                            bandera_caso_no_probabilidad = self.reinicio_time_slot(
                                lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                                vector_nodos_especiales, bandera_caso_no_probabilidad)
                            bandera_recomputo = False


                        # now we are sure that the resource is available, we start the process to map the task to
                        # the resource by gathering the data of the source
                        bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                        # print("verificacion de sources ", bandera_source_of_data, info_sensor)

                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("we are at stage 1 step 1 f")
                            print("we are going to map task ", nodo_AG, " to resource ", resource)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                            print(
                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} "
                                f"to the resource {self.dict_nodes[resource]['name']}  in the constrains node")
                            print("------------------------------------------------------------")
                        if self.s_pause:
                            input("Press Enter to continue...")
                        if self.s_prints == 'heudebug':
                            print("modulo 05 - debug")
                        # we get the latency information
                        resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                            # print(self.lista_nodos_copy)
                            # print(self.lista_nodos_copy_time)
                            print("we are going to map something so we need to add the copy nodes 03")
                            print(lista_final)

                        # we get the info of the copy nodes, the actuator and we add the copy nodes to the mapping list
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
                        # we map the task to the resource
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
                        # if self.s_prints == 'heudebug':
                        #     print(self.DG_copy.nodes)
                        #     print("the ", self.lista_predecesores_01)
                        #     print("la lista de salida es ", lista_salida_memoria)
                        # we proceed to create the special nodes, if necessary

                        self.generation_special_nodes(nodo_AG, resource, lista_final)
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
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    print(
                                        "there is no connection between the current mapped task and the next task 05")
                                bandera_no_conexion = True
                            # deactivation of the recomputation flag
                            bandera_recomputo = False

                        # if there are no more tasks to map we end the mapping here
                        if self.s_pause and self.s_prints == 'heudebug':
                            input("Press Enter to continue...")
                        if not self.lista_AG_copy:
                            lista_final.append(lista_salida_memoria)

                        # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                        # is no more successors of the current task
                        elif not sucesores_nodo_AG or bandera_no_conexion:
                            # print("ciclo elif de algo")
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                        else:
                            # in this part we only update the first group of candidates, because there are still
                            # resources and tasks
                            # print("ciclo else de algo")
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we end a cycle in stage 1b")
                                print("the current mapping list is")
                                print(lista_salida_memoria)
                                print(self.DG_copy.nodes)

                            nueva_lista_primer_grupo = []
                            if self.lista_AG_copy:
                                # to obtain the next list of possible candidates we first get the predecessors of the next
                                # task
                                predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                nueva_lista_primer_grupo = []
                                # then we gather the location of the predecessors
                                for predecesor in predecesores:
                                    lugar_mapeado = None
                                    for lugar in lista_salida_memoria:
                                        if lugar[1] == predecesor:
                                            lugar_mapeado = lugar[2]
                                    if lugar_mapeado != None:
                                        nueva_lista_primer_grupo = \
                                            list(set( nueva_lista_primer_grupo +
                                                      (list(self.DG_original.successors(lugar_mapeado)))))
                                lista_final_primer_grupo = []
                                # then we prune the list of locations by removing the resources that are occupied
                                for posible in nueva_lista_primer_grupo:
                                    if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                        2] != 'copy':
                                        pass
                                    else:
                                        lista_final_primer_grupo.append(posible)
                            if self.s_prints == 'heudebug':
                                print("LA NUEVA LISTA DE CANDIDATOS ES 05", lista_final_primer_grupo)



                            # we assign the list to the global variable
                            primer_grupo = lista_final_primer_grupo# list(self.DG_original.successors(resource))
                            # print(primer_grupo)
                            if self.s_prints == 'heudebug':
                                print("BUGG N")
                                print(primer_grupo)
                            # if there are no possible candidates we need to either verify the datapaths or
                            # create a new time slot
                            if not primer_grupo:
                                # we call the function that verifies the datapaths
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,\
                                contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)

                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                dummy_print_dg = []
                                for nd in primer_grupo:
                                    dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                print(f"the new possible candidates are {dummy_print_dg}")
                        bandera_primer_nodo = False
                        mapping = False



                    else:
                        # we enter here because the resource is available, so we proceed to verify the data dependence
                        if self.s_prints == 'heudebug':
                            print("second stage in the constrains section, final module")

                        bandera_mapping_valido = self.verificacion_data_dependence(resource,
                                                                                   nodo_AG,
                                                                                   lista_salida_memoria,
                                                                                   lista_final, copia_DG,
                                                                                   bandera_recomputo)
                        # if the data dependence is ok we proceed to map the task, if not we need to create a new time
                        # slot, the theory behind this is because maybe there are no paths to the predecessors, but if
                        # we create a new time slot we are sure that there will be a path
                        if bandera_mapping_valido:
                            # first we gather the information about the soruce of data
                            bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                            if self.s_prints == 'heudebug':
                                print("verification of sources ", bandera_source_of_data, info_sensor)

                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we are at stage 1 step 1 n")
                                print("we are going to map task ", nodo_AG, " to resource ", resource)
                            elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                                print(
                                    f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to "
                                    f"the resource {self.dict_nodes[resource]['name']} in the constrains stage")
                                print("------------------------------------------------------------")
                            if self.s_pause:
                                input("Press Enter to continue...")
                            if self.s_prints == 'heudebug':
                                print("modulo 06 - debug")
                            # we gather the data of the latency
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                # print(self.lista_nodos_copy)
                                # print(self.lista_nodos_copy_time)
                                print("we are going to map something so we need to add the copy nodes 03")
                                print(lista_final)

                            # in here we gather the data of the copy nodes, the actuator and we add the copy nodes
                            # to the mapping list

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
                            # we map the task to the resource
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
                            # if self.s_prints == 'heudebug':
                            #     print(self.DG_copy.nodes)
                            #     print("jndsijfsd", self.lista_predecesores_01)
                            #     print("la lista de salida es ", lista_salida_memoria)
                            # we proceed to create the special nodes, if necessary

                            self.generation_special_nodes(nodo_AG, resource, lista_final)
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
                                    if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                        print(
                                            "there is no connection between the current mapped task and the next task 06")
                                    bandera_no_conexion = True
                                # deactivation of the recomputation flag
                                bandera_recomputo = False

                            # if there are no more tasks to map we end the mapping here
                            if self.s_pause and self.s_prints == 'heudebug':
                                input("Press Enter to continue...")
                            if not self.lista_AG_copy:
                                lista_final.append(lista_salida_memoria)

                            # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                            # is no more successors of the current task
                            elif not sucesores_nodo_AG or bandera_no_conexion:

                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths =\
                                    self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)
                            else:
                                # in this part we only update the first group of candidates, because there are still
                                # resources and tasks
                                # print("ciclo else de algo")
                                if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                    print("we end a cycle in stage 1b")
                                    print("the current mapping list is")
                                    print(lista_salida_memoria)
                                    print(self.DG_copy.nodes)

                                nueva_lista_primer_grupo = []
                                if self.lista_AG_copy:
                                    # we get the predecessors of the next task to map
                                    predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                    nueva_lista_primer_grupo = []
                                    # we get the location of the predecessors
                                    for predecesor in predecesores:
                                        lugar_mapeado = None
                                        for lugar in lista_salida_memoria:
                                            if lugar[1] == predecesor:
                                                lugar_mapeado = lugar[2]
                                        if lugar_mapeado != None:
                                            nueva_lista_primer_grupo = \
                                                list(set( nueva_lista_primer_grupo +
                                                          (list(self.DG_original.successors(lugar_mapeado)))))
                                    lista_final_primer_grupo = []
                                    # we prune the list by removing the resources that are not available
                                    for posible in nueva_lista_primer_grupo:
                                        if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                            2] != 'copy':
                                            pass
                                        else:
                                            lista_final_primer_grupo.append(posible)
                                if self.s_prints == 'heudebug':
                                    print("the new list of possible candidates place 12", lista_final_primer_grupo)


                                # we assign the list to the global variable
                                primer_grupo = lista_final_primer_grupo# list(self.DG_original.successors(resource))
                                # print(primer_grupo)
                                if self.s_prints == 'heudebug':
                                    print("BUGG N")
                                    print(primer_grupo)
                                if not primer_grupo:
                                    # because there are no possible candidates
                                    # we call the function that verifies the datapaths
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                    primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                    vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                        self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)

                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the new possible candidates are {dummy_print_dg}")
                            bandera_primer_nodo = False
                            mapping = False
                        else:
                            # because maybe there is no path to the predecessors and due to that the verification of
                            # data dependence fail, we enter here, we will add a new time slot and the proceed to map
                            # the task to the resource
                            bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                            primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                            vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                self.no_more_resources(
                                lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                copia_DG, bandera_nodo_especial)
                            # we return from the creation of a new time slot, so we continue the process of mapping the
                            # task to the resource, we gather the information of the source of data
                            bandera_source_of_data, info_sensor = self.verification_of_source(nodo_AG, resource)
                            if self.s_prints == 'heudebug':
                                print("verificacion de sources ", bandera_source_of_data, info_sensor)

                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we are at stage 1 step 1 b")
                                print("we are going to map task ", nodo_AG, " to resource ", resource)
                            elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                                print(
                                    f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']}"
                                    f" to the resource {self.dict_nodes[resource]['name']} in the constrains stage ")
                                print("------------------------------------------------------------")
                            if self.s_pause:
                                input("Press Enter to continue...")
                            if self.s_prints == 'heudebug':
                                print("modulo 07 - debug")
                            # we gather the latency data
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(resource, nodo_AG)

                            if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                # print(self.lista_nodos_copy)
                                # print(self.lista_nodos_copy_time)
                                print("we are going to map something so we need to add the copy nodes 03")
                                print(lista_final)

                            # we get the information about the copy nodes, the actuator and we add the copy nodes
                            # to the mapping list

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
                            # we map the task to the resource
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
                            if self.s_prints == 'heudebug':
                                print(self.DG_copy.nodes)
                                print("jndsijfsd", self.lista_predecesores_01)
                                print("la lista de salida es ", lista_salida_memoria)
                            # we proceed to create the special nodes, if necessary

                            self.generation_special_nodes(nodo_AG, resource, lista_final)
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
                                    if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                        print(
                                            "there is no connection between the current mapped task and the next task 07")
                                    bandera_no_conexion = True
                                # deactivation of the recomputation flag
                                bandera_recomputo = False

                            # if there are no more tasks to map we end the mapping here
                            if self.s_pause and self.s_prints == 'heudebug':
                                input("Press Enter to continue...")
                            if not self.lista_AG_copy:
                                lista_final.append(lista_salida_memoria)

                            # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                            # is no more successors of the current task
                            elif not sucesores_nodo_AG or bandera_no_conexion:
                                if self.s_prints == 'heudebug':
                                    print("ciclo elif de algo")
                                bandera_nodo_especial, bandera_recomputo, bandera_reinicio,\
                                bandera_primer_nodo, primer_grupo, lista_salida_memoria, \
                                lista_final, vector_buffer_especiales, vector_nodos_especiales, \
                                bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                    lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                    copia_DG, bandera_nodo_especial)
                            else:
                                # in this part we only update the first group of candidates, because there are still
                                # resources and tasks
                                # print("ciclo else de algo")
                                if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                    print("we end a cycle in stage 1b")
                                    print("the current mapping list is")
                                    print(lista_salida_memoria)
                                    print(self.DG_copy.nodes)

                                nueva_lista_primer_grupo = []
                                if self.lista_AG_copy:
                                    # we get the predecessors of the next task to map
                                    predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                    nueva_lista_primer_grupo = []
                                    # we find the location of the predecessors
                                    for predecesor in predecesores:
                                        lugar_mapeado = None
                                        for lugar in lista_salida_memoria:
                                            if lugar[1] == predecesor:
                                                lugar_mapeado = lugar[2]
                                        if lugar_mapeado != None:
                                            nueva_lista_primer_grupo = \
                                                list(set( nueva_lista_primer_grupo +
                                                          (list(self.DG_original.successors(lugar_mapeado)))))
                                    lista_final_primer_grupo = []
                                    # we prune the list by removing the resources that are occupied
                                    for posible in nueva_lista_primer_grupo:
                                        if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                            2] != 'copy':
                                            pass
                                        else:
                                            lista_final_primer_grupo.append(posible)
                                if self.s_prints == 'heudebug':
                                    print("the new lit of possible candidates place 14", lista_final_primer_grupo)

                                # we assign the list to the global variable
                                primer_grupo = lista_final_primer_grupo #list(self.DG_original.successors(resource))
                                # print(primer_grupo)
                                if self.s_prints == 'heudebug':
                                    print("BUGG N")
                                    print(primer_grupo)
                                if not primer_grupo:
                                    # because the list of possible candidates is empty
                                    # we call the function that verifies the datapaths
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                    bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, \
                                    vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad, \
                                    contador_datapaths = self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)

                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the new possible candidates are {dummy_print_dg}")
                            bandera_primer_nodo = False
                            mapping = False

                ##################@@@@@@@@@@@@@@@@@@@@@@@@@@@

            else:
                # this is the normal mapping process, in here we are going to verify if all the criteria are met
                # before we map a task to a resource
                bandera_reinicio = False
                if self.s_prints == 'heudebug' or self.s_prints == 'debug' or self.s_prints == 'iter':
                    print("------------------------------------------------------------")
                    counter_iter += 1
                    print(f"iteration {counter_iter} ")
                    print(
                        f"we are going to try to map the task {self.dict_nodes_a[nodo_AG]['name']} "
                        f"which has the type {self.dict_nodes_a[nodo_AG]['op']}")
                    dummy_print_ag = []
                    for nd in sucesores_nodo_AG:
                        dummy_print_ag.append(self.dict_nodes_a[nd]['name'])
                    dummy_print_dg = []
                    for nd in primer_grupo:
                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                    print(f"the sucessors of the task are {dummy_print_ag}")
                    print(f"the possible candidates are {dummy_print_dg}")

                # time.sleep(2)
                while mapping:
                    # we start the iteration, we print some information that we use to debug

                    if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                        dummy_print_dg = []
                        for nd in lista_DG:
                            dummy_print_dg.append(self.dict_nodes[nd]['name'])
                        print(f"the remaining resources are {dummy_print_dg}")

                        print("the remaining resources are ", lista_DG)
                        print("until now the final mapping list is ", lista_final)
                        print("until now the mapping list is ", lista_salida_memoria)


                    # this counter helps us to exit from a infinite loop
                    self.counter = self.counter + 1
                    if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                        print(f"the attemp counter is {self.counter}")
                    if self.counter > len(self.DG_original)*2 or self.contador_time_slots > 2:
                        raise Exception(f"The mapping cycle, please verify your input files")
                    # we make a difference between the first time we enter the main loop, this is because we obtain the first
                    # set of possible candidates from outside, but ill make some changes to remove this part and just have
                    # a single loop


                    if bandera_primer_nodo:
                        # initialize the probability vector
                        lista_probabilidad = [0 for g in range(len(primer_grupo))]
                        # now, at this point we will check if the possible candidate can become candidate by checking the
                        # compability between operations and parameters

                        ####before we start we obtain all the descendants of the group of candidates
                        lista_total_nodos = obtencion_sucesores_de_una_lista(self.DG_original, primer_grupo)
                        # print(lista_total_nodos)
                        # the following cycle will help us get the probability of the possible candidates
                        # we compute the probability only for those possible candidates that meet the criteria, in the
                        # sense that they pass the data dependence verification, the verification of source and the
                        # parameters verification
                        # for each resource in the list of possible candidates
                        for elementos in range(0, len(primer_grupo)):
                            # we perform a first prune with the type of operation
                            if task_AG in self.DG_copy.nodes[primer_grupo[elementos]]['op'] :
                                if self.s_prints == 'heudebug':
                                    print("EMPEZAREMOS CON LOS CAMBIOS 01")
                                # next we verify the data dependence, the source of data and the parameters
                                bandera_source_of_data,info_sensor = self.verification_of_source(nodo_AG, primer_grupo[elementos])

                                bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[elementos],
                                                                                           nodo_AG,
                                                                                           lista_salida_memoria,
                                                                                           lista_final, copia_DG,
                                                                                           bandera_recomputo)


                                vector_validacion_parametros = self.verification_of_parameters(nodo_AG,primer_grupo[elementos])
                                if all(vector_validacion_parametros) and bandera_mapping_valido and bandera_source_of_data:
                                    # now we have a real possible candidate
                                    if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                        print(
                                            f"we are going to check the resource {self.dict_nodes[primer_grupo[elementos]]['name']}")
                                    # obtention of the successors of the candidate
                                    lista_sucesores = obtencion_sucesores(self.DG_original, primer_grupo[elementos])
                                    # if there are successors
                                    if sucesores_nodo_AG:
                                        # we obtain all the descendants of the first group
                                        if self.s_prints == 'debug':
                                            print("the list of all the descendants is ", lista_total_nodos)
                                            print("the list of the successors of the candidate is ", lista_sucesores)
                                        # next, we obtain the probability of this candidate
                                        obtencion_probabilidad_sucesores = self.obtencion_probabilidad(self.AG_copy,
                                                                                                                   sucesores_nodo_AG,
                                                                                                                   primer_grupo[elementos],
                                                                                                                   self.DG_copy,
                                                                                                                   lista_total_nodos,
                                                                                                                   lista_salida_memoria)
                                    else:
                                        # if the resource does not have successors we assign it with a high probability,
                                        # because we assume that probably is a sink
                                        obtencion_probabilidad_sucesores = 0.99
                                    # we store the value of the probability
                                    lista_probabilidad[elementos] = (obtencion_probabilidad_sucesores)

                                else:
                                    if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                        print(
                                            f"we are going to check the resource {self.dict_nodes[primer_grupo[elementos]]['name']}")
                                        print("possible candidate ", primer_grupo[elementos], " can not be used to map ",
                                              nodo_AG)
                                        print(
                                            f"The possible candidate {self.dict_nodes[primer_grupo[elementos]]['name']}"
                                            f" can not be used to map {self.dict_nodes_a[nodo_AG]['name']} ")
                                    # given that we dont want to map the task in this resource we assign a zero probability
                                    lista_probabilidad[elementos] = 0.00

                            else:
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    print(
                                        f"we are going to check the resource {self.dict_nodes[primer_grupo[elementos]]['name']}")
                                    print("possible candidate ", primer_grupo[elementos], " can not be used to map ",
                                          nodo_AG)
                                    print(
                                        f"The possible candidate {self.dict_nodes[primer_grupo[elementos]]['name']} can "
                                        f"not be used to map {self.dict_nodes_a[nodo_AG]['name']} ")
                                # given that we dont want to map the task in this resource we assign a zero probability
                                lista_probabilidad[elementos] = 0.00
                        # now, we check if all the values of the probability vector are zeros
                        if self.s_prints == 'heudebug':
                            print(f"03 the probability vector is {lista_probabilidad}")
                        todos_zeros = all(v == 0 for v in lista_probabilidad)
                        # there is some cases that the values of the probability vector are all zeros, so we have to check this
                        if not todos_zeros:
                            # we normalize the probability list
                            lista_probabilidad = [float(i) / sum(lista_probabilidad) for i in lista_probabilidad]
                            if self.s_prints == 'heudebug':
                                print(f"01 the probability vector is {lista_probabilidad}")
                                print("not all the values of the probability vector are zeros")
                            # at this point, we have at least one feasible resource candidate to use
                            # so we choose the one with the higher probability
                            max_value = max(lista_probabilidad)
                            max_index = lista_probabilidad.index(max_value)

                            if self.s_prints == 'heudebug':
                                print("ANOTHER CHANGE 02")
                                print(self.lista_sources_AG)
                            # from here we start the process of mapping by gathering all the information
                            # and making some final checkups
                            # first we check the source of data and the data dependence again because maybe we the
                            # last resource which we use to call this function is not the one selected to allocate the
                            # task
                            bandera_source_of_data,info_sensor = self.verification_of_source(nodo_AG, primer_grupo[max_index])
                            bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[max_index],
                                                                                       nodo_AG,
                                                                                       lista_salida_memoria,
                                                                                       lista_final, copia_DG,
                                                                                       bandera_recomputo)
                            if self.s_prints == 'heudebug':
                                print(f"the list of nodes that need to have copy function are {self.lista_nodos_copy} ")
                                print("the list until now is")
                                print(lista_salida_memoria)
                            if self.s_prints == 'debug':
                                if self.dict_nodes_a[nodo_AG]['name'] == 't3':
                                    print(bandera_mapping_valido, )
                                    # time.sleep(5)

                            # if there is no problem we follow the process and map the task
                            if bandera_mapping_valido and bandera_source_of_data:
                                # this is the mapping rutine, maybe we can put it into a function
                                vector_nodo_especial_predecesor = (primer_grupo[max_index])
                                if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                    print("we are at stage 1 step 1 y")
                                    print("we are going to map task ", nodo_AG, " to resource ", primer_grupo[max_index])
                                elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                                    print(
                                        f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} to "
                                        f"the resource {self.dict_nodes[primer_grupo[max_index]]['name']} ")
                                    print("------------------------------------------------------------")
                                if self.s_pause:
                                    input("Press Enter to continue...")
                                if self.s_prints == 'heudebug':
                                    print("modulo 08 - debug")
                                # we gather the latency data
                                resultado_latencia,resultado_latencia_total = self.obtention_latency(primer_grupo[max_index],nodo_AG)

                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    print(self.lista_nodos_copy)
                                    print(self.lista_nodos_copy_time)
                                    print(resultado_latencia,resultado_latencia_total)
                                    print("we are going to map something so we need to add the copy nodes 03")
                                    print(lista_final)
                                # we obtain the information about the actuator and we add the copy nodes
                                info_actuator = self.info_actuator_generator(nodo_AG)
                                actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(lista_final,
                                                                                                         lista_salida_memoria,
                                                                                                         nodo_AG,
                                                                                                         primer_grupo[max_index])

                                # we map the task to the resource
                                lista_salida_memoria[primer_grupo[max_index]] = [True, nodo_AG, primer_grupo[max_index],
                                                                                 self.AG.nodes[nodo_AG]['op'],
                                                                                 self.dict_nodes[
                                                                                     primer_grupo[max_index]][
                                                                                     'ops'][
                                                                                     self.AG.nodes[nodo_AG]['op']][
                                                                                     'latency'],
                                                                                 self.AG.nodes[nodo_AG]['par'],
                                                                                 self.AG.nodes[nodo_AG]['par'],
                                                                                 self.dict_nodes[
                                                                                     primer_grupo[max_index]][
                                                                                     'ops'][
                                                                                     self.AG.nodes[nodo_AG]['op']][
                                                                                     'clk'],resultado_latencia,resultado_latencia_total,info_sensor,info_actuator,actuator_sink
                                                                                 ]
                                # we keep track of the tasks that we map
                                self.counter = 0
                                self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                                if self.s_prints == 'heudebug':
                                    print("jndsijfsd",self.lista_predecesores_01)
                                    print("the mapping list is 85 ",lista_salida_memoria)
                                # we proceed to create the special nodes, if necessary
                                self.generation_special_nodes(nodo_AG, primer_grupo[max_index], lista_final)
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
                                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                            print(
                                                "there is no connection between the current mapped task and the next task 08")
                                        bandera_no_conexion = True
                                    # deactivation of the recomputation flag
                                    bandera_recomputo = False

                                # if there are no more tasks to map we end the mapping here
                                if self.s_pause and self.s_prints == 'heudebug':
                                    input("Press Enter to continue...")


                                if not self.lista_AG_copy:
                                    lista_final.append(lista_salida_memoria)
                                # otherwise we continue, but we check if the bandera_no_conexion is activated and if there
                                # is no more successors of the current task
                                elif not sucesores_nodo_AG and bandera_no_conexion:
                                    # in here we are going to check if there are datapaths available
                                    if self.s_prints == 'heudebug':
                                        print("verification of available datapaths")
                                        print("for debugging we are going to print the current mapping list")
                                        print(lista_salida_memoria)

                                    # we call the function that verifies the datapaths
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                    primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                    vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                        self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG,bandera_nodo_especial)

                                else:

                                    if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                        print("we end a cycle in stage 1c")
                                        print("the current mapping list is")
                                        print(lista_salida_memoria)
                                    # because there are still tasks to map we need to get the next possible candidates
                                    nueva_lista_primer_grupo = []
                                    if self.lista_AG_copy:
                                        # we start with the obtention of the predecessors of the next task to map
                                        predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                        nueva_lista_primer_grupo = []
                                        # then we locate where those predecessors are mapped
                                        for predecesor in predecesores:
                                            lugar_mapeado = None
                                            for lugar in lista_salida_memoria:
                                                if lugar[1] == predecesor:
                                                    lugar_mapeado = lugar[2]
                                            if lugar_mapeado != None:
                                                nueva_lista_primer_grupo = list(set( nueva_lista_primer_grupo +
                                                                                     (list(self.DG_original.successors(lugar_mapeado)))))

                                        lista_final_primer_grupo = []
                                        # then we prune the list by removing the resources occupied
                                        for posible in nueva_lista_primer_grupo:
                                            if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                                2] != 'copy':
                                                pass
                                            else:
                                                lista_final_primer_grupo.append(posible)
                                    if self.s_prints == 'heudebug':
                                        print("LA NUEVA LISTA DE CANDIDATOS ES 08", lista_final_primer_grupo)
                                    # we assign the list to the global variable
                                    primer_grupo =  lista_final_primer_grupo #list(self.DG_copy.successors(primer_grupo[max_index]))
                                    if not primer_grupo:
                                        # now in here we check if there is no possible candidates
                                        # todo verify this part, maybe we need to complete it with a creation of a new time slot
                                        sources_nodes = self.lista_sources_DG.copy()
                                        for ts in sources_nodes:
                                            if not lista_salida_memoria[ts][0] :
                                                primer_grupo.append(ts)
                                    if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                        dummy_print_dg = []
                                        for nd in primer_grupo:
                                            dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                        print(f"the new possible candidates are {dummy_print_dg}")


                                bandera_primer_nodo = False
                                mapping = False
                        else:
                            # The probability vector is full of zeros, there are cases where the probability of all of the
                            # possible candidates are zero, but we still can use one of them, the probability is zero
                            # because we only check if the successors of the resources comply with the successors of the task
                            # but can be the case where we only can map the task in one of the current candidates
                            if self.s_prints == 'heudebug':
                                print("the probability vector is full of zeros")
                                print("we are going to check if we can still use one of the candidates")
                                print("the possible candidates in this case are ", primer_grupo)

                            # we make a copy of the first group just to keep the data
                            bandera_mapeo_en_ciclo = False
                            nodo_utilizado_en_mapeo = None
                            copia_primer_grupo = list(primer_grupo)
                            for elementos in range(0, len(primer_grupo)):
                                if self.s_prints == 'heudebug':
                                    print(task_AG, self.DG_copy.nodes[primer_grupo[elementos]]['op'])
                                # we check the parameters of each candidate to see if any one of them is useful
                                if task_AG in self.DG_copy.nodes[primer_grupo[elementos]]['op']:
                                    if self.s_prints == 'heudebug':
                                        print("error tracker 100 ")
                                        print(task_AG,self.DG_copy.nodes[primer_grupo[elementos]]['op'])
                                    if self.s_prints == 'heudebug':
                                        print("new functions")

                                    vector_validacion_parametros = self.verification_of_parameters(nodo_AG,primer_grupo[elementos])
                                    bandera_source_of_data,info_sensor = self.verification_of_source(nodo_AG,primer_grupo[elementos])

                                    if self.s_prints == 'heudebug':
                                        print("ANOTHER CHANGE 03")
                                        print(self.lista_sources_AG)

                                    # call of the verification function
                                    if self.s_prints == 'debug':
                                        print(
                                            "the parameters are ok we are going to check if the data dependence is also ok")
                                    bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[elementos],
                                                                                               nodo_AG,
                                                                                               lista_salida_memoria,
                                                                                               lista_final, copia_DG,
                                                                                               bandera_recomputo)
                                    if self.s_prints == 'heudebug':
                                        print(
                                            f"the list of nodes that need to have copy function are {self.lista_nodos_copy} ")
                                        print("the list until now is")
                                        print(lista_salida_memoria)
                                    # if there is no dependecy problem
                                    if self.s_prints == 'heudebug':
                                        print(bandera_source_of_data,vector_validacion_parametros,bandera_no_match_parameters)
                                    if bandera_mapping_valido and bandera_source_of_data and all(vector_validacion_parametros):
                                        if self.s_prints == 'debug':
                                            print("we are at stage 1 step 2")
                                            print("we are going to map the task ", nodo_AG, "in the resource",
                                                  primer_grupo[elementos])
                                        elif self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                                            print(
                                                f"we are going to map the task {self.dict_nodes_a[nodo_AG]['name']} "
                                                f"on the resource {self.dict_nodes[primer_grupo[elementos]]['name']}")
                                            print("------------------------------------------------------------")
                                        # we are going to map the task
                                        if self.s_pause:
                                            input("Press Enter to continue...")
                                        if self.s_prints == 'heudebug':
                                            print("modulo 18 - debug")
                                        # we are going to obtain the latency of this node

                                        if self.s_prints == 'heudebug':
                                            print(" we are going to obtain the latency of the node 01")

                                        # we are going to obtain the latency of this node, plus the actuator info and
                                        # we are going to add the copy nodes

                                        resultado_latencia,resultado_latencia_total = self.obtention_latency(primer_grupo[elementos], nodo_AG)
                                        info_actuator = self.info_actuator_generator(nodo_AG)
                                        actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(
                                            lista_final,
                                            lista_salida_memoria,
                                            nodo_AG,
                                            primer_grupo[elementos])
                                        # we map the task to the resource
                                        lista_salida_memoria[primer_grupo[elementos]] = [True, nodo_AG,
                                                                                         primer_grupo[elementos],
                                                                                         self.AG.nodes[nodo_AG]['op'],
                                                                                         self.dict_nodes[
                                                                                             primer_grupo[elementos]][
                                                                                             'ops'][
                                                                                             self.AG.nodes[nodo_AG]['op']][
                                                                                             'latency'],
                                                                                         self.AG.nodes[nodo_AG]['par'],
                                                                                         self.AG.nodes[nodo_AG]['par'],
                                                                                         self.dict_nodes[
                                                                                             primer_grupo[elementos]][
                                                                                             'ops'][
                                                                                             self.AG.nodes[nodo_AG]['op']][
                                                                                             'clk'],resultado_latencia,resultado_latencia_total,info_sensor,info_actuator,actuator_sink]

                                        mapping = False
                                        self.counter = 0
                                        if self.s_prints == 'heudebug':
                                            print("la lista de salida es ", lista_salida_memoria)
                                        # we store the mapped task
                                        self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                                        # we continue with the creation of special nodes if we need one

                                        self.generation_special_nodes(nodo_AG, primer_grupo[elementos], lista_final)
                                        # reset of the variables
                                        bandera_caso_no_probabilidad = True
                                        bandera_nodo_especial = True
                                        # todo verify this part, maybe does not work
                                        vector_nodo_especial_predecesor = (primer_grupo[elementos])
                                        if elementos in copia_primer_grupo:
                                            copia_primer_grupo.remove(elementos)
                                        # break

                                if not mapping:
                                    bandera_mapeo_en_ciclo = True
                                    break



                            # now we return the old values to the first group
                            # if we dont have resources we create a new time slot
                            if self.s_prints == 'heudebug':
                                print(self.lista_AG_copy,mapping)

                            if bandera_mapeo_en_ciclo:

                                if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                    print("we end a cycle in stage 1a")
                                    print("the current mapping list is")
                                    print(lista_salida_memoria)
                                # we still have tasks to map so we get the next possible candidates
                                nueva_lista_primer_grupo = []
                                if self.lista_AG_copy:
                                    # we obtain the predecessors and this process is the same as the previous
                                    predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                    nueva_lista_primer_grupo = []
                                    for predecesor in predecesores:
                                        lugar_mapeado = None
                                        for lugar in lista_salida_memoria:
                                            if lugar[1] == predecesor:
                                                lugar_mapeado = lugar[2]
                                        if lugar_mapeado != None:
                                            nueva_lista_primer_grupo = \
                                                list(set( nueva_lista_primer_grupo +
                                                          (list(self.DG_original.successors(lugar_mapeado)))))
                                    lista_final_primer_grupo = []
                                    for posible in nueva_lista_primer_grupo:
                                        if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][
                                            2] != 'copy':
                                            pass
                                        else:
                                            lista_final_primer_grupo.append(posible)
                                if self.s_prints == 'heudebug':
                                    print("the new list of candidates is 800", lista_final_primer_grupo)

                                primer_grupo = lista_final_primer_grupo# list(self.DG_copy.successors(nodo_utilizado_en_mapeo))
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the new possible candidates are {dummy_print_dg}")

                            else:
                                ### this need to be verify

                                if self.lista_AG_copy or mapping:

                                    primer_grupo = copia_primer_grupo
                                    if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                        print("debug - the first group is ", primer_grupo)
                                    if primer_grupo:
                                        mapping = True
                                    else:
                                        if self.s_prints == 'debug':
                                            print("we are going to create a time slot stage 1")
                                        elif self.s_prints == 'heudebug':
                                            print("we are going to create a time slot")
                                        bandera_caso_no_probabilidad = False
                                        mapping = False
                                        bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, \
                                        lista_final, vector_buffer_especiales, vector_nodos_especiales,\
                                        bandera_caso_no_probabilidad = self.reinicio_time_slot(
                                            lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                                            vector_nodos_especiales, bandera_caso_no_probabilidad)
                                else:
                                    lista_final.append(lista_salida_memoria)
                                    mapping = False
                            bandera_primer_nodo = False



                    #### main cycle
                    else:
                        # this is the beggining of stage 2
                        # we create the probability vector
                        if self.s_prints == 'debug' or self.s_prints == 'heudebug' or self.s_prints == 'heu':
                            print("begin of stage 2")
                            print("the tasks are ",self.AG.nodes)
                            print(mapping)
                            print("the tasks left ",self.lista_AG_copy)
                            print("the possible candidates ",primer_grupo)
                            # time.sleep(2)

                        lista_probabilidad = [0 for g in range(len(primer_grupo))]
                        if self.s_prints == 'heudebug' or self.s_prints == 'debug' or self.s_prints == 'heu':
                            dummy_print_dg = []
                            for nd in primer_grupo:
                                dummy_print_dg.append(self.dict_nodes[nd]['name'])
                            print(f"The current first group of candidates are {dummy_print_dg} for {nodo_AG}")

                        # we have a list of possible candidates, in here we are going to prune that list by
                        # verifying that the resource can actually be use to map the task
                        lista_resultante = []
                        for elemento in range(0, len(primer_grupo)):
                            if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                print("error tracker 300")
                                print(f"we are going to check if the  resource {primer_grupo[elemento]} is valid")
                                # print("debug - operations of the candidate ",primer_grupo[elemento], " are ",self.DG_copy.node[primer_grupo[elemento]]['op'])
                            test_degree = False
                            # first we check the data dependence and then the verification of degree
                            bandera_mapping_valido = False
                            bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[elemento],
                                                                                       nodo_AG,
                                                                                       lista_salida_memoria,
                                                                                       lista_final, copia_DG,
                                                                                       bandera_recomputo)


                            test_degree = self.evaluation_degree(primer_grupo[elemento],nodo_AG,lista_salida_memoria)
                            # test_degree = output_degree_flag and input_degree_flag

                            ######################################################



                            if task_AG in self.DG_original.nodes[primer_grupo[elemento]]['op'] and test_degree \
                                    and bandera_mapping_valido:
                                # because the previous tests are ok we continue with the verification of parameters
                                # and the source of data
                                vector_validacion_parametros = self.verification_of_parameters(nodo_AG,primer_grupo[elemento])
                                bandera_source_of_data,info_sensor = self.verification_of_source(nodo_AG,primer_grupo[elemento])
                                # validacion_dependence = self.verificacion_data_dependence(primer_grupo[elementos],)
                                # if self.DG_copy.node[primer_grupo[elemento]]['op'] == task_AG:
                                if self.s_prints == 'heudebug':
                                    print("the flag of source of data and the validation of parameters ")
                                    print(bandera_source_of_data, vector_validacion_parametros)
                                if all(vector_validacion_parametros) and bandera_source_of_data:
                                    if self.s_prints == 'heudebug':
                                        print(f"for the resource {self.dict_nodes[primer_grupo[elemento]]['name']} the "
                                              f"validation is ok")
                                    lista_resultante.append(elemento)
                                else:
                                    if self.s_prints == 'heudebug':
                                        print(f"the resource {primer_grupo[elemento]} is not a valid one")


                        # now we have been prune the list of possible candidates, the idea is to check if there is only
                        # one candidate we assign the hightest probability to it, but if there is more than one we need
                        # to check which option is the best one
                        if self.s_prints == 'heudebug':
                            print(" the list of possible candidates is ",lista_resultante)
                            dummy_print_dg = []
                            for nd in lista_resultante:
                                dummy_print_dg.append(self.dict_nodes[primer_grupo[nd]]['name'])
                            print(f"the elements are  {dummy_print_dg}")
                        lista_probabilidad_un_nodo = [0 for g in range(len(primer_grupo))]
                        bandera_solo_un_nodo = False
                        if len(lista_resultante) == 1:
                            # if we only have one feasible candidate we assign the highest probability to it
                            for elemento in range(0, len(primer_grupo)):
                                if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                    print("error tracker 301 ", primer_grupo[elemento])

                                if task_AG in self.DG_original.nodes[primer_grupo[elemento]]['op'] and elemento in lista_resultante:
                                    # if self.DG_copy.node[primer_grupo[elemento]]['op'] == task_AG:
                                    if self.s_prints == 'heudebug':
                                        print("debug - bug 01", lista_resultante)
                                    lista_probabilidad_un_nodo[elemento] = 0.99
                            # we activate the flag of only one candidate
                            bandera_solo_un_nodo = True
                            if self.s_prints == 'heudebug' or self.s_prints == 'heudebug':
                                print("there is only one feasible candidate",lista_probabilidad_un_nodo)

                        if not bandera_solo_un_nodo and lista_resultante:
                            # if we have several feasible candidates
                            lista_total_nodos = obtencion_sucesores_de_una_lista(self.DG_original,
                                                                                 primer_grupo)

                            for elementos in range(0, len(primer_grupo)):
                                # we verify that we can use them - this is a double check TODO verify if we can remove this
                                if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                    print(
                                        f"we are going to verify the resource {self.dict_nodes[primer_grupo[elementos]]['name']}")
                                if elementos in lista_resultante:
                                    vector_validacion_parametros = self.verification_of_parameters(nodo_AG,
                                                                                                   primer_grupo[elementos])
                                else:
                                    vector_validacion_parametros = [False]

                                if self.s_prints == 'heudebug':
                                    print("bug 02",self.DG_original.nodes[primer_grupo[elementos]])
                                if task_AG in self.DG_original.nodes[primer_grupo[elementos]]['op'] and all(vector_validacion_parametros):

                                    # the candidate can be use, we obtain its successors
                                    lista_sucesores = obtencion_sucesores(self.DG_original,
                                                                      primer_grupo[elementos])
                                    # if the task as successors
                                    if sucesores_nodo_AG :
                                        if lista_sucesores:
                                            # if the resource has successors
                                            obtencion_probabilidad_sucesores = self.obtencion_probabilidad(
                                                self.AG_copy,
                                                sucesores_nodo_AG,
                                                primer_grupo[elementos],
                                                self.DG_copy,
                                                lista_total_nodos,
                                                lista_salida_memoria)
                                                # we obtain the probability of the candidate
                                        else:
                                            obtencion_probabilidad_sucesores = 0
                                    else:
                                        # if there are no more tasks to map, we need to map the task to any resource
                                        # available, so we assign high probabilities to the candidates
                                        obtencion_probabilidad_sucesores = 0.99
                                    # store the probability
                                    lista_probabilidad[elementos] = (obtencion_probabilidad_sucesores)

                                else:
                                    # if we can not use the resource we assign a probability of zero
                                    lista_probabilidad[elementos] = 0

                        else:

                            # if we only have one candidate we put the probability obtained previously
                            if len(self.AG.nodes) == 1 or len(self.AG.nodes) == 0:
                                if self.s_prints == 'heudebug' :
                                    print("error tracker 303")
                            if self.s_prints == 'heu':
                                print(f"we have only one candidate {lista_probabilidad_un_nodo}")
                            lista_probabilidad = list(lista_probabilidad_un_nodo)
                        todos_zeros = all(v == 0 for v in lista_probabilidad)
                        if not todos_zeros:
                            lista_probabilidad = [float(i) / sum(lista_probabilidad) for i in lista_probabilidad]
                        if self.s_prints == 'debug':
                            print("the probability vector in stage 2 step 1 is :", lista_probabilidad)
                            print("debug - successors of the current task", sucesores_nodo_AG)
                        elif self.s_prints == 'heudebug' or self.s_prints == 'heu':
                            print(f"the current probability vector is {lista_probabilidad} and the succesors of the "
                                  f"task are {sucesores_nodo_AG}")
                        # we obtain the max value
                        max_value = max(lista_probabilidad)
                        # if we can not use any candidate we create a error probability vector, this will be used after
                        lista_probabilidad_error = [0 for g in range(len(primer_grupo))]
                        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                            print("we are going to print the info of the hw")
                            for nodo_test in self.DG_copy.nodes:
                                    print(nodo_test, self.DG_copy.nodes[nodo_test])
                            print("done")
                        probabilidad_elemento = 0
                        if max_value == 0 :
                            # now, if all the values of the probability vector are zeros, this means that none of the
                            # possible candidates can be use, so what we do now is to check which datapath is the best one
                            # to use
                            if self.s_prints == 'heudebug':
                                print("all the values of the probability vector are zeros")
                            for elementos in range(0, len(primer_grupo)):
                                if self.s_prints == 'heudebug':
                                    print("debug - resource from first group", primer_grupo[elementos])
                                try:
                                    lista_sucesores = obtencion_sucesores(self.DG_copy, primer_grupo[elementos])
                                except:
                                    lista_sucesores = []

                                lista_total_nodos = obtencion_sucesores_de_una_lista(self.DG_original,
                                                                                     primer_grupo)
                                if self.s_prints == 'heudebug':
                                    print("debug - successors list", lista_sucesores,task_AG)
                                    print("debug - total list ", lista_sucesores, lista_total_nodos)

                                    #####
                                bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[elementos],
                                                                                           nodo_AG,
                                                                                           lista_salida_memoria,
                                                                                           lista_final,
                                                                                           copia_DG,
                                                                                           bandera_recomputo)


                                if len(lista_sucesores) == 1 and  task_AG in self.DG_copy.nodes[lista_sucesores[0]]['op'] \
                                        and nodo_AG in self.lista_sinks_AG and bandera_mapping_valido:
                                    if self.s_prints == 'heudebug':
                                        print("POSIBLE BUG")

                                    vector_validacion_parametros = self.verification_of_parameters(nodo_AG,
                                                                                                   lista_sucesores[0])
                                    # task_AG in self.DG_copy.nodes[primer_grupo[elementos]]['op']:
                                    if all(vector_validacion_parametros):
                                        probabilidad_elemento = 0.99

                                else:

                                    probabilidad_elemento = self.obtencion_probabilidad(
                                        self.AG_copy,
                                        [nodo_AG],
                                        primer_grupo[elementos],
                                        self.DG_copy,
                                        lista_total_nodos,
                                        lista_salida_memoria)

                                # we store the probability
                                lista_probabilidad_error[elementos] = (probabilidad_elemento)
                            todos_zeros = all(v == 0 for v in lista_probabilidad)
                            if not todos_zeros:
                                lista_probabilidad_error = [float(i) / sum(lista_probabilidad_error) for i in
                                                            lista_probabilidad_error]
                            if self.s_prints == 'heudebug':
                                print("the error vector is ", lista_probabilidad_error,bandera_reinicio)


                            max_value_error = max(lista_probabilidad_error)

                            if max_value_error == 0 and bandera_reinicio:

                                contador_reinicios = contador_reinicios + 1
                                # in here we keep track of how many attempts has been done
                                if contador_reinicios > 5:

                                    return -1
                                    # raise ValueError('The operation is not supported.')
                                if self.s_prints == 'heudebug':
                                    print("test 055")
                                bandera_reinicio_dummy, bandera_primer_nodo, primer_grupo, lista_salida_memoria,\
                                lista_final, vector_buffer_especiales, vector_nodos_especiales,\
                                bandera_caso_no_probabilidad = self.reinicio_time_slot(
                                    lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                                    vector_nodos_especiales, bandera_caso_no_probabilidad)
                            else:
                                # we choose the higher value and we assign its successors to the first group
                                max_index = lista_probabilidad_error.index(max_value_error)
                                primer_grupo_buffer = list(self.DG_original.successors(primer_grupo[max_index]))
                                if self.s_prints == 'heudebug':
                                    print("the resource with the maximum value is ", primer_grupo[max_index])
                                    print(" the resource is  ",primer_grupo_buffer)
                                primer_grupo = []
                                # todo verify this part
                                for candidato in primer_grupo_buffer:
                                    if lista_salida_memoria[candidato][0] and lista_salida_memoria[candidato][2] != 'copy':
                                        pass
                                    else:
                                        primer_grupo.append(candidato)

                                if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                    dummy_print_dg = []
                                    for nd in primer_grupo:
                                        dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                    print(f"the next first group of candidates are {dummy_print_dg}")
                        else:
                            # we have a feasible candidate
                            max_index = lista_probabilidad.index(max_value)
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                print("we have a feasible candidate stage 2 step 1")
                                print("debug - special node flag ", bandera_nodo_especial, "current task ", nodo_AG,
                                      "current feasible candidate", primer_grupo[max_index])
                                print("ANOTHER CHANGE 04")
                                print("sources of the app", self.lista_sources_AG)

                            # in here we are going to make another change, if we encounter a source node we need to be sure
                            # the producer of data is the correct one




                            vector_validacion_parametros = self.verification_of_parameters(nodo_AG,primer_grupo[max_index])
                            bandera_source_of_data,info_sensor = self.verification_of_source(nodo_AG,primer_grupo[max_index])
                            # we are going to verify the data dependence
                            bandera_mapping_valido = self.verificacion_data_dependence(primer_grupo[max_index], nodo_AG,
                                                                                       lista_salida_memoria, lista_final,
                                                                                       copia_DG, bandera_recomputo)
                            if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                print(f"the list of nodes that need to have copy function are {self.lista_nodos_copy} ")
                                print("the list until now is",bandera_mapping_valido)
                                print(lista_salida_memoria)
                            if self.s_prints == 'debug':
                                print("the flag of data dependence is  ", bandera_mapping_valido)
                            # bandera_mapping_valido = True
                            # time.sleep(7)
                            if bandera_mapping_valido and bandera_source_of_data and all(vector_validacion_parametros):
                                if self.s_prints == 'heudebug':
                                    print("estamos en algo paleta 01")
                                if self.s_prints == 'heudebug' or self.s_prints == 'heuiter':
                                    print(
                                        f"we are going to map task {self.dict_nodes_a[nodo_AG]['name']}"
                                        f" on the resource {self.dict_nodes[primer_grupo[max_index]]['name']}")
                                    print("------------------------------------------------------------")
                                if self.s_pause:
                                    input("Press Enter to continue...")

                                # we are going to obtain the latency of this node
                                #########
                                # we start by finding the name of the formula and the formula itself
                                if self.s_prints == 'heudebug':
                                    print(" we are going to obtain the latency of the node 02")
                                    # we are going to obtain the latency of this node
                                    #########
                                    # we start by finding the name of the formula and the formula itself
                                    # print(self.dict_info)
                                resultado_latencia,resultado_latencia_total = self.obtention_latency(primer_grupo[max_index],nodo_AG)


                                # we are going to add the copy nodes
                                if self.s_prints == 'heudebug' or self.s_prints == 'debug' or self.s_prints == 'heu':
                                    print("lista de nodos copy",self.lista_nodos_copy)
                                    print("lista de nodos en los time slots",self.lista_nodos_copy_time)
                                    print("we are going to map something so we need to add the copy nodes 03")
                                    print(lista_final)

                                info_actuator = self.info_actuator_generator(nodo_AG)
                                actuator_sink, lista_final, lista_salida_memoria = self.generation_copy_nodes(
                                    lista_final,
                                    lista_salida_memoria,
                                    nodo_AG,
                                    primer_grupo[max_index])

                                if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                    print("before the mapping ", lista_salida_memoria)
                                # we are going to map the task to the resource
                                lista_salida_memoria[primer_grupo[max_index]] = [True, nodo_AG, primer_grupo[max_index],
                                                                                 self.AG.nodes[nodo_AG]['op'],
                                                                                 self.dict_nodes[
                                                                                     primer_grupo[max_index]][
                                                                                     'ops'][
                                                                                     self.AG.nodes[nodo_AG]['op']][
                                                                                     'latency'],
                                                                                 self.AG.nodes[nodo_AG]['par'],
                                                                                 self.AG.nodes[nodo_AG]['par'],
                                                                                 self.dict_nodes[
                                                                                     primer_grupo[max_index]][
                                                                                     'ops'][
                                                                                     self.AG.nodes[nodo_AG]['op']][
                                                                                     'clk'], resultado_latencia,resultado_latencia_total,info_sensor,info_actuator,actuator_sink]
                                # reset of values
                                mapping = False
                                self.counter = 0
                                if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                    print("la lista de salida es ", lista_salida_memoria)
                                    print(mapping)

                                # we store the mapped task
                                self.lista_nodos_ya_mapeados = self.lista_nodos_ya_mapeados + [nodo_AG]
                                # creation of special nodes

                                self.generation_special_nodes(nodo_AG,primer_grupo[max_index],lista_final)

                                # we check if there are still tasks to map
                                if len(self.lista_AG_copy) > 0:
                                    # verification of the successors of the current task
                                    if self.s_prints == 'heudebug':
                                        print("entro en el ciclo paleta ")
                                    if self.lista_AG_copy[0] in obtencion_sucesores(self.AG_copy, nodo_AG):

                                        bandera_no_conexion = False
                                    else:

                                        bandera_no_conexion = True
                                    # we verify is there are still resources, datapaths availables or if we need to create
                                    # a new time slot, this part maybe can be put it in a function
                                    bandera_no_conexion = False
                                    if not bandera_no_conexion:

                                        if self.s_prints == 'debug':
                                            print("debug - ", primer_grupo[max_index])
                                        # print(primer_grupo[max_index])
                                        # print(list(self.DG_copy.successors(primer_grupo[max_index])))

                                        nueva_lista_primer_grupo = []
                                        if self.lista_AG_copy:
                                            # this part of the code is for the creation of the next list of possible
                                            # candidates, is the same as the previous sections
                                            predecesores = self.AG_copy.predecessors(self.lista_AG_copy[0])
                                            numero_predecesores = len(list(self.AG_copy.predecessors(self.lista_AG_copy[0])))
                                            if self.s_prints == 'heudebug':
                                                print(" the next task is ", (self.lista_AG_copy[0]),"the predecessors are "
                                                                                                         "",
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
                                                    nueva_lista_primer_grupo = list(set( nueva_lista_primer_grupo + (list(self.DG_original.successors(lugar_mapeado)))))

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

                                                if lista_salida_memoria[posible][0] and lista_salida_memoria[posible][2] != 'copy':
                                                    pass
                                                else:
                                                    lista_final_primer_grupo.append(posible)
                                        if self.s_prints == 'heudebug':
                                            print("LA NUEVA LISTA DE CANDIDATOS ES 10", lista_final_primer_grupo)


                                        primer_grupo =  list(set(lista_final_primer_grupo)) #list(self.DG_original.successors(primer_grupo[max_index]))
                                        if self.s_prints == 'heudebug' or self.s_prints == 'debug':
                                            dummy_print_dg = []
                                            for nd in primer_grupo:
                                                dummy_print_dg.append(self.dict_nodes[nd]['name'])
                                            print(f"the new list of possible candidates is {dummy_print_dg} "
                                                  f"for the task {self.lista_AG_copy[0]} section 01")

                                    else:

                                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, \
                                        bandera_primer_nodo, \
                                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales,\
                                        vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths =\
                                            self.no_more_resources(
                                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                            vector_buffer_especiales, vector_nodos_especiales,
                                            bandera_caso_no_probabilidad, copia_DG,bandera_nodo_especial)

                                bandera_nodo_especial = False
                                bandera_recomputo = False
                                if self.s_pause and self.s_prints == 'heudebug':
                                    input("Press Enter to continue...")
                                if not self.lista_AG_copy:
                                    if self.s_prints == 'debug' or self.s_prints == 'heudebug' or self.s_prints == 'heu':
                                        print("there are no more tasks to map stage 2")
                                    lista_final.append(lista_salida_memoria)

                            else:
                                # we reset the mapping list
                                bandera_primer_nodo = False
                                mapping = True
                                bandera_solo_un_nodo = False
                                if self.s_pause and self.s_prints == 'heudebug':
                                    input("Press Enter to continue...")
                                if self.s_prints == 'debug':
                                    print("Append module stage 2 - debug -", lista_final)
                                if not self.lista_AG_copy:
                                    lista_final.append(lista_salida_memoria)
                                    # self.lista_nodos_especiales_final.append()
                                    lista_salida_memoria = [[False, -1, -1, -1,-1,-1,-1,-1,-1,-1,-1,-1,-1] for g in range(len(copia_DG))]
                                else:
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo,\
                                    primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                    vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                        self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG, bandera_nodo_especial)

                        if  not primer_grupo:
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("we still have tasks to mapIJNSDIJNFJSF", primer_grupo, nodo_AG)
                            # if not primer_grupo:
                                # if we dont have any resource available we check the datapaths
                            # if self.lista_AG_copy:
                            if self.s_prints == 'heudebug':
                                print("la lista de tareas es ", self.lista_AG_copy)
                            if self.lista_AG_copy or mapping:
                                try:
                                    nodo_siguiente = self.lista_AG_copy[0]
                                except:
                                    nodo_siguiente = None
                                if self.s_prints == 'heudebug':
                                    print(f"BUG DE DATAPATHS, entrada a ciclo x {nodo_siguiente}")
                                # print("nodoosos",nodo_siguiente)
                                if nodo_siguiente in self.lista_sources_AG:
                                    if self.s_prints == 'heudebug':
                                        print("test bug datapaths")
                                    lista_posible = []
                                    for sour in self.lista_sources_DG:
                                        if lista_salida_memoria[sour][0] :
                                            pass
                                        else:
                                            lista_posible.append(sour)
                                    if self.s_prints == 'heudebug':
                                        print(f"veremos que tiene la lista posible {lista_posible}")
                                    if lista_posible and _lista_posible != lista_posible:
                                        _lista_posible = lista_posible
                                        primer_grupo = lista_posible
                                    else:
                                        bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo,\
                                        primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, \
                                        vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = \
                                            self.no_more_resources(
                                            lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                            copia_DG, bandera_nodo_especial)
                                else:
                                    if self.s_prints == 'heudebug':
                                        print(f"BUG DE DATAPATHS, entrada a ciclo y")
                                    bandera_nodo_especial, bandera_recomputo, bandera_reinicio, bandera_primer_nodo, \
                                    primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales,\
                                    vector_nodos_especiales, bandera_caso_no_probabilidad, contador_datapaths = self.no_more_resources(
                                        lista_salida_memoria, contador_datapaths, bandera_reinicio, lista_final,
                                        vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad,
                                        copia_DG,bandera_nodo_especial)

                                if self.s_prints == 'heudebug':
                                   print("el nuevo primer grupo es 0111", primer_grupo)


                            else:

                                lista_final.append(lista_salida_memoria)
                                mapping = False
                        else:
                            if self.counter > len(self.DG_copy) + 1:
                                if self.s_prints == 'heudebug':
                                    print(f"se activara la bandera de REINICIO")
                                bandera_reinicio = True


            # vector_buffer_especiales.append(vector_nodos_especiales)
        if self.s_prints == 'debug' or self.s_prints == 'heudebug' or self.s_prints == 'heu':
            print("end of the mapping debug - ", vector_nodos_especiales, len(lista_final), vector_buffer_especiales)
            print(f"los nodos especiales son {self.lista_nodos_especiales_final} o esta {self.lista_nodos_especiales}")
            print("the final mapping list")
            print(lista_final)

        vector_config = []
        vector_config_v2 = []
        return lista_final, vector_config, vector_config_v2


    def no_more_resources(self,lista_salida_memoria,contador_datapaths,bandera_reinicio,lista_final,
                          vector_buffer_especiales,vector_nodos_especiales,
                          bandera_caso_no_probabilidad,copia_DG,bandera_nodo_especial):
        """we call this function when there is no more resources to be used, in here we verify if there is any
        independent datapath available, if there isnt we create a new time slot, the parameters are

        :parameter lista_salida_memoria is the current mapping list
        :parameter contador_datapaths
        """

        # first we check if there is any independent datapath available
        lista_datapaths_disponibles, bandera_recomputo = self.datapaths_available(
            lista_salida_memoria)

        if self.s_prints == 'heudebug':
            print(f"We are at the no more resources function, and the list of datapaths available is"
                  f" {lista_datapaths_disponibles}")
        bandera_decision = True
        # if there is any datapath available
        if lista_datapaths_disponibles:
            bandera_decision = False
            # we remove the nodes that are occupied from the hardware graph
            self.DG_copy = self.remove_nodes_DG(lista_datapaths_disponibles)
            # we enable the flag of special nodes, meaning that we are going to reuse a datapath
            bandera_nodo_especial = True
            # we select the possible candidates from the subgraph that we just created
            primer_grupo = obtencion_sources(self.DG_copy)
            # we enable other flags, the first one is to determine that we are going to restart the mapping, and the
            # other is to let know the mapping process that there could be the need of a recomputation node
            bandera_primer_nodo = True
            bandera_recomputo = True
            # because we may end up in here several times we need a counter to define if we enter into a cycle
            contador_datapaths = contador_datapaths + 1
            # if the counter of visits is greater than the number of datapaths means that we tried to use every
            # datapath without sucess, in this case we enable the flag of restart
            if contador_datapaths > len(self.datapaths_independientes) + 1:
                bandera_reinicio = True
        else:
            # because there is no datapaths available we will create a time slot
            bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final,\
            vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad = self.reinicio_time_slot(
                lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                vector_nodos_especiales, bandera_caso_no_probabilidad)
        if self.s_prints == 'heudebug':
            print(f"we will return from the no more resources function, we add a new time slot {bandera_decision}")
        return bandera_nodo_especial,bandera_recomputo,bandera_reinicio, bandera_primer_nodo, primer_grupo,\
               lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales,\
               bandera_caso_no_probabilidad,contador_datapaths




    def generation_special_nodes(self,nodo_AG,resource,lista_final):
        """this function adds the special nodes, it traverse the resulting mapping and finds if there is a need of
        special nodes, first we add the recomputation nodes and after we find the dependency nodes between time slots
        """
        # todo verify this function, it may not work to several successors

        # we make a copy of the sinks resources of the basic structure connected to rw or ri resources
        copy_nodos_conectados_rc = self.list_sinks_connected_to_rc.copy()

        # first we find the recomputation nodes
        # from the datapaths available function we define if there is any task mapped in the occupied datapaths that
        # has a successor which is not mapped yet, so the idea is to check that for the current task, if we find that
        # the current task has a predecessor which is mapped onto another datapath we add the special node
        # if we find that there is a need of a special node we directly add it to the special node list
        if self.lista_predecesores_01:
            # there is predecessor tasks mapped to occupied datapaths
            if self.s_prints == 'debug' or 'heudebug':
                print(f"creation of a special node process, the list is {self.lista_predecesores_01}")
            # for each task in the list of predecessor mapped to occupied datapaths
            for nodo_especial in self.lista_predecesores_01:
                # if the successor of the mapped task is the current task we will add a special node, so we need to
                # find a valid sink and a valid source to defined it and add a valid information to the special nodes
                # list
                if nodo_especial[0] == nodo_AG:
                    # because we need to add a special node we first find a valid sink
                    # if the place of the predecessor is a valid sink we use that place
                    if nodo_especial[2] in copy_nodos_conectados_rc:
                        lugar_sink = nodo_especial[2]
                        # we remove that sink from the list to we dont use it anymore, if we can not remove it we
                        # reinitialize the list and remove it from there
                        try:
                            copy_nodos_conectados_rc.remove(lugar_sink)
                        except:
                            copy_nodos_conectados_rc = self.list_sinks_connected_to_rc.copy()
                            copy_nodos_conectados_rc.remove(lugar_sink)
                    else:
                        # if the place of the predecessor is not a valid sink we find a valid sink
                        lugar_sink = sink_node_from_any_node(self.DG_original, self.list_sinks_connected_to_rc,
                                                             nodo_especial[2])
                    # now we find a valid source
                    # if the current resource is a valid source we use that place
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        # if not we find a valid source
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                 resource)
                    # we use a temporal variable, the first element is the indicator that this special node represent a
                    # recomputation node (False), then the a valid sink, a valid source, the time slot,
                    # and the number of special node
                    buffer_nodo_especial = [nodo_especial[3], lugar_sink, lugar_source,
                                            len(lista_final), self.contador_recomputacion]
                    # print("buffer nodo especial", buffer_nodo_especial)
                    if self.s_prints == 'heudebug':
                        print(
                            f"We will add a recomputation node {buffer_nodo_especial} and the curren list of"
                            f" special nodes is {self.lista_nodos_especiales}")
                    # we add the special node to the list, we increase the counter and remove the element from the list
                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    self.lista_predecesores_01.remove(nodo_especial)

        # now the second part of this function, the addition of dependency nodes
        # we add the special nodes corresponding to the nodes mapped in the previous time slot
        # in here we use a list that the restart of time slot (reinicio time slot) function creates
        elementos_to_remove = []

        if self.s_prints == 'heudebug':
            print("The list of couples is ", self.vector_de_parejas_memoria)

        # if there is any task that has a successor that is not mapped to its time slot
        if self.vector_de_parejas_memoria:
            # for each element of the list
            for pareja in self.vector_de_parejas_memoria:
                # if the current task is a successor of any mapped task from another time slot
                if nodo_AG == pareja[0]:
                    # we will add another element to the list of special nodes, so we need to find a valid source,
                    # the valid sink is already found previously
                    # if the current resource is a valid source node we use that place
                    if resource in self.lista_sources_DG:
                        lugar_source = resource
                    else:
                        # if not we find a valid source to use
                        lugar_source = source_node_from_any_node(self.DG_original,
                                                                 self.lista_sources_DG,
                                                                resource)
                    # if self.s_prints == 'heudebug':
                    #     print(f"the list of occupied sources {self.lista_nodos_ocupados_source},"
                    #           f" the selected source {lugar_source}")

                    # if the valid source is already occupied we use another
                    if lugar_source in self.lista_nodos_ocupados_source:
                        copy_lista_sources = self.lista_sources_DG.copy()
                        copy_lista_sources.remove(lugar_source)
                        lugar_source_copia = source_node_from_any_node(self.DG_original,copy_lista_sources,resource)
                        if lugar_source_copia != None:
                            lugar_source = lugar_source_copia

                    # if self.s_prints == 'heudebug':
                    #     print(" buffer nodo especial" , pareja[1], lugar_source, len(lista_final),
                    #                         self.contador_recomputacion)
                    # we create a temporal variable, which consist on the identifier of dependency node (True),
                    # the valid sink, the valid source, the time slot, and the counter of special nodes
                    buffer_nodo_especial = [True, pareja[1], lugar_source, len(lista_final),
                                            self.contador_recomputacion]
                    # we add the selected source to the occupied source list
                    self.lista_nodos_ocupados_source.append(lugar_source)
                    if self.s_prints == 'heudebug':
                        print(
                            f" We will add a dependency node {buffer_nodo_especial} and the special nodes list"
                            f" is {self.lista_nodos_especiales}")
                    # we add the dependency node to the special node list, we increase the counter, we add the
                    # element to the list of elements to remove
                    self.lista_nodos_especiales.append(buffer_nodo_especial)
                    self.contador_recomputacion = self.contador_recomputacion + 1
                    elementos_to_remove.append(pareja)
            # after all the process we remove the elements that we used
            for el in elementos_to_remove:
                self.vector_de_parejas_memoria.remove(el)
        return

    def info_actuator_generator(self,nodo_AG):
        """in this function we gather the information of the actuator of the application graph, it mainly finds a
        valid actuator for a sink node of the basic structure

        """
        # todo this can be used to validate the actuator not implemented yet

        lugar_n = None
        # if the current task is part of the sinks of the basic structure
        if nodo_AG in self.lista_sinks_AG:
            # we traverse the complete structure of the application
            for nodo_total in self.AG_total.nodes:
                # print(nodo_total)
                # we cross relate the current task with the complete structure
                if self.AG_original.nodes[nodo_AG]['name'] == self.AG_total.nodes[nodo_total]['name']:
                    # print("encontrado")
                    lugar_n = nodo_total
            # we obtain the sinks nodes of the complete structure
            # todo this can be done outside of the function, maybe at the beggining
            sinks_ag_total = obtencion_sinks(self.AG_total)
            # we find the actuator that is connected to the current task
            actuator_info = sink_node_from_any_node(self.AG_total, sinks_ag_total, lugar_n)
            # we retrieve the parameters of the actuator
            # todo in here we need to add the possibility of a different type of actuator
            info_actuator = [self.AG_total.nodes[actuator_info]['name'],
                             self.AG_total.nodes[actuator_info]['par']['height'],
                             self.AG_total.nodes[actuator_info]['par']['width']]
        else:
            # because the current task is not a sink we return nothing
            info_actuator = [None, None, None]
        return info_actuator


    def generation_copy_nodes(self,lista_final,lista_salida_memoria,nodo_AG,resource):
        """this function is used for the generation of the copy nodes which are added to the resources that are in
        between two consecutive tasks which are mapped to not consecutive resources, so the copy nodes allows to
        transfer the output data from the predecessor to the successor"""

        if self.s_prints == 'heudebug':
            print("Inside of the generation of copy nodes function")
        # print(self.dict_nodes[resource])

        # we gather the name of the latency of the copy operation in the current resource
        latency_variable = self.dict_nodes[resource]['ops']['copy']['clk']
        # print(self.dict_info)
        # we retrieve the latency of the copy operation in this resource
        latency = None
        for n in self.dict_info['functions_res']:
            if n == latency_variable:
                latency = self.dict_info['functions_res'][n]

        # we call the verification of source function, which verify the source of data if the current task is source
        bandera_source_of_data,info_sensor = self.verification_of_source( nodo_AG, resource)

        # if the flag of time slot is True, this flag is defined in the verification of data dependence function,
        # and means that there is a predecessor of the current task mapped in a different time slot
        if self.lista_en_time_slots:
            if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                print("test 01 - copy nodes function")
                print(lista_final[self.lugar_time_slot - 1])
            # this list is made also  in the verification of data dependence and contains a path to a sink node
            # for each resource of the path we will assign a copy operation, taking into consideration the time slot
            for copy_node in self.lista_nodos_copy_time:
                # if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                #     print(f"test 02 - copy nodes function {copy_node}")
                if lista_final[self.lugar_time_slot ][copy_node][0]:
                    pass
                else:
                    lista_final[self.lugar_time_slot ][copy_node] = [True, None, 'copy', 'copy', 0, 0,
                                                       0, 0, latency, latency, info_sensor, 0, 0]
            # now, we add the copy nodes to the current mapping list
            for copy_node in self.lista_nodos_copy:
                # if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                #     print(f"test 03 - copy nodes function {copy_node}")
                if lista_salida_memoria[copy_node][0]:
                    pass
                else:
                    lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', 0, 0,
                                                       0, 0, latency, latency, info_sensor, 0, 0]

        else:
            # if there is no predecessor mapped in a different time slot*
            # this list is also created in the verification of data dependence function and it represent the path to
            # the current task from its predecessor
            for copy_node in self.lista_nodos_copy:
                if self.s_prints == 'heudebug' or self.s_prints == 'heu':
                    print(f"test 04 - copy nodes function {copy_node}")
                # we asign the copy operation to the resources in the path
                if lista_salida_memoria[copy_node][0]:
                    pass
                else:
                    lista_salida_memoria[copy_node] = [True, None, 'copy', 'copy', 0, 0,
                                                       0, 0, latency, latency, info_sensor, 0, 0]

        if self.s_prints == 'heudebug' or self.s_prints == 'heu':
            print("test 05 - copy nodes function")
            print(lista_final)
            print(lista_salida_memoria)
            print(" end debug")

        # we already add the nodes between tasks but we need to add the copy nodes from the sink tasks
        # to the sinks of the hardware
        actuator_sink = None
        copia_nodos_conectados_a_rc = self.list_sinks_connected_to_rc.copy()

        # in the following part of the function we add the copy nodes for two type of tasks, the sinks tasks and
        # the source tasks, the idea is that the sink tasks need to be connected to a sink resource or have a path to a
        # sink resource, likewise the source tasks need to be connected to a source resource or to a resource that has
        # a path to a source resource
        # first we check if the task is a sink but the resource is not
        if nodo_AG in self.lista_sinks_AG and resource not in self.list_sinks_connected_to_rc:
            # we initilize the valid sinks
            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
            done = True
            counter_internal = 0
            # we enter this cycle to find a valid sink
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
                else:
                    counter_internal = counter_internal + 1
                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                  copy_list_sinks_connected_to_rc,
                                                                  resource)
                # print(sink_nodo_sink_task,resource)
                if lista_salida_memoria[sink_nodo_sink_task][0]:
                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                    if counter_internal == 5:
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_original,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                        done = False
                        break

                else:
                    done = False
                    break

            # we find a valid sink and we find the path from the resource to the sink
            path_sink_node = simple_paths_from_two_nodes(self.DG_original, resource, sink_nodo_sink_task)
            if self.s_prints == 'heudebug':
                print("the paths between the sink task and the sink hardware", path_sink_node)
                print(f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            # single_path = path_sink_node.pop()
            # in the following part we find the shortest path and assign to that path copy operations
            single_path = min(path_sink_node, key=len)
            single_path.remove(resource)
            for nodo_a_sink in single_path:
                if lista_salida_memoria[nodo_a_sink][0]:
                    pass
                else:
                    lista_salida_memoria[nodo_a_sink] = [True, None, 'copy', 'copy', 0, 0,
                                                       0, 0, latency, latency, info_sensor, 0, 0]

            # now we move to the complete structure, we cross relate the sink of the basic and find the name of it
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == self.DG_original.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            # in this part we perform something
            # todo verify this part, we obtain the actuator sink and we return it
            done = True
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

        # the second case, is when the task is a source task but the resource is not
        if nodo_AG in self.lista_sources_AG and resource not in self.lista_sources_DG:
            # if self.s_prints == 'heudebug':
            #     print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            # we find a valid source in the basic structure of the hardware
            source_nodo_sink_task = source_node_from_any_node(self.DG_original,
                                                              self.lista_sources_DG,
                                                              resource)
            # we find a path from the source found and the resource
            path_source_node = simple_paths_from_two_nodes(self.DG_original, source_nodo_sink_task,
                                                           resource)
            if self.s_prints == 'heudebug':
                print("the paths between the source task and the osusdofsdf hardware",
                      path_source_node)
                print(
                    f"the sink task is {nodo_AG} and the sink of the hardware graph {resource}")
            # we add the copy nodes with regard to the path that we found
            single_path = path_source_node.pop()
            single_path.remove(resource)
            for nodo_a_source in single_path:
                lista_salida_memoria[nodo_a_source] = [True, None, 'copy', 'copy', 0, 0,
                                                       0, 0, latency, latency, info_sensor, 0, 0]


        return  actuator_sink,lista_final,lista_salida_memoria




    def remove_nodes_AG(self, lista_nodos):
        """in this function we remove a list of nodes from the basic structure of the application graph and we
        return the created subgraph"""
        copy_graph = self.AG_original.copy()
        copy_graph.remove_nodes_from(lista_nodos)
        copy_graph_buffer = self.AG_original.copy()
        copy_graph.remove_nodes_from(list(copy_graph.nodes))
        return copy_graph_buffer

    def remove_nodes_DG(self, lista_nodos):
        """in this function we remove a list of nodes from the basic structure of the hardware graph, and
        return the created subgraph"""
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
        """in this function we verify the data dependence, we find the predecessors of the current task and we check
        where they are mapped and find if there is available path that reaches the resource where we are trying to
        map the task"""

        # recurso_elegido = primer_grupo[max_index]
        bandera_mapping_valido = False
        bandera_source = False
        bandera_no_esta_en_el_mismo_time_slot = False
        # we get the predecessors of the current task
        set_predecesores = list(self.AG_copy.predecessors(nodo_AG))

        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print("predecessors ", set_predecesores)
            print("current mapping list ", lista_salida_memoria)
            print("current final list ", lista_final)

        # if self.dict_nodes_a[nodo_AG]['name']=='t3': time.sleep(5)
        self.lista_nodos_copy = []
        self.lista_nodos_copy_time = []
        self.lista_en_time_slots = False
        self.lugar_time_slot = None
        vector_predecesores_verificacion = []

        # if there are predecessors
        if set_predecesores:
            # we are going to process for each predecessor
            lugar_nodo = None
            vector_predecesores_verificacion = []
            bandera_no_esta_en_el_mismo_time_slot = False
            for predecesor in set_predecesores:
                if self.s_prints == 'heudebug':
                    print(f"we are going to check the predecessor {predecesor}")

                lugar_nodo = None
                # we are going to search for the predecessor in the current mapping list
                for elemento_lista in range(0, len(lista_salida_memoria)):
                    if predecesor == lista_salida_memoria[elemento_lista][1]:
                        lugar_nodo = elemento_lista
                # if we could not find the predecessor in the current mapping list we are going to check the
                # previous time slots
                numero_time_slot = 0
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
                if self.s_prints == 'heudebug':
                    print("The predecessor place is  ", lugar_nodo ,bandera_recomputo)

                # now, we are going to check if there is a path from the resource where the predecessor is mapped,
                # there are two cases, if the predecessor is mapped to the current mapping list or to another time slot
                vector_verificacion_no_mapeo_01 = []  ######for each node
                vector_verificacion_no_mapeo_02 = []  ######for each path

                if not bandera_no_esta_en_el_mismo_time_slot and not bandera_recomputo:
                    # if the predecessor is mapped to the current list but the recomputation flag is not enabled
                    # we find a path from the place where the predecessor is mapped to the resource
                    simple_path = simple_paths_from_two_nodes(copia_DG,
                                                              lugar_nodo,
                                                              recurso_elegido)

                    # if there are paths
                    if simple_path:
                        # we check if there is a path  available
                        while simple_path:
                            # we start with the shortest path and make a copy of it
                            path_b = min(simple_path, key=len)
                            paths_copy = simple_path.copy()
                            # we remove that path from the list of paths
                            for i in range(0, len(paths_copy)):
                                if paths_copy[i] == path_b:
                                    dummy = simple_path.pop(i)
                            path = list(path_b)
                            if lugar_nodo in path:
                                path.remove(lugar_nodo)
                            bandera_salida = False
                            vector_verificacion_no_mapeo_01 = []
                            # now we prune the path
                            path_buffer = list(path)
                            if recurso_elegido in path_buffer:
                                path_buffer.remove(recurso_elegido)
                            vector_dependency_01 = []
                            # now we check the resources in the path if there are occupied or not
                            for node in path:
                                if lista_salida_memoria[node][0]:  # and self.lista_mapping[node][2] != 'copy':#
                                    vector_dependency_01 = vector_dependency_01 + [lista_salida_memoria[node][0]]
                            # if there is any resource occupied we put a indicator of it in the verification list
                            if True in vector_dependency_01:
                                vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                            else:
                                # if there is no resource ocuppied we put an indicator of it to the verification list,
                                # also we add the resources in the path to the list of copy nodes of the current
                                # mapping list and we break the cycle
                                vector_verificacion_no_mapeo_02= vector_verificacion_no_mapeo_02 + [True]
                                self.lista_nodos_copy = self.lista_nodos_copy + path_buffer  #
                                bandera_salida = True
                            if bandera_salida:
                                break

                        # if self.s_prints == 'heudebug':
                        #     print(vector_verificacion_no_mapeo_02)
                        # because we break the cycle it means that the found a good path
                        if True in vector_verificacion_no_mapeo_02:
                            vector_predecesores_verificacion.append(True)
                    else:
                        # if self.s_prints == 'heudebug':
                        #     print("tenemos un buggazo aqui", simple_path)
                        # if there is no path it means that there is an error
                        # todo verify this part
                        vector_predecesores_verificacion.append(False)

                else:
                    # if the predecessor is in the same time slot but the recomputation flag is enabled, this means
                    # that the predecessor is mapped to a different datapath

                    if self.s_prints == 'heudebug':
                        print("we are in the case where the predecessor is mapped to a different datapath")

                    # to verify the recomputation flag
                    if bandera_recomputo:
                        # in this case we need to obtain a valid sink and a valid source, also we will generate the
                        # information for a special node of the recomputation type
                        bandera_es_sink = False
                        bandera_es_source = False
                        # if the place of the predecessor is a valid sink we keep that place if not we need
                        # to obtain a valid sink
                        if lugar_nodo in self.list_sinks_connected_to_rc:
                            bandera_es_sink = True
                        else:
                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                            done = True
                            counter_internal = 0
                            while done:
                                if copy_list_sinks_connected_to_rc:
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
                                if lista_salida_memoria[sink_nodo_sink_task][0]:
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
                            # now we have a valid sink
                            sink = sink_nodo_sink_task
                            # we obtain a simple path from the place of the predecessor to a valid sink
                            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                                      lugar_nodo,
                                                                      sink)
                            vector_verificacion_no_mapeo_01 = []  ######for each node
                            vector_verificacion_no_mapeo_02 = []  ######for each path
                            # if there are valid paths we check if there is one that we can use
                            if simple_path:
                                # the same process, we check the path to see if there is any mapped resource, if there
                                # is we discard that path
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
                                        # we add the resources of the path to the list of copy nodes
                                        self.lista_nodos_copy = self.lista_nodos_copy + path_buffer  #
                                        bandera_salida = True
                                    if bandera_salida:
                                        break
                                # if everything is ok we enable the valid sink flag
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_sink = True
                        # now, we move to the resource, we need to know if it is a valid source, if not we find a
                        # valid source
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
                                            # we add the resources of the path to the list of copy nodes
                                            self.lista_nodos_copy = self.lista_nodos_copy + unique_path
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_source = True
                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("the flags are", bandera_es_source, bandera_es_sink, recurso_elegido)
                        # if everything is ok we append the list with a true, a false in this list means that we will
                        # discard the resource
                        if bandera_es_source and bandera_es_sink:
                            vector_predecesores_verificacion.append(True)
                    else:
                        # now, the predecessor is not mapped to the same time slot
                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("the predecessor is mapped to a different time slot", numero_time_slot)
                        # we enable the flags related to different time slots
                        self.lista_en_time_slots = True
                        self.lugar_time_slot = numero_time_slot
                        # print("la tarea se mapeo en otro time slot",numero_time_slot)
                        time_slot_buffer = lista_final[numero_time_slot]
                        if self.s_prints == 'heudebug':
                            print("info of the predecessor, time slot", numero_time_slot, " data ", time_slot_buffer)
                        # we will find if the predecessors place is a valid sink
                        bandera_es_sink = False
                        bandera_es_source = False
                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            # if self.dict_nodes_a[nodo_AG]['name'] == 't3': time.sleep(5)
                            print("the elements that we are going to check ", lugar_nodo, recurso_elegido)

                        # we verify the condition of the sink, if it is in a valid sink everything is ok, if not we
                        # need to find one
                        if lugar_nodo in self.list_sinks_connected_to_rc:
                            bandera_es_sink = True
                        else:
                            # we will find a valid sink resource
                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                            done = True
                            counter_internal = 0
                            while done:
                                if copy_list_sinks_connected_to_rc:
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
                                if time_slot_buffer[sink_nodo_sink_task][0]:
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
                            # now we've found a valid sink
                            sink = sink_nodo_sink_task
                            # we find a simple path between the place of the predecessor and the valid sink
                            simple_path = simple_paths_from_two_nodes(self.DG_original,
                                                                      lugar_nodo,
                                                                      sink)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            # the same process, we iterate over the simple paths in order to find one available
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
                                    for node in path:
                                        if time_slot_buffer[node][0]:  # and self.lista_mapping[node][2] != 'copy':#

                                            vector_dependency_01 = vector_dependency_01 + [
                                                lista_salida_memoria[node][0]]
                                    if True in vector_dependency_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [False]
                                    else:  #
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [True]
                                        # we add the resources to the copy nodes in time slot list
                                        self.lista_nodos_copy_time = self.lista_nodos_copy_time + path_buffer  #
                                        bandera_salida = True
                                    if bandera_salida:
                                        break
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_sink = True
                        ### this is the part of the source, we need to verify if the resource is a valid source or
                        # we need to find one
                        if recurso_elegido in self.lista_sources_DG:
                            bandera_es_source = True
                        else:
                            # the resource is not a valid source, so we need to find a good one, its the same
                            # process as the sinks
                            source = source_node_from_any_node(copia_DG,
                                                               self.lista_sources_DG,
                                                               recurso_elegido)
                            simple_path = simple_paths_from_two_nodes(self.DG_copy,
                                                                      source,
                                                                      recurso_elegido)
                            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                                print("simple paths ", simple_path)
                                print(time_slot_buffer)
                            vector_verificacion_no_mapeo_01 = []  ######por cada nodo
                            vector_verificacion_no_mapeo_02 = []  ######por cada path
                            if simple_path:
                                for unique_path in simple_path:
                                    unique_path_buffer = list(unique_path)
                                    unique_path_buffer.remove(recurso_elegido)
                                    if self.s_prints == 'heudebug':
                                        print(f"we will add this path {unique_path_buffer} to the copy list {self.lista_nodos_copy}")
                                    vector_verificacion_no_mapeo_01 = []
                                    for nodo_in_unique in unique_path:

                                        vector_verificacion_no_mapeo_01 = vector_verificacion_no_mapeo_01 + [
                                            lista_salida_memoria[nodo_in_unique][0]]
                                    if not True in vector_verificacion_no_mapeo_01:
                                        vector_verificacion_no_mapeo_02 = vector_verificacion_no_mapeo_02 + [
                                            True]
                                        # we add the copy nodes to the list
                                        self.lista_nodos_copy = unique_path_buffer + self.lista_nodos_copy
                                        self.lista_en_time_slots = True
                                if True in vector_verificacion_no_mapeo_02:
                                    bandera_es_source = True
                        # print(f"las banderas sink {bandera_es_sink} source {bandera_es_source}")
                        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                            print("the flags in the case of different time slots (sink,source) ", bandera_es_sink, bandera_es_source)
                        if bandera_es_source and bandera_es_sink:
                            # bandera_mapping_valido = True
                            vector_predecesores_verificacion.append(True)
            # we update the final flags

            if False in vector_predecesores_verificacion:
                bandera_mapping_valido = False
            else:
                bandera_mapping_valido = True



        else:
            # because there is no predecessor, we need to only verify that the resource is a valid source or there
            # is a path available that connects a valid source to the resource
            if recurso_elegido in self.lista_sources_DG:
                bandera_mapping_valido = True
            else:
                # because the resource is not a valid source we need to find a valid source that connects to the resource
                # in here we dont need to add copy nodes because that process is done in another function
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
        if self.s_prints == 'heudebug':
            if bandera_mapping_valido:
                print("the verification of data dependence is valid ",vector_predecesores_verificacion)
            else:
                print("the node can not be mapped",vector_predecesores_verificacion)
        return bandera_mapping_valido

    def reinicio_time_slot(self, lista_salida_memoria, lista_final, copia_DG, vector_buffer_especiales,
                           vector_nodos_especiales, bandera_caso_no_probabilidad):
        """this function creates a time slot, also generates some information about the special nodes because we find
        if there are not mapped tasks that are the successors of the mapped tasks"""
        if self.s_prints == 'heuiter' or self.s_prints == 'heudebug':
            print("------------------------------------------------------------")
            print("Creation of a time slot")
            print("------------------------------------------------------------")

        if self.s_pause and self.s_prints == 'heudebug':
            input("Press Enter to continue...")
        self.counter = 0
        if self.s_prints == 'debug':
            print(vector_nodos_especiales)
        lista_nodos_mapeados = []
        # we gather all the mapped tasks
        for elemento in lista_salida_memoria:
            if elemento[0]:
                if elemento[1] != None:
                    lista_nodos_mapeados.append(elemento[1])
        # we are going to created the list that help us to add the special nodes (dependency type)
        lista_parejas = []
        lista_nodos_ag = list(self.AG_copy.nodes)
        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print(f"the list of tasks is {lista_nodos_ag} and the list of mapped nodes is {lista_nodos_mapeados}")
        # first we prune the list, because a copy node will appear as mapped but the task is None
        for elemento in lista_nodos_mapeados:
            if elemento == None:
                pass
            else:
                lista_nodos_ag.remove(elemento)
        if self.s_prints == 'heudebug':
            print("the pruned list is ", lista_nodos_ag)
        # now we will check if there is a connection of any mapped node to one not mapped
        for nodo in lista_nodos_mapeados:
            if nodo == None:
                pass
            else:
                for elemento in lista_nodos_ag:
                    path_time = list(nx.all_simple_paths(self.AG_copy, source=nodo, target=elemento, cutoff=1))
                    if path_time:
                        # because there is a path to this not mapped node we add an element to the couples list, which
                        # is the mapped node and the non mapped node which has a connection to the mapped one
                        lista_parejas.append([nodo, elemento])

        nuevo_vector_parejas = []
        contador = 0
        vector_buffer_pareja = []
        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print("now we have a list of couples", lista_parejas, self.datapaths_independientes)
        # now will go through the list to find valid data, in the sense that we need to find a valid sink,
        # the source will be found during the data dependence verification, the idea behind is that we dont know where
        # we are going to map the successor
        for parejas in lista_parejas:
            for elemento in range(0, len(lista_salida_memoria)):
                if parejas[0] == lista_salida_memoria[elemento][1]:
                    # todo verify this part of the function
                    copy_lista_sinks_rc = self.list_sinks_connected_to_rc.copy()
                    copy_lista_sinks_rc.reverse()
                    if elemento in copy_lista_sinks_rc:
                        sink = elemento
                        vector_buffer_pareja.append([parejas[1], sink, False])
                    else:
                        sink = sink_node_from_any_node(self.DG_original,copy_lista_sinks_rc,elemento)
                        vector_buffer_pareja.append([parejas[1], sink, False])

        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print("the element that we are going to add", vector_buffer_pareja)
        # we add the element to the global variable, this is used in the data dependence function
        self.vector_de_parejas_memoria = vector_buffer_pareja
        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print("now we are going to finish adding the time slot")
            print(f"the list of couples is {self.vector_de_parejas_memoria}")
            print("the current list is ", lista_salida_memoria)
        # we add the current mapping list to the final mapping list
        lista_final.append(lista_salida_memoria)
        if self.s_prints == 'heudebug':
            print("there is a bug that does not allow us to update the resources list ", list(copia_DG.nodes))
        # before we reinitialize the current mapping list we gather again the nodes that are available or
        # with a copy operation
        self.lista_nodos_time_slot_anterior = []
        for nodo in range(0,len(lista_salida_memoria)):
            if not lista_salida_memoria[nodo][0]:
                self.lista_nodos_time_slot_anterior.append(nodo)
            elif lista_salida_memoria[nodo][0] and lista_salida_memoria[nodo][2] == 'copy':
                self.lista_nodos_time_slot_anterior.append(nodo)
        # reinitialize the current mapping list
        lista_salida_memoria = [[False, -1, -1, -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] for g in range(len(copia_DG))]
        # make a new copy of the hardware graph, we obtain the possible candidates and we enable the flag of first time
        self.DG_copy = copia_DG.copy()
        primer_grupo = obtencion_sources(self.DG_copy)
        bandera_primer_nodo = True
        # we append the variable of special nodes
        # todo verify the use of this variable
        vector_buffer_especiales.append(vector_nodos_especiales)
        vector_nodos_especiales = []
        # indicate that we are going to return from the creation of time slot function
        bandera_reinicio = True
        self.contador_instancias = self.contador_instancias + len(self.DG_copy.nodes)
        if self.s_prints == 'heudebug':
            print("a new time slot was created")
            print("the possible candidates are", primer_grupo)
        bandera_caso_no_probabilidad = False
        return bandera_reinicio, bandera_primer_nodo, primer_grupo, lista_salida_memoria, lista_final, vector_buffer_especiales, vector_nodos_especiales, bandera_caso_no_probabilidad


    def datapaths_available(self, lista_salida_memoria):
        """this function searches for any independent datapath available
        :parameter lista_salida_memoria is the current mapping list"""
        if self.s_prints == 'heudebug':
            print("We are going to verify if there are datapaths available")
        vector_01 = []
        bandera_recomputo = False
        datapath_available = []
        # we are going check if any of the independent datapaths is available
        for simple_path in self.datapaths_independientes:
            # print(simple_path)
            vector_01 = []
            # for each node in the path
            for nodo in simple_path:
                # print(lista_salida_memoria[nodo][0])
                # we check if it is used
                vector_01 = vector_01 + [lista_salida_memoria[nodo][0]]
            # print(vector_01)
            # if there is no used resource in the datapath we added to a list with resources available
            if not True in vector_01:
                datapath_available = datapath_available + simple_path
        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print("test inside the verification of datapaths")
            print(self.lista_AG_copy + [self.tarea_a_mapear_global])
            print(self.lista_nodos_ya_mapeados)
        # lista_predecesores_01 = []
        # now we need to find if we need to add special nodes, in other words if there is a task mapped in the
        # datapaths ocuppied that have a successor not mapped
        for nodos_restante in self.lista_AG_copy + [self.tarea_a_mapear_global]:
            # we obtain the non mapped taks and obtain their predecessors
            predecesores = self.AG_original.predecessors(nodos_restante)
            # if there are predecessors
            if list(predecesores):
                if self.s_prints == 'heudebug':
                    print(f"the predecessors {nodos_restante} are {list(self.AG_original.predecessors(nodos_restante))}")
                    print(f"and the list is {lista_salida_memoria}")
                # for each predecessor
                for predecesor in self.AG_original.predecessors(nodos_restante):
                    # print("kjdkfnskfsdfsd")
                    # if the predecessor is already mapped
                    if predecesor in self.lista_nodos_ya_mapeados:
                        # if the predecessor is mapped in the current mapping list, this means that they
                        # are in a different datapath, and we need to find where it is
                        for elemento in range(0, len(lista_salida_memoria)):
                            if lista_salida_memoria[elemento][1] == predecesor:
                                lugar_nodo = elemento
                        # so now we have the place where the predecessor is mapped, now we verify if there will be
                        # an iteration with datapath availables
                        ####nodo restante es el nodo que no se ha mapeado, predecesor es su predecesor que ya se mapeo
                        #### y el lugar_nodo es donde se mapeo, con respecto al grafo de hardware, el ultimo elemento es
                        ####para identificar si es nodo de recomputo (False) o nodo entre time slots (True)
                        if datapath_available:
                            # now we create a temporal variable with the non mapped task, the already mapped
                            # predecessor, the place where that mapped task is, and the indicator of type of
                            # special node (False)
                            buffer_predecesor = [nodos_restante, predecesor, lugar_nodo, False]
                            # now we add it to the list, this list is used in other functions
                            self.lista_predecesores_01.append(buffer_predecesor)
        if self.s_prints == 'debug' or self.s_prints == 'heudebug':
            print(f"the list of predecessors mapped on another datapath is {self.lista_predecesores_01}")

        # we have datapaths available we enable the flag of recomputation, this will help us to know it
        if datapath_available:
            if self.s_prints == 'debug' or self.s_prints == 'heudebug':
                print(f"we still have datapaths {datapath_available}")
            bandera_recomputo = True

        return (datapath_available, bandera_recomputo)
