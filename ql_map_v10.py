import numpy as np
import networkx as nx
import random
import time
from itertools import combinations_with_replacement, permutations
import argparse
import math
import pickle
import GraphVisualization
from basic_functions import simple_paths_from_two_nodes, obtencion_sources, \
    source_node_from_any_node, sink_node_from_any_node, obtencion_sinks, sources_nodes_of_a_graph,obtencion_sucesores
from datetime import datetime
import os
from PerfoEval_v10 import performance_evaluation
import PerfoEval_v10 as PerfoEval_v10




class GraphGenerationTraining:

    def __init__(self, DG, dict_nodes_h, dict_info_h, DG_total, dict_total_h, directorio, number_app=10,
                 numero_serial=3, numero_paralelo=2, nodos_a_remover=1,
                 list_resolutions=None, selection_prints=None, maximo_output_degree=1, maximo_input_degree=1):
        # print(filepath)
        ########generacion del folder para los archivos de salida
        if list_resolutions is None:
            list_resolutions = [[1, 1], [5, 5], [10, 10], [100, 100]]

        self.maximum_input_degree = maximo_input_degree
        self.maximum_output_degree = maximo_output_degree
        self.folderpath = directorio
        self.tipo = ['parallel', 'serial', 'normal']
        self.configuration_list = ['parallel', 'sequential']

        self.number_app = number_app
        self.DG = DG
        self.dict_nodes_h = dict_nodes_h
        self.dict_info_h = dict_info_h
        self.DG_total = DG_total
        self.dict_total = dict_total_h
        self.vector_operaciones_totales = []
        self.numero_serial = numero_serial  # esto debe de ir afuera
        self.numero_paralelo = numero_paralelo  # esto debe de ir afuera
        self.nodos_a_remover = nodos_a_remover
        self.resoluciones = list_resolutions
        self.error_parametros = False
        self.s_prints = selection_prints
        if self.s_prints == 'q-l':
            print(f"estamos en la funcion de generacion de aplicaciones ")

        # print(self.dict_total)
        # for n in self.DG.nodes:
        #     print(f"el nodo es {n} y la informacion es {self.DG.nodes[n]}")
        done = True
        self.hw_num = 0

        contador_aplicaciones_completas = 0
        contador = 0
        while done:
            if contador == 100:
                raise RecursionError("An application can not be created, verify the graph generator file")
            try:

                self.dict_aplicaciones = {}
                # print(f"DENTRO DEL GENERADOR PERO EN LA ETAPA DOS {self.number_app}  ")

                # for n, data in self.dict_nodes_total.items():
                #     print(n, data)
                for n in range(0, self.number_app):
                    self.dict_aplicaciones[n] = {}
                    app_completa = bool(random.getrandbits(1))
                    # app_completa = False
                    if self.s_prints == 'q-l':
                        print(f"we are going to build a complete graph {app_completa}")
                    # print(f"we are going to build a complete graph {app_completa}")
                    if app_completa:
                        contador_aplicaciones_completas = contador_aplicaciones_completas + 1
                        self.app_generator_total()
                    else:
                        self.app_generator()
                    self.dict_aplicaciones[n]['graph'] = self.AG_origen
                    self.dict_aplicaciones[n]['graph_total'] = self.AG_total

                    self.dict_aplicaciones[n]['dict_app'] = self.dict_aplicacion
                    self.dict_aplicaciones[n]['dict_app_total'] = self.dict_aplicacion_total
                    # print("jbsdsd")
                    # print(self.dict_aplicacion_total)
                    nombre_archivo_app = self.generator_config_file_app(n)
                    self.dict_aplicaciones[n]['nombre_archivo'] = nombre_archivo_app
                if self.dict_aplicacion and self.dict_aplicacion_total:
                    done = False
            except:
                pass
            contador = contador + 1
        # print("test")
        if self.s_prints == 'q-l':
            print(f" el numero de aplicaciones completas es {contador_aplicaciones_completas}")
        # time.sleep(5)

    def app_generator_total(self):

        self.AG_origen = self.DG.copy()

        total_actuators = obtencion_sinks(self.DG)
        total_sensors = obtencion_sources(self.DG)

        seleccion_tipo = random.choice(self.tipo)
        # print(f"inicio de modulo de generacion de grafos seriales la seleccion es {seleccion_tipo}")

        numero_nodos = len(self.AG_origen.nodes)
        vector_sources_usadas = []

        # self.AG_origen = nx.disjoint_union(self.AG_copia,self.AG_copia)
        self.AG_copia = self.AG_origen.copy()

        seleccion_tipo = None

        if seleccion_tipo == 'serial':
            for i in range(0, self.numero_serial - 1):
                self.AG_origen = nx.disjoint_union(self.AG_origen, self.AG_copia)
                sources = obtencion_sources(self.AG_origen)
                sinks = obtencion_sinks(self.AG_origen)
                primer_grupo_sinks = []
                segundo_grupo_sources = []
                for so in sources:
                    if so > numero_nodos:
                        segundo_grupo_sources.append(so)
                for si in sinks:
                    if si < numero_nodos:
                        primer_grupo_sinks.append(si)
                for sink in primer_grupo_sinks:
                    try:
                        source = segundo_grupo_sources.pop()
                        self.AG_origen.add_edge(sink, source)
                    except:
                        pass
                numero_nodos = len(self.AG_origen.nodes)

        elif seleccion_tipo == 'parallel':
            for i in range(0, self.numero_paralelo - 1):
                self.AG_origen = nx.disjoint_union(self.AG_origen, self.AG_copia)

        dict_app = {}

        #### ahora generaremos la informacion real
        for nodo in self.AG_origen.nodes:
            nombre_hardware = self.AG_origen.nodes[nodo]['name']
            lugar_nodo = None
            for n, data in self.dict_total.items():
                if data['name'] == nombre_hardware:
                    lugar_nodo = n

            dict_app[nodo] = {}
            dict_app[nodo]['name'] = 't' + str(nodo)
            self.AG_origen.nodes[nodo]['name'] = 't' + str(nodo)

            vector_operaciones = self.AG_origen.nodes[nodo]['op']
            tareas_posibles = []
            for operacion in vector_operaciones:
                if operacion != 'copy' and operacion != 'disable':
                    tareas_posibles.append(operacion)

            tarea = random.choice(tareas_posibles)

            lugar = None
            dict_app[nodo]['op'] = tarea
            self.AG_origen.nodes[nodo]['op'] = tarea
            sucesores = list(self.AG_origen.successors(nodo))
            vector_edges = []
            for suc in sucesores:
                nombre_edge = 't' + str(suc)
                vector_edges.append(nombre_edge)
            dict_app[nodo]['edges'] = vector_edges
            dict_app[nodo]['param'] = {}

            if self.dict_total[lugar_nodo]['ops'][tarea]['param'] == None:
                # print("entro aqui")
                dict_app[nodo]['param'] = None
                self.AG_origen.nodes[nodo]['par'] = None
            else:
                # print("termino de debug")
                lista_parametros = self.dict_total[lugar_nodo]['ops'][tarea]['param']
                # print(lista_parametros)
                vector_parametros = []
                for parametro in lista_parametros:
                    # print(f"el parametro es {parametro}")

                    if self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro] == 'boolean':
                        vector_boolean = [True, False]
                        valor = random.choice(vector_boolean)
                        dict_app[nodo]['param'][parametro] = valor
                        temp = [parametro, valor]
                        # print("entro aqui", temp)
                        vector_parametros.append(temp)

                    else:
                        # print("test")
                        # print(self.dict_total[nodo]['ops'][tarea]['param'][parametro])
                        if len(self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]) == 1:
                            dict_app[nodo][parametro] = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                            temp = [parametro, self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]]
                            vector_parametros.append(temp)
                        elif len(self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]) == 2:
                            try:
                                item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                                rango = random.randint(item[0], item[1])
                                dict_app[nodo]['param'][parametro] = rango
                                temporal_parametros = [parametro, rango]
                                vector_parametros.append(temporal_parametros)
                            except:
                                item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                                opcion = random.choice(item)
                                dict_app[nodo]['param'][parametro] = opcion
                                temp = [parametro, opcion]
                                vector_parametros.append(temp)

                        else:
                            item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                            opcion = random.choice(item)
                            dict_app[nodo]['param'][parametro] = opcion
                            temp = [parametro, opcion]
                            vector_parametros.append(temp)
                self.AG_origen.nodes[nodo]['par'] = vector_parametros
            try:
                self.AG_origen.nodes[nodo].pop('map')
                self.AG_origen.nodes[nodo].pop('lat')
            except:
                pass
        #### agregaremos los actuadores y sensores

        dict_app_total = dict_app.copy()
        self.AG_total = self.AG_origen.copy()
        sources = obtencion_sources(self.AG_total)
        sinks = obtencion_sinks(self.AG_total)
        # print(f"los sources son {sources} y los siks son {sinks}")
        eleccion_resolucion = random.choice(self.resoluciones)
        if seleccion_tipo == 'normal':
            numero_nodos = len(self.DG)
        else:
            numero_nodos = len(self.AG_total) + len(self.DG)
        for source in sources:
            nombre = 'sensorapp' + str(numero_nodos)

            self.AG_total.add_edge(numero_nodos, source)
            dict_app_total[numero_nodos] = {}
            dict_app_total[numero_nodos]['name'] = nombre
            dict_app_total[numero_nodos]['op'] = 'interface'

            dict_app_total[numero_nodos]['param'] = {}
            dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
            dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
            dict_app_total[numero_nodos]['edges'] = [dict_app_total[source]['name']]
            self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri',
                                   par=dict_app_total[numero_nodos]['param'])
            numero_nodos = numero_nodos + 1
        for sink in sinks:
            nombre = 'actuatorapp' + str(numero_nodos)

            self.AG_total.add_edge(sink, numero_nodos)
            dict_app_total[numero_nodos] = {}
            dict_app_total[numero_nodos]['name'] = nombre
            dict_app_total[numero_nodos]['op'] = 'interface'
            # eleccion_resolucion = random.choice(self.resoluciones)
            dict_app_total[numero_nodos]['param'] = {}
            dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
            dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
            dict_app_total[numero_nodos]['edges'] = []
            dict_app_total[sink]['edges'] = [nombre]
            self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri',
                                   par=dict_app_total[numero_nodos]['param'])
            numero_nodos = numero_nodos + 1

        self.dict_aplicacion_total = dict_app_total
        self.dict_aplicacion = dict_app
        if self.s_prints == 'q-l':
            print(dict_app_total)

    def app_generator(self):

        self.AG_origen = self.DG.copy()
        # nodo_random = random.choice([1,2,3])
        # self.nodos_a_remover = nodo_random
        nodos_arquitectura = []
        for task in self.AG_origen.nodes:
            if self.AG_origen.in_degree(task) != 0 and self.AG_origen.out_degree(task) != 0:
                nodos_arquitectura.append(task)
        # nodos_arquitectura = list(self.AG_origen.nodes)
        # print("test 01")
        for n in range(0, self.nodos_a_remover):

            # print(nodos_arquitectura)
            contador_intentos = 0
            valid_node = True
            while valid_node:
                # print(contador_intentos)
                if contador_intentos > self.nodos_a_remover * 5:
                    break
                nodo_a_remover = random.choice(nodos_arquitectura)
                nodos_arquitectura.remove(nodo_a_remover)
                predecesores = self.AG_origen.predecessors(nodo_a_remover)
                sucesores = self.AG_origen.successors(nodo_a_remover)
                prede_valid = True
                suce_valid = True
                # print("nodo",nodo_a_remover)
                for pre in predecesores:
                    # print(self.DG.out_degree(pre))
                    if self.DG.out_degree(pre) > self.maximum_output_degree:
                        prede_valid = False
                        break
                for suc in sucesores:
                    if self.DG.in_degree(suc) > self.maximum_input_degree:
                        suce_valid = False
                        break
                # print(prede_valid,suce_valid,self.DG.in_degree(nodo_a_remover),self.DG.out_degree(
                #         nodo_a_remover))
                if self.DG.in_degree(nodo_a_remover) != 0 and self.DG.out_degree(
                        nodo_a_remover) != 0 and suce_valid and prede_valid:
                    # if self.DG.in_degree(nodo_a_remover) == 1 and self.DG.out_degree(nodo_a_remover) == 1:
                    valid_node = False
                    break
                contador_intentos = contador_intentos + 1
            # print(nodo_a_remover)

            self.AG_origen.remove_node(nodo_a_remover)
            for pre in predecesores:
                for suc in sucesores:
                    self.AG_origen.add_edge(pre, suc)

        total_actuators = obtencion_sinks(self.DG)
        total_sensors = obtencion_sources(self.DG)

        seleccion_tipo = random.choice(self.tipo)
        # print(f"inicio de modulo de generacion de grafos seriales la seleccion es {seleccion_tipo}")
        # print("test 02")
        numero_nodos = len(self.AG_origen.nodes)
        vector_sources_usadas = []

        # self.AG_origen = nx.disjoint_union(self.AG_copia,self.AG_copia)
        self.AG_copia = self.AG_origen.copy()
        seleccion_tipo = random.choice(['serial', 'parallel'])
        # seleccion_tipo =  None
        # print("test 03")
        if seleccion_tipo == 'serial':
            for i in range(0, self.numero_serial - 1):
                self.AG_origen = nx.disjoint_union(self.AG_origen, self.AG_copia)
                sources = obtencion_sources(self.AG_origen)
                sinks = obtencion_sinks(self.AG_origen)
                primer_grupo_sinks = []
                segundo_grupo_sources = []
                for so in sources:
                    if so > numero_nodos:
                        segundo_grupo_sources.append(so)
                for si in sinks:
                    if si < numero_nodos:
                        primer_grupo_sinks.append(si)
                for sink in primer_grupo_sinks:
                    try:
                        source = segundo_grupo_sources.pop()
                        self.AG_origen.add_edge(sink, source)
                    except:
                        pass
                numero_nodos = len(self.AG_origen.nodes)

        elif seleccion_tipo == 'parallel':
            for i in range(0, self.numero_paralelo - 1):
                self.AG_origen = nx.disjoint_union(self.AG_origen, self.AG_copia)
        # print("test 04")
        dict_app = {}

        #### ahora generaremos la informacion real
        for nodo in self.AG_origen.nodes:
            nombre_hardware = self.AG_origen.nodes[nodo]['name']
            lugar_nodo = None
            for n, data in self.dict_total.items():
                if data['name'] == nombre_hardware:
                    lugar_nodo = n

            dict_app[nodo] = {}
            dict_app[nodo]['name'] = 't' + str(nodo)
            self.AG_origen.nodes[nodo]['name'] = 't' + str(nodo)

            vector_operaciones = self.AG_origen.nodes[nodo]['op']
            tareas_posibles = []
            for operacion in vector_operaciones:
                if operacion != 'copy' and operacion != 'disable':
                    tareas_posibles.append(operacion)

            tarea = random.choice(tareas_posibles)

            lugar = None
            dict_app[nodo]['op'] = tarea
            self.AG_origen.nodes[nodo]['op'] = tarea
            sucesores = list(self.AG_origen.successors(nodo))
            vector_edges = []
            for suc in sucesores:
                nombre_edge = 't' + str(suc)
                vector_edges.append(nombre_edge)
            dict_app[nodo]['edges'] = vector_edges
            dict_app[nodo]['param'] = {}

            if self.dict_total[lugar_nodo]['ops'][tarea]['param'] == None:
                # print("entro aqui")
                dict_app[nodo]['param'] = None
                self.AG_origen.nodes[nodo]['par'] = None
            else:
                # print("termino de debug")
                lista_parametros = self.dict_total[lugar_nodo]['ops'][tarea]['param']
                # print(lista_parametros)
                vector_parametros = []
                for parametro in lista_parametros:
                    # print(f"el parametro es {parametro}")

                    if self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro] == 'boolean':
                        vector_boolean = [True, False]
                        valor = random.choice(vector_boolean)
                        dict_app[nodo]['param'][parametro] = valor
                        temp = [parametro, valor]
                        # print("entro aqui", temp)
                        vector_parametros.append(temp)

                    else:
                        # print("test")
                        # print(self.dict_total[nodo]['ops'][tarea]['param'][parametro])
                        if len(self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]) == 1:
                            dict_app[nodo][parametro] = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                            temp = [parametro, self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]]
                            vector_parametros.append(temp)
                        elif len(self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]) == 2:
                            try:
                                item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                                rango = random.randint(item[0], item[1])
                                dict_app[nodo]['param'][parametro] = rango
                                temporal_parametros = [parametro, rango]
                                vector_parametros.append(temporal_parametros)
                            except:
                                item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                                opcion = random.choice(item)
                                dict_app[nodo]['param'][parametro] = opcion
                                temp = [parametro, opcion]
                                vector_parametros.append(temp)

                        else:
                            item = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro]
                            opcion = random.choice(item)
                            dict_app[nodo]['param'][parametro] = opcion
                            temp = [parametro, opcion]
                            vector_parametros.append(temp)
                self.AG_origen.nodes[nodo]['par'] = vector_parametros
            try:
                self.AG_origen.nodes[nodo].pop('map')
                self.AG_origen.nodes[nodo].pop('lat')
            except:
                pass
        #### agregaremos los actuadores y sensores

        dict_app_total = dict_app.copy()
        self.AG_total = self.AG_origen.copy()
        sources = obtencion_sources(self.AG_total)
        sinks = obtencion_sinks(self.AG_total)
        # print(f"los sources son {sources} y los siks son {sinks}")
        eleccion_resolucion = random.choice(self.resoluciones)
        if seleccion_tipo == 'normal':
            numero_nodos = len(self.DG)
        else:
            numero_nodos = len(self.AG_total) + len(self.DG)
        for source in sources:
            nombre = 'sensorapp' + str(numero_nodos)

            self.AG_total.add_edge(numero_nodos, source)
            dict_app_total[numero_nodos] = {}
            dict_app_total[numero_nodos]['name'] = nombre
            dict_app_total[numero_nodos]['op'] = 'interface'

            dict_app_total[numero_nodos]['param'] = {}
            dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
            dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
            dict_app_total[numero_nodos]['edges'] = [dict_app_total[source]['name']]
            self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri',
                                   par=dict_app_total[numero_nodos]['param'])
            numero_nodos = numero_nodos + 1
        for sink in sinks:
            nombre = 'actuatorapp' + str(numero_nodos)

            self.AG_total.add_edge(sink, numero_nodos)
            dict_app_total[numero_nodos] = {}
            dict_app_total[numero_nodos]['name'] = nombre
            dict_app_total[numero_nodos]['op'] = 'interface'
            # eleccion_resolucion = random.choice(self.resoluciones)
            dict_app_total[numero_nodos]['param'] = {}
            dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
            dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
            dict_app_total[numero_nodos]['edges'] = []
            dict_app_total[sink]['edges'] = [nombre]
            self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri',
                                   par=dict_app_total[numero_nodos]['param'])
            numero_nodos = numero_nodos + 1
        # print("test 05")
        self.dict_aplicacion_total = dict_app_total
        self.dict_aplicacion = dict_app
        if self.s_prints == 'q-l':
            print(dict_app_total)
        # time.sleep(5)

    ######################################

    def generator_config_file_app(self, n):
        nombre = 'application' + str(n) + '-' + str(self.hw_num) + '.txt'
        with open(os.path.join(self.folderpath, nombre), 'w') as filehandle:
            filehandle.write("# APPLICATION DESCRIPTION\n")
            for n, data in self.dict_aplicacion_total.items():
                filehandle.write(data['name'])
                filehandle.write(";\n")
                filehandle.write(data['op'])
                filehandle.write(",")
                edges = ""
                primera_vez = True
                for e in data['edges']:
                    if primera_vez:
                        edges = e
                        primera_vez = False
                    else:
                        edges = edges + "," + e
                edges = "[" + edges + "]"
                filehandle.write(edges)
                filehandle.write(';\n')
                if data['param'] == None:
                    filehandle.write("[];\n")
                else:
                    filehandle.write("[")
                    primera_vez = True
                    for e in data['param']:
                        if primera_vez:
                            parametro = e + "=" + str(data['param'][e])
                            primera_vez = False
                        else:
                            parametro = "," + e + "=" + str(data['param'][e])
                        filehandle.write(parametro)
                    filehandle.write("];\n")
                filehandle.write("\n")
            filehandle.write("######----------------------------------------------END OF FILE")
        return os.path.join(self.folderpath, nombre)


