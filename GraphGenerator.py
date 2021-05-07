import networkx as nx
import time
from graphviz import Digraph
from itertools import permutations
import os
import sys
import networkx as nx
from os import path
from graphviz import Digraph
from fpdf import FPDF
from PyPDF2 import PdfFileMerger
import random
import GraphVisualization
import datetime
from basic_functions import obtencion_sinks,obtencion_sources,simple_paths_from_two_nodes




class GraphGeneration:


    def __init__(self,filepath,app_num = 0,hw_num=0,folderpath='/outputfiles/',s_prints=None,name_file=None,debug=None,
                 memory_enable=True,mux_prob=0,no_instances=False):
        # print(filepath)
        ########generacion del folder para los archivos de salida
        dir_path = os.path.dirname(os.path.realpath(__file__))
        directorio = dir_path + folderpath
        try:
            os.mkdir(directorio)
        except:
            # print(f"the directory {folderpath} already exists, the files could be overwritten")
            pass
        self.memory_enable = memory_enable
        self.mux_prob = mux_prob
        self.no_instances = no_instances
        self.folderpath = directorio
        self.s_prints = s_prints
        self.name_file = name_file
        self.debug = debug
        self.debugging = True
        ############general variables - initialization





        self.read_file(filepath)
        # print(self.list_computing_latency)
        ### this variable is for the structure of the graph
        self.tipo = ['parallel', 'serial', 'normal']
        ###this variable is for the type of configuration, there is no other tan parallel and sequential
        self.configuration_list = ['parallel', 'sequential']


        ## cuenta los nodos que tienen un grado mayor de uno, pero no tiene mayor importancia
        self.numero_limite = 2
        done = True
        self.hw_num = hw_num

        # self.dag_generation()
        if app_num != 0:

            self.number_app = app_num

        contador = 0
        while done:
            if contador == 100:
                raise RecursionError("An application can not be created, verify the graph generator file")
            # try:
            self.dag_generation()
            if self.s_prints == 'basic':
                print("regreso de la generacion del hardware",contador)
            self.generator_config_file_hw()
            if self.s_prints == 'basic':
                print("regreso de la generacion del archivo",contador)
            self.dict_aplicaciones ={}
            if self.s_prints == 'basic':
                print("DENTRO DEL GENERADOR PERO EN LA ETAPA DOS",contador)

                # for n, data in self.dict_nodes_total.items():
                #     print(n, data)

            # done = False
            try:
                for n in range(0,self.number_app):
                    if self.s_prints == 'basic':
                        print("dentro de aplicaciones ",contador)
                    self.dict_aplicaciones[n] = {}
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
        # print("DENTRO DEL GENERADOR ETAPA TRES")
        # for n, data in self.dict_nodes_total.items():
        #     print(n, data)
        # print(len(self.dict_aplicaciones))

    def generator_config_file_hw(self):
        ### tenemos que checar un bug con las memorias, debemos de juntarlas si su nombre es el mismo
        if self.s_prints == 'graphgenerator':
            print("entramos en la creacion del archivo de hw")
        # print(self.dict_info)

        #####creacion del archivo
        date_object = datetime.date.today()
        if self.name_file != None:
            nombre =   'hardware' + self.name_file + str(date_object) + '-' + str(self.hw_num) + '.txt'
        else:
            nombre = 'hardware' + str(date_object) + '-' + str(self.hw_num) + '.txt'
        self.nombre_archivo_hw = os.path.join(self.folderpath,nombre)

        #####escritura de datos
        with open(os.path.join(self.folderpath,nombre),'w') as filehandle:
            #### header
            filehandle.write("# HARDWARE DESCRIPTION\n")
            #### parte de la configuracion
            filehandle.write("configuration;\n")
            filehandle.write("type=")
            filehandle.write(self.dict_info['functions_cfg']['type_cfg'])
            filehandle.write(";\n")
            #### parte de las funciones de configuracion
            for data in self.dict_info['functions_cfg']:
                if data != 'type_cfg':
                    filehandle.write(data)
                    filehandle.write("=")
                    try:
                        filehandle.write(self.dict_info['functions_cfg'][data])
                    except:
                        filehandle.write(str(self.dict_info['functions_cfg'][data]))
                    filehandle.write(";\n")
            filehandle.write("\n")
            filehandle.write("########----------------------\n")
            filehandle.write("\n")

            #####parte de las funciones de latencia
            filehandle.write("functions;\n")
            for data in self.dict_info['functions_res']:
                filehandle.write(data)
                filehandle.write("=")
                try:
                    filehandle.write(self.dict_info['functions_res'][data])
                except:
                    filehandle.write(str(self.dict_info['functions_res'][data]))
                filehandle.write(";\n")
            filehandle.write("\n")
            filehandle.write("########----------------------\n")
            filehandle.write("\n")
            #### iniciamos la escritura de los datos de cada uno de los recursos
            filehandle.write("resources;\n")
            filehandle.write("\n")

            for n,data in self.dict_nodes_total.items():
                filehandle.write("\n")
                filehandle.write(data['name'])
                filehandle.write(";\n")
                filehandle.write(data['type'])
                filehandle.write(",")
                vector_edges = []
                filehandle.write("[")
                primera_edge = True
                for edge in data['edges']:
                    # print(edge)
                    if primera_edge:
                        try:
                            filehandle.write(edge)
                        except:
                            filehandle.write(str(edge))
                        primera_edge = False
                    else:
                        filehandle.write(",")
                        try:
                            filehandle.write(edge)
                        except:
                            filehandle.write(str(edge))


                #     try:
                #         # print(self.dict_total[int(edge)]['name'])
                #         vector_edges.append(int(self.dict_total[int(edge)]['name']))
                #     except:
                #         vector_edges.append(edge)
                # # filehandle.write(str(data['edges']))
                # print(vector_edges)
                # try:
                #     filehandle.write(vector_edges)
                # except:
                #     filehandle.write((str(vector_edges)))

                filehandle.write("];\n")
                filehandle.write("[")
                for parametro in data['fun_lat']:
                    if parametro=='formula' and data['fun_lat']['formula'] != None:
                        filehandle.write(data['fun_lat']['formula'])

                    else:
                        if parametro and data['fun_lat'][parametro] != None:
                            filehandle.write(",")
                            filehandle.write(parametro)
                            filehandle.write("=")
                            filehandle.write(str(data['fun_lat'][parametro]))
                filehandle.write("];\n")
                filehandle.write("[")
                primera = True
                limite = len(data['ops'])
                contador = 0
                if self.s_prints == 'graphgenerator':
                    print(data['ops'])

                for operacion in data['ops']:
                    if self.s_prints == 'graphgenerator':
                        print(operacion)
                    if primera:
                        filehandle.write("[")
                    else:
                        filehandle.write(",[")
                    filehandle.write(operacion)
                    filehandle.write(",")
                    if data['ops'][operacion]['param'] == None:
                        filehandle.write("[")



                    else:
                        filehandle.write("[")
                        primera_vez = True
                        for parametro in data['ops'][operacion]['param']:
                            lugar_operacion = None
                            for op in range(0,len(self.operations)):
                                if operacion == self.operations[op]:
                                    lugar_operacion = op
                            if self.s_prints == 'graphgenerator':
                                print("debug error 07 ", lugar_operacion, self.input_latency_list,op,self.operations, operacion)
                            try:
                                lista_parametros = self.input_latency_list[lugar_operacion][2]
                                # print(lista_parametros)
                            except:
                                # pass
                                if operacion == 'multiplexor':
                                    lista_parametros = [['entrada','vectorvalues'],['salida','vectorvalues']]
                                else:
                                    pass
                                    # lista_parametros = None


                            info_parametro = data['ops'][operacion]['param'][parametro]
                            if self.s_prints == 'graphgenerator':
                                if operacion == 'multiplexor':
                                    print(info_parametro)
                                    # input('test')
                            tipo_parametro = None


                            if operacion == 'multiplexor':
                                tipo_parametro = 'vectorvalues'
                            else:
                                for elemento_lista in lista_parametros:
                                    if elemento_lista[0] == parametro:
                                        tipo_parametro = elemento_lista[1]
                            if self.s_prints == 'graphgenerator':
                                if operacion == 'multiplexor':
                                    print("el nombre del parametro es ", parametro, " y su tipo es ", tipo_parametro)
                                    print(info_parametro)

                            if tipo_parametro != None:
                                if primera_vez:
                                    # filehandle.write("[")
                                    filehandle.write(parametro)
                                    filehandle.write("=")
                                    filehandle.write("[")
                                    if tipo_parametro == "range":
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write("|")
                                        filehandle.write(str(info_parametro[1]))
                                        filehandle.write("]")
                                        primera_vez = False
                                    elif tipo_parametro == "fixvalue":
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write("]")
                                        primera_vez = False
                                    elif tipo_parametro == "fixstring":
                                        filehandle.write(info_parametro[0])
                                        filehandle.write("]")
                                        primera_vez = False
                                    elif tipo_parametro == "boolean":
                                        filehandle.write("boolean")
                                        filehandle.write("]")
                                        primera_vez = False
                                    elif tipo_parametro == 'vectorstring':
                                        for stg in range(0, len(info_parametro)):
                                            filehandle.write(info_parametro[stg])
                                            if stg != len(info_parametro) - 1:
                                                filehandle.write("~")
                                        filehandle.write("]")
                                        primera_vez = False
                                    elif tipo_parametro == 'vectorvalues':
                                        for stg in range(0,len(info_parametro)):
                                            filehandle.write(str(info_parametro[stg]))
                                            if stg != len(info_parametro) - 1:
                                                filehandle.write("~")
                                        filehandle.write("]")
                                        primera_vez = False
                                else:
                                    filehandle.write(",")
                                    filehandle.write(parametro)
                                    filehandle.write("=")
                                    filehandle.write("[")
                                    if tipo_parametro == "range":
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write("|")
                                        filehandle.write(str(info_parametro[1]))
                                        filehandle.write("]")

                                    elif tipo_parametro == "fixvalue":
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write("]")

                                    elif tipo_parametro == "fixstring":
                                        filehandle.write(info_parametro[0])
                                        filehandle.write("]")

                                    elif tipo_parametro == "boolean":
                                        filehandle.write("boolean")
                                        filehandle.write("]")

                                    elif tipo_parametro == 'vectorstring':
                                        for stg in range(0, len(info_parametro)):
                                            filehandle.write(info_parametro[stg])
                                            if stg != len(info_parametro) - 1:
                                                filehandle.write("~")
                                        filehandle.write("]")

                                    elif tipo_parametro == 'vectorvalues':
                                        for stg in range(0, len(info_parametro)):
                                            filehandle.write(str(info_parametro[stg]))
                                            if stg != len(info_parametro) - 1:
                                                filehandle.write("~")
                                        filehandle.write("]")
                            else:

                                if len(info_parametro) == 2 and isinstance(info_parametro[0],int) and isinstance(info_parametro[1],int):
                                    if primera_vez:
                                        # filehandle.write("[")
                                        filehandle.write(parametro)
                                        filehandle.write("=")
                                        filehandle.write("[")
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write('|')
                                        filehandle.write(str(info_parametro[1]))
                                        filehandle.write("]")
                                        primera_vez = False
                                    else:
                                        filehandle.write(",")
                                        filehandle.write(parametro)
                                        filehandle.write("=")
                                        filehandle.write("[")
                                        filehandle.write(str(info_parametro[0]))
                                        filehandle.write('|')
                                        filehandle.write(str(info_parametro[1]))
                                        filehandle.write("]")




                            # if len(info_parametro) == 2 and isinstance(info_parametro[0],int) and isinstance(info_parametro[1],int):
                            #     if primera_vez:
                            #         filehandle.write("[")
                            #         filehandle.write(parametro)
                            #         filehandle.write("=")
                            #         filehandle.write(str(info_parametro[0]))
                            #         filehandle.write('|')
                            #         filehandle.write(str(info_parametro[1]))
                            #         filehandle.write("]")
                            #         primera_vez = False
                            #     else:
                            #         filehandle.write(",[")
                            #         filehandle.write(parametro)
                            #         filehandle.write("=")
                            #         filehandle.write(str(info_parametro[0]))
                            #         filehandle.write('|')
                            #         filehandle.write(str(info_parametro[1]))
                            #         filehandle.write("]")
                    filehandle.write("],")
                    filehandle.write("[")
                    try:
                        filehandle.write(data['ops'][operacion]['latency'])
                        filehandle.write(",")
                        filehandle.write(data['ops'][operacion]['clk'])
                    except:
                        filehandle.write(data['ops'][operacion]['param']['latency'])
                        filehandle.write(",")
                        filehandle.write(data['ops'][operacion]['param']['clk'])
                    contador = contador + 1
                    if contador == limite:
                        filehandle.write("]]")
                    else:
                        filehandle.write("]],")
                filehandle.write("];\n")


            filehandle.write("\n####-------------END OF FILE")



        filehandle.close()


    def generator_config_file_app(self,n):
        nombre =   'application' + str(n) + '-' + str(self.hw_num) + '.txt'
        with open(os.path.join(self.folderpath,nombre), 'w') as filehandle:
            filehandle.write("# APPLICATION DESCRIPTION\n")
            for n,data in self.dict_aplicacion_total.items():
                filehandle.write(data['name'])
                filehandle.write(";\n")
                filehandle.write(data['op'])
                filehandle.write(",")
                edges = ""
                primera_vez = True
                for e in data['edges']:
                    if primera_vez:
                        edges =  e
                        primera_vez = False
                    else:
                        edges = edges +"," + e
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
        return os.path.join(self.folderpath,nombre)


    def read_file(self,filepath):
        # print(type(filepath))
        if not os.path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            sys.exit()
        name_graph = nx.DiGraph()
        total_graph = nx.DiGraph()
        with open(filepath) as myFile:
            text = myFile.read()
        myFile.close()
        result = text.split('\n')
        # print(result)
        done = True
        temp = ''
        lineas = []
        #### we read the entire txt
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

        ######flags for each element
        flag_number_nodes = False
        flag_input_degree = False
        flag_output_degree = False
        flag_number_actuators = False
        flag_number_sensors = False
        flag_number_memories = False
        flag_limit_address_rm = False
        flag_limit_address_rc = False
        flag_configuration_list = False
        flag_latency_functions = False
        flag_operations_list = False
        flag_limit_parameters = False
        flag_computing_latency = False
        flag_limit_parameter_range = False
        flag_parameter_string_list = False
        flag_parameter_value_list = False
        flag_latency_copy = False
        flag_number_of_applications = False
        flag_resolutions = False ### todo esto se tiene que modificar por el numero de samples
        flag_nodes_to_remove = False
        flag_limit_parallel = False
        flag_limit_serial = False
        flag_error = False
        flag_input_samples = False
        flag_type_application = False
        flag_limit_computing_latency = False
        flag_mux_enable = False
        flag_memory_enable = False

        ####main parser, we check each field and store the information of each one
        for linea_unica in lineas:
            # print(linea_unica)
            copy_linea = linea_unica
            copy_linea = copy_linea.replace(" ", "")
            copy_linea = copy_linea.split('=')
            if len(copy_linea) != 1:
                if copy_linea[0] == 'number_nodes':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        if int(temporal_copy_linea) > 4:
                            self.nodes = int(temporal_copy_linea) - 0
                        else:
                            self.nodes = int(temporal_copy_linea) -0
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for number of nodes")
                    flag_number_nodes = True
                elif copy_linea[0] == 'node_input_degree':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.input_degree = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for input degree")
                    flag_input_degree = True
                elif copy_linea[0] == 'node_output_degree':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.output_degree = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for output degree")
                    flag_output_degree = True
                elif copy_linea[0] == 'number_actuators':
                    try:
                        self.sinks = int(copy_linea[1])
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for number of actuators")
                    flag_number_actuators = True
                elif copy_linea[0] == 'number_sensors':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.sources = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for number of sensors")
                    flag_number_sensors = True
                elif copy_linea[0] == 'number_rm':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.memory_limit = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not "
                            f"a valid value for the limit number of rm (memory resources)")
                    flag_number_memories = True
                elif copy_linea[0] == 'limit_address_space_rm':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.limite_address_space = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid"
                            f" value for the limit of address space of the rm (memory resources)")
                    flag_limit_address_rm = True
                elif copy_linea[0] == 'limit_address_space_rc':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.limite_address_single = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a "
                            f"valid value for the limit of address space of the rc (communication resources")
                    flag_limit_address_rc = True
                elif copy_linea[0] == 'limit_parameters':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.limite_tareas = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid value for "
                            f"the limit of parameters")
                    flag_limit_parameters = True
                elif copy_linea[0] == 'computing_latency':
                    # print("entrada")
                    self.list_computing_latency = []
                    lista_computing_latency = copy_linea[1].replace(" ", "")
                    lista_computing_latency = lista_computing_latency.split('],[')
                    # print(lista_input_latency)
                    for c in lista_computing_latency:
                        # print(c)
                        temporal_c = c
                        temporal_c = temporal_c.split(',')
                        nombre = temporal_c[0].strip('[')
                        valor = temporal_c[1].strip(']')
                        try:
                            temporal_append = [nombre,int(valor)]
                            self.list_computing_latency.append(temporal_append)
                        except:
                            temporal_append = [nombre,valor]
                            self.list_computing_latency.append(temporal_append)
                    flag_computing_latency = True
                elif copy_linea[0] == 'configuration_functions_list':
                    self.configuration_functions_list = []
                    lista_configuraciones = copy_linea[1].replace(" ","")
                    lista_configuraciones = lista_configuraciones.split('],[')
                    for c in lista_configuraciones:
                        temporal_c = c
                        temporal_c = temporal_c.split(',')
                        nombre = temporal_c[0].strip('[')
                        valor = temporal_c[1].strip(']')
                        parametros = None
                        if len(temporal_c) > 2:
                            parametros = temporal_c[2:]

                        try:
                            temporal_append = [nombre,int(valor)]
                            self.configuration_functions_list.append(temporal_append)
                        except:
                            if parametros != None:
                                lista_parametros = []
                                for p in parametros:
                                    p = p.split('-')
                                    try:
                                        temporal_parametro = [p[0].strip('['), int(p[1].strip(']'))]
                                    except:
                                        raise ValueError(f"Error in the graph generator file, the number "
                                                         f"{copy_linea[1]} is not a valid value for parameters of "
                                                         f"configuration cost function")
                                    lista_parametros.append(temporal_parametro)
                                temporal_append = [nombre, valor,lista_parametros]
                            else:
                                temporal_append = [nombre, valor]
                        self.configuration_functions_list.append(temporal_append)
                    # print(self.configuration_functions_list)
                    flag_configuration_list = True
                elif copy_linea[0] == 'input_latency_functions':
                    self.input_latency_list = []
                    lista_input_latency = copy_linea[1].replace(" ", "")
                    lista_input_latency = lista_input_latency.split('],[')
                    # print(lista_input_latency)
                    for c in lista_input_latency:
                        # print(c)
                        temporal_c = c
                        temporal_c = temporal_c.split(',')
                        nombre = temporal_c[0].strip('[')
                        valor = temporal_c[1].strip(']')
                        parametros = None
                        if len(temporal_c)>2:
                            parametros = temporal_c[2:]
                        # print(parametros)
                        try:
                            temporal_append = [nombre, int(valor)]
                            self.input_latency_list.append(temporal_append)
                        except:
                            if parametros != None:
                                lista_parametros = []
                                for p in parametros:
                                    p = p.split('-')
                                    temporal_parametro = [p[0].strip('['),p[1].strip(']')]
                                    lista_parametros.append(temporal_parametro)
                                temporal_append = [nombre, valor,lista_parametros]
                            else:
                                temporal_append = [nombre, valor]
                            self.input_latency_list.append(temporal_append)
                    flag_latency_functions = True
                elif copy_linea[0] == 'limit_range':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split(',')
                    # print(temporal_copy_linea[0])
                    try:
                        valor_minimo = int(temporal_copy_linea[0].strip('['))
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} "
                                         f"is not a valid value for the range of the parameters")

                    try:
                        valor_maximo = int(temporal_copy_linea[1].strip(']'))
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} "
                                         f"is not a valid value for the range of the parameters")
                    self.limite_rango = [valor_minimo, valor_maximo]
                    # print(self.limite_rango)
                    flag_limit_parameter_range = True
                elif copy_linea[0] == 'strings_list':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split(',')
                    self.vector_strings = []
                    for c in temporal_copy_linea:
                        temporal_c = c.strip('[')
                        temporal_c = temporal_c.strip(']')
                        self.vector_strings.append(temporal_c)
                    flag_parameter_string_list = True
                elif copy_linea[0] == 'resolutions':
                    self.resoluciones = []
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split('],[')
                    for c in temporal_copy_linea:
                        temporal_c = c
                        temporal_c = temporal_c.split(',')
                        try:
                            valor_uno = temporal_c[0].strip('[')
                            valor_uno = int(valor_uno)
                        except:
                            raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} "
                                             f"is not valid value for resolution")
                        try:
                            valor_dos = temporal_c[1].strip(']')
                            valor_dos = int(valor_dos)
                        except:
                            raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]}"
                                             f" is not valid value for resolution")
                        temporal_resolucion = [valor_uno,valor_dos]
                        self.resoluciones.append(temporal_resolucion)
                    flag_resolutions = True
                elif copy_linea[0] == 'nodes_to_remove':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.nodos_a_remover = int(temporal_copy_linea)
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} is"
                                         f" not a valid value for nodes to remove")
                    flag_nodes_to_remove = True
                elif copy_linea[0] == 'limit_parallel_ins':
                    temporal_copy_linea = copy_linea[1].replace(" ","")
                    try:
                        self.numero_paralelo = int(temporal_copy_linea)
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} is not a "
                                         f"valid value for the limit of parallel instances")
                    flag_limit_parallel = True
                elif copy_linea[0] == 'limit_serial_ins':
                    temporal_copy_linea = copy_linea[1].replace(" ","")
                    try:
                        self.numero_serial = int(temporal_copy_linea)
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} is "
                                         f"not a valid value for the limit of serial instances")
                    flag_limit_serial = True
                elif copy_linea[0] == 'fixed_values':
                    self.vector_fix_values = []
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split(',')

                    for c in temporal_copy_linea:
                        temporal_c = c.strip('[')
                        temporal_c = temporal_c.strip(']')
                        try:
                            valor = int(temporal_c)
                        except:
                            raise ValueError(
                                f"Error in the graph generator file, the number {copy_linea[1]} is not a "
                                f"valid value for fixed values")
                        self.vector_fix_values.append(valor)
                    flag_parameter_value_list = True
                    # print(self.vector_fix_values)
                    # input("test")
                elif copy_linea[0]== 'operations_list':
                    self.operations = []
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split(',')
                    for c in temporal_copy_linea:
                        temporal_c = c.strip('[')
                        temporal_c = temporal_c.strip(']')
                        self.operations.append(temporal_c)
                    # print(self.operations)
                    flag_operations_list = True
                elif copy_linea[0] == 'number_applications':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.number_app = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a valid "
                            f"value for the number of applications")
                    if self.number_app == 0:
                        raise ValueError(f"Error in the graph generator file, the number {self.number_app} is not a "
                                         f"valid value for the number of applications")
                    flag_number_of_applications = True
                elif copy_linea[0] == 'error_parameters':
                    if copy_linea[1] == 'true' or copy_linea[1] == 'false' or copy_linea[1] == 'TRUE' or \
                            copy_linea[1] == 'FALSE' or copy_linea[1] == 'False' or copy_linea[1] == 'True':
                        if copy_linea[1] == 'true' or copy_linea[1] == 'TRUE' or copy_linea[1] == 'True':
                            self.error_parametros = True
                        else:
                            self.error_parametros = False
                    else:
                        raise ValueError(f"Error in the graph generator file, the value {copy_linea[1]} is not a valid "
                                         f"value for error_parameters ")
                    flag_error = True
                elif copy_linea[0] == 'latency_copy':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.latency_copy_node = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a "
                            f"valid value for the latency of copy node")
                    flag_latency_copy = True
                elif copy_linea[0] == 'input_samples_range':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    temporal_copy_linea = temporal_copy_linea.split(',')
                    # print(temporal_copy_linea[0])
                    try:
                        valor_minimo = int(temporal_copy_linea[0].strip('['))
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} "
                                         f"is not a valid value for the range of input samples")

                    try:
                        valor_maximo = int(temporal_copy_linea[1].strip(']'))
                    except:
                        raise ValueError(f"Error in the graph generator file, the number {copy_linea[1]} "
                                         f"is not a valid value for the range of input samples")
                    self.input_samples = [valor_minimo, valor_maximo]
                    # print(self.limite_rango)
                    flag_input_samples = True
                elif copy_linea[0] == 'type_application':
                    if copy_linea[1] == 'image' or copy_linea[1] == 'signal':
                        self.type_application = copy_linea[1]
                    else:
                        raise  ValueError(f"Error in the graph generator file, the type {copy_linea[1]}"
                                          f" is not a valid type of application")
                    flag_type_application = True
                elif copy_linea[0] == 'limit_computing_latency':
                    temporal_copy_linea = copy_linea[1].replace(" ", "")
                    try:
                        self.limite_computing_latency = int(temporal_copy_linea)
                    except:
                        raise ValueError(
                            f"Error in the graph generator file, the number {copy_linea[1]} is not a "
                            f"valid value for the limit of the computing latency")
                    flag_limit_computing_latency = True
                elif copy_linea[0] == 'mux_enable':
                    if copy_linea[1] == 'true' or copy_linea[1] == 'false' or copy_linea[1] == 'TRUE' or \
                            copy_linea[1] == 'FALSE' or copy_linea[1] == 'False'  or copy_linea[1] == 'True':
                        if copy_linea[1] == 'true' or copy_linea[1] == 'True' or copy_linea[1] == 'TRUE':
                            self.mux_enable = True
                        else:
                            self.mux_enable = False
                        flag_mux_enable = True
                    else:
                        raise  ValueError(f"Error in the graph generator file, the value {copy_linea[1]} is not a "
                                          f"valid value for mux_enable")

                elif copy_linea[0] == 'memory_enable':
                    if copy_linea[1] == 'true' or copy_linea[1] == 'false' or copy_linea[1] == 'TRUE' or \
                            copy_linea[1] == 'FALSE' or copy_linea[1] == 'False'  or copy_linea[1] == 'True':
                        if copy_linea[1] == 'true' or copy_linea[1] == 'True' or copy_linea[1] == 'TRUE':
                            self.memory_enable = True
                        else:
                            self.memory_enable = False
                        flag_memory_enable = True
                    else:
                        raise  ValueError(f"Error in the graph generator file, the value {copy_linea[1]} is not a "
                                          f"valid value for memory_enable")

        if self.type_application == 'image' and not flag_resolutions:
            raise Exception(f"Error in the graph generator file, with type {self.type_application}, the field "
                            f"resolutions should be defined")
        if self.type_application == 'signal' and not flag_input_samples:
            raise Exception(f"Error in the graph generator file, with type {self.type_application}, the field "
                            f"input samples range should be defined")

        ## we verify that there is at least one type of input of data
        flag_input_data = False
        if flag_input_samples or flag_resolutions:
            flag_input_data = True
            flag_resolutions = True


        lista_elementos = [flag_number_nodes,flag_input_degree,flag_output_degree,flag_number_actuators,
                           flag_number_sensors,flag_number_memories,flag_limit_address_rm,flag_limit_address_rc,
                           flag_configuration_list,flag_latency_functions,flag_operations_list,flag_limit_parameters,
                           flag_computing_latency,flag_limit_parameter_range,flag_parameter_string_list,
                           flag_parameter_value_list,flag_latency_copy,flag_number_of_applications,flag_resolutions,
                           flag_nodes_to_remove,flag_limit_parallel,flag_limit_serial,flag_error,flag_type_application,
                           flag_input_data,flag_limit_computing_latency,flag_mux_enable,flag_memory_enable]
        ####we check that all fields had been completed
        if all(lista_elementos):
            pass
        else:
            elementos_faltantes = []
            for ele in range(len(lista_elementos)):
                if not lista_elementos[ele]:
                    if ele == 0:
                        elementos_faltantes.append('number_nodes')
                    elif ele == 1:
                        elementos_faltantes.append('node_input_degree')
                    elif ele == 2:
                        elementos_faltantes.append('node_output_degree')
                    elif ele == 3:
                        elementos_faltantes.append('number_actuators')
                    elif ele == 4:
                        elementos_faltantes.append('number_sensors')
                    elif ele == 5:
                        elementos_faltantes.append('number_rm')
                    elif ele == 6:
                        elementos_faltantes.append('limit_address_space_rm')
                    elif ele == 7:
                        elementos_faltantes.append('limit_address_space_rc')
                    elif ele == 8:
                        elementos_faltantes.append('configuration_functions_list')
                    elif ele == 9:
                        elementos_faltantes.append('input_latency_functions')
                    elif ele == 10:
                        elementos_faltantes.append('operations_list')
                    elif ele == 11:
                        elementos_faltantes.append('limit_parameters')
                    elif ele == 12:
                        elementos_faltantes.append('computing_latency')
                    elif ele == 13:
                        elementos_faltantes.append('limit_parameters')
                    elif ele == 14:
                        elementos_faltantes.append('strings_list')
                    elif ele == 15:
                        elementos_faltantes.append('fixed_values')
                    elif ele == 16:
                        elementos_faltantes.append('latency_copy')
                    elif ele == 17:
                        elementos_faltantes.append('number_applications')
                    elif ele == 18:
                        pass
                        # elementos_faltantes.append('resolutions')
                    elif ele == 19:
                        elementos_faltantes.append('nodes_to_remove')
                    elif ele == 20:
                        elementos_faltantes.append('limit_parallel_ins')
                    elif ele == 21:
                        elementos_faltantes.append('limit_serial_ins')
                    elif ele == 22:
                        elementos_faltantes.append('error_parameters')
                    elif ele == 23:
                        elementos_faltantes.append('type_application')
                    elif ele == 24:
                        elementos_faltantes.append('resolutions or input samples')
                    elif ele == 25:
                        elementos_faltantes.append('limit_computing_latency')
                    elif ele == 26:
                        elementos_faltantes.append('mux_enable')
                    elif ele == 27:
                        elementos_faltantes.append('memory_enable')

            raise ValueError(f"An error in the graph generator file has been encountered, please verify the following "
                             f"fields : {elementos_faltantes}")
        ###we check that the lenghss of the input latency, computing latency and tasks are the same
        if (len(self.list_computing_latency) == len(self.input_latency_list)) \
                and (len(self.list_computing_latency) == len(self.operations)):
            pass
        else:
            raise ValueError(f"An error has been encountered, please verify the number of elements in the fields :"
                             f" operations_list, input_latency_functions, computing_latency")

    def dag_generation(self):
       # generation of a random dag with a number of internal nodes (nodes that are not sinks nor sources, although
       #   because it is randomly created
       #      and it also a dag, an internal node can be a sink or a source but it is very rare), and a number of sinks
       #       and sources nodes, and with labels (operations)

        self.DG = nx.DiGraph()
        lista_entrada = []
        # print(self.nodes)
        max_clk_value = []
        contador_dobles = 0
        lista_salida = []
        done = True
        menos = 1
        distri_input_source = 50
        distri_output_sink = 50
        # while done:
        #     if (self.nodes - (self.sinks - menos) - (self.sources - menos) +1 ) > 0:
        #         numero_nodos = self.nodes - (self.sinks - menos) - (self.sources - menos) + 1
        #         done = False
        #     else:
        #         menos = menos + 1
        # self.nodes = numero_nodos
        #####in here we build the basic structure
        if self.s_prints == 'graphgenerator':
            print("the number of nodes from the specification file ",self.nodes)
            # input("yes")
        for x in range(0, self.nodes):
            nombre = 'r' + str(x)
            # print(nombre)
            self.DG.add_node(x,name=nombre,map=False)
            """"this node can have a connection with a source or with another internal node"""
            arco_input = bool(random.getrandbits(1))

            values_list = ["True", "False"]
            distribution_list = [distri_input_source, 100 - distri_input_source]
            arco_distri = random.choices(values_list, distribution_list, k=1)
            if arco_distri[0] == "True":
                arco_input = True
            else:
                arco_input = False

            if self.s_prints == 'graphgenerator':
                print(f"the selection of source or internal node is {arco_input}")

            if arco_input:
                """if the node is connected with a source node"""
                """"we select any source node randomly"""
                nodo_conector = random.randint(1, self.sources)
                nodo_conector_final = nodo_conector + self.nodes
                if not nodo_conector_final in lista_entrada:
                    nombre_interno = 'r' + str(nodo_conector_final)
                    self.DG.add_node(nodo_conector_final,name=nombre_interno,map=False)
                    """"we add the node to the source list"""
                    lista_entrada.append(nodo_conector_final)
                """""we verify if the degrees are correct"""
                if self.s_prints == 'graphgenerator':
                    print(f"the source is {nodo_conector_final}, the resource is {x}, and its name {nombre}")
                    print(f"the degrees are {self.DG.out_degree(nodo_conector_final)}, {self.output_degree}, "
                          f"{self.DG.in_degree(x)}, {self.input_degree} ")

                self.DG.add_edge(nodo_conector_final, x)
                test = nx.is_directed_acyclic_graph(self.DG)

                if self.DG.out_degree(nodo_conector_final) > self.output_degree or self.DG.in_degree(
                        x) > self.input_degree or not test:
                    # self.DG.add_edge(nodo_conector_final, x)
                    # test = nx.is_directed_acyclic_graph(self.DG)
                    """"now we test if we no created any cycle if there is a cycle we remove the edge"""
                    if self.s_prints == 'graphgenerator':
                        print("is acyclic", test)
                    # if not test:
                    self.DG.remove_edge(nodo_conector_final, x)
                    """"verificacion de grados mayores al definido"""
                if test:
                    if self.DG.degree(nodo_conector_final) > self.numero_limite - 1 or self.DG.degree(
                            x) > self.numero_limite - 1:
                        contador_dobles = contador_dobles + 1
            else:
                """we connect the new node to a internal node"""
                l = [i for i in range(self.nodes)]
                sucesores = list(self.DG.successors(x))
                l.remove(x)
                if sucesores:
                    for elements in sucesores:
                        l.remove(elements)
                if l:
                    nodo_conector = random.choice(l)
                    self.DG.add_edge(nodo_conector, x)
                    """"we check if we did not created a dag"""
                    test = nx.is_directed_acyclic_graph(self.DG)
                    if not test:
                        self.DG.remove_edge(nodo_conector, x)
                    """""we check if the degrees are correct"""
                    if self.DG.out_degree(nodo_conector) > self.output_degree or self.DG.in_degree(
                            x) > self.input_degree:
                        # print(self.DG.out_degree(nodo_conector),self.output_degree,self.DG.in_degree(
                        #     x),self.input_degree)
                        self.DG.remove_edge(nodo_conector, x)
                    else:
                        """"verificacion de grados mayores al definido"""
                        if self.DG.degree(nodo_conector) > self.numero_limite - 1 or self.DG.degree(
                                x) > self.numero_limite - 1:
                            contador_dobles = contador_dobles + 1

            """"we choose if we connect the node to a sink or to an internal node"""
            arco_output = bool(random.getrandbits(1))
            values_list = ["True", "False"]
            distribution_list = [distri_output_sink, 100 - distri_output_sink]
            arco_distri = random.choices(values_list, distribution_list, k=1)
            # print(arco_distri)
            # time.sleep(5)
            if arco_distri[0] == "True":
                arco_output = True
            else:
                arco_output = False

            if arco_output:
                """"we connect the node to a sink node"""
                nodo_conector = random.randint(1, self.sinks)
                nodo_conector_final = nodo_conector + self.nodes + self.sources

                if not nodo_conector_final in lista_salida:
                    nombre_interno = 'r' + str(nodo_conector_final)
                    self.DG.add_node(nodo_conector_final,name=nombre_interno,map=False)
                    lista_salida.append(nodo_conector_final)
                self.DG.add_edge(x, nodo_conector_final)
                test = nx.is_directed_acyclic_graph(self.DG)
                """""""""""we check the degree"""""""""
                if self.DG.out_degree(x) > self.output_degree or self.DG.in_degree(
                        nodo_conector_final) > self.input_degree or not test:
                    # self.DG.add_edge(x, nodo_conector_final)
                    # test = nx.is_directed_acyclic_graph(self.DG)
                    # if not test:
                    self.DG.remove_edge(x, nodo_conector_final)
                """"verificacion de grados mayores al definido"""

                if test:
                    if self.DG.degree(nodo_conector_final) > self.numero_limite - 1 or self.DG.degree(
                            x) > self.numero_limite - 1:
                        contador_dobles = contador_dobles + 1

            else:
                """we connect a node to a internal node"""
                l = [i for i in range(self.nodes)]
                # print(l)
                # time.sleep(5)
                predecesores = list(self.DG.predecessors(x))

                if predecesores:
                    for elements in predecesores:
                        if elements in l:
                            l.remove(elements)
                l.remove(x)
                if l:
                    nodo_conector = random.choice(l)
                    # print(nodo_conector)
                    # input("test")

                    self.DG.add_edge(x, nodo_conector)
                    test = nx.is_directed_acyclic_graph(self.DG)
                    # print(test)
                    # input("test")
                    if not test:
                        self.DG.remove_edge(x, nodo_conector)
                        """""we check if the degrees are correct"""
                    else:
                        if self.DG.out_degree(x) > self.output_degree or self.DG.in_degree(
                                nodo_conector) > self.input_degree:
                            self.DG.remove_edge(x, nodo_conector)
                            # input("test")
                        else:
                            """"verificacion de grados mayores al definido"""

                            if self.DG.degree(nodo_conector) > self.numero_limite - 1 or self.DG.degree(
                                    x) > self.numero_limite - 1:
                                contador_dobles = contador_dobles + 1

        if self.s_prints == 'graphgenerator':
            print("After the basic structure")
            print(len(self.DG.nodes))
            # input("tes")
        if self.s_prints == 'graphgenerator' and self.debugging:
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.DG, lista_vacia, 'app',
                                                          'random_dag_before_pruning', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')

        self.lista_paths = []
        lista_nodos_ocupados_sink = []
        lista_nodos_ocupados_source = []
        """""verify is there is a node with zero input degree and output degree"""
        list_nodes = list(self.DG.nodes)
        for element in list_nodes:
            if self.DG.out_degree(element) == 0 and self.DG.in_degree(element) == 0:
                self.DG.remove_node(element)

        """""we rename the nodes to have order"""
        lista_numeros = list(range(0, len(self.DG.nodes)))
        if self.s_prints == 'graphgenerator':
            print(f"the number of nodes before adding the memory nodes {len(self.DG.nodes)}")
            input_degree = []
            output_degree = []
            for nodo in self.DG.nodes:
                input_degree.append(self.DG.in_degree(nodo))
                output_degree.append(self.DG.out_degree(nodo))
            print(f"the vector of input degree is {input_degree} and the output degree is {output_degree}")









        # print("los nodos deben de estar ordenados hasta", len(self.DG.nodes),lista_numeros)
        for nodo_in_DG in self.DG.nodes:
            if nodo_in_DG in lista_numeros:
                lista_numeros.remove(nodo_in_DG)
        # print("lista restante",lista_numeros)
        for nodo_in_DG in self.DG.nodes:
            # print(nodo_in_DG,len(self.DG.nodes))
            if nodo_in_DG >= len(self.DG.nodes):
                # print("el nodos es conficltivo", nodo_in_DG)
                mapping = {nodo_in_DG: lista_numeros.pop()}
                self.DG = nx.relabel_nodes(self.DG, mapping)

        if self.s_prints == 'generatordebug' and self.debugging:
            copia_DG = self.DG.copy()
            input_list_degree = []
            output_list_degree = []
            for nodo in copia_DG.nodes:
                nombre = 'r' + str(nodo)
                copia_DG.nodes[nodo]['name'] = nombre
                output_list_degree.append(copia_DG.out_degree(nodo))
                input_list_degree.append(copia_DG.in_degree(nodo))

            lista_vacia = []
            # Graph_visual_00 = GraphVisualization.GraphRep([], copia_DG, lista_vacia, 'app',
            #                                               'random_dag_after_pruning', [], 'red',
            #                                               'black',
            #                                               'circle')
            # Graph_visual_00.f.render(view=False)
            # Graph_visual_00.f.render(view=True, format='pdf')
            print(f"number of nodes {len(copia_DG.nodes)}")
            out_dict = {i: output_list_degree.count(i) for i in output_list_degree}
            in_dict = {i: input_list_degree.count(i) for i in input_list_degree}

            print(f"input {in_dict}, output {out_dict} ")



        sources = obtencion_sources(self.DG)

        sinks = obtencion_sinks(self.DG)
        """"in here we obtain simple datapaths, for the mapping"""
        for source in sources:
            for sink in sinks:
                paths = nx.all_simple_paths(self.DG, source=source, target=sink)
                todos_los_paths = list(paths)
                if todos_los_paths:
                    self.lista_paths.append(todos_los_paths[0])

        # generacion de los dos grafos
        # generacion de un diccionario con la informacion de cada nodo
        ################ok hasta aqui tenemos un grafo con solo recursos de procesamiento vamos a ver que tiene en sus etiquetas


        ### dictionario con las funciones y el tipo de configuracion

        self.dict_info = {}
        self.dict_info['functions_cfg'] = {}
        self.dict_info['functions_cfg']['type_cfg'] = random.choice(self.configuration_list)
        for e in self.configuration_functions_list:
            self.dict_info['functions_cfg'][e[0]] = e[1]
        self.dict_info['functions_res'] = {}
        for e in self.input_latency_list:
            self.dict_info['functions_res'][e[0]] = e[1]
        for e in self.list_computing_latency:
            self.dict_info['functions_res'][e[0]] = e[1]
        self.dict_info['functions_res']['lat_sensor'] = 0
        self.dict_info['functions_res']['lat_actuator'] = 0
        self.dict_info['functions_res']['lat_mem'] = 0
        self.dict_info['functions_res']['lat_copy'] = self.latency_copy_node
        self.dict_info['functions_res']['lat_disable'] = 0
        # print(self.dict_info)

        ##### si queremos modulos de memoria
        if self.memory_enable:
            memoria = bool(random.getrandbits(1))
        else:
            memoria = False
        # memoria = True
        numero_memorias = random.randint(1, self.memory_limit)
        vector_nombres_memorias = []
        numero_canales_read = len(obtencion_sources(self.DG)) + len(obtencion_sinks(self.DG))
        numero_canales_write = len(obtencion_sinks(self.DG)) + len(obtencion_sources(self.DG))

        # print(f"si tendremos memoria {memoria} y el numero de memorias son {numero_memorias}")



        self.dict_total = {}
        self.copiaDG = self.DG.copy()
        self.mappingDG = self.DG.copy()
        contador_nodos = len(self.DG.nodes)
        computing_latency_names = []
        # operations_vector = ['copy', 'disable']

        if self.s_prints == 'graphgenerator':
            print("before the parameters")

        contador_memoria_sin_sensor = 0
        contador_sources_bug = 0
        for nodo in self.DG.nodes:
            # si tiene input degree cero es que es un source y debe de estar conectado a un sensor o memoria
            if self.DG.in_degree(nodo) == 0:
                operations_vector = ['copy', 'disable']
                for k in range(0, self.limite_tareas):
                    while True:
                        tarea_random = random.choice(self.operations)
                        if tarea_random not in operations_vector:
                            operations_vector.append(tarea_random)
                            break
                contador_sources_bug = contador_sources_bug + 1

                self.mappingDG.nodes[nodo]['op'] = operations_vector
                self.mappingDG.nodes[nodo]['name'] = 'r' + str(nodo)


                self.DG.nodes[nodo]['op'] = operations_vector
                self.DG.nodes[nodo]['name'] = 'r' +  str(nodo)
                self.DG.nodes[nodo]['lat'] = 0

                ############aqui podemos cambiar el tipo de recurso pero tendriamos que poner un if y cambiar toda
                ############la estructura siguiente, haremos el cambio mas tarde
                self.DG.nodes[nodo]['type'] = 'rp'
                self.dict_total[nodo] = {}

                # datos basicos del nodo

                self.dict_total[nodo]['name'] =  'r' + str(nodo)
                self.dict_total[nodo]['type'] = 'rp'

                sucesores = list(self.DG.successors(nodo))
                lista_edges = []
                for su in sucesores:
                    nombre_edge = 'r' + str(su)
                    lista_edges.append(nombre_edge)
                self.dict_total[nodo]['edges'] = lista_edges

                # asignaremos la configuracion
                config_datos = random.choice(self.configuration_functions_list)
                self.dict_total[nodo]['fun_lat'] = {}
                if len(config_datos) == 2:
                    self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]

                else:
                    self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]

                    # print(config_datos)
                    for n in config_datos:
                        if len(n) == 2:
                            for interno in n:
                                self.dict_total[nodo]['fun_lat'][interno[0]] = interno[1]

                ## ahora asignaremos parametros de acuerdo con la tarea
                self.dict_total[nodo]['ops'] = {}

                for tarea in operations_vector:
                    self.dict_total[nodo]['ops'][tarea] = {}
                    if tarea == 'copy':

                        self.dict_total[nodo]['ops'][tarea]['param'] = None
                        self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                        self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                    elif tarea == 'disable':
                        # self.dict_total[nodo]['ops'][tarea] = {}
                        self.dict_total[nodo]['ops'][tarea]['param'] = None
                        self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_disable'
                        self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_dis'
                    else:
                        for n in range(0,len(self.operations)):
                            lugar = None
                            # print(self.operations[n],tarea)
                            if tarea == self.operations[n]:
                                lugar = n
                                break
                        # self.dict_total[nodo][tarea] = {}
                        info_para = self.input_latency_list[lugar]
                        # print(self.list_computing_latency[lugar][0])
                        if len(info_para) == 2:
                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                            nombre_computing_latency = self.list_computing_latency[lugar][0]
                            self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                            computing_latency_names.append(nombre_computing_latency)
                        else:
                            self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                            nombre_computing_latency = self.list_computing_latency[lugar][0]
                            self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                            computing_latency_names.append(nombre_computing_latency)
                            self.dict_total[nodo]['ops'][tarea]['param'] = {}
                            # print(info_para[2])
                            for n in info_para[2]:
                                # print("parametro ", n)
                                interno = n
                                if len(n) == 2:
                                    # for interno in n:
                                        # print("interno es igual a ", )
                                        if interno[1] == 'range':
                                            limite_01 = random.randrange(self.limite_rango[0], self.limite_rango[1], 1)
                                            limite_02 = random.randrange(self.limite_rango[0], self.limite_rango[1], 1)
                                            if limite_01 > limite_02:
                                                rango_parametro = [limite_02,limite_01]
                                            else:
                                                rango_parametro = [limite_01,limite_02]

                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = rango_parametro
                                        elif interno[1] == 'fixvalue':
                                            valor_fix = random.choice(self.vector_fix_values)
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = [valor_fix,valor_fix]
                                        elif interno[1] == 'vectorvalues':
                                            vector_fix_values = []
                                            for j in range(0,self.limite_tareas):
                                                vector_fix_values.append(random.choice(self.vector_fix_values))
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = vector_fix_values
                                        elif interno[1] == 'vectorstring':
                                            vector_strings = []
                                            vector_strings_ya_usados = []
                                            limite_numero = random.randint(1,self.limite_tareas)
                                            for j in range(0,limite_numero):
                                                temporal_string = random.choice(self.vector_strings)
                                                if temporal_string not in vector_strings_ya_usados:
                                                    vector_strings.append(temporal_string)
                                                    vector_strings_ya_usados.append(temporal_string)
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = vector_strings

                                        elif interno[1] == 'fixstring':
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = random.choice(self.vector_strings)
                                        elif interno[1] == 'boolean':
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = [True , False]


                self.copiaDG.nodes[nodo]['op'] = operations_vector
                self.copiaDG.nodes[nodo]['name'] = 'r' +  str(nodo)
                self.copiaDG.nodes[nodo]['lat'] = 0
                self.copiaDG.nodes[nodo]['type'] = 'rp'

                #####tenemos dos opciones, si incluimos una memoria o si solo un sensor,
                # la opcion de la memoria significa que tenemos que agregar no solo la memoria sino que tambien un recurso de lectura

                if memoria:
                    ### adicionaremos un nodo sensor
                    temporal_numero_memorias = random.randint(1, numero_memorias)

                    ###because maybe we dont need the sensor and the memory is a rom memory
                    self.sensor_enable = bool(random.getrandbits(1))
                    # self.sensor_enable = True
                    if self.sensor_enable:
                        # input("tets")

                        nombre = 'sensor' + str(contador_nodos)
                        self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='ri', lat=0, type='ri')
                        self.copiaDG.add_edge(contador_nodos, contador_nodos + 1)

                        self.dict_total[contador_nodos] = {}
                        self.dict_total[contador_nodos]['name'] = nombre
                        self.dict_total[contador_nodos]['type'] = 'ri'
                        self.dict_total[contador_nodos]['edges'] =  [ 'mem' + str(temporal_numero_memorias)]
                        self.dict_total[contador_nodos]['ops'] = {}
                        self.dict_total[contador_nodos]['ops']['sensor'] = {}
                        self.dict_total[contador_nodos]['ops']['sensor']['param'] = None
                        self.dict_total[contador_nodos]['ops']['sensor']['latency'] = 'lat_sensor'
                        self.dict_total[contador_nodos]['ops']['sensor']['clk'] = 'lat_com_sensor'
                        self.dict_total[contador_nodos]['lat'] = 'lat_com_sensor'
                        self.dict_total[contador_nodos]['fun_lat'] = {}
                        self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                        self.dict_total[contador_nodos]['fun_lat_par'] = 0
                        self.dict_total[contador_nodos]['fun_lat_op'] = 0
                        contador_nodos = contador_nodos + 1
                        contador_memoria_sin_sensor = contador_memoria_sin_sensor + 1

                    ## adicionaremos un modulo de la memoria



                    nombre = 'mem' + str(temporal_numero_memorias)


                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='rm', lat=0, type='rm')
                    self.copiaDG.add_edge(contador_nodos, contador_nodos + 1)

                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'rm'
                    self.dict_total[contador_nodos]['edges'] =  ['rd' + str(contador_nodos + 1)]
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['memory'] = {}
                    self.dict_total[contador_nodos]['ops']['memory']['param'] ={}
                    self.dict_total[contador_nodos]['ops']['memory']['param']['add_space'] = [self.limite_address_space,self.limite_address_space]
                    self.dict_total[contador_nodos]['ops']['memory']['param']['ch_rd'] = [numero_canales_read + 1, numero_canales_read + 1]
                    self.dict_total[contador_nodos]['ops']['memory']['param']['ch_wr'] = [numero_canales_write + 1,numero_canales_write + 1]
                    self.dict_total[contador_nodos]['ops']['memory']['latency'] = 'lat_mem'
                    self.dict_total[contador_nodos]['ops']['memory']['clk'] = 'lat_com_mem'
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    vector_nombres_memorias.append(nombre)
                    contador_nodos = contador_nodos + 1


                    nombre = 'rd' + str(contador_nodos)
                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='rr', lat=0, type='rr')
                    self.copiaDG.add_edge(contador_nodos, nodo)
                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'rr'
                    self.dict_total[contador_nodos]['edges'] = [ 'r' + str(nodo)]
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['read'] = {}
                    self.dict_total[contador_nodos]['ops']['read']['param'] = {}
                    self.dict_total[contador_nodos]['ops']['read']['param']['add_space'] = [0,self.limite_address_single]
                    self.dict_total[contador_nodos]['ops']['read']['param']['latency'] = 'lat_mem'
                    nombre_computing_latency = 'lat_com_' + str(contador_nodos)
                    self.dict_total[contador_nodos]['ops']['read']['param']['clk'] = nombre_computing_latency
                    computing_latency_names.append(nombre_computing_latency)
                    self.dict_total[contador_nodos]['lat'] = nombre_computing_latency
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    contador_nodos = contador_nodos + 1


                else:


                    ### adicionaremos un nodo sensor
                    nombre = 'sensor' + str(contador_nodos)
                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False,op='ri',lat=0,type='ri')
                    self.copiaDG.add_edge(contador_nodos, nodo)

                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'ri'
                    self.dict_total[contador_nodos]['edges'] = ['r' +  str(nodo)]
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['sensor'] = {}
                    self.dict_total[contador_nodos]['ops']['sensor']['param'] = None
                    self.dict_total[contador_nodos]['ops']['sensor']['latency'] = 'lat_sensor'
                    self.dict_total[contador_nodos]['ops']['sensor']['clk'] = 'lat_com_sensor'
                    self.dict_total[contador_nodos]['lat'] = 'lat_com_sensor'
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    contador_nodos = contador_nodos + 1





            # si tiene output degree cero es que es un sink y debe de ser un actuator
            elif self.DG.out_degree(nodo) == 0:
                operations_vector = ['copy', 'disable']
                for k in range(0, self.limite_tareas):
                    while True:
                        tarea_random = random.choice(self.operations)
                        if tarea_random not in operations_vector:
                            operations_vector.append(tarea_random)
                            break
                self.DG.nodes[nodo]['op'] = operations_vector
                self.DG.nodes[nodo]['name'] = 'r' +  str(nodo)
                self.DG.nodes[nodo]['lat'] = 0
                #####aqui podemos hace el cambio para otro tipo de recurso

                self.DG.nodes[nodo]['type'] = 'rp'

                # datos basicos del nodo
                self.dict_total[nodo] = {}
                self.dict_total[nodo]['name'] =  'r' + str(nodo)
                self.dict_total[nodo]['type'] = 'rp'

                # self.dict_total[nodo]['edges'] = lista_edges ######################################
                # asignaremos la configuracion
                config_datos = random.choice(self.configuration_functions_list)
                self.dict_total[nodo]['fun_lat'] = {}
                if len(config_datos) == 2:
                    self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]
                else:
                    self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]
                    for n in config_datos:
                        if len(n) == 2:
                            for interno in n:
                                self.dict_total[nodo]['fun_lat'][interno[0]] = interno[1]

                ## ahora asignaremos parametros de acuerdo con la tarea
                self.dict_total[nodo]['ops'] = {}
                for tarea in operations_vector:
                    self.dict_total[nodo]['ops'][tarea] = {}
                    if tarea == 'copy':

                        self.dict_total[nodo]['ops'][tarea]['param'] = None
                        self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                        self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                    elif tarea == 'disable':
                        # self.dict_total[nodo]['ops'][tarea] = {}
                        self.dict_total[nodo]['ops'][tarea]['param'] = None
                        self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_disable'
                        self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_dis'
                    else:
                        for n in range(0, len(self.operations)):
                            lugar = None
                            # print(self.operations[n],tarea)
                            if tarea == self.operations[n]:
                                lugar = n
                                break
                        # self.dict_total[nodo][tarea] = {}
                        info_para = self.input_latency_list[lugar]
                        # print(info_para)
                        if len(info_para) == 2:
                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                            nombre_computing_latency = self.list_computing_latency[lugar][0]
                            self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                            computing_latency_names.append(nombre_computing_latency)
                        else:
                            self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                            nombre_computing_latency = self.list_computing_latency[lugar][0]
                            self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                            computing_latency_names.append(nombre_computing_latency)
                            self.dict_total[nodo]['ops'][tarea]['param'] = {}
                            for n in info_para[2]:
                                # print("bug sobre parametros", n)
                                interno = n
                                if len(n) == 2:
                                    # for interno in n:
                                        if interno[1] == 'range':
                                            limite_01 = random.randrange(self.limite_rango[0],
                                                                         self.limite_rango[1], 1)
                                            limite_02 = random.randrange(self.limite_rango[0],
                                                                         self.limite_rango[1], 1)
                                            if limite_01 > limite_02:
                                                rango_parametro = [limite_02, limite_01]
                                            else:
                                                rango_parametro = [limite_01, limite_02]

                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = rango_parametro
                                        elif interno[1] == 'vectorvalues':
                                            vector_fix_values = []
                                            vector_fix_values_ya_usados = []
                                            for j in range(0,self.limite_tareas):
                                                temporal_fix = random.choice(self.vector_fix_values)
                                                if temporal_fix not in vector_fix_values_ya_usados:
                                                    vector_fix_values.append(random.choice(self.vector_fix_values))
                                                    vector_fix_values_ya_usados.append(temporal_fix)
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = vector_fix_values
                                        elif interno[1] == 'vectorstring':
                                            vector_strings = []
                                            vector_strings_ya_usados = []
                                            limite_numero = random.randint(1,self.limite_tareas)
                                            for j in range(0,limite_numero):
                                                temporal_string = random.choice(self.vector_strings)
                                                if temporal_string not in vector_strings_ya_usados:
                                                    vector_strings.append(temporal_string)
                                                    vector_strings_ya_usados.append(temporal_string)
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = vector_strings
                                        elif interno[1] == 'fixvalue':
                                            valor_fix = random.choice(self.vector_fix_values)
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = [valor_fix, valor_fix]
                                        elif interno[1] == 'fixstring':
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = random.choice(
                                                self.vector_strings)
                                        elif interno[1] == 'boolean':
                                            self.dict_total[nodo]['ops'][tarea]['param'][interno[0]] = [True, False]




                self.copiaDG.nodes[nodo]['op'] = operations_vector
                self.copiaDG.nodes[nodo]['name'] = 'r' + str(nodo)
                self.copiaDG.nodes[nodo]['lat'] = 0
                self.copiaDG.nodes[nodo]['type'] = 'rp'

                if memoria:
                    temporal_numero_memorias = random.randint(1, numero_memorias)
                    nombre = 'rw' + str(contador_nodos)
                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='rw', lat=0, type='rw')
                    self.copiaDG.add_edge(nodo, contador_nodos)
                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[nodo]['edges'] = [
                        nombre]  #################se agrega aqui porque hasta aqui se agrega el nodo de escritura a la memoria
                    self.dict_total[contador_nodos]['type'] = 'rw'
                    self.dict_total[contador_nodos]['edges'] = [ 'mem' + str(temporal_numero_memorias)]
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['write'] = {}
                    self.dict_total[contador_nodos]['ops']['write']['param'] = {}
                    self.dict_total[contador_nodos]['ops']['write']['param']['add_space'] = [0,
                                                                                            self.limite_address_single]
                    self.dict_total[contador_nodos]['ops']['write']['param']['latency'] = 'lat_mem'
                    nombre_computing_latency = 'lat_com_' + str(contador_nodos)
                    self.dict_total[contador_nodos]['ops']['write']['param']['clk'] = nombre_computing_latency
                    computing_latency_names.append(nombre_computing_latency)
                    self.dict_total[contador_nodos]['lat'] = nombre_computing_latency
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    contador_nodos = contador_nodos + 1

                    ## adicionaremos un modulo de la memoria


                    nombre = 'mem' + str(temporal_numero_memorias)

                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='rm', lat=0, type='rm')
                    self.copiaDG.add_edge(contador_nodos - 1, contador_nodos )

                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'rm'
                    self.dict_total[contador_nodos]['edges'] = [ ' actuator' + str(contador_nodos + 1)]
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['memory'] = {}
                    self.dict_total[contador_nodos]['ops']['memory']['param'] = {}
                    self.dict_total[contador_nodos]['ops']['memory']['param']['add_space'] = [self.limite_address_space,
                                                                                              self.limite_address_space]
                    self.dict_total[contador_nodos]['ops']['memory']['param']['ch_rd'] = [numero_canales_read + 1,
                                                                                          numero_canales_read + 1]
                    self.dict_total[contador_nodos]['ops']['memory']['param']['ch_wr'] = [numero_canales_write + 1,
                                                                                          numero_canales_write + 1]
                    self.dict_total[contador_nodos]['ops']['memory']['latency'] = 'lat_mem'
                    self.dict_total[contador_nodos]['ops']['memory']['clk'] = 'lat_com_mem'
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    vector_nombres_memorias.append(nombre)
                    contador_nodos = contador_nodos + 1

                    ### adicionaremos un nodo sensor
                    nombre = 'actuator' + str(contador_nodos)
                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='ri', lat=0, type='ri')
                    self.copiaDG.add_edge(contador_nodos - 1, contador_nodos)

                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'ri'
                    self.dict_total[contador_nodos]['edges'] = []

                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['actuator'] = {}
                    self.dict_total[contador_nodos]['ops']['actuator']['param'] = None
                    self.dict_total[contador_nodos]['ops']['actuator']['latency'] = 'lat_actuator'
                    self.dict_total[contador_nodos]['ops']['actuator']['clk'] = 'lat_com_actuator'
                    self.dict_total[contador_nodos]['lat'] = 'lat_com_actuator'
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    contador_nodos = contador_nodos + 1



                else:


                    ### adicionaremos un nodo sensor
                    nombre = 'actuator' + str(contador_nodos)
                    self.copiaDG.add_node(contador_nodos, name=nombre, map=False, op='ri', lat=0, type='ri')
                    self.copiaDG.add_edge(nodo, contador_nodos)

                    self.dict_total[contador_nodos] = {}
                    self.dict_total[contador_nodos]['name'] = nombre
                    self.dict_total[contador_nodos]['type'] = 'ri'
                    self.dict_total[contador_nodos]['edges'] = []
                    self.dict_total[nodo]['edges'] = [nombre] #################se agrega aqui porque hasta aqui se agrega el nodo actuator
                    self.dict_total[contador_nodos]['ops'] = {}
                    self.dict_total[contador_nodos]['ops']['actuator'] = {}
                    self.dict_total[contador_nodos]['ops']['actuator']['param'] = None
                    self.dict_total[contador_nodos]['ops']['actuator']['latency'] = 'lat_actuator'
                    self.dict_total[contador_nodos]['ops']['actuator']['clk'] = 'lat_com_actuator'
                    self.dict_total[contador_nodos]['lat'] = 'lat_com_actuator'
                    self.dict_total[contador_nodos]['fun_lat'] = {}
                    self.dict_total[contador_nodos]['fun_lat']['formula'] = None
                    self.dict_total[contador_nodos]['fun_lat_par'] = 0
                    self.dict_total[contador_nodos]['fun_lat_op'] = 0
                    contador_nodos = contador_nodos + 1





            else:
                # print("nodo normal",list(self.DG.successors(nodo)), list(self.DG.predecessors(nodo)))
                # print(self.DG.in_degree(nodo),self.DG.out_degree(nodo))
                values_list = ["False", "False"]

                distribution_list = [self.mux_prob,100-self.mux_prob]

                multiplexer_buffer = random.choices(values_list,distribution_list, k=1)
                multiplexer = False
                # print(multiplexer_buffer)
                if multiplexer_buffer[0] == "True" :

                    if len(list(self.DG.successors(nodo))) >= 1 and len(list(self.DG.predecessors(nodo))) > 1:

                        multiplexer = True

                # print(multiplexer_buffer, multiplexer)
                if self.mux_enable and multiplexer:

                    operations_vector = ['multiplexor','copy', 'disable']

                    self.DG.nodes[nodo]['op'] = operations_vector

                    self.DG.nodes[nodo]['name'] = 'r' + str(nodo)
                    self.DG.nodes[nodo]['lat'] = 0
                    self.DG.nodes[nodo]['type'] = 'rmu'
                    self.dict_total[nodo] = {}

                    # print("ENTRADA A LUYX")
                    ###datos basicos del nodo


                    self.dict_total[nodo]['name'] = 'r' + str(nodo)
                    self.dict_total[nodo]['type'] = 'rmu'
                    sucesores = list(self.DG.successors(nodo))
                    lista_edges = []
                    for su in sucesores:
                        lista_edges.append('r' + str(su))
                    self.dict_total[nodo]['edges'] = lista_edges

                    # print("asignaremos configuracion")
                    # asignaremos la configuracion
                    self.dict_total[nodo]['fun_lat'] = {}
                    self.dict_total[nodo]['fun_lat']['formula'] = None
                    self.dict_total[nodo]['fun_lat_par'] = 0
                    self.dict_total[nodo]['fun_lat_op'] = 0


                    # print("asignaremos parametros")

                    ## ahora asignaremos parametros de acuerdo con la tarea
                    self.dict_total[nodo]['ops'] = {}
                    for tarea in operations_vector:
                        self.dict_total[nodo]['ops'][tarea] = {}
                        if tarea == 'copy':

                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                            self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                        elif tarea == 'disable':
                            # self.dict_total[nodo]['ops'][tarea] = {}
                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_disable'
                            self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_dis'
                        else:
                            predecesores_mux = list(self.DG.predecessors(nodo))
                            sucesores = list(self.DG.successors(nodo))
                            # if len(sucesores) == 1 and len(predecesores_mux) == 2:
                            #     self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                            #     self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                            #     self.dict_total[nodo]['ops'][tarea]['param'] = {}
                            #     self.dict_total[nodo]['ops'][tarea]['param']['MUX'] = [True, False]
                            # else:
                            self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                            self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                            self.dict_total[nodo]['ops'][tarea]['param']  = {}
                            vector_entradas= []
                            for entrada in range(len(predecesores_mux)):
                                vector_entradas.append(str(entrada))
                            self.dict_total[nodo]['ops'][tarea]['param']['input'] = predecesores_mux# vector_entradas
                            vector_salidas = []
                            # for salida in range(len(sucesores)):
                            #     vector_salidas.append(str(salida))
                            self.dict_total[nodo]['ops'][tarea]['param']['output'] =  sucesores#vector_salidas
                    # print("acabamos la asignacion")
                else:
                    # print("algo buuuuffffffffffffffffffffff", multiplexer, self.mux_enable)
                    operations_vector = ['copy','disable']
                    for k in range(0,self.limite_tareas):
                        while True:
                            tarea_random = random.choice(self.operations)
                            if tarea_random not in operations_vector:
                                operations_vector.append(tarea_random)
                                break
                    self.DG.nodes[nodo]['op'] = operations_vector
                    self.DG.nodes[nodo]['name'] = 'r' +  str(nodo)
                    self.DG.nodes[nodo]['lat'] = 0
                    self.DG.nodes[nodo]['type'] = 'rp'
                    self.dict_total[nodo] = {}

                    # datos basicos del nodo

                    self.dict_total[nodo]['name'] = 'r' + str(nodo)
                    self.dict_total[nodo]['type'] = 'rp'
                    sucesores = list(self.DG.successors(nodo))
                    lista_edges = []
                    for su in sucesores:
                        lista_edges.append('r' + str(su))
                    self.dict_total[nodo]['edges'] = lista_edges
                    # asignaremos la configuracion
                    config_datos = random.choice(self.configuration_functions_list)
                    self.dict_total[nodo]['fun_lat'] = {}
                    if len(config_datos) == 2:
                        self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]
                    else:
                        self.dict_total[nodo]['fun_lat']['formula'] = config_datos[0]
                        # print(config_datos)
                        for n in config_datos:
                            # print(n)
                            if len(n) == 2:
                                for interno in n:
                                    self.dict_total[nodo]['fun_lat'][interno[0]] = interno[1]

                    ## ahora asignaremos parametros de acuerdo con la tarea
                    self.dict_total[nodo]['ops'] = {}
                    for tarea in operations_vector:
                        self.dict_total[nodo]['ops'][tarea] = {}
                        if tarea == 'copy':

                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_copy'
                            self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_copy'
                        elif tarea == 'disable':
                            # self.dict_total[nodo]['ops'][tarea] = {}
                            self.dict_total[nodo]['ops'][tarea]['param'] = None
                            self.dict_total[nodo]['ops'][tarea]['latency'] = 'lat_disable'
                            self.dict_total[nodo]['ops'][tarea]['clk'] = 'lat_com_dis'
                        else:
                            for n in range(0, len(self.operations)):
                                lugar = None
                                # print(self.operations[n],tarea)
                                if tarea == self.operations[n]:
                                    lugar = n
                                    break
                            # self.dict_total[nodo][tarea] = {}
                            info_para = self.input_latency_list[lugar]
                            # print(info_para)
                            if len(info_para) == 2:
                                self.dict_total[nodo]['ops'][tarea]['param'] = None
                                self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                                nombre_computing_latency = self.list_computing_latency[lugar][0]
                                self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                                computing_latency_names.append(nombre_computing_latency)
                            else:
                                self.dict_total[nodo]['ops'][tarea]['latency'] = info_para[0]
                                nombre_computing_latency = self.list_computing_latency[lugar][0]
                                self.dict_total[nodo]['ops'][tarea]['clk'] = nombre_computing_latency
                                computing_latency_names.append(nombre_computing_latency)
                                self.dict_total[nodo]['ops'][tarea]['param'] = {}
                                for n in info_para[2]:
                                    if len(n) == 2:
                                            if n[1] == 'range':
                                                limite_01 = random.randrange(self.limite_rango[0], self.limite_rango[1], 1)
                                                limite_02 = random.randrange(self.limite_rango[0], self.limite_rango[1], 1)
                                                if limite_01 > limite_02:
                                                    rango_parametro = [limite_02, limite_01]
                                                else:
                                                    rango_parametro = [limite_01, limite_02]

                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = rango_parametro
                                            elif n[1] == 'fixvalue':
                                                valor_fix = random.choice(self.vector_fix_values)
                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = [valor_fix, valor_fix]
                                            elif n[1] == 'fixstring':
                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = random.choice(
                                                    self.vector_strings)
                                            elif n[1] == 'boolean':
                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = [True, False]

                                            elif n[1] == 'vectorvalues':
                                                vector_fix_values = []
                                                vector_fix_values_ya_usados = []
                                                for j in range(0, self.limite_tareas):
                                                    temporal_fix = random.choice(self.vector_fix_values)
                                                    if temporal_fix not in vector_fix_values_ya_usados:
                                                        vector_fix_values.append(random.choice(self.vector_fix_values))
                                                        vector_fix_values_ya_usados.append(temporal_fix)
                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = vector_fix_values
                                            elif n[1] == 'vectorstring':
                                                vector_strings = []
                                                vector_strings_ya_usados = []
                                                limite_numero = random.randint(1, self.limite_tareas)
                                                for j in range(0, limite_numero):
                                                    temporal_string = random.choice(self.vector_strings)
                                                    if temporal_string not in vector_strings_ya_usados:
                                                        vector_strings.append(temporal_string)
                                                        vector_strings_ya_usados.append(temporal_string)
                                                self.dict_total[nodo]['ops'][tarea]['param'][n[0]] = vector_strings







                if self.mux_enable and multiplexer:
                    self.copiaDG.nodes[nodo]['op'] = operations_vector
                    self.copiaDG.nodes[nodo]['name'] = 'r' + str(nodo)
                    self.copiaDG.nodes[nodo]['lat'] = 0
                    self.copiaDG.nodes[nodo]['type'] = 'rmu'
                else:
                    self.copiaDG.nodes[nodo]['op'] = operations_vector
                    self.copiaDG.nodes[nodo]['name'] = 'r' + str(nodo)
                    self.copiaDG.nodes[nodo]['lat'] = 0
                    self.copiaDG.nodes[nodo]['type'] = 'rp'

        if self.s_prints == 'graphgenerator':
            print("before the assignment of the latencies of the comunication resources")

        max_clk_value = []
        vector_latency_names = []
        for u in computing_latency_names:
            if u not in vector_latency_names:
                valor = random.randint(0, self.limite_computing_latency)
                self.dict_info['functions_res'][u] = valor
                max_clk_value.append(valor)
                vector_latency_names.append(u)
        self.dict_info['functions_res']['lat_com_sensor'] = 1
        self.dict_info['functions_res']['lat_com_actuator'] = 1
        self.dict_info['functions_res']['lat_com_copy'] = self.latency_copy_node
        self.dict_info['max_clk'] = max(max_clk_value)

        self.dict_mapping = {}
        contador_nodos = 0
        for n,data in self.dict_total.items():
            if data['type'] == 'rp':
                self.dict_mapping[contador_nodos] = {}
                self.dict_mapping[contador_nodos] = data
                contador_nodos = contador_nodos + 1
        if self.s_prints == 'graphgenerator':
            print("estamos casi al final ")
        # print("imprimiremos el diccionario de solo nodos de procesamiento")
        # for n,data in self.dict_mapping.items():
        #     print(n,data)

        self.dict_nodes_total = {}
        contador_nodos = 0
        vector_nombres = []
        for n,data in self.dict_total.items():
            if data['name'] not in vector_nombres:
                self.dict_nodes_total[contador_nodos] = {}
                self.dict_nodes_total[contador_nodos] = data
                vector_nombres.append(data['name'])
                contador_nodos = contador_nodos + 1
            else:
                vector_edges_01 = []
                vector_edges_02 = []
                for n_valid,data_valid in self.dict_nodes_total.items():
                    if data['name'] == data_valid['name']:
                        vector_edges_01 = data_valid['edges']
                        vector_edges_02 =  vector_edges_01 + data['edges']
                        self.dict_nodes_total[n_valid]['edges'] = vector_edges_02

        if self.s_prints == 'graphgenerator':
            print("acabamos el proceso")


        ###### ahora los diccionarios de salida importantes son :
        ###### self.dict_nodes_total que contiene todos los nodos
        ###### self.dict_mapping que contiene los nodos para mapear
        ###### los grafos se mantienen igual
        ###### copiaDG es el grafo total y DG es el grafo solo para mapping


        ###### si queremos el diccionario original podemos tomarlo de
        ###### self.dict_total


        #
        #
        # print("DENTRO DEL GENERADOR")
        # for n,data in self.dict_nodes_total.items():
        #     print(n,data)

        ###### transformaremos los diccionarios en algo que se oueda utilizar


        #

        if self.debug == 'graphs':
            lista_vacia = []
            Graph_visual_00 = GraphVisualization.GraphRep([], self.DG, lista_vacia, 'app',
                                                          'randomgeneratorfinal', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_00.f.render(view=False)
            Graph_visual_00.f.render(view=True, format='pdf')

            Graph_visual_01 = GraphVisualization.GraphRep([], self.copiaDG, lista_vacia, 'app',
                                                          'randomgeneratorfinaltotal', [], 'red',
                                                          'black',
                                                          'circle')
            Graph_visual_01.f.render(view=False)
            Graph_visual_01.f.render(view=True, format='pdf')

            for nodo in self.copiaDG.nodes:
                print(nodo,self.copiaDG.nodes[nodo])
            print("ahora seguiremos con la otra")
            for nodo in self.DG.nodes:
                print(nodo,self.DG.nodes[nodo])
            print("acabamos")
            # input("antes del error")
        # print(contador_memoria_sin_sensor,contador_sources_bug)
        self.probabilidad_sensor_rm = int((contador_memoria_sin_sensor*100) / contador_sources_bug)
        # print("la probabilidad es ",self.probabilidad_sensor_rm)
        # Graph_visual_00.f.render(view=False)
        # Graph_visual_00.f.render(view=True, format='pdf')
        # print("imprimiremos algo ")


    def app_generator(self):
        self.AG_origen = self.DG.copy()
        # print("antes del pruning")
        ##### we need to prune the hardware graph removing all the mux nodes
        self.AG_prune_mux = self.AG_origen.copy()
        lista_nodos = self.AG_origen.nodes
        for nodo in lista_nodos:

            if self.AG_prune_mux.nodes[nodo]['type'] == 'rmu':
                # print(nodo)
                predecesores = (self.AG_prune_mux.predecessors(nodo))
                sucesores = (self.AG_prune_mux.successors(nodo))
                self.AG_prune_mux.remove_node(nodo)
                for pre in predecesores:
                    for suc in sucesores:
                        self.AG_prune_mux.add_edge(pre, suc)

        self.AG_origen = self.AG_prune_mux
        # print("luego del pruning",len(self.DG.nodes),len(self.AG_origen))
        # for nodo in self.AG_origen.nodes:
        #     try:
        #         self.AG_origen.nodes[nodo]['type']
        #     except:
        #         print("NO DATOS", nodo,self.AG_origen.nodes[nodo])
        #### next we remove some nodes
        for n in range(0,self.nodos_a_remover):
            nodos_arquitectura = list(self.AG_origen.nodes)
            # print(nodos_arquitectura)
            contador_intentos = 0
            valid_node = True
            while valid_node:
                if contador_intentos > self.nodos_a_remover * 5:
                    break
                nodo_a_remover = random.choice(nodos_arquitectura)
                if self.DG.in_degree(nodo_a_remover) == 1 and self.DG.out_degree(nodo_a_remover)==1:
                    valid_node = False
                    break
                contador_intentos = contador_intentos + 1
            # print(nodo_a_remover)
            predecesores = (self.AG_origen.predecessors(nodo_a_remover))
            sucesores = (self.AG_origen.successors(nodo_a_remover))
            self.AG_origen.remove_node(nodo_a_remover)
            for pre in predecesores:
                for suc in sucesores:
                    self.AG_origen.add_edge(pre,suc)

        total_actuators = obtencion_sinks(self.DG)
        total_sensors = obtencion_sources(self.DG)
        # print("luego de la remocion de nodos")

        ### then we select which type of application we are going to create, it can be:
        # normal = one instance
        # serial = several instances connected in a serial fashion
        # parallel = several parallel instances
        if self.no_instances:
            seleccion_tipo = 'normal'
        else:
            seleccion_tipo = random.choice(self.tipo)



        numero_nodos = len(self.AG_origen.nodes)
        vector_sources_usadas = []

        # After the selection, if serial or parallel has been chosen we enter any of the following if
        self.AG_copia = self.AG_origen.copy()
        if seleccion_tipo == 'serial':
            for i in range(0,self.numero_serial-1):
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
                        self.AG_origen.add_edge(sink,source)
                    except:
                        pass
                numero_nodos = len(self.AG_origen.nodes)

        elif seleccion_tipo == 'parallel':
            for i in range(0,self.numero_paralelo - 1):
                self.AG_origen = nx.disjoint_union(self.AG_origen, self.AG_copia)

        dict_app = {}

        # print("luego de la seleccion de tipo")
        #### now we will assign the information to the nodes
        for nodo in self.AG_origen.nodes:
            # print("inicio de debug ",nodo,self.AG_origen.nodes[nodo])
            nombre_hardware = self.AG_origen.nodes[nodo]['name']
            # print("busqueda de nombre")
            dict_app[nodo] = {}
            dict_app[nodo]['name'] = 't' + str(nodo)
            self.AG_origen.nodes[nodo]['name'] = 't' + str(nodo)

            vector_operaciones = self.AG_origen.nodes[nodo]['op']
            tareas_posibles = []
            # print("debug 01")

            for operacion in vector_operaciones:
                if operacion != 'copy' and operacion != 'disable':
                    tareas_posibles.append(operacion)
            tarea = random.choice(tareas_posibles)
            lugar = None
            dict_app[nodo]['op'] = tarea
            self.AG_origen.nodes[nodo]['op'] = tarea
            sucesores = list(self.AG_origen.successors(nodo))
            vector_edges = []
            # print("debug 02")
            for suc in sucesores:
                nombre_edge = 't' + str(suc)
                vector_edges.append(nombre_edge)
            dict_app[nodo]['edges'] = vector_edges
            # print("debug 03")
            for op in range(0,len(self.operations)):
                if tarea == self.operations[op]:
                    lugar = op
                    break
            # print("debug 04")
            dict_app[nodo]['param'] = {}
            if len(self.input_latency_list[lugar])==2:
                dict_app[nodo]['param'] = None
                self.AG_origen.nodes[nodo]['par'] = None
            else:

                lista_parametros = self.input_latency_list[lugar][2]
                # print(lista_parametros)
                vector_parametros = []
                for parametro in lista_parametros:
                    if parametro[1] == 'range':
                        nombre_nodo = None
                        lista_parametros = None
                        lugar_nodo = None
                        for n,data in self.dict_total.items():
                            if self.dict_total[n]['name'] == nombre_hardware:
                                lista_parametros = self.dict_total[n]['ops']
                                lugar_nodo = n


                        vector_parametros_app = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro[0]]
                        error_en_parametros = bool(random.getrandbits(1))
                        # print(vector_parametros_app)
                        limite_inferior = vector_parametros_app[0]
                        limite_superior = vector_parametros_app[1]
                        if error_en_parametros and self.error_parametros:
                            #### si manejaremos error
                            rango = random.randint(limite_superior + 1, limite_superior*2)
                            dict_app[nodo]['param'][parametro[0]] = rango
                            temporal_parametros = [parametro[0], rango]
                            vector_parametros.append(temporal_parametros)
                        else:
                            rango = random.randint(limite_inferior,limite_superior)
                            dict_app[nodo]['param'][parametro[0]] = rango
                            temporal_parametros = [parametro[0],rango]
                            vector_parametros.append(temporal_parametros)
                    elif parametro[1] == 'fixvalue':
                        lugar_nodo = None
                        for n,data in self.dict_total.items():
                            if self.dict_total[n]['name'] == nombre_hardware:
                                lugar_nodo = n
                        vector_parametros_app = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro[0]]
                        # print(vector_parametros_app)
                        error_en_parametros = bool(random.getrandbits(1))
                        if error_en_parametros and self.error_parametros:
                            valor = vector_parametros_app[0] + 10
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0], valor]
                            temporal_parametros.append(temporal_parametros)
                        else:
                            valor = (vector_parametros_app[0])
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0],valor]
                            temporal_parametros.append(temporal_parametros)
                    elif parametro[1] == 'boolean':
                        vector_boolean = [True,False]
                        valor = random.choice(vector_boolean)
                        dict_app[nodo]['param'][parametro[0]] = valor
                        temporal_parametros = [parametro[0], valor]
                        temporal_parametros.append(temporal_parametros)
                    elif parametro[1] == 'vectorvalues':
                        lugar_nodo = None
                        for n, data in self.dict_total.items():
                            if self.dict_total[n]['name'] == nombre_hardware:
                                lugar_nodo = n
                        vector_parametros_app = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro[0]]
                        # print(vector_parametros_app)
                        error_en_parametros = bool(random.getrandbits(1))
                        if error_en_parametros and self.error_parametros:
                            done = True
                            while done:
                                valor_error = random.choice(vector_parametros_app)
                                valor_error  = valor_error + 1
                                if valor_error not in vector_parametros_app:
                                    break
                            valor = valor_error
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0], valor]
                            temporal_parametros.append(temporal_parametros)
                        else:
                            valor = random.choice(vector_parametros_app)
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0], valor]
                            temporal_parametros.append(temporal_parametros)
                    elif parametro[1] == 'vectorstring' or parametro[1] == 'fixstring':
                        lugar_nodo = None
                        for n, data in self.dict_total.items():
                            if self.dict_total[n]['name'] == nombre_hardware:
                                lugar_nodo = n
                        vector_parametros_app = self.dict_total[lugar_nodo]['ops'][tarea]['param'][parametro[0]]
                        # print(vector_parametros_app)
                        error_en_parametros = bool(random.getrandbits(1))
                        if error_en_parametros and self.error_parametros:

                            valor = 'error'
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0], valor]
                            temporal_parametros.append(temporal_parametros)
                        else:
                            valor = random.choice(vector_parametros_app)
                            dict_app[nodo]['param'][parametro[0]] = valor
                            temporal_parametros = [parametro[0], valor]
                            temporal_parametros.append(temporal_parametros)
                self.AG_origen.nodes[nodo]['par'] = vector_parametros

            # print("debug 05")
            try:
                self.AG_origen.nodes[nodo].pop('map')
                self.AG_origen.nodes[nodo].pop('lat')
            except:
                pass


        # print("luego de la aplicacion de parametros")
        # print(dict_app)
        # print("desplegaremos la informacion del grafo recien creado")
        # for nodo in self.AG_origen.nodes:
        #     print(nodo, self.AG_origen.nodes[nodo])
        # print("finalizamos el despliegue de informacion")



        #### agregaremos los actuadores y sensores

        dict_app_total = dict_app.copy()
        self.AG_total = self.AG_origen.copy()
        sources = obtencion_sources(self.AG_total)
        sinks = obtencion_sinks(self.AG_total)
        # print("luego de la obtencion de sources and sinks")
        #####in here we select the type of input, but at this moment we will pass both information
        ##### todo in here we define the op of the sensors, we can make it random to include memory

        if self.type_application == 'signal':
            samples = random.randint(self.input_samples[0], self.input_samples[1])
            if seleccion_tipo == 'normal':
                numero_nodos = len(self.DG)
            else:
                numero_nodos = len(self.AG_total) + len(self.DG)
            for source in sources:
                nombre = 'sensorapp' + str(numero_nodos)

                self.AG_total.add_edge(numero_nodos, source)
                dict_app_total[numero_nodos] = {}
                dict_app_total[numero_nodos]['name'] = nombre
                ######cambio solo interface type
                if self.sensor_enable and bool(random.getrandbits(1)):
                    dict_app_total[numero_nodos]['op'] = 'interface'
                else:
                    dict_app_total[numero_nodos]['op'] = 'interface'
                    # dict_app_total[numero_nodos]['op'] = 'rm'
                dict_app_total[numero_nodos]['param'] = {}
                dict_app_total[numero_nodos]['param']['type'] = self.type_application
                dict_app_total[numero_nodos]['param']['samples'] = samples
                # dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
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
                dict_app_total[numero_nodos]['param']['type'] = self.type_application
                dict_app_total[numero_nodos]['param']['samples'] = samples
                # dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
                dict_app_total[numero_nodos]['edges'] = []
                dict_app_total[sink]['edges'] = [nombre]
                self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri',
                                       par=dict_app_total[numero_nodos]['param'])
                numero_nodos = numero_nodos + 1
        else:
            eleccion_resolucion = random.choice(self.resoluciones)

            # print(f"los sources son {sources} y los siks son {sinks}")

            if seleccion_tipo == 'normal':
                numero_nodos = len(self.DG)
            else:
                numero_nodos = len(self.AG_total) + len(self.DG)
            # print("antes de lo de los sources")
            for source in sources:
                nombre = 'sensorapp' + str(numero_nodos)

                self.AG_total.add_edge(numero_nodos,source)
                dict_app_total[numero_nodos] = {}
                dict_app_total[numero_nodos]['name'] = nombre
                values_list = ["True", "False"]
                distribution_list = [self.probabilidad_sensor_rm, 100 - self.probabilidad_sensor_rm]
                # print(distribution_list)
                memoria_sensor = random.choices(values_list, distribution_list, k=1)
                habilitador = True

                # print(memoria_sensor)
                # aqui se cambio
                if memoria_sensor[0] == 'True':
                    habilitador = True
                # print(habilitador)
                if  habilitador:
                    dict_app_total[numero_nodos]['op'] = 'interface'
                else:
                    dict_app_total[numero_nodos]['op'] = 'rm'

                dict_app_total[numero_nodos]['param'] = {}
                dict_app_total[numero_nodos]['param']['type'] = self.type_application
                dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
                dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
                dict_app_total[numero_nodos]['edges'] = [dict_app_total[source]['name']]
                self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri', par=dict_app_total[numero_nodos]['param'])
                numero_nodos = numero_nodos + 1
            # print("antes de los sinks")
            for sink in sinks:
                nombre = 'actuatorapp' + str(numero_nodos)

                self.AG_total.add_edge(sink,numero_nodos)
                dict_app_total[numero_nodos] = {}
                dict_app_total[numero_nodos]['name'] = nombre
                dict_app_total[numero_nodos]['op'] = 'interface'
                # eleccion_resolucion = random.choice(self.resoluciones)
                dict_app_total[numero_nodos]['param'] = {}
                dict_app_total[numero_nodos]['param']['type'] = self.type_application
                dict_app_total[numero_nodos]['param']['width'] = eleccion_resolucion[0]
                dict_app_total[numero_nodos]['param']['height'] = eleccion_resolucion[1]
                dict_app_total[numero_nodos]['edges'] = []
                dict_app_total[sink]['edges'] = [nombre]
                self.AG_total.add_node(numero_nodos, name=nombre, op='interface', type='ri', par=dict_app_total[numero_nodos]['param'])
                numero_nodos = numero_nodos + 1

        # print("desplegaremos la informacion del grafo recien creado")
        # for nodo in self.AG_total.nodes:
        #     print(nodo, self.AG_total.nodes[nodo])
        # print("finalizamos el despliegue de informacion")


        # print("luego de los sensores y actuadores")


        self.dict_aplicacion_total = dict_app_total
        self.dict_aplicacion = dict_app
        # print(dict_app_total)

    ######################################











#
# test = GraphGeneration('20191226_graphgenerator.txt', app_num=5)
# print("impresion de datos del hardware")
# for n,data in test.dict_total.items():
#     print(n,data)
# print(test.dict_info)
# lista_vacia = []
# Graph_visual_00 = generic_classes_v1.GraphRep([], test.copiaDG, lista_vacia, 'app', 'total', [], 'red', 'black',
#                                               'circle')
# Graph_visual_00.f.render(view=False)
# Graph_visual_00.f.render(view=True, format='pdf')
#
# Graph_visual_00 = generic_classes_v1.GraphRep([], test.DG, lista_vacia, 'app', 'mapping', [], 'red', 'black',
#                                               'circle')
# Graph_visual_00.f.render(view=False)
# Graph_visual_00.f.render(view=True, format='pdf')
#
# print("impresion de datos de la aplicacion")
# print(test.dict_aplicacion_total)
# print(test.dict_aplicacion)
# print(test.dict_aplicaciones)
#
# Graph_visual_00 = generic_classes_v1.GraphRep([], ag_total, lista_vacia, 'app', 'aplicacion_output', [], 'red', 'black',
#                                               'circle')
# Graph_visual_00.f.render(view=False)
# Graph_visual_00.f.render(view=True, format='pdf')