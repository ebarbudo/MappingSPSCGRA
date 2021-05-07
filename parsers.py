
import os
import sys
import networkx as nx
from os import path
from graphviz import Digraph
from fpdf import FPDF
from PyPDF2 import PdfFileMerger
import random
import subprocess




def constrains_read_v1(filepath):
    if not os.path.isfile(filepath):
        print("File path {} does not exist. Exiting...".format(filepath))
        sys.exit()

    with open(filepath) as myFile:
        text = myFile.read()
    result = text.split('\n')
    done = True
    temp = ''
    lineas = []
    while done:
        elemento = ''
        # we test if there is more lines in the variable that holds all the text file
        if result:
            elemento = result.pop(0)
        else:
            done = False
        # if the line starts with a # or a space we just discarded it
        if elemento.startswith('#') or not elemento.strip():
            pass
        else:
            # if we find a ';' we integrate the line with the temporal strings and put it in the general
            # variable that holds all the complete lines
            if ';' in elemento:
                temp = temp + elemento.strip(';')
                linea = temp
                lineas.append(linea)
                temp = ''
            else:
                # because we havent found any ';' we store the string in the temporal variable
                temp = temp + elemento
    # print(lineas)
    lista_constraints = []
    lista_tareas_constrains = []
    for linea_unica in lineas:
        if linea_unica == 'mapping':
            pass
        else:
            vector = linea_unica
            vector = vector.split(',')
            vector_temporal = [vector[0].strip('['), vector[1].strip(']')]
            lista_constraints.append(vector_temporal)
            lista_tareas_constrains.append(vector[0].strip('['))

    return lista_tareas_constrains, lista_constraints