class QLearning_V1:

    def __init__(self, DG, AG, dict_nodes_h,
                 dict_info_h, selection_prints, dict_nodes_a, selection_pause, dict_info_a, DG_total,
                 AG_total, dict_total_h, lista_constrains,
                 lista_tareas_constrains, name_pickle, debugging, directorio, debug_info,debugging_options,
                 selection_prints_during_perfo, DG_total_unroll,method_evaluation,iteration,folder_txt,rewards=None,
                 episodes_training=10000, start_of_decay_training = 1500, end_decay_training = 7000,
                 episodes_training_online = 10000, start_of_decay_training_online = 1500, end_decay_training_online = 7000,
                 gamma = 0.9, learning_rate=0.1,decay_gamma=0,epsilon=1.0):


        self.iteration = iteration
        self.numero_aplicaciones_training = 10
        self.DG = DG.copy()
        self.DG_copy = DG.copy()
        self.AG_app = AG
        self.AG_copy_app = AG.copy()
        self.dict_total_h = dict_total_h
        self.s_prints = selection_prints
        self.dict_nodes_a_app = dict_nodes_a
        self.selection_pause = selection_pause
        self.dict_info_a_app = dict_info_a
        self.DG_total = DG_total
        self.debug_info = debug_info
        self.AG_total_app = AG_total.copy()
        # self.AG_total = AG_total
        self.lista_constrains = lista_constrains
        self.lista_tarea_constrains = lista_tareas_constrains
        self.folder_txt = folder_txt
        self.dict_nodes_h = dict_nodes_h
        self.dict_info_h = dict_info_h
        self.debugging = debugging
        self.name_pickle = name_pickle
        self.directorio = directorio
        self.counter_online_training = 0
        self.lista_nodos_especiales = []
        self.contador_online_training = 0
        ##########local and mapping rewards percents
        if rewards != None:
            self.total_mapping_reward = rewards[0]
            self.verification_parameters_reward = rewards[1]
            self.verification_of_data_dependence_reward = rewards[2]
            self.verification_of_source_reward = rewards[3]
            self.verification_of_actuator_reward = rewards[4]
            self.latency_reward = rewards[5]
            self.verification_degree_reward = rewards[6]
            self.suc_and_prede_parameters = rewards[7]
            self.performance_evaluation_reward = rewards[8]
        else:
            self.total_mapping_reward = 0.4
            self.verification_parameters_reward = 0.75
            self.verification_of_data_dependence_reward = 0.80
            self.verification_of_source_reward = 0.10
            self.verification_of_actuator_reward = 0.10
            self.latency_reward = 0.10
            self.verification_degree_reward = 0.15
            self.suc_and_prede_parameters = 0.20
            self.performance_evaluation_reward = 0.5

        self.bandera_debug = False
        self.list_sinks_connected_to_rc = self.sinks_connected_to_rc()
        #### we use this factor to obtain the uprank and the downrank #######
        self.factor_rank = 4

        self.episodes_training = episodes_training
        self.start_of_decay_training = start_of_decay_training
        self.end_decay_training = end_decay_training
        self.episodes_training_online = episodes_training_online
        self.start_of_decay_training_online = start_of_decay_training_online
        self.end_decay_training_online = end_decay_training_online
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.decay_gamma = decay_gamma
        self.epsilon = epsilon
        self.enable_online_training = True
        #### variables for the performance evaluation during the online training
        self.debugging_options = debugging_options
        self.selection_prints_during_perfo = selection_prints_during_perfo
        self.DG_total_unroll = DG_total_unroll
        self.method_evaluation = method_evaluation
        # self.latency_matrix_result = self.latency_matrix()
        # if self.s_prints == 'q-l':
        #     print(self.latency_matrix_result)

        self.qlearning_mapping()



    def sinks_connected_to_rc(self):
        list_sinks_connected_to_rc = []
        bandera_salida = True
        for nodo in self.DG.nodes:
            # print(nodo)
            # print(self.dict_nodes[nodo])
            edges_nodo = self.dict_nodes_h[nodo]['edges']
            bandera_salida = True
            for i in edges_nodo:
                # print(f"edge {i}")
                if i:
                    for n, data in self.dict_total_h.items():
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
                if letra == '(' or letra == ')' or letra == '*' or letra == '+' or \
                        letra == '/' or letra == '-' or letra == ' ' or contador_linea == len(
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

    def obtention_computing_latency(self, resource, node_AG, dict_nodes_h, application, dict_info_h, dict_nodes_a):

        # finally we evaluate the formula with the input and store the result in the results list
        name_clk = dict_nodes_h[resource][
            'ops'][
            application.nodes[node_AG]['op']][
            'clk']

        value_clk = None
        for el in dict_info_h['functions_res']:
            if el == name_clk:
                value_clk = dict_info_h['functions_res'][el]

        # print(self.dict_info)
        # value_clk = self.dict_info['max_clk']
        if value_clk == None:
            raise UnboundLocalError(
                f"Parameter {name_clk} is not described in the functions section")
        ######ahora obtendremos el valor de la latencia de computo, debido a que puede ser una ecuacion o una
        # constante necesitamos hacer una verificacion previa y tambien sacar los valores
        # normalmente ya tenemos la ecuacion, entonces es separarla y asignar valores
        if isinstance(value_clk, str):
            # si la latencia de computacion es una ecuacion
            # print("LA LATENCIA DE COMPUTO ES UNA ECUACION")
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
            # print(f"el vector parametro es {vector_parametro}")
            for param_formula in vector_parametro:
                # print("debug de algun error",param_formula)
                if param_formula == 'width':
                    pass
                elif param_formula == 'height':
                    pass
                else:
                    # in here we are going to look the value in the dict of the nodes
                    for pa in dict_nodes_a[node_AG]['param']:
                        # print(pa)
                        if param_formula == pa:
                            globals()[pa] = dict_nodes_a[node_AG]['param'][pa]
            value_clk = eval(value_clk)
            # print("EL VALOR DE LA ECUACION ES ", value_clk)
        else:
            value_clk = value_clk

        return value_clk

    def latency_matrix(self, application, hardware, dict_nodes_a_app, dict_info_h, dict_nodes_h):
        latency_matrix = [[0 for x in range(len(hardware))] for y in range(len(application))]
        for task in application:
            # print(task)
            op = dict_nodes_a_app[task]['op']
            # print(op)
            vector_computing_latencies = [0 for x in range(len(hardware.nodes))]
            for resource in hardware:
                if op in hardware.nodes[resource]['op']:
                    value_clk = self.obtention_computing_latency(resource, task, dict_nodes_h,
                                                                 application, dict_info_h, dict_nodes_a_app)
                    vector_computing_latencies[resource] = value_clk
                else:
                    vector_computing_latencies[resource] = - self.latency_reward
            vector_without_negatives = []
            for elemento_vector in range(len(vector_computing_latencies)):
                if vector_computing_latencies[elemento_vector] > 0:
                    vector_without_negatives.append(vector_computing_latencies[elemento_vector])
            maximum_value = max(vector_without_negatives)
            minimum_value = min(vector_without_negatives)
            for elemento_vector in range(len(vector_computing_latencies)):
                if vector_computing_latencies[elemento_vector] < 0:
                    latency_matrix[task][elemento_vector] = -self.latency_reward
                else:
                    if maximum_value - minimum_value == 0:
                        latency_matrix[task][elemento_vector] = self.latency_reward
                    else:
                        latency_matrix[task][elemento_vector] = self.latency_reward * ((maximum_value -
                                                                                        vector_computing_latencies[
                                                                                            elemento_vector])
                                                                                       / (
                                                                                                   maximum_value - minimum_value))
        return latency_matrix

    def qlearning_mapping(self):

        if self.s_prints == 'q-l' or self.s_prints == 'qldebug' or self.s_prints == 'qliter':
            print("Begin of the main function of the q-learning approach")
        start_time = datetime.now()
        training_rewards_mapping = []
        training_rewards_resources = []
        now = start_time.strftime("%H:%M:%S.%f")
        if self.s_prints == 'qliter':
            print(f"Begin of the retrieve of a stored pickle or the training {now} ")
        if self.name_pickle:
            if self.s_prints == 'q-l' or self.s_prints == 'qliter':
                print(f"We are going to retrieve a previous computed q table with a name of {self.name_pickle}")
            with open(os.path.join(self.directorio, self.name_pickle), 'rb') as f:
                self.Q = pickle.load(f)
            if self.s_prints == 'q-l':
                print(f"The structure of the q table is {self.Q.shape}")

        else:

            if self.s_prints == 'q-l' or self.s_prints == 'qldebug' or self.s_prints == 'qliter':
                print(f"There is no previous computed q table, we start with the creation of training graphs, "
                      f"the number of training applications is {self.numero_aplicaciones_training} ")

            if self.debugging:
                selec_prints_generation_graphs = 'q-l'
            else:
                selec_prints_generation_graphs = None

            a = datetime.now()

            maximum_input, maximum_output, self.vector_operaciones, \
            self.dict_data_hw, vector_degree_input, vector_degree_output = self.caracteristicas_degree()

            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"degree characteristics, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            a = datetime.now()
            SetAppsForTraining = GraphGenerationTraining(self.DG, self.dict_nodes_h, self.dict_info_h, self.DG_total,
                                                         self.dict_total_h, self.directorio,
                                                         self.numero_aplicaciones_training, nodos_a_remover=1,
                                                         selection_prints=selec_prints_generation_graphs,
                                                         maximo_output_degree=maximum_output,
                                                         maximo_input_degree=maximum_input)

            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"generation of the training graphs, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            # input("test")
            if self.s_prints == 'q-l' or self.s_prints == 'qldebug':
                for nodo in self.DG.nodes:
                    print(f"el nodo es {nodo} y sus datos son {self.DG.nodes[nodo]}")
            # for nodo in self.AG.nodes:
            # input("test")
            #     print(f"task {nodo} y sus datos son {self.AG.nodes[nodo]}")
            # visualizacion de las aplicaciones de entrenamiento
            if self.debugging:
                for n in range(self.numero_aplicaciones_training):
                    nombre = 'apptraining' + str(n)
                    lista_vacia = []
                    Graph_visual_00 = GraphVisualization.GraphRep([], SetAppsForTraining.dict_aplicaciones[n]['graph'],
                                                                  lista_vacia, 'app', nombre, [], 'red', 'black',
                                                                  'circle')
                    Graph_visual_00.f.render(view=False)
                    Graph_visual_00.f.render(view=True, format='pdf')

            if self.s_prints == 'q-l':
                print("imprimiremos el vector de operaciones")
                print(self.vector_operaciones)
                print("imprimiremos el dict data hw")
                print(self.dict_data_hw)
            if maximum_input > 1 and maximum_output > 1:
                rank = int(len(self.DG) / self.factor_rank)
                self.rank = int(len(self.DG) / self.factor_rank)
            else:
                rank = len(self.DG) + 8
                self.rank = len(self.DG) + 8
            if self.s_prints == 'q-l':
                print(f"rank {rank} rank {self.rank}")
                input("impresion del rank")
            # self.dict_data_app, self.contador_pickles,contador_general = self.x_axis_generation_latest(maximum_input,maximum_output,
            #                                                 self.vector_operaciones,vector_degree_input,
            #                                                 vector_degree_output,rank)
            a = datetime.now()
            self.dict_data_app, self.contador_pickles, contador_general, self.only_i, self.only_j = self.x_axis_generation_more_recent(
                maximum_input + 0,
                maximum_output + 0,
                self.vector_operaciones,
                vector_degree_input,
                vector_degree_output,
                rank)
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"generation of the q table information, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            if self.s_prints == 'debug':
                # print(self.dict_data_app).
                print(self.only_i)
                print(self.only_j)
                # for n,item in self.dict_data_app['case'].items():
                #     print(n,item)
                #     print("")
                # input("test ...")

            # self.Q = np.array(np.zeros([contador_general, len(self.DG.nodes)]))
            self.Q = np.matrix(np.zeros([contador_general, len(self.DG.nodes)]))

            if self.s_prints == 'q-l' or self.s_prints == 'qldebug':
                print(f"The structure of the q table is {self.Q.shape}")
            # time.sleep(5)
            # hyperparameters

            gamma = self.gamma  # discount factor, ratio between rewards in a short  or long period
            # this factor will decrease during the training, near 1 prefers long period rewards, near 0 prefers
            # short period rewards
            LEARNING_RATE = self.learning_rate  # how fast the agent learns
            EPISODES = self.episodes_training
            decay_gamma = self.gamma / EPISODES
            epsilon = self.epsilon # this is the variable that controls the explotation and the exploration
            # decay_epsilon = 0
            decay_epsilon = epsilon / 4000  # (EPISODES // 2) este no se utiliza
            START_EPSILON_DECAYING = self.start_of_decay_training
            END_EPSILON_DECAYING = self.end_decay_training
            epsilon_decay_value = epsilon / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)
            # print("testst",epsilon_decay_value)
            # input("test ...")
            # we are going to start the training
            s_prints = self.s_prints
            a = datetime.now()
            self.training_rewards_mapping, self.training_rewards_resources = self.training(gamma,
                                                                                 EPISODES, LEARNING_RATE,
                                                                                 decay_gamma, epsilon, decay_epsilon,
                                                                                 START_EPSILON_DECAYING,
                                                                  END_EPSILON_DECAYING,
                                                                  epsilon_decay_value, SetAppsForTraining, s_prints)
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"End of the training, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            #
            # self.latency_matrix_result = self.latency_matrix(self.AG_app, self.DG, self.dict_nodes_a_app,
            #                                                  self.dict_info_h, self.dict_nodes_h)
            # self.training(self.AG_app, self.dict_nodes_a_app, self.AG_total_app, self.dict_info_a_app)
        if self.s_prints == 'qliter':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - start_time
            print(
                f"Begin of the mapping process, "
                f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            print()
        # input('enter ...')

        self.lista_mapping = self.mapping()
        # print(self.mapping())
        # print("regresamos del mapeo")
        if self.s_prints == 'q-l':
            print(self.lista_mapping)
            for nodo in self.DG.nodes:
                print(f"the resource is {nodo} and the data {self.DG.nodes[nodo]}")
            for nodo in self.AG.nodes:
                print(f"the task is {nodo} and the data {self.AG.nodes[nodo]}")

    def generation_datapaths(self,input_graph):
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



    def generation_special_nodes(self,lista_final):
        ### tenemos que checar bien esta funcion

        datapaths = self.generation_datapaths(self.DG)
        lista_nodos_especiales = []
        if self.s_prints == 'qldebug':
            print("entrada del la generacion de nodos especiales")
            print("la lista final es ")
            for time_slot in lista_final:
                print("the time slot")
                print(time_slot)
                # print("the resources")
                # for resource in time_slot:
                #     print(resource)
            print(f"los datapaths {datapaths} y la lista {lista_nodos_especiales}")

        for task in self.AG_copy.nodes:
            if self.s_prints == 'qldebug':
                print(f"vamos a checar tarea {task}")
            #####obtenemos el lugar de la tarea
            contador_time_slot_tarea = 0
            lugar = None
            time_slot_tarea = None
            for elemento in lista_final:
                if self.s_prints == 'qldebug':
                    print("the time slot is ")
                    print(elemento)


                for resource in elemento:
                    if self.s_prints == 'qldebug':
                        print("the resource is ")
                        print(resource)
                        print(f"estamos comparando {task} a {resource[1]}")
                    if resource[1] == task:
                        lugar = resource[2]
                        time_slot_tarea = contador_time_slot_tarea
                        break
                # if lugar == None:
                if lugar != None:
                    break
                contador_time_slot_tarea = contador_time_slot_tarea + 1
            if self.s_prints == 'qldebug':
                print("seguimos checando la tarea 01", lugar, "el time slot ", time_slot_tarea)
            #####busquemos el source mas cercano de la tarea
            lugar_tarea = lugar
            self.sources_DG = obtencion_sources(self.DG)
            if lugar_tarea in self.sources_DG:
                if self.s_prints == 'qldebug':
                    print("bug")
                source_node_tarea = lugar_tarea
            else:
                source_node_tarea = source_node_from_any_node(self.DG,self.sources_DG,lugar_tarea)
            if self.s_prints == 'qldebug':
                print("seguimos checando la tarea 02")
            #####obtenemos el lugar de su predecesor y si se necesita crear un nodo especial se anade
            predecesores = self.AG_copy.predecessors(task)
            contador_special_nodes = 0
            for pre in predecesores:
                lugar = None
                time_slot_predecesor = None
                contador_time_slot_predecesor = 0
                if self.s_prints == 'qldebug':
                    print(f"vamos a checar el predecesor {pre}")
                for elemento in lista_final:
                    for resource in elemento:
                        if resource[1] == pre:
                            ####hemos encontrado el lugar del predecesor
                            ####tenemos que averiguar si el predecesor esta en el mismo time slot
                            if contador_time_slot_predecesor != time_slot_tarea:
                                ###la tarea no esta en el mismo time slot, entonces incluiremos un nodo especial
                                if resource[2] in self.list_sinks_connected_to_rc:
                                    sink_node_prede = resource[2]
                                else:
                                    try:
                                        distancia = 100000
                                        distancia_buffer = 1000000
                                        for sink_rc in self.list_sinks_connected_to_rc:
                                            if sink_rc in self.DG.successors(resource[2]):
                                                sink_node_prede = sink_rc
                                                break
                                            else:
                                                paths = simple_paths_from_two_nodes(self.DG,resource[2],sink_rc)
                                                if paths:
                                                    for pth in paths:
                                                        if len(pth) < distancia_buffer:
                                                            distancia_buffer = len(pth)
                                                if distancia_buffer < distancia:
                                                    sink_node_prede = sink_rc
                                    except:
                                        sink_node_prede = sink_node_from_any_node(self.DG,self.list_sinks_connected_to_rc,resource[2])
                                nodo_especial_a_anexar = [True,source_node_tarea,sink_node_prede,
                                                          contador_time_slot_tarea,task]
                                lista_nodos_especiales.append(nodo_especial_a_anexar)
                                contador_special_nodes = contador_special_nodes + 1
                            else:
                                path_lugar_tarea_a_prede = simple_paths_from_two_nodes(self.DG,resource[2],lugar_tarea)
                                if path_lugar_tarea_a_prede:
                                    pass
                                else:
                                    for path in datapaths:
                                        if lugar_tarea in path:
                                            if resource[2] not in path:
                                                path_recurso = []
                                                for path_buffer in datapaths:
                                                    if resource[2] in path_buffer:
                                                        path_recurso = path_buffer
                                                        break
                                                if resource[2] in self.list_sinks_connected_to_rc:
                                                    sink_node_prede = resource[2]
                                                else:
                                                    try:
                                                        distancia = 100000
                                                        distancia_buffer = 1000000
                                                        for sink_rc in self.list_sinks_connected_to_rc:

                                                            if sink_rc in self.DG.successors(resource[2]):
                                                                sink_node_prede = sink_rc
                                                                break
                                                            else:
                                                                if sink_rc in path_recurso:
                                                                    paths = simple_paths_from_two_nodes(self.DG, resource[2],
                                                                                                        sink_rc)
                                                                    if paths:
                                                                        for pth in paths:
                                                                            if len(pth) < distancia_buffer:
                                                                                distancia_buffer = len(pth)
                                                                    if distancia_buffer < distancia:
                                                                        sink_node_prede = sink_rc
                                                    except:
                                                        sink_node_prede = sink_node_from_any_node(self.DG,
                                                                                                  self.list_sinks_connected_to_rc,
                                                                                                  resource[2])





                                                # if resource[2] in self.sinks_DG:
                                                #     sink_node_prede = resource[2]
                                                # else:
                                                #     sink_node_prede = sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc,
                                                #                                           resource[2])
                                                # break
                                                nodo_especial_a_anexar = [False, sink_node_prede,source_node_tarea,
                                                                          contador_time_slot_tarea,task]
                                                lista_nodos_especiales.append(nodo_especial_a_anexar)
                                                contador_special_nodes = contador_special_nodes + 1

                    contador_time_slot_predecesor = contador_time_slot_predecesor + 1


        # print(lista_nodos_especiales)
        # input("Salida de los nodos especiales")






        # lista_nodos_especiales = []
        return lista_nodos_especiales


    def mapping(self):
        if self.s_prints == 'qliter':
            print("We are going to start the mapping process")
        # lista_total = []

        # lista_mapping = [[False, False, False] for n in range(0, len(self.DG.nodes))]
        self.AG = self.AG_app
        self.AG_copy = self.AG
        self.dict_nodes_a = self.dict_nodes_a_app
        self.dict_info_a = self.dict_info_a_app
        self.AG_total = self.AG_total_app
        copy_AG = self.AG.copy()
        copy_DG = self.DG.copy()

        self.total_reward_mapping = []
        self.total_reward_resources = []
        if self.s_prints == 'q-l':
            for nodo in copy_DG.nodes:
                print(nodo, copy_DG.nodes[nodo])
            for nodo in copy_AG.nodes:
                print(nodo, copy_AG.nodes[nodo])

            print(f"iniciaremos la creacion de la lista de estados")
        lista_entrada = self.creacion_lista_estados(copy_AG, self.vector_operaciones, self.dict_data_app, self.only_i,
                                                    self.only_j)
        state_visits = []
        self.latency_matrix_result = self.latency_matrix(self.AG, self.DG, self.dict_nodes_a,
                                                         self.dict_info_h, self.dict_nodes_h)
        for caso in lista_entrada:
            state_visits.append(not np.any(self.Q[caso[1],]))
        # print(any(state_visits))
        # input("estamos debugeando algo ")
        if any(state_visits) or self.enable_online_training:
            # print("test entrada online training")
            training_online_reward_mapping, training_online_reward_resources = self.training_online(self.AG_app,
                                                                                                    self.dict_nodes_a_app,
                                                                                                    self.AG_total_app,
                                                                                                    self.dict_info_a_app)
            self.total_reward_mapping.append(training_online_reward_mapping)
            self.total_reward_resources.append(training_online_reward_resources)

        # self.training_online(self.AG_app, self.dict_nodes_a_app, self.AG_total_app, self.dict_info_a_app)

        mapped_nodes = []
        if self.s_prints == 'q-l':
            print(f"finalizamos la creacion de la lista de estados iniciaremos el mapping")
        mapping = True
        fail_counter = 0
        limit_fails = 1000
        done = True

        ####sinks and sources of all the graphs, we need them during the mapping
        self.sources_AG_total = obtencion_sources(self.AG_total_app)
        self.sources_DG_total = obtencion_sources(self.DG_total)
        self.sinks_DG_total = obtencion_sinks(self.DG_total)
        self.sinks_DG = obtencion_sinks(self.DG)
        self.sinks_AG = obtencion_sinks(self.AG_app)
        self.sources_DG = obtencion_sources(self.DG)
        self.sources_AG = obtencion_sources(self.AG_app)
        self.sinks_AG_total = obtencion_sinks(self.AG_total_app)
        contador = 0
        while done:
            copy_DG = self.DG.copy()
            copy_AG = self.AG.copy()
            lista_entrada_copy = self.creacion_lista_estados(copy_AG, self.vector_operaciones, self.dict_data_app, self.only_i,
                                                    self.only_j)
            # lista_entrada_copy = lista_entrada.copy()
            try:
                # input("test 01")
                c = datetime.now()

                now = c.strftime("%H:%M:%S.%f")

                print(f"Start of the iteration {self.iteration} of the mapping, current time {now} the processing ")
                text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

                text_file.write("\nStart of the mapping " + str(
                    self.iteration) + ", current time " + now)
                text_file.close()
                lista_mapping = self.mapping_inner_cycle(copy_AG, lista_entrada_copy, copy_DG)
                # input("enteer 01")

                if lista_mapping:
                    g = datetime.now()

                    now = g.strftime("%H:%M:%S.%f")
                    d = g - c

                    print(
                        f"end of the iteration {self.iteration} of the mapping, current time {now} the processing "
                        f"time is {d.seconds} seconds "
                        f"{d.microseconds} microseconds")

                    text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

                    text_file.write(
                    "\nEnd of the iteration " + str(
                        self.iteration) + " of the mapping, current time " + now + " the processing time is " + str(
                        d.seconds) + " microseconds " + str(d.microseconds))
                    text_file.close()
                    done = False

                else:
                    if self.s_prints == 'qliter':
                        print("We are going to start another online training")
                    training_online_reward_mapping,training_online_reward_resources = self.training_online(self.AG_app,
                                                                                                           self.dict_nodes_a_app,
                                                                                                           self.AG_total_app,
                                                                                                           self.dict_info_a_app)
                    self.total_reward_mapping.append(training_online_reward_mapping)
                    self.total_reward_resources.append(training_online_reward_resources)

                    # input("salida del training sin error")
            except:
                # input("test entrada de error")
                if contador == 20:
                    raise Exception(f"Mapping error")
                else:
                    #
                    # input("entrada al error")
                    if self.s_prints == 'qliter':
                        print("We are going to start again an online training")
                    training_online_reward_mapping,training_online_reward_resources = self.training_online(self.AG_app,
                                                                                                           self.dict_nodes_a_app,
                                                                                                           self.AG_total_app,
                                                                                                           self.dict_info_a_app)
                    self.total_reward_mapping.append(training_online_reward_mapping)
                    self.total_reward_resources.append(training_online_reward_resources)
                    # input("salida del training con error")
                contador = contador + 1


        if self.s_prints == 'qliter':
            print("We finish the mapping process, we return the mapping")
        return lista_mapping

    def mapping_inner_cycle(self, copy_AG, lista_entrada, copy_DG):
        fail_counter = 0
        limit_fails = len(self.DG.nodes) + 2
        lista_total = []

        lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                         range(0, len(self.DG_copy))]
        if self.s_prints == 'qldebug':
            print("VAMOS A INICIAR EL VERDADERO MAPPING!!!!!!!!!", copy_AG.nodes)
        # input("entrada al mapeao")
        # self.s_prints = None

        for nodo_app in range(0, len(copy_AG.nodes)):
            mapping = True
            ###inicio de mapping, gathering information
            initial_state = lista_entrada.pop(0)
            caso = initial_state[1]
            fail_counter = 0
            if self.s_prints == 'qldebug':
                print(f"iniciaremos el mapeo de la tarea {nodo_app}, su caso es {caso}, "
                      f"el estado inicial es {initial_state}")


            vector_actions = self.Q[caso,]
            vector_actions = vector_actions.tolist()
            vector_actions = vector_actions[0]
            vector_actions_buffer = vector_actions.copy()
            if self.s_prints == 'qldebug':
                print("the vector actiobns buffer is ", vector_actions_buffer, max(vector_actions_buffer))
            candidatos = []
            # input("test bug")
            numero_candidatos = 10
            try:
                if self.s_prints == 'qldebug':
                    print("entrada modulo de error de seleccion de candidatos")
                for n in range(numero_candidatos):
                    # print("test 01")
                    mejor_candidato = max(vector_actions_buffer)
                    # print("test 02",mejor_candidato,vector_actions_buffer)
                    # lugar = vector_actions_buffer.index(mejor_candidato)
                    # print("test 03",vector_actions_buffer,lugar)
                    vector_actions_buffer.remove(mejor_candidato)
                    # print("test 04",vector_actions_buffer)
                    candidato = vector_actions.index(mejor_candidato)
                    candidatos.append(candidato)
            except:
                vector_actions_buffer = vector_actions.copy()
                if self.s_prints == 'qldebug':
                    print("entrada a modulo de excepcion de seleccion de candidatos",vector_actions_buffer)
                mejor_candidato = max(vector_actions_buffer)
                vector_actions_buffer.remove(mejor_candidato)
                # print("test 04",vector_actions_buffer)
                candidato = vector_actions.index(mejor_candidato)
                candidatos.append(candidato)
            # print(candidatos)
            candidatos_respaldo = candidatos.copy()
            # input("test cambios")
            if self.s_prints == 'qldebug':
                print(f"la lista de candidatos es {candidatos}")
            while mapping:
                if self.s_prints == 'qldebug':
                    print("inicio de ciclo para la tarea ", initial_state[0], "el numero de intentos es ",fail_counter)
                    print(f"a lista total tiene {len(lista_total)} time slots y es ")
                    print(lista_total)
                    print(f"la lista mappping es {lista_mapping}")
                if fail_counter > limit_fails:
                    # input("test")
                    raise Exception(f"The mapping cycle, please verify your input files")



                # lista_hardware, lista_app = self.busqueda_de_datos(0, initial_state[0], DG, app)
                #### pick of the resource
                if self.s_prints == 'qldebug':
                    print("we are going to pick the candidate from the list of candidates", candidatos)
                done_resource_picking = True
                contador_resource_picking = 0
                while done_resource_picking:
                    if candidatos:
                        if copy_DG.nodes:
                            resource_candidate = candidatos.pop(0)
                            if self.s_prints == 'qldebug':
                                print("el posible candidato es ", resource_candidate, "00",copy_DG.nodes)
                            if resource_candidate in copy_DG.nodes:
                                if self.s_prints == 'qldebug':
                                    print("el candidato si esta disponible 00")
                                action = resource_candidate
                                done_resource_picking = False
                                break
                            else:
                                if contador_resource_picking == numero_candidatos + 1:
                                    if self.s_prints == 'qldebug':
                                        print("anexo de un time slot 01")
                                        print(lista_total)
                                        print(lista_mapping)

                                    lista_total.append(lista_mapping)
                                    lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g
                                                     in
                                                     range(0, len(self.DG_copy))]
                                    copy_DG = self.DG.copy()
                                    action = candidatos_respaldo[0]
                                    if self.s_prints == 'qldebug':
                                        print("el posible candidato es ", action, "05", copy_DG.nodes)
                                        print(lista_total)
                                    done_resource_picking = False
                                    break
                                else:
                                    contador_resource_picking = contador_resource_picking + 1
                        else:
                            if self.s_prints == 'qldebug':
                                print("anexo de un time slot 02")
                            lista_total.append(lista_mapping)
                            lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                             range(0, len(self.DG_copy))]
                            copy_DG = self.DG.copy()
                            action = candidatos_respaldo[0]
                            if self.s_prints == 'qldebug':
                                print("el posible candidato es ", action, "01",copy_DG.nodes)
                            done_resource_picking = False
                            break
                    else:
                        candidatos = candidatos_respaldo.copy()
                        if copy_DG.nodes:
                            resource_candidate = candidatos.pop(0)
                            if self.s_prints == 'qldebug':
                                print("el posible candidato es ", resource_candidate)
                            if resource_candidate in copy_DG.nodes:
                                action = resource_candidate
                                if self.s_prints == 'qldebug':
                                    print("el posible candidato es ", action, "02",copy_DG.nodes)
                                done_resource_picking = False
                                break
                        else:
                            if self.s_prints == 'qldebug':
                                print("anexo de un time slot 03")
                            lista_total.append(lista_mapping)
                            lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                             range(0, len(self.DG_copy))]
                            copy_DG = self.DG.copy()
                            action = candidatos_respaldo[0]
                            if self.s_prints == 'qldebug':
                                print("el posible candidato es ", action, "03",copy_DG.nodes)
                            done_resource_picking = False
                            break

                if self.s_prints == 'qldebug':
                    print(f"the candidate is {action} for the task {initial_state[0]}")

                copy_DG.remove_node(action)
                if self.s_prints == 'qldebug':
                    print(f"el recurso seleccionado es {action} para intentar mapear la tarea {initial_state[0]} y"
                          f" los nodos restantes son {copy_DG.nodes}")
                if self.AG_copy_app.nodes[initial_state[0]]['op'] in self.DG.nodes[action]['op']:
                    if self.s_prints == 'qldebug':
                        # print(f"la tarea {initial_state[0]} es una tarea que se puede implementar en {action}")
                        print("checaremos sus parametros")
                    vector_validacion_parametros = self.verification_of_parameters(initial_state[0],
                                                                                   action)
                    if self.s_prints == 'qldebug':
                        print(f"bug 05 - terminamos de checar sus parametros {vector_validacion_parametros}")
                    bandera_source_of_data, info_sensor = self.verification_of_source(initial_state[0],
                                                                                      action, self.sources_AG_total)
                    if self.s_prints == 'q-l':
                        print(f"checamos la fuente de datos {bandera_source_of_data,info_sensor}")

                    if all(vector_validacion_parametros) and bandera_source_of_data:
                        if self.s_prints == 'qldebug':
                            print(f"estamos dentro del ciclo ya para mapear")
                        if initial_state[0] in self.sources_AG:
                            if self.s_prints == 'qldebug':
                                print("todo va bien, la tarea es un source node ")
                            resultado_latencia, resultado_latencia_total = self.obtention_latency(
                                action,
                                initial_state[0])
                            if self.s_prints == 'qldebug':
                                print(f"las latencias son {resultado_latencia,resultado_latencia_total}")
                            actuator_sink = self.only_actuator_sink(initial_state[0], action)
                            if self.s_prints == 'qldebug':
                                print(f" el sink o algo asi es {actuator_sink}")
                            info_actuator = self.info_actuator_generator(initial_state[0])
                            if self.s_prints == 'qldebug':
                                print(f"el info del actuator es {info_actuator}")
                            actuator_sink,lista_mapping = self.generation_copy_nodes(initial_state[0], action, lista_mapping)
                            if self.s_prints == 'qldebug':
                                print(f"vamos a mapear algo la tarea {initial_state[0]} en el recurso {action}, "
                                      f"la lista hasta ahorita es {lista_mapping}")
                                print(f"la lista total es {lista_total}")
                            if self.s_prints== 'qliter':
                                print(f"We are going to map task {self.dict_nodes_a[initial_state[0]]['name']} "
                                      f"onto the resource "
                                f"{self.dict_nodes_h[action]['name']} debug")

                            lista_mapping[action] = [True, initial_state[0], action,
                                                     self.AG_app.nodes[initial_state[0]]['op'],
                                                     self.dict_nodes_h[action]['ops'][
                                                         self.AG_app.nodes[initial_state[0]]['op']][
                                                         'latency'],
                                                     self.AG_app.nodes[initial_state[0]]['par'],
                                                     self.AG_app.nodes[initial_state[0]]['par'],
                                                     self.dict_nodes_h[action]['ops'][
                                                         self.AG_app.nodes[initial_state[0]]['op']][
                                                         'clk'],
                                                     resultado_latencia,
                                                     resultado_latencia_total,
                                                     info_sensor, info_actuator,
                                                     actuator_sink]
                            fail_counter = 0


                            mapping = False
                            # input("se finalizo el mapping source")
                        else:
                            ####is the same of the other algorithms, the task is not a source task, so we need to
                            ####verify several things
                            node_AG = initial_state[0]
                            predecessors = self.AG_app.predecessors(node_AG)

                            ######para debugear la verificacion de datos
                            if  self.s_prints == 'qldebug':
                                print("estamos por entrar en la funcion de verificacion de dependencia")


                            valid_place, special_nodes_01, lista_nodos_copy, lista_nodos_copy_time_slot, \
                            bandera_time_slots, time_slot_copy_nodes = self.verification_of_dependence(
                                predecessors, lista_total, action,node_AG,lista_mapping)
                            if self.s_prints == 'qldebug':
                                print("la lista mapping es ")
                                print(lista_mapping)
                                print(" la lista total es")
                                print(lista_total)
                                print(f"resultado de la dependencia de datos {valid_place}, los nodos {special_nodes_01}, otra "
                                      f"cosa {lista_nodos_copy}, otra cosa mas {lista_nodos_copy_time_slot}")


                            if valid_place:
                                resultado_latencia,resultado_latencia_total = self.obtention_latency(action,node_AG)
                                latency_copy = self.obtention_latency_copy_node(action)

                                if self.s_prints == 'qldebug':
                                    print(f"ya estamos casi por mapear algo, la lista de copy nodes {lista_nodos_copy} ,   {lista_nodos_copy_time_slot}")
                                for copy_node in lista_nodos_copy:
                                    if lista_mapping[copy_node][0]:
                                        pass
                                    else:
                                        lista_mapping[copy_node] = [True, None, 'copy', 'copy', copy_node,
                                                                        node_AG,
                                                                         0, 0, latency_copy,
                                                                         latency_copy, 0, 0,
                                                                         0]

                                for copy_node in lista_nodos_copy_time_slot:
                                    if lista_total[time_slot_copy_nodes][copy_node][0]:
                                        pass
                                    else:
                                        lista_total[time_slot_copy_nodes][copy_node] = [True, None, 'copy', 'copy', copy_node,
                                                                         node_AG,
                                                                         0, 0, latency_copy,
                                                                         latency_copy, 0, 0,
                                                                         0]
                                actuator_sink,lista_mapping = self.generation_copy_nodes(node_AG, action, lista_mapping)
                                info_actuator = self.info_actuator_generator(node_AG)
                                if self.s_prints == 'qldebug':
                                    print(f"vamos a mapear la tarea {initial_state[0],node_AG}  en el recurso {action}")
                                    print(f"la lista mapping hasta ahora es {lista_mapping} y la lista total {lista_total}")
                                if self.s_prints == 'qliter':
                                    print(f"We are going to map task {self.dict_nodes_a[node_AG]['name']} "
                                          f"onto the resource "
                                          f"{self.dict_nodes_h[action]['name']}")
                                lista_mapping[action] = [True, node_AG, action,
                                                           self.AG_app.nodes[node_AG]['op'],
                                                           self.dict_nodes_h[action]['ops'][
                                                               self.AG_app.nodes[node_AG]['op']][
                                                               'latency'],
                                                           self.AG_app.nodes[node_AG]['par'],
                                                           self.AG_app.nodes[node_AG]['par'],
                                                           self.dict_nodes_h[action]['ops'][
                                                               self.AG_app.nodes[node_AG]['op']][
                                                               'clk'],
                                                           resultado_latencia,
                                                           resultado_latencia_total,
                                                           info_sensor,
                                                           info_actuator, actuator_sink]
                                fail_counter = 0
                                mapping = False
                                # input("se finalizo el mapping no source")

                fail_counter = fail_counter + 1

        # input("test")
        # self.s_prints = 'qliter'

        if lista_total:
            lista_total.append(lista_mapping)
            lista_final = lista_total
            self.lista_nodos_especiales = self.generation_special_nodes(lista_total)
        else:
            lista_final = [lista_mapping]
            lista_total = lista_final
            self.lista_nodos_especiales = self.generation_special_nodes(lista_total)

        #######addition of the special nodes
        if self.s_prints == 'qldebug':
            print(f"HEMOS TERMINADO EL MAPPING {lista_mapping}")
            print("lista total")
            print(lista_final)
            print("nodos especiales")
            print(self.lista_nodos_especiales)
            # input("debug algo")



        return lista_final

    def training_online(self, input_application_graph, dict_application, input_application_graph_total,
                        dict_application_total):
        c_total = datetime.now()

        now = c_total.strftime("%H:%M:%S.%f")

        print(f"Start of the iteration {self.contador_online_training} of the on-line training, current time {now}")
        text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

        text_file.write(
            "\nStart of the iteration " + str(self.contador_online_training) + " of the on-line training, current time " + now)
        text_file.close()


        if self.s_prints == 'qliter' or self.s_prints == 'qldebug':
            print("We are going to start an online mapping")
            # input("enter")
        # input("test entrenamiento online")
        gamma = self.gamma  # discount factor, ratio between rewards in a short  or long period
        # this factor will decrease during the training, near 1 prefers long period rewards, near 0 prefers
        # short period rewards
        self.counter_online_training = self.counter_online_training + 1
        if self.s_prints == 'q-l':
            print("we are going to start the online training01")

        LEARNING_RATE = self.learning_rate  # how fast the agent learns
        EPISODES = self.episodes_training_online
        decay_gamma = self.gamma / EPISODES
        epsilon = self.epsilon  # this is the variable that controls the explotation and the exploration
        # decay_epsilon = 0
        decay_epsilon = epsilon / 4000  # (EPISODES // 2) este no se utiliza
        START_EPSILON_DECAYING = self.start_of_decay_training_online
        END_EPSILON_DECAYING = self.end_decay_training_online
        if self.s_prints == 'q-l':
            print("we are going to start the online training02")

        epsilon_decay_value = epsilon / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)
        # now we start the training
        self.dict_nodes = self.dict_nodes_h
        if self.s_prints == 'q-l':
            print("we are going to start the online training03")
        self.AG_total = self.AG_total_app.copy()
        lista_entrada_master = self.creacion_lista_estados(input_application_graph,
                                                           self.vector_operaciones, self.dict_data_app, self.only_i,
                                                              self.only_j)
        training_reward_mapping = []
        training_reward_resources = []
        training_reward_mapping = []
        training_reward_resources_buffer = []
        training_reward_mapping_buffer = []
        training_reward_resources = []
        contador_smooth_graph = 0
        primera_vez_performance = True
        contador_smooth_graph_resources = 0
        if self.s_prints == 'q-l':
            print("we are going to start the online training")

        for i in range(EPISODES):
            # selec = random.randint(0, len(SetAppsForTraining.dict_aplicaciones.items()) - 1)
            # if self.s_prints == 'q-l':
            #     print(f"CREAREMOS la lista de estados con la aplicacion {selec}")
            # time.sleep(1)
            o = datetime.now()
            lista_mapping = [[False, False, False] for n in range(0, len(self.DG.nodes))]
            lista_final = []
            # test directo con la entrada
            # self.AG = self.AG_app
            # application_graph = self.AG.copy()
            # self.AG_copy = self.AG
            # self.dict_nodes_a = self.dict_nodes_a_app
            # self.dict_info_a = self.dict_info_a_app
            # self.AG_total = self.AG_total_app
            # copy_AG = self.AG.copy()
            # copy_DG = self.DG.copy()
            # self.AG_copia = self.AG.copy()
            # lista_entrada = self.creacion_lista_estados(self.AG,self.vector_operaciones,self.dict_data_app)
            #####entrenamiento normal
            lista_entrada = lista_entrada_master.copy()
            copy_AG = input_application_graph.copy()
            application_graph = input_application_graph.copy()
            self.AG_copia = input_application_graph.copy()
            self.AG = input_application_graph.copy()
            self.dict_nodes_a = dict_application
            self.dict_info_a = dict_application_total
            self.AG_total = input_application_graph_total
            # print(f"la lista de entrada sera {lista_entrada}")

            # debug se muestran los grafos de entrada
            # lista_vacia = []
            # Graph_visual_00 = GraphVisualization.GraphRep([],  self.AG,
            #                                               lista_vacia, 'app', 'app01_test', [], 'red', 'black',
            #                                               'circle')
            # Graph_visual_00.f.render(view=False)
            # Graph_visual_00.f.render(view=True, format='pdf')
            #
            # lista_vacia = []
            # Graph_visual_00 = GraphVisualization.GraphRep([], self.DG,
            #                                               lista_vacia, 'app', 'hw01_test', [], 'red', 'black',
            #                                               'circle')
            # Graph_visual_00.f.render(view=False)
            # Graph_visual_00.f.render(view=True, format='pdf')
            #
            # for nodo in self.DG.nodes:
            #     print(f"nodo es {nodo} y sus datos son {self.DG.nodes[nodo]} y el episodio es {i}")
            # for nodo in self.AG.nodes:
            #     print(f"la tarea es {nodo} y sus datos son {self.AG.nodes[nodo]}")

            copy_DG = self.DG.copy()
            SOURCES_AG = sources_nodes_of_a_graph(input_application_graph)
            SOURCES_DG = sources_nodes_of_a_graph(self.DG)
            mapped_nodes = []
            # mapping loop
            for nodo_app in range(0, len(copy_AG.nodes)):
                # we select a state ( task to map )
                estado = lista_entrada.pop(0)
                if self.s_prints == 'q-l':
                    print(f"el estado es {estado}")
                    if estado[1] == None:
                        input("el estado es none en training online")
                # we select a resource
                # depending of the epsilon we can select it randomly or from the q table
                if np.random.random() < epsilon:
                    # we are going to select a random resource
                    available_act = self.available_actions(copy_DG)
                    # print(available_act, " bug - 01")
                    action = self.sample_next_action(available_act)
                else:
                    # we are going to select a resource depending of the values of the q table

                    # we obtain the resource with the maximum value
                    max_index = np.where(self.Q[estado[1],] == np.max(self.Q[estado[1],]))[1]
                    if max_index.shape[0] > 1:
                        max_index = int(np.random.choice(max_index, size=1))
                    else:
                        max_index = int(max_index)
                    # we check if the resource is actually available
                    if max_index in copy_DG.nodes:
                        action = max_index
                    else:
                        # if it is not available we select a random resource
                        # available_act = self.available_actions(copy_DG)
                        # action = self.sample_next_action(available_act)

                        vector_actions = self.Q[estado[1],]
                        lista_buffer = vector_actions.copy()
                        lista_buffer.sort()
                        vector_actions_buffer = vector_actions.copy()
                        vector_actions_buffer = list(vector_actions_buffer.tolist())
                        lista_buffer = list(lista_buffer.tolist())
                        lista_buffer.reverse()
                        done = True
                        decay = -2
                        counter = 0
                        while done:
                            indice = len(lista_buffer[0]) + decay
                            # there are cases that all the resources have zero as q value so we test if we reach the last
                            # item of the vector of resources, if we do reach it we select a random resource
                            if counter == 3:
                                if self.s_prints == 'q-l':
                                    print("entrada a mas casos de lo normal")
                                lista_final.append(lista_mapping)
                                lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                                 range(0, len(self.DG_copy))]
                                copy_DG = self.DG.copy()
                                action = max_index
                                done = False
                            else:

                                try:
                                    lista_buffer[0][indice]
                                    for el in range(0, len(vector_actions_buffer[0])):
                                        if vector_actions_buffer[0][el] == lista_buffer[0][indice]:
                                            lugar = el
                                            break
                                    if lugar in copy_DG.nodes:
                                        done = False
                                    decay = decay - 1
                                    action = lugar
                                except:
                                    available_act = self.available_actions(copy_DG)
                                    # print(available_act)
                                    action = self.sample_next_action(available_act)
                                    done = False
                            if done:
                                counter = counter + 1
                # we remove the resource and map the task
                copy_DG.remove_node(action)

                lista_mapping[action] = [True, estado[0], action, copy_AG.nodes[estado[0]]['op'],
                                         copy_AG.nodes[estado[0]]['par']]
                # we obtain the local reward
                premio_local = self.local_reward(action, estado[0], self.DG, application_graph, lista_mapping)  #
                if self.s_prints == 'q-l':
                    print(f"el premio es {premio_local} por tomar la accion {action}")
                # self.update(estado[0], action, gamma, premio_local, LEARNING_RATE, 0)
                # we store the information of the task, the resource, the place in the q table and the local reward
                mapped_nodes.append([estado[0], action, estado[1], premio_local])  #
                if not copy_DG:
                    lista_final.append(lista_mapping)
                    lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                     range(0, len(self.DG_copy))]
                    copy_DG = self.DG.copy()

            if self.s_prints == 'q-l':
                print(f"la lista mapping es {lista_mapping}")
                print(f"la lista final es {lista_final}")
                # we add the mapping list to the final list
            lista_final.append(lista_mapping)
            #     # the mapping is finish, we obtain again the topological sorting, i think that we can remove this
            lista_topologica = list(nx.topological_sort(application_graph))
            #     # now we obtain the global mapping
            premio_general, premio_source,premio_performance = self.premio_mapping(lista_final, self.DG, application_graph,
                                                                lista_topologica, SOURCES_AG, SOURCES_DG)

            debugging = False
            if premio_performance > 0:
                if primera_vez_performance:

                    episode_latency = premio_performance
                    premio_latencia = 0
                    primera_vez_performance = False
                else:

                    if episode_latency > premio_performance:
                        premio_latencia = self.performance_evaluation_reward
                        episode_latency = premio_performance
                    else:
                        premio_latencia = -self.performance_evaluation_reward

                # input("el premio mapping es mayor de cero")

            else:
                premio_latencia = -self.performance_evaluation_reward

            if self.s_prints == 'q-l':
                print(f"EL PREMIO GENERAL ES {premio_general} y el premio source {premio_source}")
            # we are going to update the q table
            contador_estados = 0
            premio_general = premio_general + premio_source
            vector_local_premios = []
            for el in mapped_nodes:
                premio_total = premio_general + el[3] + premio_latencia
                vector_local_premios.append(el[3])
                try:
                    premio_total_next = premio_general + mapped_nodes[contador_estados + 1][3]
                except:
                    premio_total_next = premio_general + premio_general * 2

                self.update(el[2], el[1], gamma, premio_total, LEARNING_RATE, premio_total_next)
                contador_estados = contador_estados + 1
            # we update the gamma value, remember that a value near of 1 is mostly long period reward, near 0 is
            # a short period
            gamma = gamma - decay_gamma
            if self.s_prints == 'qldebug' or self.s_prints == 'qliter':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - o

                print(
                    f"Episode {i} of the {self.counter_online_training} online training, the mapping reward is {premio_general}, "
                    f"the local rewards are {vector_local_premios}, the overall local "
                    f"reward is {sum(vector_local_premios) / len(vector_local_premios)}, epsilon is {epsilon}, the processing time"
                    f" is {c.seconds} seconds {c.microseconds} microseconds")
            # also we update the epsilon, we want at the beggining mostly exploration, at the end pure explotation
            # training_reward_mapping.append(premio_general)
            # training_reward_resources.append(sum(vector_local_premios) / len(vector_local_premios))

            training_reward_mapping_buffer.append(premio_general)
            training_reward_resources_buffer.append(sum(vector_local_premios) / len(vector_local_premios))
            if contador_smooth_graph == 100:
                training_reward_resources.append(
                    sum(training_reward_resources_buffer) / len(training_reward_resources_buffer))
                elemento_01 = sum(training_reward_resources_buffer) / len(training_reward_resources_buffer)
                elemento_02 = sum(training_reward_mapping_buffer) / len(training_reward_mapping_buffer)
                # training_reward_mapping.append(sum(training_reward_mapping_buffer) / len(training_reward_mapping_buffer))
                elemento_03 = elemento_01 + elemento_02
                training_reward_mapping.append(elemento_03)
                contador_smooth_graph = 0
                training_reward_mapping_buffer = []
                training_reward_resources_buffer = []
            else:
                contador_smooth_graph = contador_smooth_graph + 1








            if END_EPSILON_DECAYING >= i >= START_EPSILON_DECAYING:
                epsilon -= epsilon_decay_value
        # we finish the training
        end = time.time()
        # print(self.Q)
        g = datetime.now()

        now = g.strftime("%H:%M:%S.%f")
        d = g - c_total

        print(
            f"end of the iteration {self.iteration} of the on-line training, current time {now} the processing "
            f"time is {d.seconds} seconds "
            f"{d.microseconds} microseconds")
        text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

        text_file.write(
            "\nEnd of the iteration " + str(
                self.iteration) + " of the on-line training, current time " + now + " the processing time is " + str(
                d.seconds) + " microseconds " + str(d.microseconds))
        text_file.close()
        self.contador_online_training = self.contador_online_training + 1
        return training_reward_mapping,training_reward_resources

    def training(self, gamma, EPISODES, LEARNING_RATE, decay_gamma, epsilon, decay_epsilon, START_EPSILON_DECAYING,
                 END_EPSILON_DECAYING,
                 epsilon_decay_value, SetAppsForTraining, s_prints):

        c_total = datetime.now()

        now = c_total.strftime("%H:%M:%S.%f")

        print(f"Start of the iteration {self.iteration} of the off-line training, current time {now}")
        text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

        text_file.write("\nStart of the iteration " + str(self.iteration) + " of the off-line training, current time " + now)
        text_file.close()
        if s_prints == 'q-l' or self.s_prints == 'qldebug':
            print("We are going to start the training")
        # now we start the training
        self.dict_nodes = self.dict_nodes_h
        training_reward_mapping = []
        training_reward_mapping_buffer = []
        training_reward_resources = []
        contador_smooth_graph = 0
        contador_smooth_graph_resources = 0
        training_reward_resources_buffer = []
        for i in range(EPISODES):
            o = datetime.now()
            selec = random.randint(0, len(SetAppsForTraining.dict_aplicaciones.items()) - 1)

            if s_prints == 'q-l':
                print(f"Creation of the state table with the application  {selec}")
            lista_total = []
            lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                             range(0, len(self.DG_copy))]
            lista_final = []
            # test directo con la entrada
            # self.AG = self.AG_app
            # application_graph = self.AG.copy()
            # self.AG_copy = self.AG
            # self.dict_nodes_a = self.dict_nodes_a_app
            # self.dict_info_a = self.dict_info_a_app
            # self.AG_total = self.AG_total_app
            # copy_AG = self.AG.copy()
            # copy_DG = self.DG.copy()
            # self.AG_copia = self.AG.copy()
            # lista_entrada = self.creacion_lista_estados(self.AG,self.vector_operaciones,self.dict_data_app)
            #####entrenamiento normal
            a = datetime.now()
            lista_entrada = self.creacion_lista_estados(SetAppsForTraining.dict_aplicaciones[selec]['graph'],
                                                        self.vector_operaciones, self.dict_data_app, self.only_i,
                                                        self.only_j)
            copy_AG = SetAppsForTraining.dict_aplicaciones[selec]['graph'].copy()
            application_graph = SetAppsForTraining.dict_aplicaciones[selec]['graph'].copy()
            self.AG_copia = SetAppsForTraining.dict_aplicaciones[selec]['graph'].copy()
            self.AG = SetAppsForTraining.dict_aplicaciones[selec]['graph'].copy()
            self.dict_nodes_a = SetAppsForTraining.dict_aplicaciones[selec]['dict_app']
            self.dict_info_a = SetAppsForTraining.dict_aplicaciones[selec]['dict_app_total']
            self.AG_total = SetAppsForTraining.dict_aplicaciones[selec]['graph_total']
            self.latency_matrix_result = self.latency_matrix(self.AG, self.DG, self.dict_nodes_a,
                                                             self.dict_info_h, self.dict_nodes_h)

            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"creation of the state list and the latency matrix, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")

            if self.s_prints == 'q-l':
                print(f"la lista de entrada sera {lista_entrada}")

            # debug se muestran los grafos de entrada
            # lista_vacia = []
            # Graph_visual_00 = GraphVisualization.GraphRep([],  self.AG,
            #                                               lista_vacia, 'app', 'app01_test', [], 'red', 'black',
            #                                               'circle')
            # Graph_visual_00.f.render(view=False)
            # Graph_visual_00.f.render(view=True, format='pdf')
            #
            # lista_vacia = []
            # Graph_visual_00 = GraphVisualization.GraphRep([], self.DG,
            #                                               lista_vacia, 'app', 'hw01_test', [], 'red', 'black',
            #                                               'circle')
            # Graph_visual_00.f.render(view=False)
            # Graph_visual_00.f.render(view=True, format='pdf')
            #
            # for nodo in self.DG.nodes:
            #     print(f"nodo es {nodo} y sus datos son {self.DG.nodes[nodo]} y el episodio es {i}")
            # for nodo in self.AG.nodes:
            #     print(f"la tarea es {nodo} y sus datos son {self.AG.nodes[nodo]}")

            copy_DG = self.DG.copy()
            SOURCES_AG = sources_nodes_of_a_graph(SetAppsForTraining.dict_aplicaciones[selec]['graph'])
            SOURCES_DG = sources_nodes_of_a_graph(self.DG)
            mapped_nodes = []

            # mapping loop
            for nodo_app in range(0, len(copy_AG.nodes)):
                a = datetime.now()
                # we select a state ( task to map )
                estado = lista_entrada.pop(0)
                if self.s_prints == 'q-l':
                    print(f"el estado es {estado}")
                    # if estado[1] == None:
                    #     input("se ha encontrado un none")

                # we select a resource
                # depending of the epsilon we can select it randomly or from the q table
                if np.random.random() < epsilon:
                    # we are going to select a random resource
                    available_act = self.available_actions(copy_DG)
                    # print(available_act, " bug - 01")
                    action = self.sample_next_action(available_act)
                else:
                    # we are going to select a resource depending of the values of the q table

                    # we obtain the resource with the maximum value
                    max_index = np.where(self.Q[estado[1],] == np.max(self.Q[estado[1],]))[1]
                    # if copy_DG.nodes:
                    if max_index.shape[0] > 1:
                        max_index = int(np.random.choice(max_index, size=1))
                    else:
                        max_index = int(max_index)
                    # we check if the resource is actually available
                    if max_index in copy_DG.nodes:
                        action = max_index
                    else:
                        # if it is not available we select a random resource
                        # available_act = self.available_actions(copy_DG)
                        # action = self.sample_next_action(available_act)

                        vector_actions = self.Q[estado[1],]
                        lista_buffer = vector_actions.copy()
                        lista_buffer.sort()
                        vector_actions_buffer = vector_actions.copy()
                        vector_actions_buffer = list(vector_actions_buffer.tolist())
                        lista_buffer = list(lista_buffer.tolist())
                        lista_buffer.reverse()
                        done = True
                        decay = -2
                        counter = 0
                        while done:
                            indice = len(lista_buffer[0]) + decay
                            # there are cases that all the resources have zero as q value so we test if we reach the last
                            # item of the vector of resources, if we do reach it we select a random resource
                            if counter == 3:
                                if self.s_prints == 'q-l':
                                    print("entrada a mas casos de lo normal")
                                lista_final.append(lista_mapping)
                                lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                                 range(0, len(self.DG_copy))]
                                copy_DG = self.DG.copy()
                                action = max_index
                                done = False
                                # max_index = np.where(self.Q[estado[1],] == np.max(self.Q[estado[1],]))[1]
                                # if self.s_prints == 'q-l':
                                #     print(
                                #         f"el maximo indice es {max_index} y el caso {estado[1]} es {self.Q[estado[1],]} para la tarea {estado} y"
                                #         f" la lista de nodos restantes es de {copy_DG.nodes}")
                                # if max_index.shape[0] > 1:
                                #     max_index = int(np.random.choice(max_index, size=1))
                                # else:
                                #     max_index = int(max_index)
                                # if max_index in copy_DG.nodes:
                                #     action = max_index
                                #     done = False
                                # else:
                                #     vector_actions = self.Q[estado[1],]
                                #     lista_buffer = vector_actions.copy()
                                #     lista_buffer.sort()
                                #     vector_actions_buffer = vector_actions.copy()
                                #     vector_actions_buffer = list(vector_actions_buffer.tolist())
                                #     lista_buffer = list(lista_buffer.tolist())
                                #     lista_buffer.reverse()
                                #     done = True
                                #     decay = -2
                                #     while done:
                                #         indice = len(lista_buffer[0]) + decay
                                #         try:
                                #             lista_buffer[0][indice]
                                #             for el in range(0, len(vector_actions_buffer[0])):
                                #                 if vector_actions_buffer[0][el] == lista_buffer[0][indice]:
                                #                     lugar = el
                                #                     break
                                #             if lugar in copy_DG.nodes:
                                #                 done = False
                                #             decay = decay - 1
                                #             action = lugar
                                #         except:
                                #             available_act = self.available_actions(copy_DG)
                                #             action = self.sample_next_action(available_act)
                                #             done = False
                            else:
                                try:
                                    lista_buffer[0][indice]
                                    for el in range(0, len(vector_actions_buffer[0])):
                                        if vector_actions_buffer[0][el] == lista_buffer[0][indice]:
                                            lugar = el
                                            break
                                    if lugar in copy_DG.nodes:
                                        done = False
                                    decay = decay - 1
                                    action = lugar
                                except:
                                    available_act = self.available_actions(copy_DG)
                                    # print(available_act)
                                    action = self.sample_next_action(available_act)
                                    done = False
                                if done:
                                    counter = counter + 1

                    # else:
                    #     # if we dont have more resources we create a time slot, and we select the resource
                    #     lista_total.append(lista_mapping)
                    #     lista_mapping = [[False, False, False] for n in range(0, len(self.DG.nodes))]
                    #     copy_DG = self.DG.copy()
                    #     if max_index.shape[0] > 1:
                    #         max_index = int(np.random.choice(max_index, size=1))
                    #     else:
                    #         max_index = int(max_index)
                    #     if max_index in copy_DG.nodes:
                    #         action = max_index
                    #     else:
                    #         vector_actions = self.Q[estado[1],]
                    #         lista_buffer = vector_actions.copy()
                    #         lista_buffer.sort()
                    #         vector_actions_buffer = vector_actions.copy()
                    #         vector_actions_buffer = list(vector_actions_buffer.tolist())
                    #         lista_buffer = list(lista_buffer.tolist())
                    #         lista_buffer.reverse()
                    #         done = True
                    #         decay = -2
                    #         while done:
                    #             indice = len(lista_buffer[0]) + decay
                    #             try:
                    #                 lista_buffer[0][indice]
                    #                 for el in range(0, len(vector_actions_buffer[0])):
                    #                     if vector_actions_buffer[0][el] == lista_buffer[0][indice]:
                    #                         lugar = el
                    #                         break
                    #                 if lugar in copy_DG.nodes:
                    #                     done = False
                    #                 decay = decay - 1
                    #                 action = lugar
                    #             except:
                    #                 available_act = self.available_actions(copy_DG)
                    #                 action = self.sample_next_action(available_act)
                    #                 done = False
                # we remove the resource and map the task
                copy_DG.remove_node(action)

                lista_mapping[action] = [True, estado[0], action, copy_AG.nodes[estado[0]]['op'],
                                         copy_AG.nodes[estado[0]]['par']]
                # we obtain the local reward
                t = datetime.now()
                premio_local = self.local_reward(action, estado[0], self.DG, application_graph, lista_mapping)  #
                if self.debug_info == 'remove' or self.debug_info == 'total':
                    b = datetime.now()
                    now = b.strftime("%H:%M:%S.%f")
                    c = b - t
                    print(
                        f"local reward, "
                        f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                if self.s_prints == 'q-l':
                    print(f"el premio es {premio_local} por tomar la accion {action}")
                # self.update(estado[0], action, gamma, premio_local, LEARNING_RATE, 0)
                # we store the information of the task, the resource, the place in the q table and the local reward
                mapped_nodes.append([estado[0], action, estado[1], premio_local])  #
                if not copy_DG:
                    lista_final.append(lista_mapping)
                    lista_mapping = [[False, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] for g in
                                     range(0, len(self.DG_copy))]
                    copy_DG = self.DG.copy()
                if self.debug_info == 'remove' or self.debug_info == 'total':
                    b = datetime.now()
                    now = b.strftime("%H:%M:%S.%f")
                    c = b - a
                    print(
                        f"End of the mapping of task {estado[0]} "
                        f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            if self.s_prints == 'q-l':
                print(f"la lista mapping es {lista_mapping}")
                print(f"la lista final es {lista_final}")
            # we add the mapping list to the final list
            u = datetime.now()
            lista_final.append(lista_mapping)
            #     # the mapping is finish, we obtain again the topological sorting, i think that we can remove this
            lista_topologica = list(nx.topological_sort(application_graph))
            #     # now we obtain the global mapping
            premio_general, premio_source,premio_performance = self.premio_mapping(lista_final, self.DG, application_graph,
                                                                lista_topologica, SOURCES_AG, SOURCES_DG)
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"Mapping reward, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            if self.s_prints == 'q-l':
                print(f"EL PREMIO GENERAL ES {premio_general} y el premio source {premio_source}")
            # we are going to update the q table
            contador_estados = 0
            premio_general = premio_general + premio_source
            vector_local_premios = []
            for el in mapped_nodes:
                premio_total = premio_general + el[3]
                vector_local_premios.append(el[3])
                try:
                    premio_total_next = premio_general + mapped_nodes[contador_estados + 1][3]

                except:
                    premio_total_next = premio_general + premio_general * 2

                self.update(el[2], el[1], gamma, premio_total, LEARNING_RATE, premio_total_next)
                contador_estados = contador_estados + 1
                if self.s_prints == 'q-l':
                    print("regreso del update")
            # we update the gamma value, remember that a value near of 1 is mostly long period reward, near 0 is
            # a short period
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - o
                print(
                    f"End of episode, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            if self.s_prints == 'qliter':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - o
                print(
                    f"Episode {i}, the mapping reward is {premio_general}, the local rewards are {vector_local_premios}, "
                    f"epsilon is {epsilon}, the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            gamma = gamma - decay_gamma
            training_reward_mapping_buffer.append(premio_total_next) #preùio_general
            training_reward_resources_buffer.append(sum(vector_local_premios) / len(vector_local_premios))
            if contador_smooth_graph == 100:
                training_reward_resources.append(sum(training_reward_resources_buffer) / len(training_reward_resources_buffer))
                elemento_01 = sum(training_reward_resources_buffer) / len(training_reward_resources_buffer)
                elemento_02 = sum(training_reward_mapping_buffer) / len(training_reward_mapping_buffer)
                # training_reward_mapping.append(sum(training_reward_mapping_buffer) / len(training_reward_mapping_buffer))
                elemento_03 = elemento_01 + elemento_02
                training_reward_mapping.append(elemento_03)
                contador_smooth_graph = 0
                training_reward_mapping_buffer = []
                training_reward_resources_buffer = []
            else:
                contador_smooth_graph = contador_smooth_graph + 1

            # also we update the epsilon, we want at the beggining mostly exploration, at the end pure explotation
            if END_EPSILON_DECAYING >= i >= START_EPSILON_DECAYING:
                epsilon -= epsilon_decay_value
        # we finish the training
        end = time.time()
        if self.s_prints == 'q-l':
            print(self.Q)

        g = datetime.now()

        now = g.strftime("%H:%M:%S.%f")
        d = g - c_total

        print(
            f"end of the iteration {self.iteration} of the off-line training, current time {now} the processing "
            f"time is {d.seconds} seconds "
            f"{d.microseconds} microseconds")
        text_file = open(os.path.join(self.folder_txt, "results.txt"), "a")

        text_file.write(
            "\nEnd of the iteration " + str(self.iteration) + " of the off-line training, current time " + now + " the processing time is " + str(d.seconds) + " microseconds " + str(d.microseconds))
        text_file.close()
        return training_reward_mapping,training_reward_resources

    def update(self, current_state, action, gamma, reward, LEARNING_RATE, premio_next):
        if self.s_prints == 'q-l':
            print(current_state, action, gamma, reward)
        max_index = np.where(self.Q[current_state,] == np.max(self.Q[current_state,]))[1]
        if max_index.shape[0] > 1:
            max_index = int(np.random.choice(max_index, size=1))
        else:
            max_index = int(max_index)
        max_value = self.Q[current_state, max_index]
        old_value = self.Q[current_state, action]
        # this is the bellman equation
        new_value = (1 - LEARNING_RATE) * old_value + LEARNING_RATE * (reward + gamma * max_value)
        # new_value = reward + gamma * max_value
        # print("vamos a imprimir lo que modificaremos de la q")
        if self.s_prints == 'q-l':
            print(current_state, action)
        # if new_value < 0:
        # input("test")
        self.Q[current_state, action] = new_value

    def premio_mapping(self, lista_mapping, hardware_graph, application_graph, lista_topologica, sources_app,
                       sources_hw):
        # initialization of the reward
        premio_total = 0

        if self.s_prints == 'q-l':
            print("we start the process of the mapping reward")
            print(f"la lista topologica es {lista_topologica}")

        # for each task we are going to see where it is mapped and see if the mapping is correct
        premio_por_source = 0
        premio_latencia_mapping = 0
        vector_resultado_source = []
        for e in lista_topologica:
            # we need to locate the task

            lugar_tarea = None
            lugar_time_slot = None

            for u in range(len(lista_mapping)):
                time_slot = lista_mapping[u]
                for elemento in range(len(time_slot)):
                    if time_slot[elemento][1] == e:
                        lugar_tarea = elemento
                        lugar_time_slot = u
                        break
            if lugar_tarea == None:
                if self.s_prints == 'q-l':
                    print(e)
                    print(lista_mapping)

            # for time_slot in lista_mapping:
            #     for elemento in time_slot:
            #         if elemento[1] == e:
            #
            # for ui in range(0, len(lista_mapping)):
            #     if lista_mapping[ui][1] == e:
            #         # we found the place where the task is mapped
            #         lugar_tarea = ui

            # try:
            #     new_validacion_parameters = self.verification_of_parameters(e, lugar_tarea)
            #     if all(new_validacion_parameters):
            #         pass
            #     else:
            #         return  -5
            # except:
            #     return  -5

            # obtencion de informacion sobre el source
            bandera_source, dummy = self.verification_of_source(e, lugar_tarea, sources_app)
            vector_resultado_source.append(bandera_source)
            premio_latencia_mapping = premio_latencia_mapping + self.latency_matrix_result[e][lugar_tarea]
            # obtencion de informacion sobre dependencia
            premio_tarea = self.verificacion_dependence(lista_mapping, e,application_graph)
            if self.s_prints == 'q-l':
                print(f"el premio de la tarea es de {premio_tarea} y el premio de source es de {premio_por_source}")
            if premio_tarea < 0:
                # input("test")
                return -self.total_mapping_reward, -self.verification_of_source_reward, -self.performance_evaluation_reward
            # premio_total = premio_total + premio_tarea + premio_por_source

            # print(f"la tarea es {e} y su premio es de {premio_tarea}")

        # # because all the tasks are correctly map we return a positive reward

        #####si llega hasta aqui
        if all(vector_resultado_source):
            premio_source = self.verification_of_source_reward
        else:
            premio_source = -self.verification_of_source_reward

        return self.total_mapping_reward, premio_source,premio_latencia_mapping

    def degree_verification(self, nodo_AG, selected_resource, lista_salida_memoria):
        # caso de input degree
        if self.s_prints == 'q-l':
            print(("we are going to check the degree of the resource"))
        input_degree_flag = False
        if self.DG.in_degree(selected_resource) == self.AG.in_degree(nodo_AG):
            input_degree_flag = True
        elif self.DG.in_degree(selected_resource) > self.AG.in_degree(nodo_AG):
            predecesores_tarea = self.AG.predecessors(nodo_AG)
            predecesores_recurso = self.DG.predecessors(selected_resource)
            for pr in predecesores_recurso:

                if lista_salida_memoria[pr][0] and lista_salida_memoria[pr][
                    1] not in predecesores_tarea:
                    input_degree_flag = False
                    break
                else:
                    input_degree_flag = True
        elif self.DG.in_degree(selected_resource) == 0:
            input_degree_flag = True
        # caso de output degree
        output_degree_flag = False
        if self.DG.out_degree(selected_resource) >= self.AG.out_degree(nodo_AG):
            if self.s_prints == 'q-l':
                print("test modificacion de grados 1")
            output_degree_flag = True
        else:
            sucesor_degree = self.DG.successors(selected_resource)
            conteo_sucesores = self.DG.out_degree(selected_resource)
            for su in sucesor_degree:
                conteo_sucesores = conteo_sucesores + self.DG.out_degree(su)
            conteo_predecesores = self.DG.in_degree(
                selected_resource)
            predecesor_degree = self.DG.predecessors(selected_resource)
            for pr in predecesor_degree:
                conteo_predecesores = conteo_predecesores + self.DG.in_degree(pr)
            if conteo_sucesores >= self.AG.out_degree(
                    nodo_AG) and conteo_predecesores >= self.AG.in_degree(nodo_AG):
                output_degree_flag = True
            else:
                if self.DG.out_degree(selected_resource) == 0:
                    output_degree_flag = True
                else:
                    output_degree_flag = False
            if self.s_prints == 'q-l':
                print("test modificacion de grados 2", conteo_sucesores, conteo_predecesores,
                      output_degree_flag)
        test_degree = output_degree_flag and input_degree_flag
        if self.s_prints == 'basic' or self.s_prints == 'q-l':
            print(
                f"degree flag {test_degree},  "
                f"input degree flag {input_degree_flag} and the ouput degree flag {output_degree_flag}")
        return test_degree

    def local_reward(self, resource, task, hardware_graph, application_graph, lista_salida_memoria):
        # initialization of the reward
        premio = 0
        if self.s_prints == 'q-l':
            print("estamos en la funcion de premios locales")
        # for nodo in hardware_graph.nodes:
        #     print(nodo,hardware_graph.nodes[nodo])
        # we give a reward if the resource can implement the selected task
        if application_graph.nodes[task]['op'] in hardware_graph.nodes[resource]['op']:
            new_validacion_parameters = self.verification_of_parameters(task, resource)
            if self.s_prints == "q-l":
                print("bug 75")
            if all(new_validacion_parameters):
                premio = premio + self.verification_parameters_reward
            else:
                premio = premio - self.verification_parameters_reward
        else:
            premio = premio - self.verification_parameters_reward

        # reward of degree
        test_degree = self.degree_verification(task, resource, lista_salida_memoria)
        if test_degree:
            premio = premio + self.verification_degree_reward
        else:
            premio = premio - self.verification_degree_reward

        # reward of latency
        #  if self.s_prints == 'q-l':
        #      print(task,resource)
        #      print(len(self.latency_matrix_result), len(self.latency_matrix_result[0]))
        premio = premio + self.latency_matrix_result[task][resource]

        #  reward if the predeccessor tasks are compatible with the predecessor of the resource
        predecesores_app = list(application_graph.predecessors(task))
        predecesores_hw = list(hardware_graph.predecessors(resource))
        premio_suc_prede = self.suc_and_prede_parameters / 2
        lista_operaciones = []
        for prede in predecesores_hw:
            lista_operaciones = lista_operaciones + hardware_graph.nodes[prede]['op']
        if not predecesores_app:
            if not predecesores_hw:
                premio = premio + premio_suc_prede
            else:
                premio = premio - premio_suc_prede
        else:
            for pre in predecesores_app:
                if application_graph.nodes[pre]['op'] in lista_operaciones:
                    premio = premio + (premio_suc_prede / len(predecesores_app))
                else:
                    premio = premio - (premio_suc_prede / len(predecesores_app))

        # reward if the successor tasks are compatible with the successor of the resource
        lista_operaciones = []
        sucesores_app = list(application_graph.successors(task))
        sucesores_hw = list(hardware_graph.successors(resource))
        for suc in sucesores_hw:
            lista_operaciones = lista_operaciones + hardware_graph.nodes[suc]['op']
        if not sucesores_app:
            if not sucesores_hw:
                premio = premio + premio_suc_prede
            else:
                premio = premio - premio_suc_prede
        else:
            for suc in sucesores_app:
                if application_graph.nodes[suc]['op'] in lista_operaciones:
                    premio = premio + (premio_suc_prede / len(sucesores_app))
                else:
                    premio = premio - (premio_suc_prede / len(sucesores_app))

        # print(f"el premio sera de  {premio}")
        return premio

    # available actions (resources) in the graph
    def available_actions(self, input_graph):
        lista_nodos = list(input_graph.nodes)
        return lista_nodos

    # from a list of possible actions we select one
    def sample_next_action(self, available_act):
        next_action = int(np.random.choice(available_act, 1))
        return next_action

    def list_downward_upward(self, input_graph, rank):
        lista_result = {}
        for n in input_graph.nodes:
            ancestors = nx.ancestors(input_graph, n)
            subgraph = nx.subgraph(input_graph, ancestors)
            downward_number = len(nx.dag_longest_path(subgraph))
            descendants = nx.descendants(input_graph, n)
            subgraph = nx.subgraph(input_graph, descendants)
            upward_number = len(nx.dag_longest_path(subgraph))
            lista_result[n] = {}
            if upward_number > rank:
                # print(upward_number,rank)
                # input('el upward es mayor')
                lista_result[n]['upward'] = rank
            else:
                lista_result[n]['upward'] = upward_number

            if downward_number > rank:
                # input("el down es mayor")
                lista_result[n]['downward'] = rank
            else:
                lista_result[n]['downward'] = downward_number
        # print(lista_result)
        # input('test')
        return lista_result

    def creacion_lista_estados(self, input_graph, vector_operaciones, dict_data_app, info_prede, info_suc):
        # creation of the list of states
        # we use a list to have a sense of order, in this case the topological sorting, also
        # it helps in the rewards section, the idea is create a list with all the elementary information
        # required for the process, so we will traverse the dictionary of operaciones only once
        # topological = list(nx.topological_sort((input_graph)))
        lista_entrada = []

        ######creation list of downward and upward
        list_ranks = self.list_downward_upward(input_graph, self.rank)
        a = datetime.now()

        for u in nx.topological_sort(input_graph):
            h = datetime.now()
            # we search for the place of the operation in the list
            lugar = self.busqueda_caso(input_graph.nodes[u]['op'], input_graph.nodes[u]['par'], vector_operaciones)
            # now we search for the places of the operations of the predecessors
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - h
                print(
                    f"Task {u}, stage 1, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            h = datetime.now()
            operaciones_predecesor = []
            input_degree_predecessors = []
            for pre in input_graph.predecessors(u):
                operaciones_predecesor.append(
                    self.busqueda_caso(input_graph.nodes[pre]['op'], input_graph.nodes[pre]['par'], vector_operaciones))
                input_degree_predecessors.append(input_graph.in_degree(pre))
            # now we search for the place of the operations of the successors
            operaciones_sucesores = []
            output_degree_successors = []
            for suc in input_graph.successors(u):
                operaciones_sucesores.append(
                    self.busqueda_caso(input_graph.nodes[suc]['op'], input_graph.nodes[suc]['par'], vector_operaciones))
                output_degree_successors.append(input_graph.out_degree(suc))

            output_degree_successors = sorted(output_degree_successors)
            input_degree_predecessors = sorted(input_degree_predecessors)
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - h
                print(
                    f"Task {u}, stage 2, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            downward_number = list_ranks[u]['downward']
            upward_number = list_ranks[u]['upward']

            # print(f" las operaciones prede {operaciones_predecesor} las operaciones sucesores {operaciones_sucesores}")
            # print(f"el downward is {downward_number} and the upward is {upward_number}")
            h = datetime.now()
            lugar_dictionario = self.busqueda_latest(dict_data_app, lugar, input_graph.in_degree(u),
                                                     sorted(operaciones_predecesor),
                                                     input_graph.out_degree(u), sorted(operaciones_sucesores),
                                                     input_degree_predecessors, output_degree_successors,
                                                     downward_number, upward_number, info_prede, info_suc)

            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - h
                print(
                    f"Task {u}, stage 3, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            # lugar_dictionario = self.busqueda_newest(dict_data_app, lugar, input_graph.in_degree(u), sorted(operaciones_predecesor),
            #                                   input_graph.out_degree(u), sorted(operaciones_sucesores),
            #                                   input_degree_predecessors,output_degree_successors,downward_number,upward_number)
            # print(f" el lugar de diccionario es {lugar_dictionario}")
            if lugar_dictionario == None:
                for n, item in dict_data_app['case'].items():
                    print(n, item)
                    # print("")
                    if item['downward'] == 3:
                        print(item['upward'])
                print(lugar, input_graph.in_degree(u), operaciones_predecesor,
                      input_graph.out_degree(u), operaciones_sucesores,
                      input_degree_predecessors, output_degree_successors, downward_number, upward_number)
                input('test none encontrado')
            # print("el termino que buscamos es ")
            # print(input_graph.in_degree(u), operaciones_predecesor,
            #                                   input_graph.out_degree(u), operaciones_sucesores)
            elemento_append = [u, lugar_dictionario]
            # elemento_to_append = [u, lugar, input_graph.in_degree(u), operaciones_predecesor, input_graph.out_degree(u),
            #                      operaciones_sucesores]
            lista_entrada.append(elemento_append)

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Inside of the creation list function, "
                f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        return lista_entrada

    def caracteristicas_degree(self):
        """
        function to obtain the main characteristics of the hardware graph, which are:
        input_degree, output_degree, operations of the resource and its successors and predecessors.
        Now, there are 4 outputs

        maximum_input,maximum_output,

        vector_operaciones is a dictionary with the following structure
                vector_operaciones[contador_operaciones][operacion_unica]['param']
                where the contador_operaciones counts the number of different types of operations, even if the name
                is the same but the parameters range are different
                the only operations that it does not count are the copy and the disable


        dict_data_hw is a dictionary with the following structure
            dict_data_hw[nodo]['in'] = input_degree of nodo
            dict_data_hw[nodo]['out'] = out_degree of nodo
            dict_data_hw[nodo]['inop'] = list of the operations of the predeccessors, all the operations
                                           of all predecessors
            dict_data_hw[nodo]['outop'] = list of the operations of the successors, all the operations of all
                                         successors

        """

        dict_data_hw = {}
        degree_list_input = []
        degree_list_output = []
        numero_nodos = []
        for nodo in self.DG.nodes:
            degree_list_input.append(self.DG.in_degree(nodo))
            degree_list_output.append(self.DG.out_degree(nodo))
            numero_nodos.append(nodo)

        maximum_input = max(degree_list_input)
        maximo_valor_nodo = max(numero_nodos)
        maximum_output = max(degree_list_output)
        if self.s_prints == 'q-l':
            print(f"the maximum output {maximum_output} maximum input {maximum_input}")
            # input("test")
        self.tabla_valores = [None for n in range(0, len(self.DG.nodes))]

        vector_operaciones = {}
        vector_respaldo = []
        vector_con_las_operaciones = []
        contador_operaciones = 0
        dictionario_operaciones = {}
        contador_nodos = 0
        for nodo in self.DG.nodes:
            self.tabla_valores[contador_nodos] = nodo
            contador_nodos = contador_nodos + 1
            # print(f"el nodo es {nodo} y sus datos son {self.DG.nodes[nodo]}")
            dictionario_operaciones[nodo] = {}
            dict_data_hw[nodo] = {}
            dict_data_hw[nodo]['in'] = self.DG.in_degree(nodo)
            dict_data_hw[nodo]['out'] = self.DG.out_degree(nodo)

            lista_operaciones = []
            for operacion_unica in self.DG.nodes[nodo]['op']:
                # print(f"la operacion es {operacion_unica} y el contador es {contador_operaciones} para nodo {nodo}")
                if operacion_unica != 'copy' and operacion_unica != 'disable':
                    if operacion_unica not in vector_respaldo:
                        vector_operaciones[contador_operaciones] = {}
                        vector_operaciones[contador_operaciones][operacion_unica] = {}
                        vector_operaciones[contador_operaciones][operacion_unica]['name'] = operacion_unica
                        vector_operaciones[contador_operaciones][operacion_unica]['param'] = \
                        self.dict_nodes_h[nodo]['ops'][operacion_unica]['param']
                        vector_respaldo.append(operacion_unica)
                        temp = [operacion_unica, nodo, contador_operaciones]
                        lista_operaciones.append(contador_operaciones)
                        vector_con_las_operaciones.append(temp)
                        contador_operaciones = contador_operaciones + 1

                    else:
                        lugar_nodo = None
                        contador = 0
                        lugar_dato = None
                        for elemento in vector_con_las_operaciones:
                            if elemento[0] == operacion_unica:
                                lugar_nodo = elemento[1]
                                lugar_dato = contador
                            contador = contador + 1
                        parametros_1 = self.dict_nodes_h[nodo]['ops'][operacion_unica]['param']
                        parametros_2 = self.dict_nodes_h[lugar_nodo]['ops'][operacion_unica]['param']
                        if parametros_1 == parametros_2:
                            lista_operaciones.append(vector_con_las_operaciones[lugar_dato][2])
                        else:
                            vector_operaciones[contador_operaciones] = {}
                            vector_operaciones[contador_operaciones][operacion_unica] = {}
                            vector_operaciones[contador_operaciones][operacion_unica]['name'] = operacion_unica
                            vector_operaciones[contador_operaciones][operacion_unica]['param'] = \
                                self.dict_nodes_h[nodo]['ops'][operacion_unica]['param']
                            lista_operaciones.append(contador_operaciones)
                            temp = [operacion_unica, nodo]
                            contador_operaciones = contador_operaciones + 1

                # print(contador_operaciones)

            dictionario_operaciones[nodo]['operaciones'] = lista_operaciones
        # print(vector_operaciones)
        # print(dictionario_operaciones)
        for nodo in self.DG.nodes:
            # print(f"el nodo es {nodo} y sus datos son {self.DG.nodes[nodo]}")
            dictionario_predecesores = []
            for pre in self.DG.predecessors(nodo):
                # print(f"el predecesor es {pre} y sus datos son {self.DG.nodes[pre]}")
                for n, data in dictionario_operaciones.items():
                    if n == pre:
                        dictionario_predecesores.append(data['operaciones'])

            dict_data_hw[nodo]['inop'] = dictionario_predecesores

            dictionario_sucesores = []
            for suc in self.DG.successors(nodo):
                # print(f"el sucesor es {suc} y sus datos son {self.DG.nodes[suc]}")
                for n, data in dictionario_operaciones.items():
                    if n == suc:
                        dictionario_sucesores.append(data['operaciones'])
            dict_data_hw[nodo]['outop'] = dictionario_sucesores

        # print(dict_data_hw)
        return maximum_input, maximum_output, vector_operaciones, dict_data_hw, set(degree_list_input), set(
            degree_list_output)

    def x_axis_generation(self, maximum_input, maximum_output, vector_operaciones):
        if self.s_prints == 'q-l':
            print("estamos en la funcion de generacion del eje x")
        counter = 0
        vector_diccionario = []
        for n, data in vector_operaciones.items():
            vector_diccionario.append(n)
        # print(vector_diccionario)
        dict_data_app = {}
        dict_data_app['case'] = {}
        for el in vector_diccionario:
            for i in range(0, maximum_input + 1):
                for j in range(0, maximum_output + 1):
                    if i == 0 and j == 0:
                        dict_data_app['case'][counter] = {}
                        dict_data_app['case'][counter]['task'] = el
                        dict_data_app['case'][counter]['in'] = i
                        dict_data_app['case'][counter]['inop'] = []
                        dict_data_app['case'][counter]['out'] = j
                        dict_data_app['case'][counter]['outop'] = []
                        counter += 1
                    elif i == 0 and j > 0:
                        seq = list(combinations_with_replacement(vector_diccionario, j))
                        # print(seq)
                        for combi in seq:
                            dict_data_app['case'][counter] = {}
                            dict_data_app['case'][counter]['task'] = el
                            dict_data_app['case'][counter]['in'] = i
                            dict_data_app['case'][counter]['inop'] = []
                            dict_data_app['case'][counter]['out'] = j
                            dict_data_app['case'][counter]['outop'] = combi
                            counter += 1
                    elif i > 0 and j == 0:
                        seq = list(combinations_with_replacement(vector_diccionario, i))
                        # print(seq)
                        for combi in seq:
                            dict_data_app['case'][counter] = {}
                            dict_data_app['case'][counter]['task'] = el
                            dict_data_app['case'][counter]['in'] = i
                            dict_data_app['case'][counter]['inop'] = combi
                            dict_data_app['case'][counter]['out'] = j
                            dict_data_app['case'][counter]['outop'] = []
                            counter += 1
                    elif i > 0 and j > 0:
                        seq_i = list(combinations_with_replacement(vector_diccionario, i))
                        seq_j = list(combinations_with_replacement(vector_diccionario, j))
                        # print(seq_i,seq_j)
                        for combi_j in seq_j:
                            for combi_i in seq_i:
                                dict_data_app['case'][counter] = {}
                                dict_data_app['case'][counter]['task'] = el
                                dict_data_app['case'][counter]['in'] = i
                                dict_data_app['case'][counter]['inop'] = combi_i
                                dict_data_app['case'][counter]['out'] = j
                                dict_data_app['case'][counter]['outop'] = combi_j
                                counter += 1
        return dict_data_app

    def x_axis_generation_new(self, maximum_input, maximum_output, vector_operaciones, vector_degree_input,
                              vector_degree_output, rank):
        if self.s_prints == 'q-l':
            print("estamos en la funcion de generacion del eje x nueva")
        counter = 0
        vector_diccionario = []
        for n, data in vector_operaciones.items():
            vector_diccionario.append(n)
        # print(vector_diccionario)
        dict_data_app = {}
        dict_data_app['case'] = {}
        contador_pickles = 0
        contador_pasos = 0
        limite_lista = 9000000
        for el in vector_diccionario:
            # print(el)
            for i in range(0, maximum_input + 1):
                for j in range(0, maximum_output + 1):
                    #### no successors no predecessors
                    if i == 0 and j == 0:
                        dict_data_app['case'][counter] = {}
                        dict_data_app['case'][counter]['task'] = el  ####type of task
                        dict_data_app['case'][counter]['in'] = i  ###input degree of the task of interest
                        dict_data_app['case'][counter]['inop'] = []  ###type of tasks of the predecessors
                        dict_data_app['case'][counter]['out'] = j  ###output degree of the tasks of interest
                        dict_data_app['case'][counter]['outop'] = []  ###type of tasks of the successors
                        dict_data_app['case'][counter]['in_prede'] = []  ###vector of input degree of the predecessors
                        dict_data_app['case'][counter]['out_suc'] = []  ###vector of output degree of the successors
                        dict_data_app['case'][counter]['downward'] = 0  ##downward
                        dict_data_app['case'][counter]['upward'] = 0  ##upward
                        contador_pasos = contador_pasos + 1
                        # print(counter)
                        counter += 1

                        if contador_pasos > limite_lista:
                            name_pickle = 'estados' + '_' + str(contador_pickles)
                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                pickle.dump(dict_data_app, f)
                            dict_data_app = {}
                            dict_data_app['case'] = {}
                            contador_pickles = contador_pickles + 1
                            contador_pasos = 0

                    #### no predecessors yes successors
                    elif i == 0 and j > 0:
                        seq = list(combinations_with_replacement(vector_diccionario, j))
                        seq_output = list(combinations_with_replacement(vector_degree_output, j))
                        # print(seq)
                        for combi_output in seq_output:
                            for combi in seq:
                                for up_ward_number in range(1, rank + 1):
                                    dict_data_app['case'][counter] = {}
                                    dict_data_app['case'][counter]['task'] = el
                                    dict_data_app['case'][counter]['in'] = i
                                    dict_data_app['case'][counter]['inop'] = []
                                    dict_data_app['case'][counter]['out'] = j
                                    dict_data_app['case'][counter]['outop'] = combi
                                    dict_data_app['case'][counter]['in_prede'] = []
                                    dict_data_app['case'][counter]['out_suc'] = sorted(combi_output)
                                    dict_data_app['case'][counter]['downward'] = 0
                                    dict_data_app['case'][counter]['upward'] = up_ward_number
                                    # print(counter)
                                    counter += 1
                                    contador_pasos = contador_pasos + 1

                                    if contador_pasos > limite_lista:
                                        name_pickle = 'estados' + '_' + str(contador_pickles)
                                        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                            pickle.dump(dict_data_app, f)
                                        dict_data_app = {}
                                        dict_data_app['case'] = {}
                                        contador_pickles = contador_pickles + 1
                                        contador_pasos = 0
                    #### yes predecesors no successors
                    elif i > 0 and j == 0:
                        seq = list(combinations_with_replacement(vector_diccionario, i))
                        seq_input = list(combinations_with_replacement(vector_degree_input, i))
                        # print(seq)
                        for combi_input in seq_input:
                            for combi in seq:
                                for downward_number in range(1, rank + 1):
                                    dict_data_app['case'][counter] = {}
                                    dict_data_app['case'][counter]['task'] = el
                                    dict_data_app['case'][counter]['in'] = i
                                    dict_data_app['case'][counter]['inop'] = combi
                                    dict_data_app['case'][counter]['out'] = j
                                    dict_data_app['case'][counter]['outop'] = []
                                    dict_data_app['case'][counter]['in_prede'] = sorted(combi_input)
                                    dict_data_app['case'][counter]['out_suc'] = []
                                    dict_data_app['case'][counter]['downward'] = downward_number
                                    dict_data_app['case'][counter]['upward'] = 0
                                    # print(counter)
                                    counter += 1
                                    contador_pasos += 1
                                    if contador_pasos > limite_lista:
                                        name_pickle = 'estados' + '_' + str(contador_pickles)
                                        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                            pickle.dump(dict_data_app, f)
                                        dict_data_app = {}
                                        dict_data_app['case'] = {}
                                        contador_pickles = contador_pickles + 1
                                        contador_pasos = 0
                    #### both predecessors and successors
                    elif i > 0 and j > 0:
                        seq_i = list(combinations_with_replacement(vector_diccionario, i))
                        seq_j = list(combinations_with_replacement(vector_diccionario, j))
                        seq_input = list(combinations_with_replacement(vector_degree_input, i))
                        seq_output = list(combinations_with_replacement(vector_degree_output, j))
                        # seq_ranks = list(combinations_with_replacement(list(range(1,rank+1)), 2))
                        seq_ranks = sorted(set(list(permutations(list(range(1, rank + 1)), 2)) +
                                               list(combinations_with_replacement(list(range(1, rank + 1)), 2))))
                        # print(seq_i,seq_j)
                        for combi_input in seq_input:
                            for combi_output in seq_output:
                                for combi_j in seq_j:
                                    for combi_i in seq_i:
                                        for combi_ranks in seq_ranks:
                                            dict_data_app['case'][counter] = {}
                                            dict_data_app['case'][counter]['task'] = el
                                            dict_data_app['case'][counter]['in'] = i
                                            dict_data_app['case'][counter]['inop'] = combi_i
                                            dict_data_app['case'][counter]['out'] = j
                                            dict_data_app['case'][counter]['outop'] = combi_j
                                            dict_data_app['case'][counter]['in_prede'] = sorted(combi_input)
                                            dict_data_app['case'][counter]['out_suc'] = sorted(combi_output)
                                            dict_data_app['case'][counter]['downward'] = combi_ranks[0]
                                            dict_data_app['case'][counter]['upward'] = combi_ranks[1]
                                            # print(counter)
                                            counter += 1

                                            contador_pasos += 1
                                            if contador_pasos > limite_lista:
                                                name_pickle = 'estados' + '_' + str(contador_pickles)
                                                with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                    pickle.dump(dict_data_app, f)
                                                dict_data_app = {}
                                                dict_data_app['case'] = {}
                                                contador_pickles = contador_pickles + 1
                                                contador_pasos = 0

        name_pickle = 'estados' + '_' + str(contador_pickles)
        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
            pickle.dump(dict_data_app, f)
        dict_data_app = {}
        dict_data_app['case'] = {}
        # contador_pickles = contador_pickles + 1
        # contador_pasos = 0
        return dict_data_app, contador_pickles, counter

    def x_axis_generation_newest(self, maximum_input, maximum_output, vector_operaciones, vector_degree_input,
                                 vector_degree_output, rank):
        if self.s_prints == 'q-l':
            print("estamos en la funcion de generacion del eje x nueva")
        counter = 0
        vector_diccionario = []
        for n, data in vector_operaciones.items():
            vector_diccionario.append(n)
        # print(vector_diccionario)
        dict_data_app = {}
        dict_data_app['case'] = {}
        contador_pickles = 0
        contador_pasos = 0
        limite_lista = 9000000
        for el in vector_diccionario:
            # print(el)
            dict_data_app['case'][el] = {}
            for i in range(0, maximum_input + 1):
                dict_data_app['case'][el][i] = {}
                for j in range(0, maximum_output + 1):
                    dict_data_app['case'][el][i][j] = {}
                    for k in range(0, rank + 1):  ####downward
                        dict_data_app['case'][el][i][j][k] = {}
                        for h in range(0, rank + 1):  ###upward
                            dict_data_app['case'][el][i][j][k][h] = {}

                            #### no successors no predecessors
                            if i == 0 and j == 0:
                                dict_data_app['case'][el][i][j][k][h][counter] = {}
                                dict_data_app['case'][el][i][j][k][h][counter][
                                    'inop'] = []  ###type of tasks of the predecessors
                                dict_data_app['case'][el][i][j][k][h][counter][
                                    'outop'] = []  ###type of tasks of the successors
                                dict_data_app['case'][el][i][j][k][h][counter][
                                    'in_prede'] = []  ###vector of input degree of the predecessors
                                dict_data_app['case'][el][i][j][k][h][counter][
                                    'out_suc'] = []  ###vector of output degree of the successors
                                contador_pasos = contador_pasos + 1

                                counter += 1

                                if contador_pasos > limite_lista:
                                    name_pickle = 'estados' + '_' + str(contador_pickles)
                                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                        pickle.dump(dict_data_app, f)
                                    dict_data_app = {}
                                    dict_data_app['case'] = {}
                                    dict_data_app['case'][el] = {}
                                    dict_data_app['case'][el][i] = {}
                                    dict_data_app['case'][el][i][j] = {}
                                    dict_data_app['case'][el][i][j][k] = {}
                                    dict_data_app['case'][el][i][j][k][h] = {}
                                    contador_pickles = contador_pickles + 1
                                    contador_pasos = 0

                            #### no predecessors yes successors
                            elif i == 0 and j > 0:
                                seq = list(combinations_with_replacement(vector_diccionario, j))
                                seq_output = list(combinations_with_replacement(vector_degree_output, j))
                                # print(seq)
                                for combi_output in seq_output:
                                    for combi in seq:

                                        dict_data_app['case'][el][i][j][k][h][counter] = {}
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'inop'] = []  ###type of tasks of the predecessors
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'outop'] = combi  ###type of tasks of the successors
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'in_prede'] = []  ###vector of input degree of the predecessors
                                        dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = sorted(
                                            combi_output)  ###vector of output degree of the successors
                                        contador_pasos = contador_pasos + 1
                                        # print(counter)
                                        counter += 1

                                        if contador_pasos > limite_lista:
                                            name_pickle = 'estados' + '_' + str(contador_pickles)
                                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                pickle.dump(dict_data_app, f)
                                            dict_data_app = {}
                                            dict_data_app['case'] = {}
                                            dict_data_app['case'][el] = {}
                                            dict_data_app['case'][el][i] = {}
                                            dict_data_app['case'][el][i][j] = {}
                                            dict_data_app['case'][el][i][j][k] = {}
                                            dict_data_app['case'][el][i][j][k][h] = {}
                                            contador_pickles = contador_pickles + 1
                                            contador_pasos = 0
                            #### yes predecesors no successors
                            elif i > 0 and j == 0:
                                seq = list(combinations_with_replacement(vector_diccionario, i))
                                seq_input = list(combinations_with_replacement(vector_degree_input, i))
                                # print(seq)
                                for combi_input in seq_input:
                                    for combi in seq:
                                        dict_data_app['case'][el][i][j][k][h][counter] = {}
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'inop'] = combi  ###type of tasks of the predecessors
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'outop'] = []  ###type of tasks of the successors
                                        dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = sorted(
                                            combi_input)  ###vector of input degree of the predecessors
                                        dict_data_app['case'][el][i][j][k][h][counter][
                                            'out_suc'] = []  ###vector of output degree of the successors
                                        contador_pasos = contador_pasos + 1
                                        # print(counter)
                                        counter += 1

                                        if contador_pasos > limite_lista:
                                            name_pickle = 'estados' + '_' + str(contador_pickles)
                                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                pickle.dump(dict_data_app, f)
                                            dict_data_app = {}
                                            dict_data_app['case'] = {}
                                            dict_data_app['case'][el] = {}
                                            dict_data_app['case'][el][i] = {}
                                            dict_data_app['case'][el][i][j] = {}
                                            dict_data_app['case'][el][i][j][k] = {}
                                            dict_data_app['case'][el][i][j][k][h] = {}
                                            contador_pickles = contador_pickles + 1
                                            contador_pasos = 0
                            #### both predecessors and successors
                            elif i > 0 and j > 0:
                                seq_i = list(combinations_with_replacement(vector_diccionario, i))
                                seq_j = list(combinations_with_replacement(vector_diccionario, j))
                                seq_input = list(combinations_with_replacement(vector_degree_input, i))
                                seq_output = list(combinations_with_replacement(vector_degree_output, j))
                                # seq_ranks = list(combinations_with_replacement(list(range(1,rank+1)), 2))
                                # seq_ranks = sorted(set(list(permutations(list(range(1, rank + 1)), 2)) +
                                #                        list(combinations_with_replacement(list(range(1, rank + 1)), 2))))
                                # print(seq_i,seq_j)
                                for combi_input in seq_input:
                                    for combi_output in seq_output:
                                        for combi_j in seq_j:
                                            for combi_i in seq_i:
                                                dict_data_app['case'][el][i][j][k][h][counter] = {}
                                                dict_data_app['case'][el][i][j][k][h][counter][
                                                    'inop'] = combi_i  ###type of tasks of the predecessors
                                                dict_data_app['case'][el][i][j][k][h][counter][
                                                    'outop'] = combi_i  ###type of tasks of the successors
                                                dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = sorted(
                                                    combi_input)  ###vector of input degree of the predecessors
                                                dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = sorted(
                                                    combi_output)  ###vector of output degree of the successors
                                                contador_pasos = contador_pasos + 1
                                                # print(counter)
                                                counter += 1

                                                if contador_pasos > limite_lista:
                                                    name_pickle = 'estados' + '_' + str(contador_pickles)
                                                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                        pickle.dump(dict_data_app, f)
                                                    dict_data_app = {}
                                                    dict_data_app['case'] = {}
                                                    dict_data_app['case'][el] = {}
                                                    dict_data_app['case'][el][i] = {}
                                                    dict_data_app['case'][el][i][j] = {}
                                                    dict_data_app['case'][el][i][j][k] = {}
                                                    dict_data_app['case'][el][i][j][k][h] = {}
                                                    contador_pickles = contador_pickles + 1
                                                    contador_pasos = 0

        name_pickle = 'estados' + '_' + str(contador_pickles)
        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
            pickle.dump(dict_data_app, f)
        dict_data_app = {}
        dict_data_app['case'] = {}
        # contador_pickles = contador_pickles + 1
        # contador_pasos = 0
        return dict_data_app, contador_pickles, counter

    def x_axis_generation_latest(self, maximum_input, maximum_output, vector_operaciones, vector_degree_input,
                                 vector_degree_output, rank):
        if self.s_prints == 'q-l':
            print("estamos en la funcion de generacion del eje x nueva")
        counter = 0
        vector_diccionario = []
        for n, data in vector_operaciones.items():
            vector_diccionario.append(n)
        # print(vector_diccionario)
        dict_data_app = {}
        dict_data_app['case'] = {}
        contador_pickles = 0
        contador_pasos = 0
        limite_lista = 9000000
        for el in vector_diccionario:
            # print(el)
            dict_data_app['case'][el] = {}
            for i in range(0, maximum_input + 1):
                dict_data_app['case'][el][i] = {}
                for j in range(0, maximum_output + 1):
                    dict_data_app['case'][el][i][j] = {}
                    for k in range(0, rank + 1):  ####downward
                        dict_data_app['case'][el][i][j][k] = {}
                        for h in range(0, rank + 1):  ###upward
                            dict_data_app['case'][el][i][j][k][h] = {}

                            #### no successors no predecessors
                            if i == 0 and j == 0:
                                dict_data_app['case'][el][i][j][k][h][None] = {}  # inop
                                dict_data_app['case'][el][i][j][k][h][None][None] = {}  # outop
                                dict_data_app['case'][el][i][j][k][h][None][None][None] = {}  # in_prede
                                dict_data_app['case'][el][i][j][k][h][None][None][None][None] = counter  # out_suc

                                # dict_data_app['case'][el][i][j][k][h][counter] = {}
                                # dict_data_app['case'][el][i][j][k][h][counter]['inop'] = []     ###type of tasks of the predecessors
                                # dict_data_app['case'][el][i][j][k][h][counter]['outop'] = []    ###type of tasks of the successors
                                # dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = [] ###vector of input degree of the predecessors
                                # dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = []  ###vector of output degree of the successors
                                contador_pasos = contador_pasos + 1

                                counter += 1

                                if contador_pasos > limite_lista:
                                    name_pickle = 'estados' + '_' + str(contador_pickles)
                                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                        pickle.dump(dict_data_app, f)
                                    dict_data_app = {}
                                    dict_data_app['case'] = {}
                                    dict_data_app['case'][el] = {}
                                    dict_data_app['case'][el][i] = {}
                                    dict_data_app['case'][el][i][j] = {}
                                    dict_data_app['case'][el][i][j][k] = {}
                                    dict_data_app['case'][el][i][j][k][h] = {}
                                    dict_data_app['case'][el][i][j][k][h][None] = {}  # inop
                                    dict_data_app['case'][el][i][j][k][h][None][None] = {}  # outop
                                    dict_data_app['case'][el][i][j][k][h][None][None][None] = {}
                                    contador_pickles = contador_pickles + 1
                                    contador_pasos = 0

                            #### no predecessors yes successors
                            elif i == 0 and j > 0:
                                seq = list(combinations_with_replacement(vector_diccionario, j))
                                seq_output = list(combinations_with_replacement(vector_degree_output, j))
                                # print(seq)
                                for combi_output in seq_output:

                                    for combi in seq:

                                        dict_data_app['case'][el][i][j][k][h][None] = {}
                                        dict_data_app['case'][el][i][j][k][h][None][str(combi)] = {}
                                        dict_data_app['case'][el][i][j][k][h][None][str(combi)][None] = {}
                                        dict_data_app['case'][el][i][j][k][h][None][str(combi)][None][
                                            str(sorted(combi_output))] = counter

                                        # dict_data_app['case'][el][i][j][k][h][counter] = {}
                                        # dict_data_app['case'][el][i][j][k][h][counter]['inop'] = []  ###type of tasks of the predecessors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['outop'] = str(combi)  ###type of tasks of the successors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = []  ###vector of input degree of the predecessors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = str(sorted(combi_output))  ###vector of output degree of the successors
                                        contador_pasos = contador_pasos + 1
                                        # print(counter)
                                        counter += 1

                                        if contador_pasos > limite_lista:
                                            name_pickle = 'estados' + '_' + str(contador_pickles)
                                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                pickle.dump(dict_data_app, f)
                                            dict_data_app = {}
                                            dict_data_app['case'] = {}
                                            dict_data_app['case'][el] = {}
                                            dict_data_app['case'][el][i] = {}
                                            dict_data_app['case'][el][i][j] = {}
                                            dict_data_app['case'][el][i][j][k] = {}
                                            dict_data_app['case'][el][i][j][k][h] = {}
                                            dict_data_app['case'][el][i][j][k][h][None] = {}
                                            dict_data_app['case'][el][i][j][k][h][None][str(combi)] = {}
                                            dict_data_app['case'][el][i][j][k][h][None][str(combi)][None] = {}

                                            contador_pickles = contador_pickles + 1
                                            contador_pasos = 0
                            #### yes predecesors no successors
                            elif i > 0 and j == 0:
                                seq = list(combinations_with_replacement(vector_diccionario, i))
                                seq_input = list(combinations_with_replacement(vector_degree_input, i))
                                # print(seq)
                                for combi_input in seq_input:
                                    for combi in seq:
                                        dict_data_app['case'][el][i][j][k][h][str(combi)] = {}
                                        dict_data_app['case'][el][i][j][k][h][str(combi)][None] = {}
                                        dict_data_app['case'][el][i][j][k][h][str(combi)][None][
                                            str(sorted(combi_input))] = {}
                                        dict_data_app['case'][el][i][j][k][h][str(combi)][None][
                                            str(sorted(combi_input))][None] = counter
                                        # dict_data_app['case'][el][i][j][k][h][counter] = {}
                                        # dict_data_app['case'][el][i][j][k][h][counter]['inop'] = str(combi)  ###type of tasks of the predecessors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['outop'] = []  ###type of tasks of the successors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = str(sorted(combi_input))  ###vector of input degree of the predecessors
                                        # dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = []  ###vector of output degree of the successors
                                        contador_pasos = contador_pasos + 1
                                        # print(counter)
                                        counter += 1

                                        if contador_pasos > limite_lista:
                                            name_pickle = 'estados' + '_' + str(contador_pickles)
                                            with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                pickle.dump(dict_data_app, f)
                                            dict_data_app = {}
                                            dict_data_app['case'] = {}
                                            dict_data_app['case'][el] = {}
                                            dict_data_app['case'][el][i] = {}
                                            dict_data_app['case'][el][i][j] = {}
                                            dict_data_app['case'][el][i][j][k] = {}
                                            dict_data_app['case'][el][i][j][k][h] = {}
                                            dict_data_app['case'][el][i][j][k][h][str(combi)] = {}
                                            dict_data_app['case'][el][i][j][k][h][str(combi)][None] = {}
                                            dict_data_app['case'][el][i][j][k][h][str(combi)][None][
                                                str(sorted(combi_input))] = {}
                                            contador_pickles = contador_pickles + 1
                                            contador_pasos = 0
                            #### both predecessors and successors
                            elif i > 0 and j > 0:
                                seq_i = list(combinations_with_replacement(vector_diccionario, i))
                                seq_j = list(combinations_with_replacement(vector_diccionario, j))
                                seq_input = list(combinations_with_replacement(vector_degree_input, i))
                                seq_output = list(combinations_with_replacement(vector_degree_output, j))
                                # seq_ranks = list(combinations_with_replacement(list(range(1,rank+1)), 2))
                                # seq_ranks = sorted(set(list(permutations(list(range(1, rank + 1)), 2)) +
                                #                        list(combinations_with_replacement(list(range(1, rank + 1)), 2))))
                                # print(seq_i,seq_j)
                                for combi_input in seq_input:
                                    for combi_output in seq_output:
                                        for combi_j in seq_j:
                                            for combi_i in seq_i:

                                                dict_data_app['case'][el][i][j][k][h][str(combi_i)] = {}
                                                dict_data_app['case'][el][i][j][k][h][str(combi_i)][str(combi_j)] = {}
                                                dict_data_app['case'][el][i][j][k][h][str(combi_i)][str(combi_j)][
                                                    str(sorted(combi_input))] = {}
                                                dict_data_app['case'][el][i][j][k][h][str(combi_i)][str(combi_j)][
                                                    str(sorted(combi_input))][str(sorted(combi_output))] = counter

                                                # dict_data_app['case'][el][i][j][k][h][counter] = {}
                                                # dict_data_app['case'][el][i][j][k][h][counter]['inop'] = str(combi_j)  ###type of tasks of the predecessors
                                                # dict_data_app['case'][el][i][j][k][h][counter]['outop'] = str(combi_i)  ###type of tasks of the successors
                                                # dict_data_app['case'][el][i][j][k][h][counter]['in_prede'] = str(sorted( combi_input))  ###vector of input degree of the predecessors
                                                # dict_data_app['case'][el][i][j][k][h][counter]['out_suc'] = str(sorted(combi_output)) ###vector of output degree of the successors
                                                contador_pasos = contador_pasos + 1
                                                # print(counter)
                                                counter += 1

                                                if contador_pasos > limite_lista:
                                                    name_pickle = 'estados' + '_' + str(contador_pickles)
                                                    with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                                        pickle.dump(dict_data_app, f)
                                                    dict_data_app = {}
                                                    dict_data_app['case'] = {}
                                                    dict_data_app['case'][el] = {}
                                                    dict_data_app['case'][el][i] = {}
                                                    dict_data_app['case'][el][i][j] = {}
                                                    dict_data_app['case'][el][i][j][k] = {}
                                                    dict_data_app['case'][el][i][j][k][h] = {}
                                                    dict_data_app['case'][el][i][j][k][h][str(combi_i)] = {}
                                                    dict_data_app['case'][el][i][j][k][h][str(combi_i)][
                                                        str(combi_j)] = {}
                                                    dict_data_app['case'][el][i][j][k][h][str(combi_i)][str(combi_j)][
                                                        str(sorted(combi_input))] = {}
                                                    contador_pickles = contador_pickles + 1
                                                    contador_pasos = 0

        name_pickle = 'estados' + '_' + str(contador_pickles)
        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
            pickle.dump(dict_data_app, f)
        dict_data_app = {}
        dict_data_app['case'] = {}
        # contador_pickles = contador_pickles + 1
        # contador_pasos = 0
        return dict_data_app, contador_pickles, counter

    def x_axis_generation_more_recent(self, maximum_input, maximum_output, vector_operaciones, vector_degree_input,
                                      vector_degree_output, rank):
        if self.s_prints == 'q-l':
            print("estamos en la funcion de generacion del eje x nueva")
        counter = 0
        vector_diccionario = []
        for n, data in vector_operaciones.items():
            vector_diccionario.append(n)
        # print(vector_diccionario)
        dict_data_app = {}
        dict_data_app['case'] = {}
        contador_pickles = 0
        contador_pasos = 0
        limite_lista = 10000
        contador_elemento = 0
        dict_only_j = {}
        for j in range(0, maximum_output + 1):
            seq = list(combinations_with_replacement(vector_diccionario, j))
            seq_output = list(combinations_with_replacement(vector_degree_output, j))
            dict_only_j[j] = {}
            for seq_elemento in seq:  ####tasks of successors
                for seq_output_elemento in seq_output:  #####degree of successors
                    dict_only_j[j][contador_elemento] = {}
                    dict_only_j[j][contador_elemento]['out_suc'] = sorted(seq_output_elemento)
                    dict_only_j[j][contador_elemento]['outop'] = seq_elemento
                    contador_elemento = contador_elemento + 1
        total_j_elements = contador_elemento
        contador_elemento = 0
        dict_only_i = {}
        for i in range(0, maximum_input + 1):
            dict_only_i[i] = {}
            seq = list(combinations_with_replacement(vector_diccionario, i))
            seq_input = list(combinations_with_replacement(vector_degree_input, i))
            for seq_elemento in seq:
                for seq_input_elemento in seq_input:
                    dict_only_i[i][contador_elemento] = {}
                    dict_only_i[i][contador_elemento]['in_prede'] = sorted(seq_input_elemento)
                    dict_only_i[i][contador_elemento]['inop'] = seq_elemento
                    contador_elemento = contador_elemento + 1
        total_i_elements = contador_elemento
        contador_elemento = 0

        for el in vector_diccionario:
            # print(el)
            dict_data_app['case'][el] = {}
            for i in range(0, maximum_input + 1):
                dict_data_app['case'][el][i] = {}
                for j in range(0, maximum_output + 1):
                    dict_data_app['case'][el][i][j] = {}
                    for k in range(0, rank + 1):  ####downward
                        dict_data_app['case'][el][i][j][k] = {}
                        for h in range(0, rank + 1):  ###upward
                            dict_data_app['case'][el][i][j][k][h] = {}
                            for u in dict_only_i[i].keys():
                                # print(u)
                                dict_data_app['case'][el][i][j][k][h][u] = {}
                                for y in dict_only_j[j].keys():
                                    dict_data_app['case'][el][i][j][k][h][u][y] = counter

                                    contador_pasos = contador_pasos + 1
                                    counter = counter + 1
                                    if contador_pasos > limite_lista:
                                        name_pickle = 'estados' + '_' + str(contador_pickles)
                                        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
                                            pickle.dump(dict_data_app, f)
                                        dict_data_app = {}
                                        dict_data_app['case'] = {}
                                        dict_data_app['case'][el] = {}
                                        dict_data_app['case'][el][i] = {}
                                        dict_data_app['case'][el][i][j] = {}
                                        dict_data_app['case'][el][i][j][k] = {}
                                        dict_data_app['case'][el][i][j][k][h] = {}
                                        dict_data_app['case'][el][i][j][k][h][u] = {}  #
                                        contador_pickles = contador_pickles + 1
                                        contador_pasos = 0

        name_pickle = 'estados' + '_' + str(contador_pickles)
        with open(os.path.join(self.directorio, name_pickle), 'wb') as f:
            pickle.dump(dict_data_app, f)
        dict_data_app = {}
        dict_data_app['case'] = {}
        # contador_pickles = contador_pickles + 1
        # contador_pasos = 0
        return dict_data_app, contador_pickles, counter, dict_only_i, dict_only_j

    def y_axis_generatio(self):
        dict_data_hw = {}
        for nodo in self.DG.nodes:
            dict_data_hw[nodo] = {}
            dict_data_hw[nodo]['task'] = self.DG.node[nodo]['op']
            dict_data_hw[nodo]['in'] = self.DG.in_degree(nodo)
            op_prede = []
            for prede in self.DG.predecessors(nodo):
                op_prede.append(self.DG.node[prede]['op'])
            dict_data_hw[nodo]['inop'] = op_prede
            dict_data_hw[nodo]['out'] = self.DG.out_degree(nodo)
            op_suc = []
            for succ in self.DG.successors(nodo):
                op_suc.append(self.DG.node[succ]['op'])
            dict_data_hw[nodo]['outop'] = op_suc

    def busqueda_caso(self, task, parametros, vector_operaciones):
        lugar_vector = None
        # print("estamos en la funcion de busqueda de casos")
        # print(task,parametros,vector_operaciones)
        for i, data in vector_operaciones.items():
            for d in data:
                if d == task:
                    # print(f"los parametros son {parametros} y los otros son {vector_operaciones[i][task]['param']}")
                    vector_prueba = []
                    # por cada uno de los parametros
                    if parametros == None:
                        if parametros == vector_operaciones[i][task]['param']:
                            lugar_vector = i
                            break
                    else:
                        # print("estamos en else")
                        for par in parametros:

                            for el in vector_operaciones[i][task]['param'].items():

                                if el[0] == par[0]:
                                    # print(f"bla el parametro es {par} y el otro es {el}")
                                    if el[1] == 'boolean':
                                        # print("entro en el estado boolean")
                                        if par[1] == True or par[1] == False:
                                            # print("si esta bien")
                                            vector_prueba.append(True)

                                        else:
                                            vector_prueba.append(False)
                                    elif len(el[1]) == 2:
                                        if type(el[1][0]) == str:
                                            if par[1] in el[1]:
                                                vector_prueba.append(True)
                                            else:
                                                vector_prueba.append(False)
                                        else:
                                            if par[1] >= el[1][0] and par[1] <= el[1][1]:
                                                vector_prueba.append(True)
                                            else:
                                                vector_prueba.append(False)
                                    else:
                                        if par[1] in el[1]:
                                            vector_prueba.append(True)
                                        else:
                                            vector_prueba.append(False)
                        # print(vector_prueba)
                        if False not in vector_prueba:
                            lugar_vector = i
                            break

                        # if parametros == vector_operaciones[i][task]['param']:
                        #     lugar_vector = i
        if self.s_prints == 'q-l':
            print(f"vamos a regresar el lugar {lugar_vector}")
        return lugar_vector

    def busqueda_new(self, dict_data_app, task, in_deg, in_op, out_deg, out_op, in_prede, out_suc, down_number,
                     up_number):
        i = None
        print(self.contador_pickles)
        if self.contador_pickles == 0:
            print("iniciaremos la busqueda cargando la lista, solo un pickle")
            name_pickle = 'estados' + '_' + str(self.contador_pickles)
            with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                dict_data_app = pickle.load(f)

            try:
                dict_for_test = dict_data_app['case'][task][in_deg][out_deg][down_number][up_number]
                for n, item in dict_for_test.items():
                    if list(item['inop']) == in_op or list(reversed(item['inop'])) == in_op:
                        if list(item['outop']) == out_op or list(reversed(item['outop'])) == out_op:
                            if list(item['out_suc']) == out_suc:
                                if list(item['in_prede']) == in_prede:
                                    return n
            except:
                pass

        else:
            print("iniciaremos la busqueda cargando la lista, varios pickles", self.contador_pickles)
            for pckl in range(self.contador_pickles):
                name_pickle = 'estados' + '_' + str(pckl)
                with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                    dict_data_app = pickle.load(f)
                try:
                    dict_for_test = dict_data_app['case'][task][in_deg][out_deg][down_number][up_number]
                    for n, item in dict_for_test.items():
                        print(n, item)
                        if list(item['inop']) == in_op or list(reversed(item['inop'])) == in_op:
                            if list(item['outop']) == out_op or list(reversed(item['outop'])) == out_op:
                                if list(item['out_suc']) == out_suc:
                                    if list(item['in_prede']) == in_prede:
                                        return n
                except:
                    pass

        if i == None:
            print("no se encontro el lugar")
            print(in_op, out_op, in_prede, out_suc)
            input(" hubo un problema 02")

    def busqueda_newest(self, dict_data_app, task, in_deg, in_op, out_deg, out_op, in_prede, out_suc, down_number,
                        up_number):
        i = None
        print(self.contador_pickles)
        if self.contador_pickles == 0:
            print("iniciaremos la busqueda cargando la lista, solo un pickle")
            name_pickle = 'estados' + '_' + str(self.contador_pickles)
            with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                dict_data_app = pickle.load(f)

            try:
                # dict_for_test = dict_data_app['case'][task][in_deg][out_deg][down_number][up_number]
                # for n,item in dict_for_test.items():
                #     if list(item['inop']) == in_op or list(reversed(item['inop'])) == in_op:
                #         if list(item['outop']) == out_op or list(reversed(item['outop'])) == out_op:
                #             if list(item['out_suc']) ==out_suc:
                #                 if list(item['in_prede']) == in_prede:
                #                     return n
                if in_op:
                    inop = str(in_op)
                else:
                    inop = None
                if out_op:
                    outop = str(out_op)
                else:
                    outop = None

                if in_prede:
                    inpre = str(in_prede)
                else:
                    inpre = None

                if out_suc:
                    outsuc = str(out_suc)
                else:
                    outsuc = None

                return dict_data_app['case'][task][in_deg][out_deg][down_number][up_number][inop][outop][inpre][outsuc]
            except:
                pass

        else:
            print("iniciaremos la busqueda cargando la lista, varios pickles", self.contador_pickles)
            for pckl in range(self.contador_pickles):
                print(pckl)
                name_pickle = 'estados' + '_' + str(pckl)
                with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                    dict_data_app = pickle.load(f)
                try:
                    #         dict_for_test = dict_data_app['case'][task][in_deg][out_deg][down_number][up_number]
                    #         for n, item in dict_for_test.items():
                    #             print(n, item)
                    #             if list(item['inop']) == in_op or list(reversed(item['inop'])) == in_op:
                    #                 if list(item['outop']) == out_op or list(reversed(item['outop'])) == out_op:
                    #                     if list(item['out_suc']) == out_suc:
                    #                         if list(item['in_prede']) == in_prede:
                    #                             return n
                    if in_op:
                        inop = str(in_op)
                    else:
                        inop = None
                    if out_op:
                        outop = str(out_op)
                    else:
                        outop = None

                    if in_prede:
                        inpre = str(in_prede)
                    else:
                        inpre = None

                    if out_suc:
                        outsuc = str(out_suc)
                    else:
                        outsuc = None
                    print("estamos checando el bug")
                    print(task, in_deg, out_deg, down_number, up_number, inop, outop, inpre, outsuc)
                    return dict_data_app['case'][task][in_deg][out_deg][down_number][up_number][inop][outop][inpre][
                        outsuc]
                except:
                    pass

        if i == None:
            print("no se encontro el lugar")
            print(in_op, out_op, in_prede, out_suc)
            input(" hubo un problema 01")

    def busqueda_latest(self, dict_data_app, task, in_deg, in_op, out_deg, out_op, in_prede, out_suc, down_number,
                        up_number, info_prede, info_suc):

        a = datetime.now()
        i = None
        caso_i = None
        # print("ESTAMOS DEBUG")
        for u, item in info_prede[in_deg].items():
            # print(u)
            if list(item['inop']) == in_op or \
                    list(reversed(item['inop'])) == in_op:
                if list(item['in_prede']) == in_prede:
                    caso_i = u
                    break

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Task {task}, inside search case, stage 1, "
                f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        a = datetime.now()
        caso_j = None
        # print("CASO J")
        # print(info_suc[out_deg])
        for u, item in info_suc[out_deg].items():
            # print(u)
            if list(item['outop']) == out_op or \
                    list(reversed(item['outop'])) == out_op:
                if list(item['out_suc']) == out_suc:
                    caso_j = u
                    break

        if self.debug_info == 'remove' or self.debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a
            print(
                f"Task {task}, inside search case, stage 2, "
                f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
        # print(caso_j,caso_i)
        # print(self.contador_pickles)
        if self.contador_pickles == 0:
            # print("iniciaremos la busqueda cargando la lista, solo un pickle")
            a = datetime.now()
            name_pickle = 'estados' + '_' + str(self.contador_pickles)
            with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                dict_data_app = pickle.load(f)
            if self.debug_info == 'remove' or self.debug_info == 'total':
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                print(
                    f"Task {task}, inside search case, stage 3, "
                    f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            try:
                # print(task,in_deg,out_deg,down_number,up_number,caso_i,caso_j)
                # print(dict_data_app['case'][task][in_deg][out_deg][down_number])
                return dict_data_app['case'][task][in_deg][out_deg][down_number][up_number][caso_i][caso_j]
            except:
                # print(caso_j,caso_i)
                # print(dict_data_app['case'][task][in_deg][out_deg][down_number][up_number][caso_i])
                pass

        else:
            # print("iniciaremos la busqueda cargando la lista, varios pickles",self.contador_pickles)
            for pckl in range(self.contador_pickles):
                # print(pckl)
                a = datetime.now()
                name_pickle = 'estados' + '_' + str(pckl)
                with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                    dict_data_app = pickle.load(f)

                if self.debug_info == 'remove' or self.debug_info == 'total':
                    b = datetime.now()
                    now = b.strftime("%H:%M:%S.%f")
                    c = b - a
                    print(
                        f"Task {task}, inside search case, stage 3, "
                        f"current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
                try:
                    # print("estamos checando el bug")
                    # print(task,in_deg,out_deg,down_number,up_number,caso_i,caso_j)
                    # # print(dict_data_app['case'][task])
                    # for n, data in dict_data_app['case'][task].items():
                    #     print(" inicio de algo  ")
                    #     print(n)
                    #     print("  ")
                    #     print(data)
                    #     print("  ")
                    # print(" 01 ")
                    # print(dict_data_app['case'][task][in_deg])
                    # print(" 02 ")
                    # print(dict_data_app['case'][task][in_deg][out_deg])
                    # print(" 03 ")
                    # print(dict_data_app['case'][task][in_deg][out_deg][down_number])
                    # print(" 04 ")
                    # print(dict_data_app['case'][task][in_deg][out_deg][down_number][up_number])
                    # print(" 05 ")
                    return dict_data_app['case'][task][in_deg][out_deg][down_number][up_number][caso_i][caso_j]
                except:
                    # print("error")
                    # print(caso_i,caso_j)
                    # print(dict_data_app['case'][task][in_deg][out_deg][down_number][up_number])
                    pass

        if i == None:
            print("no se encontro el lugar dentro de la funcion")
            print(in_op, out_op, in_prede, out_suc, caso_i, caso_j)
            # print(self.contador_pickles, dict_data_app)
            input(" hubo un problema 045555")

    def busqueda(self, dict_data_app, task, in_deg, in_op, out_deg, out_op, in_prede, out_suc, down_number, up_number):
        i = None
        print(self.contador_pickles)
        if self.contador_pickles == 0:
            name_pickle = 'estados' + '_' + str(self.contador_pickles)
            with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                dict_data_app = pickle.load(f)

            for i in dict_data_app['case']:

                if dict_data_app['case'][i]['task'] == task:
                    # print("task")
                    if dict_data_app['case'][i]['in'] == in_deg:
                        # print("indeg")
                        if list(dict_data_app['case'][i]['inop']) == in_op or \
                                list(reversed(dict_data_app['case'][i]['inop'])) == in_op:
                            # print("inope")
                            if dict_data_app['case'][i]['out'] == out_deg:
                                # print("outdeg")
                                if list(dict_data_app['case'][i]['outop']) == out_op or \
                                        list(reversed(dict_data_app['case'][i]['outop'])) == out_op:
                                    # print("outop")
                                    if list(dict_data_app['case'][i]['in_prede']) == in_prede:
                                        # print("inpredeg")
                                        if list(dict_data_app['case'][i]['out_suc']) == out_suc:
                                            # print("outsucdeg")
                                            if dict_data_app['case'][i]['downward'] == down_number:
                                                # print("down")
                                                if dict_data_app['case'][i]['upward'] == up_number:
                                                    # print("up")
                                                    return i

        else:
            for pckl in range(self.contador_pickles):
                name_pickle = 'estados' + '_' + str(pckl)
                with open(os.path.join(self.directorio, name_pickle), 'rb') as f:
                    dict_data_app = pickle.load(f)

                for i in dict_data_app['case']:

                    if dict_data_app['case'][i]['task'] == task:
                        # print("task")
                        if dict_data_app['case'][i]['in'] == in_deg:
                            # print("indeg")
                            if list(dict_data_app['case'][i]['inop']) == in_op or \
                                    list(reversed(dict_data_app['case'][i]['inop'])) == in_op:
                                # print("inope")
                                if dict_data_app['case'][i]['out'] == out_deg:
                                    # print("outdeg")
                                    if list(dict_data_app['case'][i]['outop']) == out_op or \
                                            list(reversed(dict_data_app['case'][i]['outop'])) == out_op:
                                        # print("outop")
                                        if list(dict_data_app['case'][i]['in_prede']) == in_prede:
                                            # print("inpredeg")
                                            if list(dict_data_app['case'][i]['out_suc']) == out_suc:
                                                # print("outsucdeg")
                                                if dict_data_app['case'][i]['downward'] == down_number:
                                                    # print("down")
                                                    if dict_data_app['case'][i]['upward'] == up_number:
                                                        # print("up")
                                                        return i

        if i == None:
            print("no se encontro el lugar")
            input(" hubo un problema 03")

    ################funciones del mapping

    def verification_of_parameters(self, node_AG, resource):

        try:
            test_01 = self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param']
        except:
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
                    # print(param)
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
                            if self.s_prints == 'q-l':
                                print(
                                    f" el parametro es {param} app param {self.dict_nodes_a[node_AG]['param'][param]} hw parametros {self.dict_nodes[resource]['ops'][self.AG_copia.nodes[node_AG]['op']]['param'][param]}")
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
        # if self.s_prints == 'basic':
        if self.s_prints == 'q-l':
            print("la validacion de parametros ha terminado", new_validacion_parameters)
            print(f" se intento mapear task {node_AG} en el recurso {resource}")
        # input("Press Enter to continue...")
        return new_validacion_parameters

    def verification_of_source(self, node_AG, resource, lista_sources_AG):

        # todo cambiar todo lo relacionado a height and width

        if self.s_prints == 'qldebug':
            print(f"entrada a verificacion de source {lista_sources_AG}, el nodo es {node_AG} y el recurso {resource}")
        # for nodo in self.AG.nodes:
        #     print(f"tarea es {nodo} y sus datos son {self.AG_total.nodes[nodo]}")
        #
        # for nodo in self.DG_total.nodes:
        #     print(f"ahora el recurso es {nodo} y sus datos son {self.DG_total.nodes[nodo]}")
        bandera_source_of_data = False
        info_sensor = []
        # if self.s_prints == 'basic':
        #     print("ANOTHER CHANGE 01")
        #     print(self.lista_sources_AG)
        #
        # print(self.dict_info_a)
        # print(self.dict_nodes_a)

        if node_AG in lista_sources_AG:
            if self.s_prints == 'qldebug':
                print("it is a source node")
                # print(self.dict_nodes_a)
                # print(self.dict_info_a)
                # print(self.dict_total)
                # print(self.dict_nodes)
            lugar_nodo = None
            # print(self.dict_info_a)
            # print(self.dict_nodes_a)
            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         lugar_nodo)
            if self.s_prints == 'qldebug':
                print("verificacion de datos", self.AG_total.nodes[source_total_app]['par']['height'])

            lugar_nodo = None
            for n, data in self.dict_total_h.items():

                if self.dict_nodes_h[resource]['name'] == self.dict_total_h[n][
                    'name']:
                    lugar_nodo = n
            lista_sources_dg_total = obtencion_sources(self.DG_total)
            source_total_hw = source_node_from_any_node(self.DG_total,
                                                        lista_sources_dg_total,
                                                        lugar_nodo)
            # print(source_total_app,source_total_hw)
            if self.s_prints == 'qldebug':
                print(f"the source app es {source_total_app} y el source hw es {source_total_hw}")
            ########################################
            ############ aqui podemos cambiar lo que checamos y sus nombres
            if self.dict_total_h[source_total_hw]['type'] == 'ri' and \
                    self.dict_info_a[source_total_app][
                        'op'] == 'interface':
                bandera_source_of_data = True
            elif self.dict_total_h[source_total_hw]['type'] == 'rm' and \
                    self.dict_info_a[source_total_app]['op'] == 'memory':
                bandera_source_of_data = True
            else:
                bandera_source_of_data = False
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
        else:
            if self.s_prints == 'qldebug':
                print("entro al otro ciclo")
                for nodo in self.AG_total.nodes:
                    print(nodo,self.AG_total.nodes[nodo])
            lista_sources_ag_total = obtencion_sources(self.AG_total)
            if self.s_prints == 'q-l':
                print(lista_sources_ag_total, node_AG)

            for n, data in self.dict_info_a.items():
                if self.dict_nodes_a[node_AG]['name'] == self.dict_info_a[n]['name']:
                    lugar_nodo = n
            source_total_app = source_node_from_any_node(self.AG_total,
                                                         lista_sources_ag_total,
                                                         lugar_nodo)
            if self.s_prints == 'qldebug':
                print(source_total_app,lista_sources_ag_total,node_AG)
                print(self.AG_total.nodes[source_total_app])
            info_sensor = [self.AG_total.nodes[source_total_app]['name'],
                           self.AG_total.nodes[source_total_app]['par']['height'],
                           self.AG_total.nodes[source_total_app]['par']['width']]
            bandera_source_of_data = True
        # print(info_sensor)
        return bandera_source_of_data, info_sensor

    def verificacion_dependence(self, lista_final, tarea,application_graph):

        if isinstance(lista_final[0][0], bool):
            lista_final = [lista_final]

        sinks = self.sinks_connected_to_rc()
        sources = obtencion_sources(self.DG)
        sinks_AG = obtencion_sinks(application_graph)
        # donde esta el recurso
        lugar_recurso = None
        numero_instancia_recurso = None
        contador_instancia = 0
        for instancia in lista_final:
            for elemento in instancia:
                if elemento[0]:
                    if elemento[1] == tarea:
                        lugar_recurso = elemento[2]
                        numero_instancia_recurso = contador_instancia
                        break
            if lugar_recurso != None:
                break
            contador_instancia = contador_instancia + 1
        if self.s_prints == 'q-l':
            print(f"el lugar de la tarea {tarea} es {lugar_recurso} y esta en el time slot {numero_instancia_recurso}")
        bandera_mapping_valido = False
        set_predecesores = list(self.AG.predecessors(tarea))
        if self.s_prints == 'q-l':
            print(f"los predecesores son {set_predecesores}")
        if set_predecesores:
            # la tarea tiene predecesores hay que checar en donde estan
            for pre in set_predecesores:
                lugar_nodo = None
                numero_instancia = None
                contador_instancias = 0
                for instancia in lista_final:
                    for elemento in instancia:
                        if elemento[0]:
                            if elemento[1] == pre:
                                lugar_nodo = elemento[2]
                                numero_instancia = contador_instancias
                                break
                    if lugar_nodo != None:
                        break
                    contador_instancias = contador_instancias + 1

                # ya tenemos el lugar entonces veremos si existe un path entre ellos
                if self.s_prints == 'q-l':
                    print(f" el predecesor es {pre} y su lugar es {lugar_nodo} en la instancia {numero_instancia}")
                if numero_instancia == numero_instancia_recurso:
                    if self.s_prints == 'q-l':
                        print("estan en la misma instancia")
                    instancia_seleccionada = lista_final[numero_instancia]
                    paths = simple_paths_from_two_nodes(self.DG, lugar_nodo, lugar_recurso)
                    if self.s_prints == 'q-l':
                        print(f"los paths son {paths} ")
                    if paths:
                        for unique_path in paths:
                            copy_unique = unique_path
                            try:
                                copy_unique = copy_unique.remove(lugar_recurso)
                                copy_unique = copy_unique.remove(lugar_nodo)
                            except:
                                pass
                            if copy_unique:
                                for nodo in copy_unique:
                                    if instancia_seleccionada[nodo][0]:
                                        return -4
                    else:
                        return -4
                else:
                    instancia_recurso = lista_final[numero_instancia_recurso]
                    instancia_seleccionada = lista_final[numero_instancia]
                    if lugar_nodo not in sinks:
                        path_a_source = sink_node_from_any_node(self.DG, sinks, lugar_nodo)
                        if self.s_prints == 'q-l':
                            print(path_a_source)
                        try:
                            path_a_source = path_a_source.remove(lugar_nodo)
                        except:
                            pass
                        if self.s_prints == 'q-l':
                            print(path_a_source)
                        if path_a_source:
                            if isinstance(path_a_source, int):
                                if instancia_seleccionada[path_a_source][0]:
                                    return -4
                            else:
                                for nodo in path_a_source:
                                    if instancia_seleccionada[nodo][0]:
                                        return -4
                    if lugar_recurso not in sources:
                        path_a_sink = source_node_from_any_node(self.DG, sources, lugar_recurso)
                        try:
                            path_a_sink = path_a_sink.remove(lugar_recurso)
                        except:
                            pass
                        if path_a_sink:
                            #######error 15/04/2021
                            if isinstance(path_a_sink, int):
                                path_a_sink = [path_a_sink]
                            for nodo in path_a_sink:
                                if instancia_recurso[nodo][0]:
                                    return -4

        else:
            if self.s_prints == 'q-l':
                print("la tarea no tiene predecesores")
            if lugar_recurso not in sources:
                instancia_recurso = lista_final[numero_instancia_recurso]
                path_a_source = source_node_from_any_node(self.DG, sources, lugar_recurso)
                try:
                    path_a_source = path_a_source.remove(lugar_recurso)
                except:
                    pass
                if self.s_prints == 'q-l':
                    print(f" existe el path a source y es {path_a_source}")
                if path_a_source:
                    if isinstance(path_a_source, int):
                        if instancia_recurso[path_a_source][0]:
                            return - 4
                    else:
                        for nodo in path_a_source:
                            if instancia_recurso[nodo][0]:
                                return -4

        # si la tarea es un sink necesitamos saber si tiene un path hacia un sink en el hardware
        if tarea in sinks_AG:
            if lugar_recurso in sinks:
                pass
            else:
                instancia_recurso = lista_final[numero_instancia_recurso]

                path_a_source = sink_node_from_any_node(self.DG, sinks, lugar_recurso)
                if self.s_prints == 'qldebug':
                    print(path_a_source)
                try:
                    path_a_source = path_a_source.remove(lugar_recurso)
                except:
                    pass
                if self.s_prints == 'qldebug':
                    print(path_a_source)
                if path_a_source:
                    if isinstance(path_a_source, int):
                        if instancia_recurso[path_a_source][0]:
                            return -4
                    else:
                        for nodo in path_a_source:
                            if instancia_recurso[nodo][0]:
                                return -4




        if self.s_prints == 'q-l':
            print("end of the verification of data dependence")
        # time.sleep(1)
        return 5

    def verification_of_dependence(self, predecessors,  element_buffer, resource,
                                   nodo_AG, lista_mapping):
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
        lista_nodos_copy = []
        lista_nodos_copy_time_slot = []
        time_slot_copy_nodes = 0
        # if nodo_AG == 2 and resource == 1:
        #     self.bandera_debug = False
        # else:
        #     self.bandera_debug = False
        if self.bandera_debug or self.s_prints == 'qldebug':
            print("inside of the verification of dependence function ")
        datapaths = self.generation_datapaths(self.DG)
        # some internal variables
        special_nodes_list = []
        same_time_slot = True
        # final flag True if the data dependency is correct
        valid_place = False
        vector_valid_places = []
        bandera_time_slots = False
        datapath_buffer = []
        for path in datapaths:
            if resource in path:
                datapath_buffer =  path
                break
        # now we are going to iterate for each predecessor
        descendientes = obtencion_sucesores(self.DG,resource)
        descendientes = list(set(descendientes).intersection(datapath_buffer))
        for predecessor in predecessors:
            if self.s_prints == 'qldebug' or self.bandera_debug:
                print("predecesor", predecessor)
            # we check if the predecessor is in the same slot using the attribute self.lista_mapping
            node_place = None
            for h in lista_mapping:
                if h[0]:
                    if predecessor == h[1]:
                        node_place = h[2]
            if self.s_prints == 'qldebug' or self.bandera_debug:
                print(f"the node place is {node_place}, testtstststts")
            # if the predecessor is not in the same time slot we need to iterate over the previous time slots
            contador_time_slots = None
            if node_place == None:
                same_time_slot = False
                contador_time_slots = 0
                for n_time_slot in range(0, len(element_buffer)):
                    ins = element_buffer[n_time_slot]
                    for u in ins:
                        # if self.s_prints == 'debug' or self.bandera_debug:
                        #     print(u)
                        if u[0]:
                            if predecessor == u[1]:
                                node_place = u[2]
                                contador_time_slots += n_time_slot
                                break


            if self.s_prints == 'qldebug':
                print("the first attempt was not succesful, ",node_place, same_time_slot,contador_time_slots,descendientes)
            # now we have the place of the predecessor
            # we are going to have two cases, if the predecessor is in the same slot or not
            vector_02 = []
            if same_time_slot:

                if node_place not in descendientes:
                    if self.s_prints == 'qldebug':
                        print(f"predecessor in the same slot")
                    # we obtain the paths from the predecessor to the resource
                    paths = list(nx.all_simple_paths(self.DG, node_place, resource))
                    # in this list we are going to store the data of the nodes of the path
                    vector_dependency_02 = []
                    flag_recomputation = False
                    bandera_salida = False
                    if paths:
                        # if there are paths it means that there is no need for a recomputation node
                        # for path_b in paths:
                        if self.s_prints == 'qldebug':
                            print("there is a path")
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
                            if self.s_prints == 'qldebug':
                                print(f"el path a checar es {path}")
                                print(f" y la lista mapping es {lista_mapping}")
                            vector_dependency_01 = []
                            for node in path:

                                if lista_mapping[node][0] :#and lista_mapping[node][2] != 'copy':#

                                    vector_dependency_01 = vector_dependency_01 + [lista_mapping[node][0]]
                            if True in vector_dependency_01:
                                vector_dependency_02 = vector_dependency_02 + [False]
                            else:  #
                                lista_nodos_copy = lista_nodos_copy + path_buffer  #
                                bandera_salida = True
                                vector_dependency_02 = vector_dependency_02 + [True]
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
                        if self.s_prints == 'qldebug':
                            print("There are not paths, we are going to verify the dependency in the others "
                                  "paths", node_place,self.list_sinks_connected_to_rc)
                        valid_sink = False
                        valid_source = False
                        datapaths = self.generation_datapaths(self.DG)
                        datapath_buffer = []
                        for path in datapaths:
                            if node_place\
                                    in path:
                                datapath_buffer = path
                                break
                        if self.s_prints == 'qldebug':
                            print(f"el datapath del predecessor es {datapath_buffer}")
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
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place)
                                    if sink_nodo_sink_task == None:
                                        counter_internal = counter_internal + 1
                                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      node_place)
                                else:
                                    counter_internal = counter_internal + 1
                                    copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                                  copy_list_sinks_connected_to_rc,
                                                                                  node_place)
                                # print(sink_nodo_sink_task,resource)
                                if lista_mapping[sink_nodo_sink_task][0] or sink_nodo_sink_task not in datapath_buffer:
                                    copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                    if counter_internal == 5:
                                        # copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc
                                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                                      copy_list_sinks_connected_to_rc,
                                                                                      node_place)
                                        done = False
                                        break

                                else:
                                    done = False
                                    break

                            #########"""

                            sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)

                            path_to_sink = simple_paths_from_two_nodes(self.DG, node_place, sink)
                            vector_02 = []
                            if self.s_prints == 'qldebug':
                                print("el sink en verificacion de algo ", sink)
                                print(f"los paths {path_to_sink}")
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
                                    lista_nodos_copy = lista_nodos_copy + path_buffer
                                    # self.lista_nodos_copy = path_buffer
                                    ##################################

                                    vector_01 = []
                                    for no in single_buffer:
                                        vector_01 = vector_01 + [lista_mapping[no][0]]
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
                                    lista_nodos_copy = lista_nodos_copy + path_buffer
                                    ##################################

                                    vector_01 = []
                                    for no in single_buffer:
                                        vector_01 = vector_01 + [lista_mapping[no][0]]
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
                        if self.s_prints == 'qldebug':
                            print(f"the resulting flags are {valid_source} and {valid_sink}")
                        if valid_source and valid_sink:
                            valid_place = True
                            # as the mapping is valid we create a special node to specify the re-computation
                            # print("test of recomputation node",sink_buffer,source_buffer,nodo_AG)
                            if self.s_prints == 'qldebug':
                                print(f"estamos checando el bug 01 {element_buffer}")
                            try:
                                if not isinstance(element_buffer[0][0], bool):
                                    numero_time_slots = len(element_buffer) - 1

                                else:
                                    numero_time_slots = 0
                            except:
                                numero_time_slots = 0

                            dummy_buffer = [False, sink_buffer, source_buffer, numero_time_slots, 0]
                            special_nodes_list.append(dummy_buffer)
                        # valid_place = False
                else:
                    if self.s_prints == 'qldebug':
                        print("bug x-1")
                    valid_place = False


            else:
                # in this case, the predecessor is not mapped in the same time slot
                try:
                    if self.s_prints == 'qldebug':
                       print(f"the node place is {node_place} and the valid sinks are "
                             f"{self.list_sinks_connected_to_rc}")

                    datapath_buffer = []
                    datapaths = self.generation_datapaths(self.DG)
                    for path_element in datapaths:
                        if node_place in path_element:
                            datapath_buffer = path_element
                            break

                    if node_place in self.list_sinks_connected_to_rc:
                        nodo_sink = node_place
                    else:
                        #### este es un bug tenemos que checar bien que pasa
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        done = True
                        counter_internal = 0
                        while done:
                            if copy_list_sinks_connected_to_rc:
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            else:
                                counter_internal = counter_internal + 1
                                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                                sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                              copy_list_sinks_connected_to_rc,
                                                                              node_place)
                            # print(sink_nodo_sink_task,resource)
                            if element_buffer[contador_time_slots][sink_nodo_sink_task][0] \
                                    or sink_nodo_sink_task not in datapath_buffer:
                                copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                                if counter_internal == 5:
                                    # copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()

                                    sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
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
                    if self.s_prints == 'qldebug':
                        print(f"the resulting sink is {nodo_sink} the node place is {node_place}")
                    if resource in self.sources_DG:
                        nodo_source = resource
                    else:
                        nodo_source = source_node_from_any_node(self.DG, self.sources_DG, resource)
                    if self.s_prints == 'qldebug':
                        print(f"the resulting nodo source is {nodo_source}, the resource is {resource}")
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
                                vector_01 = vector_01 + [lista_mapping[no][0]]
                            # print(vector_01)
                            if not True in vector_01:
                                # print("test 01")
                                bandera_mapping_valido_time_slots_source = True
                                # print("test 02")
                                vector_02 = vector_02 + [False]
                                # print("test 03")
                                lista_nodos_copy = lista_nodos_copy + path_buffer + [nodo_source]
                                # print("test 04")
                                break
                    else:
                        if resource in self.sources_DG:
                            bandera_mapping_valido_time_slots_source = True
                    ############proceso para el sink dentro de element buffer
                    if self.s_prints == 'qldebug':
                        print(f"bandera de source is {bandera_mapping_valido_time_slots_source}")
                    paths_sinks = simple_paths_from_two_nodes(self.DG, node_place, nodo_sink)
                    if self.s_prints == 'qldebug':
                        print("solo checando bug",paths_sinks)
                    path_buffer_respaldo = []
                    if paths_sinks:
                        # for path in paths_sinks:
                        while paths_sinks:

                            path_b = min(paths_sinks, key=len)
                            if self.s_prints == 'qldebug':
                                print(f" el path seleccionado es {path_b}, {node_place}, {nodo_sink}")
                                print(element_buffer)
                            path_buffer_respaldo = list(path_b)
                            if node_place in path_b:
                                path_b.remove(node_place)
                            if nodo_sink in path_b:
                                path_b.remove(nodo_sink)
                            vector_01 = []
                            if path_b:

                                for nod_path in path_b:
                                    if self.s_prints == 'qldebug':
                                        print(f"debug error {nod_path} *+- ")
                                        print(element_buffer[contador_time_slots])
                                        print(element_buffer[contador_time_slots][nod_path])
                                    # if element_buffer[contador_time_slots][nod_path][0]\
                                    #         and element_buffer[contador_time_slots][nod_path][2] != 'copy':
                                    vector_01 = [element_buffer[contador_time_slots][nod_path][0]] + vector_01
                                    if self.s_prints == 'qldebug':
                                        print(f"estamos siguiendo el error")
                            else:
                                if self.s_prints == 'qldebug':
                                    print(f"no hay path debug error bla")
                                bandera_mapping_valido_time_slots_sink = True
                                break
                            if self.s_prints == 'qldebug':
                                print(f"estamos reparando el bug {vector_01}")
                            if not True in vector_01:
                                bandera_mapping_valido_time_slots_sink = True
                                break
                            else:
                                cuenta_paths_sinks = len(paths_sinks)
                                for n in range(0, cuenta_paths_sinks):
                                    if paths_sinks[n] == path_buffer_respaldo:
                                        paths_sinks.remove(n)
                                        break

                    else:
                        if self.s_prints == 'qldebug':
                            print("entramos en uno error de que no hay paths")
                        if nodo_sink == node_place:
                            bandera_mapping_valido_time_slots_sink = True
                    if self.s_prints == 'qldebug':
                        print(f"the resulting flags are {bandera_mapping_valido_time_slots_sink} and {bandera_mapping_valido_time_slots_source}")
                    lista_nodos_copy_time_slot = []

                    if bandera_mapping_valido_time_slots_sink and bandera_mapping_valido_time_slots_source:
                        if path_buffer_respaldo:
                            lista_nodos_copy_time_slot = lista_nodos_copy_time_slot + path_buffer_respaldo

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

                        time_slot_copy_nodes = contador_time_slots
                        bandera_time_slots = True
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
                    if self.s_prints == 'qldebug':
                        print("creo que entramos al estado excepcion")
                    valid_place = False

            vector_valid_places = vector_valid_places + [valid_place]
        if self.s_prints == 'qldebug':
            print("vector valid places", vector_valid_places)
            # input("debug verification of dependence - Enter to continue")
        if False in vector_valid_places:
            final_valid = False
            bandera_time_slots = False
        else:
            final_valid = True
            # for i in self.lista_nodos_copy_time_slot:


        ####ultima validacion, buscamos que si la tarea es un sink, donde se va a mapear sea
        # igual un sink o tenga un path hacia un sink
        if nodo_AG in self.sinks_AG:
            if resource in self.list_sinks_connected_to_rc:
                pass
            else:
                # because the predecessor is not a sink node we search for a sink node that is reachable from
                # the predecessor
                # print("We are going to check if the predecessor is mapped to a node that can reach a sink")

                #############""
                datapaths = self.generation_datapaths(self.DG)
                datapath_buffer = []
                for path in datapaths:
                    if resource in path:
                        datapath_buffer = path
                        break
                copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                done = True
                counter_internal = 0
                while done:
                    if copy_list_sinks_connected_to_rc:
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                    else:
                        counter_internal = counter_internal + 1
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                    # print(sink_nodo_sink_task,resource)
                    if lista_mapping[sink_nodo_sink_task][0] or sink_nodo_sink_task not in datapath_buffer:
                        copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                        if counter_internal == 5:
                            # copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc
                            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                          copy_list_sinks_connected_to_rc,
                                                                          resource)
                            done = False
                            break

                    else:
                        done = False
                        break

                #########"""

                sink = sink_nodo_sink_task  # sink_node_from_any_node(self.DG, self.list_sinks_connected_to_rc, node_place)
                if self.s_prints == 'qldebug':
                    print("el sink en verificacion de algo ", sink)
                path_to_sink = simple_paths_from_two_nodes(self.DG, resource, sink)
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
                        # single_buffer.remove(resource)

                        # esto es para indicar los nodos copy
                        path_buffer = list(single_buffer)
                        if resource in path_buffer:
                            path_buffer.remove(resource)
                        # lista_nodos_copy = lista_nodos_copy + path_buffer
                        # self.lista_nodos_copy = path_buffer
                        ##################################

                        vector_01 = []
                        for no in single_buffer:
                            vector_01 = vector_01 + [lista_mapping[no][0]]
                        # print(vector_01)
                        if True in vector_01:
                            vector_02 = vector_02 + [False]
                        else:
                            vector_02 = vector_02 + [True]
                            break
                    if False in vector_02:
                        final_valid = False
                    # else:
                    #     if final_valid
                    #     final_valid = True
                        # path_buffer = list(single_buffer)
                        # if resource in path_buffer:
                        #     path_buffer.remove(resource)
                        # self.lista_nodos_copy = self.lista_nodos_copy + path_buffer
                        # sink_buffer = sink

                else:
                    final_valid = False


        return final_valid, special_nodes_list, lista_nodos_copy, lista_nodos_copy_time_slot, \
               bandera_time_slots, time_slot_copy_nodes


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
            self.dict_nodes_h[resource]['ops'][self.AG_app.nodes[node_AG]['op']]['latency']

        # now we are going to look for the actual function in the info dict
        for data in self.dict_info_h['functions_res']:
            if data == name_function:
                function_formula = self.dict_info_h['functions_res'][data]

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
        if self.s_prints == 'qldebug':
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

        if self.s_prints == 'qldebug':
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
                if self.s_prints == 'qldebug':
                    # basic validation of the variable
                    print(param_formula)
                # in here we are going to look the value in the dict of the nodes and use globals to assign the value
                # to the variable
                # todo: maybe in here we can introduce other equations or other function like sin or cos
                for pa in self.dict_nodes_a[node_AG]['param']:
                    if self.s_prints == 'qldebug':
                        print("formula test ")
                        print(pa, self.dict_nodes_a[node_AG]['param'][pa])
                    if param_formula == pa:
                        globals()[pa] = self.dict_nodes_a[node_AG]['param'][pa]

        # the next step is the computing latency, in the framework it is also an equation so we need to perform some
        # steps
        # first we obtain the name of the equation
        name_clk = self.dict_nodes_h[resource][
            'ops'][
            self.AG.nodes[node_AG]['op']][
            'clk']
        if self.s_prints == 'debug':
            print(self.dict_info_h)

        # second we obtain the actual equation from the info dict
        value_clk = None
        for el in self.dict_info_h['functions_res']:
            if el == name_clk:
                value_clk = self.dict_info_h['functions_res'][el]

        # if we dont find the equation we raise an error
        if value_clk == None:
            raise UnboundLocalError(f"Parameter {name_clk} is not described in the functions section")

            ######ahora obtendremos el valor de la latencia de computo, debido a que puede ser una ecuacion o una
            # constante necesitamos hacer una verificacion previa y tambien sacar los valores
            # normalmente ya tenemos la ecuacion, entonces es separarla y asignar valores
        # now we have the equation, it can be a string or a constant so we verify which one is it
        if isinstance(value_clk, str):
            # if the computing latency is an equation
            if self.s_prints == 'qldebug':
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

            if self.s_prints == 'qldebug':
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
            if self.s_prints == 'qldebug':
                print("the final value of the equation is  ", value_clk)
        else:
            # if the equation is an integer we dont do anything
            value_clk = value_clk

        # now we have the computing latency and the paramters and we can evaluate the entire equation, but as we said
        # it can be an integer or a string so we check it
        if isinstance(function_formula, str):
            resultado_latencia = eval(function_formula) * self.dict_info_h['max_clk'] + value_clk
        else:
            resultado_latencia = function_formula * self.dict_info_h['max_clk'] + value_clk
        # finally we evaluate the latency if this resource is the last item of the critical path
        # todo: in here we need to change this to a general form
        resultado_latencia_total = width * height * value_clk

        if self.s_prints == 'qldebug':
            print(
                f"we exit the obtention latency function, the values are {resultado_latencia} and {resultado_latencia_total}")
        return resultado_latencia, resultado_latencia_total




    def only_actuator_sink(self, node_AG, resource):
        actuator_sink = None
        if node_AG in self.sinks_AG and resource not in self.sinks_DG:
            if self.s_prints == 'qldebug':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES - bug")
            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                          self.sinks_DG,
                                                          resource)
            path_sink_node = simple_paths_from_two_nodes(self.DG_copy,
                                                         resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'qldebug':
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
                        self.DG_copy.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.sinks_DG_total.copy()
            if self.s_prints =='qldebug':
                print(f"the place is {lugar_sink_t}, copia sinks {copia_sinks}")
            if lugar_sink_t in copia_sinks:
                actuator_sink = lugar_sink_t
            else:
                while done:
                    sink_test = copia_sinks.pop()
                    if simple_paths_from_two_nodes(self.DG_total, lugar_sink_t, sink_test):
                        actuator_sink = sink_test
                        done = False
                        break

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
                if self.AG.nodes[node_AG]['name'] == \
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

    def generation_copy_nodes(self, node_AG, resource, lista_mapping):
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
        bandera_source_of_data, info_sensor = self.verification_of_source(node_AG, resource,self.sources_AG)
        actuator_sink = None
        datapaths = self.generation_datapaths(self.DG)
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

            if self.s_prints == 'qldebug':
                print("WE ARE GOING TO ADD THE FINAL COPY NODES")
            # we obtain a sink node from the resource
            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
            copy_list_sinks_connected_to_rc.reverse()
            done = True
            counter_internal = 0

            datapath_buffer = []
            for path in datapaths:
                if resource in path:
                    datapath_buffer = path
                    break
            if self.s_prints == 'qldebug':
                print(f"the path of the resource is {datapath_buffer} and the resource is {resource}")

            bandera_sucesor = True
            sucesores_resource = self.DG_copy.successors(resource)
            for suc in sucesores_resource:
                if suc in copy_list_sinks_connected_to_rc:
                    sink_nodo_sink_task = suc
                    bandera_sucesor = False
                    break
            bandera_path = False
            if bandera_sucesor:
                while done:
                    if copy_list_sinks_connected_to_rc:
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                    else:
                        counter_internal = counter_internal + 1
                        copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                      copy_list_sinks_connected_to_rc,
                                                                      resource)
                    # print(sink_nodo_sink_task,resource)
                    if self.s_prints == 'qldebug':
                        print(f"checaremos el sink {sink_nodo_sink_task} si esta en {datapath_buffer}")
                    if lista_mapping[sink_nodo_sink_task][0] or sink_nodo_sink_task not in datapath_buffer:
                        copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                        if counter_internal == 5:
                            copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                            sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                                                                          copy_list_sinks_connected_to_rc,
                                                                          resource)
                            done = False
                            break

                    else:
                        done = False
                        break
                        # if sink_nodo_sink_task in datapath_buffer:
                        #     done = False
                        #     bandera_path = True
                        #     break
                        # else:
                        #     copy_list_sinks_connected_to_rc.remove(sink_nodo_sink_task)
                        #     # if counter_internal == 5:
                        #     #     copy_list_sinks_connected_to_rc = self.list_sinks_connected_to_rc.copy()
                        #     #     sink_nodo_sink_task = sink_node_from_any_node(self.DG_copy,
                        #     #                                                   copy_list_sinks_connected_to_rc,
                        #     #                                                   resource)
                        #     #     done = False
                        #     #     break

            # now we obtain the path from the resource to the sink node

            path_sink_node = simple_paths_from_two_nodes(self.DG_copy,
                                                         resource,
                                                         sink_nodo_sink_task)
            if self.s_prints == 'qldebug' or debug:
                # basic validation
                print("the paths between the sink task and the sink hardware",
                      path_sink_node)
                print(
                    f"the selected sink is {sink_nodo_sink_task} "
                    f"the sink task is {node_AG} and the sink of the hardware graph {resource}")
            # now we obtain the shortest path
            single_path = min(path_sink_node, key=len)
            # single_path = path_sink_node.pop()
            # we remove the resource from that path
            single_path.remove(resource)
            if self.s_prints == 'qldebug':
                print(f"el path es {single_path}, debug error de conectores")
            # and now we start assingning copy operations to all the nodes in the path
            for nodo_a_sink in single_path:
                if lista_mapping[nodo_a_sink][0] and lista_mapping[nodo_a_sink][3] != 'copy':
                    pass
                else:
                    lista_mapping[nodo_a_sink] = [True, None, 'copy', 'copy', 0, nodo_a_sink,
                                                  node_AG, 0, latency, latency, info_sensor, 0, 0]
            # now we end the addition of the copy nodes we need to find the name of the actuator that we used
            lugar_sink_t = None
            for s_nodos in self.DG_total:
                if self.DG_total.nodes[s_nodos]['name'] == \
                        self.DG_copy.nodes[sink_nodo_sink_task]['name']:
                    lugar_sink_t = s_nodos
            done = True
            copia_sinks = self.sinks_DG_total.copy()
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
                path_source_node = simple_paths_from_two_nodes(self.DG_copy, source_nodo,
                                                               resource)
                # print(path_source_node)
                if self.s_prints == 'qldebug' or debug:
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
                        if lista_mapping[no][2] != 'copy':
                            vector_test.append(lista_mapping[no][0])
                    if self.s_prints == 'qldebug':
                        print(single_path)
                    if not True in vector_test:
                        for nodo_a_source in single_path:
                            if debug:
                                print(nodo_a_source)
                            if lista_mapping[nodo_a_source][0] and lista_mapping[nodo_a_source][3] != 'copy':
                                pass
                            else:
                                lista_mapping[nodo_a_source] = [True, None, 'copy', 'copy', 0, nodo_a_source,
                                                                node_AG, 0, latency, latency, info_sensor, 0, 0]
                        bandera_salida = True
                        break
                if bandera_salida:
                    if debug:
                        print(lista_mapping)
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

        return actuator_sink, lista_mapping




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
        for n in self.dict_info_h['functions_res']:
            if n == latency_variable:
                latency = self.dict_info_h['functions_res'][n]
        return latency
















