def text_to_graph_v4(filepath,type_graph):
    '''
    function to parse the config file and obtain the input graphs and info dicts
    :param filepath: path to file
    :param type_graph: what type of input that we are going to create, options: 'hw', 'app'
    :return: depending of the type of graph we return the following items:

        'app'
        name_graph = graph with only tasks
        dict_nodes_tasks = dictionary with the information of only the tasks
        dict_nodes_total = dictionary with the information of the complete application graph
        total_graph = complete application graph
        last two items are not used

        'hw'
        name_graph = graph with only the processing resources
        dict_nodes = dictionary with the info of only the processing resources
        info = info of the config cost and latency
        total_graph = complete hardware graph
        dict_total = dictionary with the information of the complete hardware graph
        copy_total_graph = unroll graph

    '''

    if not os.path.isfile(filepath):
        print("File path {} does not exist. Exiting...".format(filepath))
        sys.exit()
    name_graph = nx.DiGraph()
    total_graph = nx.DiGraph()
    with open(filepath) as myFile:
        text = myFile.read()
    result = text.split('\n')
    # print("ijnifn")


    if type_graph =='hw':
        info = {}
        # info['config'] = {}
        dict_nodes = {}
        dict_nodes_t = {}
        dict_nodes_p = {}
        dict_total = {}
        counter_nodes = 0
        flag_cfg = False
        flag_fun = False
        flag_res = False
        flag_rp = False
        # global variables that we need to obtain from the file
        l_cfg_par = None
        l_cfg_op = None
        cfg_function = None
        flag_name_res = True
        flag_type_res = False
        flag_config_res = False
        flag_fun_res = False
        flag_name_res = True
        flag_type_res = False
        flag_config_res = False
        flag_fun_res = False

        info['functions_cfg'] = {}
        info['functions_res'] = {}
        vector_clks = []
        # the following cycle helps to form the basic lines for the parser, what we do is to wait until we find
        # a ';' and form the line, even if, in the configuration file, the information is break into several
        # lines, we form one single line with the information required for the parser
        done = True
        temp = ''
        lineas = []
        while done:
            elemento = ''
            # we test if there is more lines in the variable that holds all the text file
            if result:
                elemento = result.pop(0)
            else:
                done = False
            # if the line starts with a # or a space we just discarded it
            if elemento.startswith('#') or not elemento.strip():
                pass
            else:
                # if we find a ';' we integrate the line with the temporal strings and put it in the general
                # variable that holds all the complete lines
                if ';' in elemento:
                    temp = temp + elemento.strip(';')
                    linea = temp
                    lineas.append(linea)
                    temp = ''
                else:
                # because we havent found any ';' we store the string in the temporal variable
                    temp = temp + elemento


        # now that we have all the complete lines we start the process
        for linea_unica in lineas:

            # the first thing is to detect if we are dealing with the configuration information, functions or
            # resources information, for this we detect the words 'configuration', 'functions' and 'resources'
            # and we activate the correct flags, we can add more fields if necessary

            if linea_unica == 'configuration' or linea_unica == 'functions' or linea_unica=='resources':

                if linea_unica == 'configuration':
                    flag_cfg = True
                    flag_fun = False
                    flag_res = False
                elif linea_unica == 'functions':
                    flag_cfg = False
                    flag_fun = True
                    flag_res = False
                elif linea_unica == 'resources':
                    flag_cfg = False
                    flag_fun = False
                    flag_res = True

            # the first field is the configuration field, in here we store the configuration cost functions and their
            # variables, each one in one key of the dictionary, we dont use branching in here
            # the key for accessing the information will be
            # info['functions_cfg'][name of the variable or function]
            # we store everything in the info dictionary
            if flag_cfg:
                vector = linea_unica
                # print("hay algo raro")
                # print(vector)
                vector = vector.split('=')
                if len(vector) > 1:
                    # print(vector)
                    if vector[0].strip() == 'type':
                        info['functions_cfg']['type_cfg'] = vector[1].strip()
                    else:
                        try:
                            # we remove any extra space
                            vector[1] = vector[1].replace(" ","")
                            info['functions_cfg'][vector[0].strip()] = int(vector[1].strip())
                        except:
                            # we remove any extra space
                            vector[1] = vector[1].replace(" ","")
                            info['functions_cfg'][vector[0].strip()] = vector[1].strip()

            # now we are going to parse the functions, in here we can store several functions and their keys will be
            # info['function_res'][name of the function]
            if flag_fun:
                vector = linea_unica
                vector = vector.split('=')
                if len(vector) > 1:
                    try:
                        # we remove the extra space
                        vector[1] = vector[1].replace(" ","")
                        info['functions_res'][vector[0].strip()] = int(vector[1])
                    except:
                        # we remove the extra space
                        vector[1] = vector[1].replace(" ","")
                        info['functions_res'][vector[0].strip()] = vector[1]

            # finally, we start to parse the resources information, in here we have several fields and each one
            # has a different information, the structure of the dictionary is as follows:
            # name of the dictionary =  dict_nodes_t
            # keys of the dictionary
            # general key for each node => dict_nodes_t[name of the node]
            # edges => dict_nodes_t[name of the node]['edges']
            #


            if flag_res:
                linea_unica = linea_unica.replace(" ","")
                if linea_unica == 'resources':
                    pass
                else:
                    # print(dict_nodes_t)
                    vector = linea_unica
                    vector = vector.split(',')
                    # the first thing to store is the name of the resource
                    if flag_name_res:
                        if len(vector) == 1 and not '=' in vector[0]:
                            name_node = vector[0]
                            dict_nodes_t[name_node] = {}
                            flag_name_res = False
                            flag_type_res = True
                    # next we will obtain the type of the resource and the output edges
                    elif flag_type_res:
                        # we check if the type of the resource is a valid one, if not we raise an error
                        if vector[0] == 'rp' or vector[0] == 'rm' or vector[0] == 'rmu' or vector[0] == 'rr' or vector[0] == 'rw' or vector[0] == 'ri':
                            # now that we know that the type of resource is valid we can extract the edges
                            dict_nodes_t[name_node]['type'] = vector[0]
                            vector.pop(0)
                            edges_buffer = []
                            for edge in vector:
                                # we remove the innecessary elements
                                edge = edge.strip('[')
                                edge = edge.strip(']')
                                edge = edge.strip()
                                edges_buffer.append(edge)
                            # print(edges_buffer)
                            # if edges_buffer:
                            dict_nodes_t[name_node]['edges'] = edges_buffer
                            # else:
                            #     dict_nodes_t[name_node]['edges'] = ''
                            flag_type_res = False
                            flag_config_res = True
                            flag_fun_res = False
                        else:
                            raise TypeError(f" the value of {vector[0]} does not correspond to a valid resource type, the node name is {name_node}")
                    elif flag_config_res:
                        # in here we store the information about the configuration cost for each resource, the first
                        # field should be the name of the function and the following ones the variables
                        # print(linea_unica)
                        copia_config = linea_unica
                        copia_config = copia_config.strip('[')
                        copia_config = copia_config.strip(']')
                        if copia_config:
                            if len(vector) == 1:
                                dict_nodes_t[name_node]['config'] = {}
                                dict_nodes_t[name_node]['config']['formula'] = copia_config
                            else:
                                # print(vector)
                                vector [0] = vector[0].strip('[')
                                dict_nodes_t[name_node]['config'] = {}
                                dict_nodes_t[name_node]['config']['formula'] = vector[0]
                                vector.pop(0)
                                for n in range(0,len(vector)):
                                    parametro = vector[n]
                                    parametro = parametro.split('=')
                                    try:
                                        # in here we can use the name of the parameter described in the file or any name
                                        dict_nodes_t[name_node]['config'][parametro[0]] = int(parametro[1].strip(']'))
                                    except:
                                        raise ValueError(f"the value of the parameter {parametro[0]} of node {name_node} is not correct")
                        else:
                            dict_nodes_t[name_node]['config'] = {}
                            dict_nodes_t[name_node]['config']['formula'] = None


                        flag_config_res = False
                        flag_fun_res = True
                    elif flag_fun_res:
                        # now we reach the final stage per node, the type of tasks that the resource can perform
                        # print(vector)
                        vector[0] = vector[0].strip('[')
                        vector[len(vector) - 1] = vector[len(vector) - 1 ].strip(']')
                        # we declare this counter to know which element we are dealing with, the counter will be
                        # zero for the name of the task, will be one for the parameters of the task and two for the
                        # latency function, if we add more fields we can do it
                        conteo_dato = 0
                        dict_nodes_t[name_node]['ops'] = {}
                        # print(" el vector original es ", vector)
                        # print(dict_nodes_t)
                        for dato in vector:
                            # print(dato,conteo_dato)
                            if conteo_dato == 0:
                                # the first thing is the name of the task
                                name_task = dato.strip('[')
                                dict_nodes_t[name_node]['ops'][name_task] = {}
                                dict_nodes_t[name_node]['ops'][name_task]['param'] = {}
                                conteo_dato = conteo_dato + 1
                            elif conteo_dato == 1:
                                # the second thing is the parameters of the data, for some cases it can be
                                # none, like for the interface resources

                                copia_dato = dato.split('=')
                                # first case, if there are no parameters
                                if len(copia_dato) == 1:
                                    dato = dato.strip('[')
                                    dato = dato.strip(']')
                                    if dato:
                                        # print("bug")
                                        dict_nodes_t[name_node]['ops'][name_task]['latency'] = dato.strip('[')
                                        conteo_dato = 3
                                    else:
                                        dict_nodes_t[name_node]['ops'][name_task]['param'] = None
                                        conteo_dato = conteo_dato + 1
                                else:
                                    # now, in here we have several cases,
                                    # first, if the parameter values are in a range
                                    copia_rango = copia_dato[1].split('|')
                                    if len(copia_rango) > 1 :
                                        try:
                                            limite_inferior = int(copia_rango[0].strip('['))
                                        except:
                                            raise ValueError(f" the value {copia_rango[0]} of parameter {name_task} from  resource {name_node} is not valid")
                                        try:
                                            limite_superior = int(copia_rango[1].strip(']'))
                                        except:
                                            raise ValueError(f" the value {copia_rango[1]} of parameter {name_task} from resource {name_node} is not valid")

                                        dict_nodes_t[name_node]['ops'][name_task]['param'][copia_dato[0].strip('[')] = [limite_inferior,limite_superior]

                                    else:
                                        # we split the string with ',' as a separator, this will give us the parameters
                                        # that represent a set of fixed values o possible values either integer or strings
                                        copia_elementos = copia_dato[1].split(',')
                                        if len(copia_elementos) > 1 :
                                            temporal_parametros = []
                                            for valor in copia_elementos:
                                                # we remove the square brackets
                                                valor = valor.strip('[')
                                                valor = valor.strip(']')
                                                try:
                                                    temporal_parametros.append(int(valor))
                                                except:
                                                    temporal_parametros.append((valor))
                                            dict_nodes_t[name_node]['ops'][name_task]['param'][copia_dato[0].strip('[')] = temporal_parametros
                                        else:
                                            # it could be the case that the values of the parameter are a set of strings
                                            # for this case we split with a '~' as a separator
                                            copia_strings = copia_dato[1].split('~')
                                            if len(copia_strings) > 1:
                                                temporal_parametros = []
                                                for ele_string in copia_strings:
                                                    ele_string = ele_string.strip('[')
                                                    ele_string = ele_string.strip(']')
                                                    try:
                                                        temporal_parametros.append((ele_string))
                                                    except:
                                                        temporal_parametros.append((ele_string))
                                                dict_nodes_t[name_node]['ops'][name_task]['param'][copia_dato[0].strip('[')] = temporal_parametros
                                            else:
                                                # if it is not a range neither a set of fixed values, then it is a fix
                                                # value either integer or string
                                                # print(copia_dato)
                                                copia_dato[1] = copia_dato[1].strip('[')
                                                copia_dato[1] = copia_dato[1].strip(']')
                                                try:
                                                    dict_nodes_t[name_node]['ops'][name_task]['param'][
                                                        copia_dato[0].strip('[')] = [int(copia_dato[1]), int(copia_dato[1])]
                                                except:
                                                    if copia_dato[1] == 'boolean':
                                                        dict_nodes_t[name_node]['ops'][name_task]['param'][
                                                        copia_dato[0].strip('[')] = ['True','False']
                                                    else:
                                                        dict_nodes_t[name_node]['ops'][name_task]['param'][copia_dato[0].strip('[')] = copia_dato[1]
                            elif conteo_dato == 2:
                                # print("lllega hasta aui")
                                # print(dato)
                                dato = dato.strip(']')
                                dict_nodes_t[name_node]['ops'][name_task]['latency'] = dato.strip('[')
                                conteo_dato = 3
                            elif conteo_dato == 3:
                                dict_nodes_t[name_node]['ops'][name_task]['clk'] = dato.strip(']')
                                for latency in info['functions_res'].items():
                                    # print(latency)
                                    if latency[0] == dato.strip(']'):
                                        vector_clks.append(latency[1])
                                        # print("se encotnro algo")
                                # vector_clks.append(dato.strip(']'))
                                conteo_dato=0


                        flag_type_res = False
                        flag_config_res = False
                        flag_fun_res = False
                        flag_name_res = True


        # now we have the required information about the resources, and we are going to create the input graphs
        # we create two graphs, one we called total which has all the nodes from the configuration file and
        # another which we will called normal graph which only has the resources required for the mapping
        # print(info['functions_cfg']['type_cfg'])
        # print(info['functions_cfg']['cfg_function'])
        #print(vector_clks)
        info['max_clk'] = 0 #max(vector_clks)
        # print(info['max_clk'])
        # print(info['functions_res']['lat_com_r5'])
        #
        # for n in dict_nodes_t.items():
        #     print(n)
        #
        # print("we are going to print the dict_nodes_t")
        # print(dict_nodes_t)
        # for n in dict_nodes_t:
        #     print(n)
        # for n,data in dict_nodes_t.items():
        #     print(n)

        contador_nodos = 0
        for n , data in dict_nodes_t.items():
            # print(n)
            if data['type'] == 'rp' or data['type'] == 'rmu':
                dict_nodes[contador_nodos] = {}
                dict_nodes[contador_nodos]['name'] = n
                dict_nodes[contador_nodos]['type'] = data['type']
                dict_nodes[contador_nodos]['edges'] = data['edges']

                dict_nodes[contador_nodos]['ops'] = {}
                dict_nodes[contador_nodos]['ops'] = data['ops']
                # dict_total[contador_nodos]['fun_lat'] = {}
                dict_nodes[contador_nodos]['fun_lat'] = data['config']

                # dict_nodes[contador_nodos]['fun_lat_par'] = data['config']['param1']
                # dict_nodes[contador_nodos]['fun_lat_op'] = data['config']['param2']
                operations_vector = []
                for u in data['ops']:
                    operations_vector.append(u)
                name_graph.add_node(contador_nodos,op=operations_vector, name= n)
                contador_nodos += 1


        # print(info)

        dict_total = {}
        contador_nodos = 0
        vector_nombres = []
        # this vector will have the names of the memory resources, this will help to unroll the graph
        vector_unrolling_nodes = []
        for n, data in dict_nodes_t.items():
            # print(n)
            # print(data)
            if data['type'] == 'rp' or data['type'] == 'rmu':
                dict_total[contador_nodos] = {}
                dict_total[contador_nodos]['name'] = n
                dict_total[contador_nodos]['type'] = data['type']
                dict_total[contador_nodos]['edges'] = data['edges']
                dict_total[contador_nodos]['ops'] = {}
                dict_total[contador_nodos]['ops'] = data['ops']
                dict_total[contador_nodos]['fun_lat'] = {}
                dict_total[contador_nodos]['fun_lat'] = data['config']
                # print(data['config'])
                # dict_total[contador_nodos]['fun_lat_par'] = data['config']['param1']
                # dict_total[contador_nodos]['fun_lat_op'] = data['config']['param2']
                operations_vector = []
                for u in data['ops']:
                    operations_vector.append(u)
                total_graph.add_node(contador_nodos, op=operations_vector,name=n,lat=0,type=data['type'])

                contador_nodos += 1
            elif data['type'] == 'ri':# or data['type'] == 'rw' or data['type'] == 'rr':
                vector_nombres.append(n)
                dict_total[contador_nodos] = {}
                dict_total[contador_nodos]['name'] = n
                dict_total[contador_nodos]['type'] = data['type']
                dict_total[contador_nodos]['edges'] = data['edges']
                dict_total[contador_nodos]['ops'] = data['ops']
                try:
                    dict_total[contador_nodos]['lat'] = data['ops']['sensor']['clk']
                except:
                    dict_total[contador_nodos]['lat'] = data['ops']['actuator']['clk']
                dict_total[contador_nodos]['fun_lat'] = {}
                dict_total[contador_nodos]['fun_lat'] = data['config']
                # dict_total[contador_nodos]['fun_lat']['formula'] = 'None'
                dict_total[contador_nodos]['fun_lat_par'] = 0
                dict_total[contador_nodos]['fun_lat_op'] = 0

                for formula in info['functions_res'].items():
                    # print(formula)
                    if formula[0] == dict_total[contador_nodos]['lat']:
                        valor = formula[1]

                total_graph.add_node(contador_nodos, op='ri', lat=valor,name=n,type='ri')

                contador_nodos += 1
            elif data['type'] == 'rw' or data['type'] == 'rr':
                vector_nombres.append(n)
                dict_total[contador_nodos] = {}
                dict_total[contador_nodos]['name'] = n
                dict_total[contador_nodos]['type'] = data['type']
                dict_total[contador_nodos]['edges'] = data['edges']
                dict_total[contador_nodos]['ops'] = data['ops']

               # bug 01 - i think that we can merge together this try with an if below, where we add the node
                try:
                    dict_total[contador_nodos]['lat'] = data['ops']['write']['clk']
                except:
                    dict_total[contador_nodos]['lat'] = data['ops']['read']['clk']
                #
                dict_total[contador_nodos]['fun_lat'] = {}
                dict_total[contador_nodos]['fun_lat'] = data['config']
                # dict_total[contador_nodos]['fun_lat']['formula'] = 'constant'
                dict_total[contador_nodos]['fun_lat_par'] = 2
                dict_total[contador_nodos]['fun_lat_op'] = 2
                # print(dict_total[contador_nodos]['lat'])
                # print(info['functions_res'])
                for formula in info['functions_res'].items():
                    # print(formula)
                    if formula[0] == dict_total[contador_nodos]['lat']:
                        valor = formula[1]
                        # print(valor)
                if data['type'] == 'rw':
                    total_graph.add_node(contador_nodos, op='rw', lat=valor ,name = n,type='rw')
                else:
                    total_graph.add_node(contador_nodos, op='rr',lat=valor,name = n,type='rr' )
                contador_nodos += 1
            elif data['type'] == 'rm':
                vector_nombres.append(n)
                dict_total[contador_nodos] = {}
                dict_total[contador_nodos]['name'] = n
                dict_total[contador_nodos]['type'] = data['type']
                # print(data['edges'])
                dict_total[contador_nodos]['edges'] = data['edges']
                dict_total[contador_nodos]['fun_lat'] = {}
                dict_total[contador_nodos]['fun_lat'] = data['config']
                # dict_total[contador_nodos]['fun_lat']['formula'] = 'None'
                dict_total[contador_nodos]['ops'] = data['ops']
                dict_total[contador_nodos]['fun_lat_par'] = 0
                dict_total[contador_nodos]['fun_lat_op'] = 0
                total_graph.add_node(contador_nodos, op='rm',lat=0 , name = n, type='rm')
                vector_unrolling_nodes.append(contador_nodos)
                contador_nodos += 1



        # print(dict_total)
        # print(total_graph.nodes)
        # edges para el grafo total
        for n, data in dict_total.items():
            if data['type']:
                for ed in data['edges']:
                    # print("edge", ed)
                    if ed:
                        number_edge = None
                        for el, d in dict_total.items():

                            if d['name'] == ed:
                                # print(d['name'], el)
                                number_edge = el
                        if number_edge == None:
                            print(f"Error : Value of edge {ed} not valid, verify input file")
                            raise ValueError
                        else:
                            # print(f"addition of edge from  {n} y el nombre real es {number_edge}")
                            total_graph.add_edge(n, number_edge)

        # edges del grafo de processing resources
        # print(vector_nombres)
        for n, data in dict_nodes.items():
            if data['type'] == 'rp' or data['type'] == 'rmu':
                for ed in data['edges']:
                    # print("edge", ed)
                    if ed:
                        if ed not in vector_nombres:
                            number_edge = None
                            for el, d in dict_nodes.items():
                                if d['name'] == ed:

                                    # print(d['name'],el)
                                    number_edge = el
                            if number_edge == None:
                                print(f"Error : Value of edge {ed} not valid, verify input file")
                                raise ValueError
                            else:
                                # print(f"addition of edge from  {n} y el nombre real es {number_edge}")
                                name_graph.add_edge(n, number_edge)

        #
        # we have the total_graph, but we need to change the display format
        # print(dict_total)

        # for nodo in total_graph.nodes:
        #     print(nodo,total_graph.nodes[nodo])
        # print("debug of the unroll procedure")
        # print(vector_unrolling_nodes)
        copy_total_graph = total_graph.copy()
        for nodo in total_graph:
            # print(total_graph.nodes[nodo])
            predecesores_ri = []
            predecesores_normal = []
            sucesores_ri = []
            sucesores_normal = []
            if nodo in vector_unrolling_nodes:
                # first we try to find the predecessors and the successors, we also make a division between the
                # interface nodes and the rest of them
                predecesores = total_graph.predecessors(nodo)

                if len(list(total_graph.predecessors(nodo))) > dict_total[nodo]['ops']['memory']['param']['ch_wr'][0]:
                    raise ValueError(f"number of implemented write channels of memory node {dict_total[nodo]['name']} exceed the maximum value")

                for pre in predecesores:
                    if total_graph.nodes[pre]['op'] == 'ri':
                        predecesores_ri.append(pre)
                    else:
                        predecesores_normal.append(pre)
                sucesores = total_graph.successors(nodo)
                if len(list(total_graph.successors(nodo))) > dict_total[nodo]['ops']['memory']['param']['ch_rd'][0]:
                    raise ValueError(f"number of implemented read channels of memory node {dict_total[nodo]['name']} exceed the maximum value")
                for suc in sucesores:
                    # print(total_graph.nodes[suc])
                    if total_graph.nodes[suc]['op'] == 'ri':
                        sucesores_ri.append(suc)
                    else:
                        sucesores_normal.append(suc)
                # print("ahora verificaremos los predecesores y sucesores y su tipo ")
                # # print(predecesores,sucesores)
                # print(predecesores_ri,predecesores_normal,sucesores_normal,sucesores_ri)
                # now that we have the predecessors and the successors separated we remove the memory node and
                # start to interconnect the rest
                # print(sucesores_normal,sucesores_ri,predecesores_normal,predecesores_ri)
                copy_total_graph.remove_node(nodo)
                # we store the data from the memory node
                copy_op = total_graph.nodes[nodo]['op']
                copy_name = total_graph.nodes[nodo]['name']
                copy_lat = total_graph.nodes[nodo]['lat']
                primera_vez_memory = True
                # start the unrolling
                variable_number_nodos = len(copy_total_graph.nodes)
                contador_nodos_unrolling = len(copy_total_graph.nodes) + 1
                # print()
                # first case we only have one sensor
                vector_parejas_prede = []
                if len(predecesores_ri) == 1:

                    copy_total_graph.add_node(nodo,op=copy_op, name=copy_name,lat=copy_lat)

                    for s_n in sucesores_normal:
                        # print("el nodo solo bla", copy_name, nodo,s_n)
                        copy_total_graph.add_edge(predecesores_ri[0],nodo)
                        copy_total_graph.add_edge(nodo,s_n)
                        # nodo = nodo  + 1
                        # contador_nodos_unrolling = contador_nodos_unrolling + 1
                elif len(predecesores_ri) == len(sucesores_normal):
                    # print("test 01",predecesores_ri,sucesores_normal)
                    # prede_copia = predecesores_normal.copy()
                    for nodo_ri in predecesores_ri:
                        # print("deberia de generar dos aqui",contador_nodos_unrolling,"tests")
                        nodo_normal = sucesores_normal.pop()
                        copy_total_graph.add_node(contador_nodos_unrolling,op=copy_op,name=copy_name,lat=copy_lat)
                        copy_total_graph.add_edge(nodo_ri,contador_nodos_unrolling)
                        copy_total_graph.add_edge(contador_nodos_unrolling,nodo_normal)
                        contador_nodos_unrolling = contador_nodos_unrolling + 1


                else:
                    copy_total_graph.add_node(contador_nodos_unrolling,op=copy_op,name=copy_name,lat=copy_lat)
                    for s_n in sucesores_normal:
                        copy_total_graph.add_edge(contador_nodos_unrolling,s_n)
                    for nodo_ri in predecesores_ri:
                        copy_total_graph.add_edge(nodo_ri,contador_nodos_unrolling)
                #####hace falta mas casos
                contador_nodos_unrolling = len(copy_total_graph.nodes) +1
                # print("bibdsfsd")
                nodo = contador_nodos_unrolling
                if len(sucesores_ri) == 1:
                    copy_total_graph.add_node(nodo,op=copy_op,name=copy_name,lat=copy_lat)
                    for p_n in predecesores_normal:
                        # print("path")
                        # print("ahora es el predecesor", nodo,p_n,copy_name)
                        copy_total_graph.add_edge(p_n,nodo)
                        copy_total_graph.add_edge(nodo,sucesores_ri[0])
                        contador_nodos_unrolling = contador_nodos_unrolling + 1
                elif len(sucesores_ri) == len(predecesores_normal):
                    # print("test ddd")
                    for nodo_ri in sucesores_ri:
                        # print("deberia de genera dos aqui",contador_nodos_unrolling)
                        nodo_normal = predecesores_normal.pop()
                        # print(nodo_ri,copy_total_graph.nodes[nodo_ri])
                        copy_total_graph.add_node(contador_nodos_unrolling,op=copy_op,name=copy_name,lat=copy_lat)
                        copy_total_graph.add_edge(nodo_normal,contador_nodos_unrolling)
                        copy_total_graph.add_edge(contador_nodos_unrolling,nodo_ri)
                        contador_nodos_unrolling = contador_nodos_unrolling +  1
                else:

                    copy_total_graph.add_node(contador_nodos_unrolling,name=copy_name,lat=copy_lat,op=copy_op)
                    for p_n in predecesores_normal:
                        copy_total_graph.add_edge(p_n,contador_nodos_unrolling)
                    for nodo_ri in sucesores_ri:
                        copy_total_graph.add_edge(contador_nodos_unrolling,nodo_ri)



        # for elemento in dict_nodes_t.items():
        #     print(elemento)

        dict_nodes_h = dict_nodes
        dict_total_h = dict_total

        return name_graph ,dict_nodes_h,info,total_graph,dict_total_h,copy_total_graph


    #################################################
    # APPLICATION
    #############################################
    else:

        # the following cycle helps to form the basic lines for the parser, what we do is to wait until we find
        # a ';' and form the line, even if, in the configuration file, the information is break into several
        # lines, we form one single line with the information required for the parser
        done = True
        temp = ''
        lineas = []
        lista_nodos_interface = []
        while done:
            elemento = ''
            # we test if there is more lines in the variable that holds all the text file
            if result:
                elemento = result.pop(0)
            else:
                done = False
            # if the line starts with a # or a space we just discarded it
            if elemento.startswith('#') or not elemento.strip():
                pass
            else:
                # if we find a ';' we integrate the line with the temporal strings and put it in the general
                # variable that holds all the complete lines
                if ';' in elemento:
                    temp = temp + elemento.strip(';')
                    linea = temp
                    lineas.append(linea)
                    temp = ''
                else:
                    # because we havent found any ';' we store the string in the temporal variable
                    temp = temp + elemento


        vector_nombres = []
        counter_nodes = 0
        counter_nodes_total = 0
        dict_nodes = {} # dictionary with the info of each node
        dict_nodes_total = {}
        dict_nodes_tasks = {}
        flag_name_task = True
        flag_type_task = False
        flag_param_task = False

        for elemento in lineas:

            vector = elemento
            vector = vector.split(',')
            # the first thing to store is the name of the resource
            if flag_name_task:
                if len(vector) == 1 and not '=' in vector[0]:
                    name_node = vector[0]
                    dict_nodes[name_node] = {}
                    flag_name_task = False
                    flag_type_task = True
            elif flag_type_task:
                # now that we know that the type of resource is valid we can extract the edges
                type_task = vector[0].split()
                if type_task[0] == 'interface':
                    lista_nodos_interface.append(name_node)
                dict_nodes[name_node]['type'] = type_task[0]
                vector.pop(0)
                edges_buffer = []
                for edge in vector:
                    # we remove the innecessary elements
                    edge = edge.strip('[')
                    edge = edge.strip(']')
                    edge = edge.strip()
                    edges_buffer.append(edge)
                # print(edges_buffer)
                # if edges_buffer:
                dict_nodes[name_node]['edges'] = edges_buffer
                # else:
                #     dict_nodes_t[name_node]['edges'] = ''
                flag_type_task = False
                flag_param_task = True
                flag_name_task = False

            elif flag_param_task:
                # now we reach the final stage per node, the type of tasks that the resource can perform
                # print(vector)
                vector[0] = vector[0].strip('[')
                vector[len(vector) - 1] = vector[len(vector) - 1].strip(']')
                # we declare this counter to know which element we are dealing with, the counter will be
                # zero for the name of the task, will be one for the parameters of the task and two for the
                # latency function, if we add more fields we can do it
                conteo_dato = 0
                dict_nodes[name_node]['param'] = {}


                if vector[0]:
                    for dato in vector:
                        # print(dato)
                        copia_dato = dato.split('=')
                        copia_dato[0] = copia_dato[0].strip('[')
                        copia_dato[0] = copia_dato[0].strip(']')
                        copia_dato[0] = copia_dato[0].strip()
                        copia_dato[1] = copia_dato[1].strip('[')
                        copia_dato[1] = copia_dato[1].strip(']')
                        copia_dato[1] = copia_dato[1].strip()
                        # print("antes de",copia_dato[0],copia_dato[1])
                        try:
                            dict_nodes[name_node]['param'][copia_dato[0].strip('[')] = int(copia_dato[1])
                        except:
                            dict_nodes[name_node]['param'][copia_dato[0].strip('[')] = copia_dato[1]
                else:
                    dict_nodes[name_node]['param'] = None
                flag_name_task = True
                flag_param_task = False
                flag_type_task = False

        # print(dict_nodes)

        # we are going to create two dictionaries, one with the data of only the tasks and the other with the data of
        # all the nodes

        counter_total = 0
        counter_tasks = 0
        for n, data in dict_nodes.items():
            if data['type'] == 'interface':
                dict_nodes_total[counter_total] = {}
                dict_nodes_total[counter_total]['name'] = n
                dict_nodes_total[counter_total]['op'] = data['type']
                dict_nodes_total[counter_total]['edges'] = data['edges']
                dict_nodes_total[counter_total]['param'] = data['param']
                counter_total = counter_total + 1
            else:
                dict_nodes_total[counter_total] = {}
                dict_nodes_total[counter_total]['name'] = n
                dict_nodes_total[counter_total]['op'] = data['type']
                dict_nodes_total[counter_total]['edges'] = data['edges']
                dict_nodes_total[counter_total]['param'] = data['param']
                counter_total = counter_total + 1

                dict_nodes_tasks[counter_tasks] = {}
                dict_nodes_tasks[counter_tasks]['name'] = n
                dict_nodes_tasks[counter_tasks]['op'] = data['type']
                copia_edges = []
                for ed in data['edges']:
                    if ed not in lista_nodos_interface:
                        copia_edges.append(ed)
                dict_nodes_tasks[counter_tasks]['edges'] = copia_edges
                dict_nodes_tasks[counter_tasks]['param'] = data['param']
                counter_tasks = counter_tasks + 1

        # print(lista_nodos_interface)
        # print(dict_nodes_tasks)
        # print(dict_nodes_total)
        #

        # now we are going to create the graph
        # we are going to create two graphs one that shows the all the nodes and another one that we are going to use
        # for the mapping
        #the first one will be the one with only the tasks

        for n, data in dict_nodes_tasks.items():
            name_graph.add_node(n, name = data['name'], op=data['op'], par=data['param'])
            # print(data['edges'])
            for ed in data['edges']:
                # print(ed)
                number_edge = None
                for el, d in dict_nodes_tasks.items():
                    # print(d['name'],ed)
                    if d['name'] == ed:
                        number_edge = el
                if number_edge == None:
                    print(f"Error : Value of edge {ed} not valid, verify input file")
                    raise ValueError
                else:
                    # print(f"addition of edge from  {n} y el nombre real es {number_edge}")
                    name_graph.add_edge(n, number_edge)

        # the second one will have all the nodes of the application graph

        for n, data in dict_nodes_total.items():
            total_graph.add_node(n, name=data['name'], op=data['op'], par=data['param'])
            # print(data['edges'])
            if data['edges'][0]:
                for ed in data['edges']:
                    # print(ed)
                    number_edge = None
                    for el, d in dict_nodes_total.items():
                        # print(d['name'],ed)
                        if d['name'] == ed:
                            number_edge = el
                    if number_edge == None:
                        print(f"Error : Value of edge {ed} not valid, verify input file")
                        raise ValueError
                    else:
                        # print(f"addition of edge from  {n} y el nombre real es {number_edge}")
                        total_graph.add_edge(n, number_edge)
        # print(dict_nodes_tasks)
        # print(dict_nodes_total)
    return name_graph, dict_nodes_tasks, dict_nodes_total,total_graph, [],[]
