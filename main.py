###################GENERIC IMPORTS
import subprocess
import sys
import os
import re
import argparse
import time
import pickle
import multiprocessing
from multiprocessing import Queue
from datetime import datetime,timedelta
import csv
from itertools import permutations,combinations
import random
from collections import deque

##################LIBRARIES THAT COULD NOT BE IN THE ENVIROMENT, SO WE NEED TO INSTALL THEM
try:
    from fpdf import FPDF
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'fpdf'])
    from fpdf import FPDF

try:
    import networkx as nx
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'networkx'])
    import networkx as nx

try:
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'matplotlib'])
    import matplotlib.pyplot as plt

try:
    from graphviz import Digraph
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'graphviz'])
    from graphviz import Digraph

try:
    from PyPDF2 import PdfFileMerger
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'PyPDF2'])
    from PyPDF2 import PdfFileMerger

try:
    from pympler.asizeof import asizeof
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'pympler'])
    from pympler.asizeof import asizeof


try:
    from scipy.ndimage.filters import gaussian_filter1d

except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'scipy'])
    from scipy.ndimage.filters import gaussian_filter1d




# try:
#     from memory_profiler import memory_usage
#     # from pympler.asizeof import asizeof
# except ImportError:
#     subprocess.call([sys.executable, "-m", "pip", "install", 'memory_profiler'])
#     from memory_profiler import memory_usage
#


#########################IMPORTS OF THE DEVELOPED SCRIPTS


# script that constains functions that we use for most of the other scripts
from basic_functions import obtencion_sinks,obtencion_sources,obtencion_sucesores

# script that helps to deal with the terminal input arguments
from argument_parser import arguments

# script for the random generator
from GraphGenerator import GraphGeneration

# script for the constrains and the parser of the configuration files
import parsers

# script that creates the graphs from lists (input and output graphs)
import GraphVisualization

# script of the heuristic approach (original version)
import heu_map_v20

# script of the heuristic approach (bayes version)
import bayes_map_v20 as bayes_map_v10

# script of the performance evaluation
from PerfoEval_v10 import performance_evaluation
import PerfoEval_v10 as PerfoEval_v10
from PerfoEval_v40 import performance_evaluation as perfomance_evaluation_exh



# script of the exhaustive approach (multi version)
import ex_map_multi_v50 as ex_map_multi_v10

# script of the exhaustive approach (no multi)
import  ex_map_no_multi_v10

# script of the list-based algorithm
import list_map_v40 as list_map_v20

# script of the q-learning algorithm
import ql_map_v10


# parsers, all the arguments are explained in the readme file, only a summary and the options are shown

parser = argparse.ArgumentParser()


filepath_hw,filepath_app,filepath_con,filepath_gen,filepath_savefolder,selection_algo,selection_prints,\
            selection_modules,pool_range_min,pool_range_max,number_iterations,method_evaluation,debug_info,\
            selection_pause,debugging_options,save_info,selection_show,selection_show_implementation_graph,\
            selection_no_nodes,random_generator,HwBenchmark,AppBenchmark,graph_generator,exh_multi,LIMIT_STORE_LIST,\
            LIMIT_PROCESS_LIST,heu_type,BAYES_LATENCY,BAYES_DISTANCE,list_type,EPISODES_OFFLINE,DECAY_START_OFFLINE,\
            EPISODES_ONLINE,DECAY_START_ONLINE,filepath_rewards,DECAY_END_ONLINE,DECAY_END_OFFLINE,LIMIT_TIME_SLOTS = arguments(parser)





######################
'''generation of the input graphs and the dictionary with
the general information'''

cell_size = 2
cell_lenght = 300
font_titulo = 12
font_texto = 5
lista_vacia = []

##initialization of the variables
dict_total_h = None
dict_nodes_h = None
dict_info_h = None
dict_nodes_a = None
dict_info_a = None
DG_total = None
DG_total_unroll = None
AG_total = None
DG = None
AG = None


# we create the folder where we are going to store all the results
# first we create a folder where we are going to store the output files, the folder is defined by the arg -folder,
# and it will be created in the current path, if the folder already exist we print a
# warning, if the path is not valid we raise an error, if there is no path defined we select the current path
dir_path = os.path.dirname(os.path.realpath(__file__))
# print(f"the path where we are going to store all the output results is ", dir_path)
if filepath_savefolder:
    try:
        directorio = dir_path + '/' + filepath_savefolder
    except:
        print(f"name of directory {filepath_savefolder} is not valid")
else:
    directorio = dir_path

try:
    os.mkdir(directorio)
except:
    print(f"the directory {filepath_savefolder} already exists, the files could be overwritten")
    pass



if selection_prints == 'main' or selection_prints == 'basic' or selection_prints == 'debug':
    print(f"Random generator enable :  {random_generator}")
    print(f"Selected algorithm {selection_algo} and verbosity option {selection_prints}")

####we obtain the information about the hardware graph, if we are in the benchmark mode
#  the reading is inside the if of bench

if selection_algo != 'bench':
    if not random_generator:
        # if we dont select random generator we obtain the information from the configuration files for both the app and
        # the hw, we passed to the parser and we obtain the input graphs and the dictionaries with their information

        t0 = datetime.now()

        DG,dict_nodes_h,dict_info_h,DG_total,dict_total_h,DG_total_unroll = parsers.text_to_graph_v4(filepath_hw,'hw')

        if selection_prints == 'main' and debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - t0
            print(
                f"Building of the hw graph and its dictionaries, current time {now} "
                f"the processing time is {c.seconds} seconds {c.microseconds} microseconds")

        t0 = datetime.now()

        AG,dict_nodes_a,dict_info_a,AG_total,AG_dummy,    AG_dummy_unroll = parsers.text_to_graph_v4(filepath_app,'app')

        if selection_prints == 'main' and debug_info == 'total':
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - t0
            print(
                f"Building of the app graph and its dictionaries, current time {now} the processing time is "
                f"{c.seconds} seconds {c.microseconds} microseconds")


    else:
        # if we select the random generator we obtain the info from the configuration files produced by the generator,
        #   and this information in inside the object graph_generator, for more details about this object refer to
        #   the function GraphGeneration info

        DG, dict_nodes_h, dict_info_h, DG_total, dict_total_h, DG_total_unroll = parsers.text_to_graph_v4(
            graph_generator.nombre_archivo_hw, 'hw')


#### we proceed to read the constrains file if there is any
try:
    lista_tareas_constrains,lista_constraints = parsers.constrains_read_v1(filepath_con)
except:
    lista_tareas_constrains = []
    lista_constraints = []


if selection_prints=='main' or selection_prints == 'basic' and selection_algo != 'bench':
    print("the dictionary with all the info about the hardware is ")
    print(dict_total_h)
    print("this is the end of the dict")
    print(dict_info_h)



# visualization of the input graphs, if we select the bench option, the visualization is inside of the bench if

if selection_show  and selection_algo != 'bench':

    # first we create the hardware graph and show it
    GraphVisualization.GenerationGraphPdf(cell_size,cell_lenght,font_titulo,font_texto,'hw',True,
                                          DG_total_unroll,False,os.path.join(directorio, "hw01"),   os.path.join(directorio, 'hw_info_nt.pdf') ,
                                          os.path.join(directorio, 'hw_complete.pdf'),
                                          dict_info_h,DG_total,dict_total_h)
    plot01 = subprocess.Popen("evince '%s'" % os.path.join(directorio, 'hw_complete.pdf'), shell=True)

    # now for the application graph
    if not random_generator:
        # if the random generator is disable this means that there is only one applicatin graph, so we build it and show it
        GraphVisualization.GenerationGraphPdf(cell_size, cell_lenght, font_titulo, font_texto, 'app', True, AG_total,
                                              False, os.path.join(directorio, "app01"),   os.path.join(directorio, 'app_info_nt.pdf') ,
                                              os.path.join(directorio, 'app_complete01.pdf'),
                                              [], [], [])
        plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, 'app_complete01.pdf'), shell=True)

    else:

        # if the random generator is enable, there is a possibility that there are more than one application graph, so
        # we go through the object and build all the application graphs inside it and show them
        for aplicacion in range(len(graph_generator.dict_aplicaciones)):
            name_final = "app_complete_" + str(aplicacion) + ".pdf"
            AG, dict_nodes_a, dict_info_a, AG_total, AG_dummy, AG_dummy_unroll = parsers.text_to_graph_v4(
                graph_generator.dict_aplicaciones[aplicacion]['nombre_archivo'], 'app')
            GraphVisualization.GenerationGraphPdf(cell_size, cell_lenght, font_titulo, font_texto, 'app', True,
                                                  AG_total,
                                                  False, os.path.join(directorio, "app01"), os.path.join(directorio, 'app_info_nt.pdf'),
                                                  os.path.join(directorio, name_final)   ,
                                                  [], [], [])
            plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, name_final) , shell=True)



####################################MAPPING ALGORITHMS###############################

if selection_algo == 'heu':

    timing_list_heu_map = []
    timing_list_heu_perfo = []
    timing_list_heu_total = []
    a = datetime.now()

    print(f"General start of the heuristic approach", a.strftime("%H:%M:%S.%f"))

    for iteracion in range(number_iterations):

        if heu_type == 'original':

            b = datetime.now()
            print(f"start of iteration {iteracion} of the heuristic "
                  f"mapping (mapping sucess approach)", b.strftime("%H:%M:%S.%f"))

            # generation of the simple datapaths
            # datapaths = heu_map_v20.generation_datapaths(DG)

            if selection_prints == 'main':
                # print("The simple datapaths of the hardware are ",datapaths)
                print("Info about the application")
                for nodo in AG.nodes:
                    print(nodo, AG.nodes[nodo])
                print("Info about the hardware")
                for nodo in DG.nodes:
                    print(nodo,DG.nodes[nodo])
                print("End")

            # main call
            test_final = heu_map_v20.HeuristicMethod(DG, AG ,dict_nodes_h,dict_info_h,selection_prints,
                                                      dict_nodes_a,selection_pause, dict_info_a,DG_total,AG_total,dict_total_h,
                                               debugging_options,lista_constraints,lista_tareas_constrains)

            c = datetime.now()

            now = c.strftime("%H:%M:%S.%f")
            d = c - b

            print(
                f"end of the heuristic approach, current time {now} the processing time is {d.seconds} seconds "
                f"{d.microseconds} microseconds")

            timing_list_heu_map.append(d)

            if selection_prints == 'main':
                print(f"we are going to print the time slots of the implementation "
                      f"graph in the heuristic approach, the lenght of the list is {len(test_final.lista_final)}")
                for elemento in test_final.lista_final:
                    print("time slot  ", elemento)
                print(f"the special nodes {test_final.lista_nodos_especiales}")



        else:

            b = datetime.now()
            print(f"start of iteration {iteracion} of the heuristic mapping (bayes approach)", b.strftime("%H:%M:%S.%f"))



            if selection_prints == 'main':
                # print("The simple datapaths of the hardware are ",datapaths)
                print("Info about the application")
                for nodo in AG.nodes:
                    print(nodo, AG.nodes[nodo])
                print("Info about the hardware")
                for nodo in DG.nodes:
                    print(nodo, DG.nodes[nodo])
                print("End")

            # main call
            test_final = bayes_map_v10.HeuristicMethod(DG, AG, dict_nodes_h, dict_info_h, selection_prints,
                                                     dict_nodes_a, selection_pause, dict_info_a, DG_total, AG_total,
                                                     dict_total_h,
                                                     debugging_options, lista_constraints,
                                                       lista_tareas_constrains, BAYES_DISTANCE, BAYES_LATENCY)

            c = datetime.now()

            now = c.strftime("%H:%M:%S.%f")
            d = c - b

            print(
                f"end of the heuristic approach, current time {now} the processing time is {d.seconds} seconds "
                f"{d.microseconds} microseconds")

            timing_list_heu_map.append(d)

            if selection_prints == 'main':
                print(f"we are going to print the time slots of the implementation "
                      f"graph in the heuristic approach, the lenght of the list is {len(test_final.lista_final)}")
                for elemento in test_final.lista_final:
                    print("time slot  ", elemento)
                print(f"the special nodes {test_final.lista_nodos_especiales}")

        if selection_modules == 'total':
            # modulo de evaluacion de desempeno
            g = datetime.now()
            print(f"start of performance evaluation in the heuristic process ", g.strftime("%H:%M:%S.%f"))

            if isinstance(test_final.lista_final[0][0][0], bool):
                if selection_prints == 'main':
                    print("bug when we have just one instance from the first stage")
                list_to_graph = test_final.lista_final[0]
            else:
                list_to_graph = test_final.lista_final


            if selection_prints == 'basic':
                print(test_final.lista_nodos_especiales)
                print("WE ARE GOING TO START THE PERFORMANCE EVALUATION ")
                print("  ")


            #####variable para debuggear ciertas partes de la evaluacion de performance
            debugging = True



            #evaluacion de desempeno
            longest,MAP,graph_total,MAP_performance,maximum_clock= \
                performance_evaluation(test_final.lista_final, DG,
                                                                        test_final.lista_nodos_especiales,
                                                                        debugging_options,
                                                                       'bla','perfo',selection_prints,selection_pause,
                                                                        dict_nodes_h,dict_nodes_a,DG_total_unroll,
                                                                        dict_info_h,dict_total_h,dict_info_a,
                                                                        debugging,DG_total_unroll,AG_total,
                                       method_evaluation,AG).perf_eval()



            if selection_prints == 'main':
                print(f"longest {longest}")


            name_implementation_graph = 'implementation_graph_heu_' + str(iteracion) + '.pdf'
            vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                    dict_nodes_a, longest, maximum_clock,
                                         MAP_performance,os.path.join(directorio, name_implementation_graph),
                                                                                    os.path.join(directorio, 'final_graph'),directorio)



            if selection_prints == 'main':
                print("the critical path is ", vector_longest)
            print(f"the value of the overall latency is {MAP_performance} clock cycles")
            c = datetime.now()

            now = c.strftime("%H:%M:%S.%f")
            d = c - g

            print(
                f"end of performance evaluation in the heuristic approach, current time {now} the processing "
                f"time is {d.seconds} seconds "
                f"{d.microseconds} microseconds")

            timing_list_heu_perfo.append(d)
            t = c -b
            timing_list_heu_total.append(t)
            print(f"the overall time is {t.seconds} seconds {t.microseconds} microseconds")
            #para visualizar el pdf con los datos del grafo e informacion de la impementacion

            if selection_show_implementation_graph:
                plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, name_implementation_graph), shell=True)

    print(f"the average time of the heuristic mapping algorithm is "
          f"{(sum(timing_list_heu_map, timedelta()) / len(timing_list_heu_map)).total_seconds()}")
    print(f"the average time of the performance evaluation is "
          f"{(sum(timing_list_heu_perfo, timedelta()) / len(timing_list_heu_perfo)).total_seconds()}")

    print(f"The number of iterations is {number_iterations} "
          f"and the average overall time "
          f"is {(sum(timing_list_heu_total, timedelta()) / len(timing_list_heu_total)).total_seconds()}, "
          f"the current time is", datetime.now().strftime("%H:%M:%S.%f"))


def perfo_multi(union_lista):
    list_to_graph = union_lista.pop(0)
    DG = union_lista.pop(0)
    lista_nodos_especiales = union_lista.pop(0)
    debugging_options = union_lista.pop(0)
    nombre_debug_performance = union_lista.pop(0)
    name_debug = union_lista.pop(0)
    selection_prints_during_perfo = union_lista.pop(0)
    debug_info = union_lista.pop(0)
    dict_nodes_h = union_lista.pop(0)
    dict_nodes_a = union_lista.pop(0)
    dict_info_h = union_lista.pop(0)
    dict_total_h = union_lista.pop(0)
    dict_info_a = union_lista.pop(0)
    # union_lista.pop(False)
    DG_total_unroll = union_lista.pop(0)
    AG_total = union_lista.pop(0)
    method_evaluation = union_lista.pop(0)
    AG = union_lista.pop(0)
    LIMIT_TIME_SLOTS = union_lista.pop(0)
    contador_time_slots_correctos = union_lista.pop(0)


    if LIMIT_TIME_SLOTS != None:
        if len(list_to_graph) > LIMIT_TIME_SLOTS:
            MAP_performance = 1000000000000000000000000000000000000000000000000000000
        else:
            try:
                # print(f"there is a preliminary mapping with {LIMIT_TIME_SLOTS} time slots")
                contador_time_slots_correctos = contador_time_slots_correctos + 1
                latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
                    perfomance_evaluation_exh(
                        list_to_graph, DG, lista_nodos_especiales, debugging_options,
                        nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                        dict_nodes_h,
                        dict_nodes_a, DG_total_unroll,
                        dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                        AG).perf_eval()


                # latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
                #     PerfoEval_v10.performance_evaluation_function_v2(
                #         list_to_graph, DG, lista_nodos_especiales, debugging_options,
                #         nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                #         dict_nodes_h,
                #         dict_nodes_a, DG_total_unroll,
                #         dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                #         AG)
            except:

                MAP_performance = 1000000000000000000000000000000000000000000000000000000
    else:
        try:
            latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
                perfomance_evaluation_exh(
                    list_to_graph, DG, lista_nodos_especiales, debugging_options,
                    nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                    dict_nodes_h,
                    dict_nodes_a, DG_total_unroll,
                    dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                    AG).perf_eval()

            # latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
            #     PerfoEval_v10.performance_evaluation_function_v2(
            #         list_to_graph, DG, lista_nodos_especiales, debugging_options,
            #         nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
            #         dict_nodes_h,
            #         dict_nodes_a, DG_total_unroll,
            #         dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
            #         AG)
        except:

            MAP_performance = 1000000000000000000000000000000000000000000000000000000
    elemento = [MAP_performance,list_to_graph,lista_nodos_especiales,contador_time_slots_correctos]
    q.put(elemento)
    # return MAP_performance


if selection_algo == 'exh':

    # file to write the results
    folder_txt = directorio + '/folder_result/'
    try:
        os.mkdir(folder_txt)
    except:
        pass
    try:
        text_file = open(os.path.join(folder_txt,"results.txt"), "x")
    except:
        os.remove(os.path.join(folder_txt,"results.txt"))
        text_file = open(os.path.join(folder_txt, "results.txt"), "x")
    text_file.write("-------------------------------------------------------------------\n")
    text_file.write("Exhaustive approach \n")
    text_file.write("specifications of the test: hw: " + filepath_hw + ", app: " + filepath_app + ",\n")
    text_file.write("threads for the mapping: " + str(LIMIT_PROCESS_LIST) + ", threads for the performance evaluation: "
            + str(pool_range_min) + "-" +str(pool_range_max))
    text_file.close()



    print("Begin of the exhaustive approach")
    if exh_multi == 'multi':
        print("We will use multiprocessing")
        for number_of_pools in range(pool_range_min,pool_range_max):
            timing_list_exh = []
            timing_list_perfo = []
            timing_list_total = []
            print(" ")
            print("start of the process with number of processes spawn",LIMIT_PROCESS_LIST,
                  " for the exhaustive algo and ",number_of_pools," for the performance evaluation")


            for iteracion in range(number_iterations):

                # debug_info = 'total'
                start_exh = time.clock()
                a = datetime.now()

                print(f"start of the exhaustive approach, date:",a.strftime("%d/%m"), ", time ",a.strftime("%H:%M:%S.%f"))
                text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                text_file.write("\nstart of the exhaustive approach, date: " + a.strftime("%d/%m") + ", time: " + a.strftime("%H:%M:%S.%f"))
                text_file.close()
                # main function, the final results are two lists one of the mappings and another of the special nodes for the
                # mappings both of them are related  benchmark_new_version_backup

                number_pickles,final_node,flag_one_node = \
                    ex_map_multi_v10.exhaustive_algorithm_multi_version(DG, AG, debug_info, [],dict_nodes_h,
                                                                        dict_info_h,selection_prints,dict_nodes_a,
                                                                        selection_pause,dict_info_a,DG_total, AG_total,
                                                                        dict_total_h,lista_constraints,
                                                                        lista_tareas_constrains,directorio,
                                                                        LIMIT_PROCESS_LIST,
                                                                        LIMIT_STORE_LIST,list_type,LIMIT_TIME_SLOTS).mapping()


                end_exh = time.clock()
                b = datetime.now()
                now = b.strftime("%H:%M:%S.%f")
                c = b - a
                current_date = b.strftime("%d/%m")
                print("---------------------------------------")
                print(
                    f"end of the exhaustive approach, current date {current_date}, current time {now} the "
                    f"processing time is  {c.days} days {c.seconds} seconds {c.microseconds} microseconds")
                print(f"the number of pickles generated is {number_pickles}, "
                      f"each pickle has {LIMIT_STORE_LIST} preliminary mappings")
                timing_list_exh.append(c)
                text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                text_file.write("\nend of the exhaustive approach, current date: " + current_date + ", current time: " + now)
                text_file.write("\nprocessing time is " + str(c.days) + " days " + str(c.seconds) + " seconds " + str(c.microseconds) + " microseconds")
                text_file.close()
                ######almacenaremos todas las variables anteriores en una sola lista y la enviaremos a
                # las funciones de creacion de grafos
                debugging = False

                vector = []
                graphs = []
                perfo = []
                number_of_lists_processed = 0
                if selection_modules == 'total':

                    q = Queue()


                    e = datetime.now()
                    now = e.strftime("%H:%M:%S.%f")
                    current_date = e.strftime("%d/%m")
                    print(f"start of the performance evaluation, the current date {current_date}, current time is {now}")
                    text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                    text_file.write("\nstart of the performance evaluation, the current date is " + current_date + ", the current time is " + now)
                    text_file.close()
                    start_performance_benchmark = time.time()
                    # We can select the type of verbosity during the performance evaluation, it is recommended to select none and
                    # only change it if we are going to debug
                    selection_prints_during_perfo = selection_prints

                    latencia_resultado = 1000000000000000000000000000000000000
                    aproximado_de_total_listas = number_pickles*LIMIT_STORE_LIST
                    contador_time_slots = [0 for n in range(len(AG.nodes))]
                    contador_time_slots_correctos = 0
                    for n in range(0, number_pickles):
                        # print("another pickle ")
                        name_pickle = 'currentlist' + '_' + str(final_node) + '_' + str(n)
                        # name_pickle = 'partiallist' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_mapping_large = pickle.load(f)
                        name_pickle = 'specialnodes' + '_' + str(final_node) + '_' + str(n)
                        # name_pickle = 'specialnodes' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_nodes_mapping_large = pickle.load(f)
                        # print("another pickle the number of list is ", len(lista_total_mapping_large))
                        # the list could has up to 1000 lists, we need to divide it and then process it
                        if len(lista_total_mapping_large) > 0:
                            number_of_pickles_large = 0
                            limit_number_list = number_of_pools
                            number_of_lists = len(lista_total_mapping_large)
                            inicio_lista = len(lista_total_mapping_large)
                            # print(lista_total_mapping_large)
                            no_zero = True
                            while no_zero:
                                if number_of_lists - limit_number_list > 0:
                                    name_pickle = 'partiallist' + str(number_of_pickles_large)
                                    # print(lista_total_mapping[0:1])
                                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                        pickle.dump(lista_total_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                                    name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                        pickle.dump(lista_total_nodes_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                                    number_of_lists = number_of_lists - limit_number_list
                                else:
                                    name_pickle = 'partiallist' + str(number_of_pickles_large)
                                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                        pickle.dump(lista_total_mapping_large[0:number_of_lists], f)
                                    name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                        pickle.dump(lista_total_nodes_mapping_large[0:number_of_lists], f)
                                    no_zero = False
                                number_of_pickles_large = number_of_pickles_large + 1

                            lista_total_mapping_large = []
                            lista_total_nodes_mapping_large = []

                            # print(number_of_pickles_large)
                            for n_large in range(0, number_of_pickles_large):
                                name_pickle = 'partiallist' + str(n_large)
                                # name_pickle = 'partiallist' + str(n)
                                with open(os.path.join(directorio, name_pickle), 'rb') as f:
                                    lista_total_mapping = pickle.load(f)
                                os.remove(os.path.join(directorio, name_pickle))
                                name_pickle = 'partialspecialnodes' + str(n_large)
                                # name_pickle = 'specialnodes' + str(n)
                                with open(os.path.join(directorio, name_pickle), 'rb') as f:
                                    lista_total_nodes_mapping = pickle.load(f)
                                os.remove(os.path.join(directorio, name_pickle))

                                # print(f" we are going to evaluate {len(lista_total_mapping)} mapping lists")

                                #### con multi
                                processes = []
                                number_of_lists_processed = number_of_lists_processed + len(lista_total_mapping)
                                bandera_bug = False
                                time_slots = []
                                for i in range(len(lista_total_mapping)):
                                    elemento_a_evaluar = lista_total_mapping[i]
                                    if isinstance(elemento_a_evaluar[0][0], bool):
                                        list_to_graph = [elemento_a_evaluar]
                                        # print(list_to_graph, i)
                                        time_slots.append(i)
                                        # bandera_bug = True
                                    else:
                                        list_to_graph = elemento_a_evaluar
                                    # we retrieve also the information about the special nodes
                                    try:
                                        lista_nodos_especiales = lista_total_nodes_mapping[i]

                                    except:
                                        lista_nodos_especiales = []

                                    contador_time_slots[len(list_to_graph) - 1] = contador_time_slots[
                                                                                  len(list_to_graph) - 1] + 1
                                    j = 4
                                    name_debug = 'validacion-' + str(j)
                                    # if j == 4:
                                    #     selection_prints_during_perfo = 'none'
                                    # else:
                                    #     selection_prints_during_perfo = 'none'
                                    nombre_debug_performance = 'bla' + str(j)
                                    union_list = []
                                    union_list.append(list_to_graph)
                                    union_list.append(DG)
                                    union_list.append(lista_nodos_especiales)
                                    union_list.append(debugging_options)
                                    union_list.append(nombre_debug_performance)
                                    union_list.append(name_debug)
                                    union_list.append(selection_prints_during_perfo)
                                    union_list.append(debug_info)
                                    union_list.append(dict_nodes_h)
                                    union_list.append(dict_nodes_a)
                                    union_list.append(dict_info_h)
                                    union_list.append(dict_total_h)
                                    union_list.append(dict_info_a)
                                    union_list.append(DG_total_unroll)
                                    union_list.append(AG_total)
                                    union_list.append(method_evaluation)
                                    union_list.append(AG)
                                    union_list.append(LIMIT_TIME_SLOTS)
                                    union_list.append(contador_time_slots_correctos)
                                    t = multiprocessing.Process(target=perfo_multi, args=(union_list,))
                                    processes.append(t)
                                    t.start()



                                for one_process in processes:
                                    one_process.join()

                                resulting_list = []
                                while not q.empty():
                                    resulting_list.append(q.get())
                                performance_list = []
                                for j in range(len(resulting_list)):
                                    performance_list.append(resulting_list[j][0])
                                # print(performance_list)
                                min_index = min(range(len(performance_list)), key=performance_list.__getitem__)
                                MAP_performance = resulting_list[min_index][0]
                                if MAP_performance != None:
                                    if MAP_performance < latencia_resultado:
                                        latencia_resultado = MAP_performance

                                        lista_mapping_best = resulting_list[min_index][1].copy()
                                        lista_nodos_especiales_best = resulting_list[min_index][2].copy()

                            e_2 = datetime.now()
                            now = e_2.strftime("%H:%M:%S.%f")
                            current_date = e_2.strftime("%d/%m")
                            aproximado_de_proceso = (100*LIMIT_STORE_LIST*n)/aproximado_de_total_listas
                            print(f"The percentage of already processed lists is {aproximado_de_proceso}, "
                                  f"current date {current_date}, current time {now}")

                    # after passing through all the possible mappings we ended up with the best and this one we ultimate process
                    # again, this seems like a but that we need to fix todo fix this thing

                    latency_evaluation, MAP, graph_total, MAP_performance, maximum_clock = \
                        perfomance_evaluation_exh(
                            lista_mapping_best, DG,
                            lista_nodos_especiales_best,
                            debugging_options,
                            'bla', 'perfo', selection_prints, debug_info, dict_nodes_h, dict_nodes_a, DG_total_unroll,
                            dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll,
                            AG_total, method_evaluation, AG).perf_eval()


                    nombre_implementation_graph = "implementation_graph_exh_" + str(iteracion) + "_" +\
                                                  str(number_of_pools) + ".pdf"
                    nombre_final_graph = 'final_graph_' + str(iteracion) + '_' + str(number_of_pools)


                    # after we perform again the evaluation we build the implementation graph
                    vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                            dict_nodes_a, latency_evaluation,
                                                                                            maximum_clock,
                                                                                            MAP_performance,
                                                                                            os.path.join(directorio,
                                                                                                         nombre_implementation_graph),
                                                                                            os.path.join(directorio,
                                                                                                         nombre_final_graph),directorio)

                    end_performance_benchmark = time.time()
                    time_benchmark_performance = end_performance_benchmark - start_performance_benchmark
                    if selection_prints == 'main':
                        print("the critical path is ", vector_longest)
                    print(f"the value of the overall latency is {MAP_performance} clock cycles")

                    d = datetime.now()
                    now = d.strftime("%H:%M:%S.%f")
                    f = d - e

                    current_date = d.strftime("%d/%m")
                    print(
                        f"end of the performance evaluation, current date {current_date}, current time {now} the processing time is {f.days} days {f.seconds} "
                        f"seconds {f.microseconds} microseconds for {number_of_lists_processed} mapping lists")
                    g = d - a
                    print(
                        f"The overall processing time is  {g.days} days  {g.seconds} seconds {g.microseconds} microseconds")
                    if selection_show_implementation_graph:
                        plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, nombre_implementation_graph),
                                              shell=True)
                    timing_list_perfo.append(f)
                    timing_list_total.append(g)
                    text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                    text_file.write("\nThe value of the overall latency is " + str(MAP_performance) + " clock cycles")
                    text_file.write("\nEnd of the performance evaluation, current date is " + current_date + ", current time " + now)
                    text_file.write("\nThe processing time is " + str(f.days) + " days, " + str(f.seconds) + " seconds, " + str(f.microseconds) + " microseconds" )
                    text_file.write("\nThe number of mapping list is " + str(number_of_lists_processed))
                    for n_time_slot in range(len(contador_time_slots)):
                        text_file.write(
                            "\nThe number of mappings with " + str(n_time_slot + 1) + "time slots is " + str(
                                contador_time_slots[n_time_slot]))
                    text_file.write("\nThe overall processing time is " + str(g.days) + " days, " + str(g.seconds) + " seconds, " + str(g.microseconds) + " microseconds")
                    text_file.close()

            average_time_exh = (sum(timing_list_exh, timedelta()) / len(timing_list_exh)).total_seconds()
            print(f"the average time of the exhaustive algorithm is "
                  f"{average_time_exh}")

            text_file = open(os.path.join(folder_txt, "results.txt"), "a")
            text_file.write("\nThe average time of the exhaustive algorithm is " + str(average_time_exh))
            text_file.close()

            if selection_modules == 'total':
                average_time_perfo = (sum(timing_list_perfo, timedelta()) / len(timing_list_perfo)).total_seconds()
                print(f"the average time of the performance evaluation is "
                      f"{average_time_perfo}")
                average_time_total = (sum(timing_list_total, timedelta()) / len(timing_list_total)).total_seconds()
                print(f"the number of processes spawn is {number_of_pools}, the number of iterations is {number_iterations} "
                      f"and the average overall time "
                      f"is {average_time_total}")
                text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                text_file.write("\nThe average time of the performance evaluation is " + str(average_time_perfo))
                text_file.write("\nThe number of processes spawn is " + str(number_of_pools) + " the number of iterations is " + str(number_iterations))
                text_file.write("\nAnd the average overall time is " + str(average_time_total))
                text_file.close()
    else:
        # debug_info = 'total'
        start_exh = time.clock()
        a = datetime.now()
        print(f"start of the exhaustive approach without multiprocessing", a.strftime("%H:%M:%S.%f"))
        timing_list_exh = []
        timing_list_perfo = []
        timing_list_total = []
        for iteracion in range(number_iterations):
            print(f"iteration {iteracion}")
            # main function, the final results are two lists one of the mappings and another of the special nodes for the
            # mappings both of them are related  benchmark_new_version_backup

            number_pickles, final_node, flag_one_node = ex_map_no_multi_v10.ex_map_no_multi(DG, AG, debug_info, [],
                                                                                                dict_nodes_h,
                                                                                                dict_info_h,
                                                                                                selection_prints,
                                                                                                dict_nodes_a,
                                                                                                selection_pause,
                                                                                                dict_info_a,
                                                                                                DG_total, AG_total,
                                                                                                dict_total_h,
                                                                                                lista_constraints,
                                                                                                lista_tareas_constrains,
                                                                                                directorio).mapping()

            end_exh = time.clock()
            b = datetime.now()
            now = b.strftime("%H:%M:%S.%f")
            c = b - a

            print(
                f"end of the exhaustive approach, current time {now} the processing time is {c.seconds} seconds {c.microseconds} microseconds")
            timing_list_exh.append(c)


            ######almacenaremos todas las variables anteriores en una sola lista y la enviaremos a
            # las funciones de creacion de grafos
            debugging = False

            vector = []
            graphs = []
            perfo = []
            number_of_lists_processed = 0
            if selection_modules == 'total':

                e = datetime.now()
                t0 = datetime.now()
                now = t0.strftime("%H:%M:%S.%f")

                print(f"start of the performance evaluation, the current time is {now}")
                start_performance_benchmark = time.time()
                # We can select the type of verbosity during the performance evaluation, it is recommended to select none and
                # only change it if we are going to debug
                selection_prints_during_perfo = None
                latencia_resultado = 10000000000000000000000000000

                for n in range(0, number_pickles):
                    name_pickle = 'currentlist' + '_' + str(final_node) + '_' + str(n)
                    # name_pickle = 'partiallist' + str(n)
                    with open(os.path.join(directorio, name_pickle), 'rb') as f:
                        lista_total_mapping_large = pickle.load(f)
                    name_pickle = 'specialnodes' + '_' + str(final_node) + '_' + str(n)
                    # name_pickle = 'specialnodes' + str(n)
                    with open(os.path.join(directorio, name_pickle), 'rb') as f:
                        lista_total_nodes_mapping_large = pickle.load(f)

                    # the list could has up to 1000 lists, we need to divide it and then process it
                    number_of_pickles_large = 0
                    limit_number_list = 100
                    number_of_lists = len(lista_total_mapping_large)
                    inicio_lista = len(lista_total_mapping_large)

                    no_zero = True
                    while no_zero:
                        if number_of_lists - limit_number_list > 0:
                            name_pickle = 'partiallist' + str(number_of_pickles_large)
                            # print(lista_total_mapping[0:1])
                            with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                pickle.dump(lista_total_mapping_large[number_of_lists - limit_number_list:number_of_lists],
                                            f)
                            name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                            with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                pickle.dump(
                                    lista_total_nodes_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                            number_of_lists = number_of_lists - limit_number_list
                        else:
                            name_pickle = 'partiallist' + str(number_of_pickles_large)
                            with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                pickle.dump(lista_total_mapping_large[0:number_of_lists], f)
                            name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                            with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                pickle.dump(lista_total_nodes_mapping_large[0:number_of_lists], f)
                            no_zero = False
                        number_of_pickles_large = number_of_pickles_large + 1

                    lista_total_mapping_large = []
                    lista_total_nodes_mapping_large = []
                    # print(number_of_pickles_large)
                    for n_large in range(0, number_of_pickles_large):
                        name_pickle = 'partiallist' + str(n_large)
                        # name_pickle = 'partiallist' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_mapping = pickle.load(f)
                        os.remove(os.path.join(directorio, name_pickle))
                        name_pickle = 'partialspecialnodes' + str(n_large)
                        # name_pickle = 'specialnodes' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_nodes_mapping = pickle.load(f)
                        os.remove(os.path.join(directorio, name_pickle))

                        number_of_lists_processed = number_of_lists_processed + len(lista_total_mapping)
                         ### sin multi
                        while lista_total_mapping:

                            # first element of the list
                            elemento_a_evaluar = lista_total_mapping.pop(0)
                            # we check if the element has several time slots or only one, this because of one error during the
                            # performance that takes a mapping list with only one time slot as a mapping list of a number of time slots
                            # equal to the number of elements of the mapping list
                            if isinstance(elemento_a_evaluar[0][0], bool):
                                list_to_graph = [elemento_a_evaluar]
                            else:
                                list_to_graph = elemento_a_evaluar
                            # we retrieve also the information about the special nodes
                            try:
                                lista_nodos_especiales = lista_total_nodes_mapping.pop(0)

                            except:
                                lista_nodos_especiales = []

                            # debug part, in here we can select one particular mapping and see if there is an error during the
                            # processing of it

                            name_debug = 'validacion-' + str(4)
                            # if j == 4:
                            #     selection_prints_during_perfo = 'none'
                            # else:
                            #     selection_prints_during_perfo = 'none'
                            nombre_debug_performance = 'bla' + str(4)

                            # we perform the evaluation
                            try:
                                latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
                                    PerfoEval_v10.performance_evaluation_function_v2(
                                        list_to_graph, DG, lista_nodos_especiales, debugging_options,
                                        nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                                        dict_nodes_h,
                                        dict_nodes_a, DG_total_unroll,
                                        dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                                        AG)
                            except:
                                print("test")
                                MAP_performance = None

                            # if the evaluation is succesfull we see if it is better or worse than the previous one and we keep the best
                            if MAP_performance != None:
                                if MAP_performance < latencia_resultado:
                                    latencia_resultado = MAP_performance

                                    lista_mapping_best = list_to_graph.copy()
                                    lista_nodos_especiales_best = lista_nodos_especiales.copy()

                # after passing through all the possible mappings we ended up with the best and this one we ultimate process
                # again, this seems like a but that we need to fix todo fix this thing

                latency_evaluation, MAP, graph_total, MAP_performance, maximum_clock = \
                    performance_evaluation(
                        lista_mapping_best, DG,
                        lista_nodos_especiales_best,
                        debugging_options,
                        'bla', 'perfo', selection_prints, debug_info, dict_nodes_h, dict_nodes_a, DG_total_unroll,
                        dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll,
                        AG_total, method_evaluation, AG).perf_eval()

                nombre_implementation_graph = "implementation_graph_exh_" + str(iteracion) + ".pdf"
                nombre_final_graph = 'final_graph_' + str(iteracion)

                # after we perform again the evaluation we build the implementation graph
                vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP,
                                                                                        selection_prints,
                                                                                        dict_nodes_a,
                                                                                        latency_evaluation,
                                                                                        maximum_clock,
                                                                                        MAP_performance,
                                                                                        os.path.join(directorio,
                                                                                                     nombre_implementation_graph),
                                                                                        os.path.join(directorio,
                                                                                                     nombre_final_graph),
                                                                                        directorio)

                end_performance_benchmark = time.time()
                time_benchmark_performance = end_performance_benchmark - start_performance_benchmark
                if selection_prints == 'main':
                    print("the critical path is ", vector_longest)
                print(f"the value of the overall latency is {MAP_performance} clock cycles")

                d = datetime.now()
                now = d.strftime("%H:%M:%S.%f")
                f = d - e
                print(
                    f"end of the performance evaluation, current time {now} the processing time is {f.seconds} "
                    f"seconds {f.microseconds} microseconds for {number_of_lists_processed} mapping lists")
                g = d - a
                print(
                    f"The overall processing time is {g.seconds} seconds {g.microseconds} microseconds")
                if selection_show_implementation_graph:
                    plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, nombre_implementation_graph),
                                              shell=True)
                timing_list_perfo.append(f)
                timing_list_total.append(g)
        print(f"the average time of the exhaustive algorithm is "
              f"{(sum(timing_list_exh, timedelta()) / len(timing_list_exh)).total_seconds()}")
        print(f"the average time of the performance evaluation is "
              f"{(sum(timing_list_perfo, timedelta()) / len(timing_list_perfo)).total_seconds()}")
        print(f" the number of iterations is {number_iterations} "
              f"and the average overall time "
              f"is {(sum(timing_list_total, timedelta()) / len(timing_list_total)).total_seconds()}")




def perfo_multi_list(union_lista):
    list_to_graph = union_lista.pop(0)
    DG = union_lista.pop(0)
    lista_nodos_especiales = union_lista.pop(0)
    debugging_options = union_lista.pop(0)
    nombre_debug_performance = union_lista.pop(0)
    name_debug = union_lista.pop(0)
    selection_prints_during_perfo = union_lista.pop(0)
    debug_info = union_lista.pop(0)
    dict_nodes_h = union_lista.pop(0)
    dict_nodes_a = union_lista.pop(0)
    dict_info_h = union_lista.pop(0)
    dict_total_h = union_lista.pop(0)
    dict_info_a = union_lista.pop(0)
    # union_lista.pop(False)
    DG_total_unroll = union_lista.pop(0)
    AG_total = union_lista.pop(0)
    method_evaluation = union_lista.pop(0)
    AG = union_lista.pop(0)
    LIMIT_TIME_SLOTS = union_lista.pop(0)
    contador_time_slots_correctos = union_lista.pop(0)


    if LIMIT_TIME_SLOTS != None:
        if len(list_to_graph) > LIMIT_TIME_SLOTS:
            MAP_performance = 1000000000000000000000000000000000000000000000000000000
        else:
            try:
                # print(f"there is a preliminary mapping with {LIMIT_TIME_SLOTS} time slots")
                contador_time_slots_correctos = contador_time_slots_correctos + 1
                latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = performance_evaluation(
                        list_to_graph, DG, lista_nodos_especiales, debugging_options,
                        nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                        dict_nodes_h,
                        dict_nodes_a, DG_total_unroll,
                        dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                        AG).perf_eval()


                # latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
                #     PerfoEval_v10.performance_evaluation_function_v2(
                #         list_to_graph, DG, lista_nodos_especiales, debugging_options,
                #         nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                #         dict_nodes_h,
                #         dict_nodes_a, DG_total_unroll,
                #         dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                #         AG)
            except:

                MAP_performance = 1000000000000000000000000000000000000000000000000000000
    else:
        try:
            latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = performance_evaluation(
                    list_to_graph, DG, lista_nodos_especiales, debugging_options,
                    nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
                    dict_nodes_h,
                    dict_nodes_a, DG_total_unroll,
                    dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
                    AG).perf_eval()


            # latency_evaluation_b, MAP, graph01, MAP_performance, dummy_clock = \
            #     PerfoEval_v10.performance_evaluation_function_v2(
            #         list_to_graph, DG, lista_nodos_especiales, debugging_options,
            #         nombre_debug_performance, name_debug, selection_prints_during_perfo, debug_info,
            #         dict_nodes_h,
            #         dict_nodes_a, DG_total_unroll,
            #         dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll, AG_total, method_evaluation,
            #         AG)
        except:

            MAP_performance = 1000000000000000000000000000000000000000000000000000000
    elemento = [MAP_performance,list_to_graph,lista_nodos_especiales,contador_time_slots_correctos]
    q.put(elemento)
    # return MAP_performance




def all_topological_sorts(G):

    count = dict(G.in_degree())
    # vertices with indegree 0
    D = deque([v for v, d in G.in_degree() if d == 0])
    # stack of first value chosen at a position k in the topological sort
    bases = []
    current_sort = []
    contador_topos = 0
    # do-while construct
    while True:
        assert all([count[v] == 0 for v in D])

        if len(current_sort) == len(G):
            print(current_sort)
            yield list(current_sort)
            contador_topos = contador_topos + 1
            if contador_topos> 10000:
                break
            # clean-up stack
            while len(current_sort) > 0:
                assert len(bases) == len(current_sort)
                q = current_sort.pop()

                # "restores" all edges (q, x)
                # NOTE: it is important to iterate over edges instead
                # of successors, so count is updated correctly in multigraphs
                for _, j in G.out_edges(q):
                    count[j] += 1
                    assert count[j] >= 0
                # remove entries from D
                while len(D) > 0 and count[D[-1]] > 0:
                    D.pop()

                # corresponds to a circular shift of the values in D
                # if the first value chosen (the base) is in the first
                # position of D again, we are done and need to consider the
                # previous condition
                D.appendleft(q)
                if D[-1] == bases[-1]:
                    # all possible values have been chosen at current position
                    # remove corresponding marker
                    bases.pop()
                else:
                    # there are still elements that have not been fixed
                    # at the current position in the topological sort
                    # stop removing elements, escape inner loop
                    break

        else:
            if len(D) == 0:
                raise ValueError("Graph contains a cycle.")

            # choose next node
            q = D.pop()
            # "erase" all edges (q, x)
            # NOTE: it is important to iterate over edges instead
            # of successors, so count is updated correctly in multigraphs
            for _, j in G.out_edges(q):
                count[j] -= 1
                assert count[j] >= 0
                if count[j] == 0:
                    D.append(j)
            current_sort.append(q)

            # base for current position might _not_ be fixed yet
            if len(bases) < len(current_sort):
                bases.append(q)

        if len(bases) == 0:
            break





if selection_algo == 'list':

    timing_list_map = []
    timing_list_perfo = []
    timing_list_total = []
    a = datetime.now()
    #####ecomputation enable, we need to verify if it works for all the cases
    recomputation_enable = False
    for nodo in DG_total:
        if DG_total.nodes[nodo]['type'] == 'rm':
            recomputation_enable = True
            break
        # print(DG_total.nodes[nodo])

    # input("enter something")
    print(f"General start of the list-based approach", a.strftime("%H:%M:%S.%f"))


    if list_type == 'alltopo':
        print(f"it will be applied to all topological sortings, recomputation enable {recomputation_enable}")
    else:
        print(f"it will be applied to only one topological sorting, recomputation enable {recomputation_enable}")

    # print(start_heuristic_process)
    # obtenemos los datapaths independientes
    datapaths = list_map_v20.generation_datapaths(DG)

    if selection_prints == 'main':
        print("The independent datapaths are ", datapaths)
        print("lets verify the application")
        for nodo in AG.nodes:
            print(nodo, AG.nodes[nodo])
        print("lets continue with the hardware")
        for nodo in DG.nodes:
            print(nodo, DG.nodes[nodo])
        print("end of the debug")

    # main call

    all_topologicals = False
    topological_app = []
    topological_hw = []
    list_selection = False

    sources_dg = obtencion_sources(DG)
    if list_type == 'alltopo':

        for number_of_pools in range(pool_range_min, pool_range_max):
            timing_list_map = []
            timing_list_perfo = []
            timing_list_total = []
            print(" ")
            print("start of the process with number of processes spawn", number_of_pools)
            z = datetime.now()
            for iteracion in range(number_iterations):
                k = datetime.now()
                print(f"start of iteration {iteracion}")
                all_topologicals = True

                bandera_multiple_lists = True
                number_of_lists = 200000000
                # in this lsit we will put all the lists that we obtain from the permutations of the source nodes and the rest
                # of the nodes
                vector_listas = []

                # all_topological_list = nx.all_topological_sorts(DG)
                all_topological_list = all_topological_sorts(DG)
                # for n in range(20):
                #     print(list(nx.topological_sort(DG)))
                # input(" test")
                application_topological = list(nx.topological_sort(AG))
                number_pickles = 0
                limit_number_list = 200
                lista_total_mapping = []
                lista_total_nodes_mapping = []
                counter_topo = 0

                # print(f"the number of total topological sorting {len(list(all_topological_list))}")
                for single_topological in all_topological_list:

                    # print(single_topological)
                    print(f"we will iterate with the sorting {single_topological}")
                    # print(lista_total_mapping)
                    try:
                        test_final = list_map_v20.ListBasedMapping(DG, AG, datapaths, dict_nodes_h, dict_info_h, selection_prints,
                                                               dict_nodes_a, selection_pause, dict_info_a, DG_total, AG_total,
                                                               dict_total_h,
                                                               debugging_options, lista_constraints, lista_tareas_constrains,
                                                               all_topologicals, application_topological, single_topological,
                                                                   list_selection,recomputation_enable)


                        lista_total_mapping.append(test_final.lista_final)
                        lista_total_nodes_mapping.append(test_final.lista_nodos_especiales)
                    except:
                        pass
                    if len(lista_total_mapping) > 999:
                        number_of_lists = len(lista_total_mapping)
                        inicio_lista = len(lista_total_mapping)
                        no_zero = True
                        while no_zero:
                            if number_of_lists - limit_number_list > 0:
                                name_pickle = 'list_based_mappings' + str(number_pickles)
                                # print(lista_total_mapping[0:1])
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_mapping[number_of_lists - limit_number_list:number_of_lists], f)
                                name_pickle = 'list_based_special_nodes' + str(number_pickles)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_nodes_mapping[number_of_lists - limit_number_list:number_of_lists], f)
                                number_of_lists = number_of_lists - limit_number_list
                            else:
                                name_pickle = 'list_based_mappings' + str(number_pickles)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_mapping[0:number_of_lists], f)
                                name_pickle = 'list_based_special_nodes' + str(number_pickles)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_nodes_mapping[0:number_of_lists], f)
                                no_zero = False
                            number_pickles = number_pickles + 1
                        lista_total_mapping = []
                        lista_total_nodes_mapping = []
                    counter_topo = counter_topo + 1

                c = datetime.now()
                d = c - k
                timing_list_map.append(d)

                print(f"end of the list-based mapping process using {counter_topo} topological sortings, the "
                      f"processing time "
                      f"is {d.seconds} seconds {d.microseconds} microseconds, the current time "
                      f"is ",c.strftime("%H:%M:%S.%f"))

                number_of_lists = len(lista_total_mapping)
                inicio_lista = len(lista_total_mapping)
                no_zero = True

                while no_zero:
                    if number_of_lists - limit_number_list > 0:
                        name_pickle = 'list_based_mappings' + str(number_pickles)
                        # print(lista_total_mapping[0:1])
                        with open(os.path.join(directorio, name_pickle), 'wb') as f:
                            pickle.dump(lista_total_mapping[number_of_lists - limit_number_list:number_of_lists], f)
                        name_pickle = 'list_based_special_nodes' + str(number_pickles)
                        with open(os.path.join(directorio, name_pickle), 'wb') as f:
                            pickle.dump(lista_total_nodes_mapping[number_of_lists - limit_number_list:number_of_lists], f)
                        number_of_lists = number_of_lists - limit_number_list
                    else:
                        name_pickle = 'list_based_mappings' + str(number_pickles)
                        with open(os.path.join(directorio, name_pickle), 'wb') as f:
                            pickle.dump(lista_total_mapping[0:number_of_lists], f)
                        name_pickle = 'list_based_special_nodes' + str(number_pickles)
                        with open(os.path.join(directorio, name_pickle), 'wb') as f:
                            pickle.dump(lista_total_nodes_mapping[0:number_of_lists], f)
                        no_zero = False
                    number_pickles = number_pickles + 1
                lista_total_mapping = []
                lista_total_nodes_mapping = []

                debugging = False

                vector = []
                graphs = []
                perfo = []

                if selection_modules == 'total':
                    b = datetime.now()
                    print(f"start of the performance evaluation in iteracion {iteracion}, the number of pools is {number_of_pools}"
                          f" the current time is ", b.strftime("%H:%M:%S.%f"))
                    q = Queue()

                    # lista_total_nodes_mapping = []
                    # lista_total_mapping = []
                    # lista_total_nodes_mapping.clear()
                    # lista_total_mapping.clear()
                    counter_evaluations = 0
                    # We can select the type of verbosity during the performance evaluation, it is recommended to select none and
                    # only change it if we are going to debug
                    selection_prints_during_perfo = None
                    latencia_resultado = 10000000000000000000000000000

                    for n in range(0, number_pickles):
                        name_pickle = 'list_based_mappings' + str(n)
                        # name_pickle = 'partiallist' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_mapping_large = pickle.load(f)
                        # os.remove(os.path.join(directorio, name_pickle))
                        name_pickle = 'list_based_special_nodes' + str(n)
                        # name_pickle = 'specialnodes' + str(n)
                        with open(os.path.join(directorio, name_pickle), 'rb') as f:
                            lista_total_nodes_mapping_large = pickle.load(f)
                        # os.remove(os.path.join(directorio, name_pickle))

                        # the list could has up to 1000 lists, we need to divide it and then process it
                        number_of_pickles_large = 0
                        limit_number_list = number_of_pools
                        number_of_lists = len(lista_total_mapping_large)
                        inicio_lista = len(lista_total_mapping_large)
                        # print(lista_total_mapping_large)
                        no_zero = True
                        while no_zero:
                            if number_of_lists - limit_number_list > 0:
                                name_pickle = 'partiallist' + str(number_of_pickles_large)
                                # print(lista_total_mapping[0:1])
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_mapping_large[number_of_lists - limit_number_list:number_of_lists],
                                                f)
                                name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(
                                        lista_total_nodes_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                                number_of_lists = number_of_lists - limit_number_list
                            else:
                                name_pickle = 'partiallist' + str(number_of_pickles_large)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_mapping_large[0:number_of_lists], f)
                                name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                                with open(os.path.join(directorio, name_pickle), 'wb') as f:
                                    pickle.dump(lista_total_nodes_mapping_large[0:number_of_lists], f)
                                no_zero = False
                            number_of_pickles_large = number_of_pickles_large + 1

                        lista_total_mapping_large = []
                        lista_total_nodes_mapping_large = []
                        # print(number_of_pickles_large)
                        for n_large in range(0, number_of_pickles_large):
                            name_pickle = 'partiallist' + str(n_large)
                            # name_pickle = 'partiallist' + str(n)
                            with open(os.path.join(directorio, name_pickle), 'rb') as f:
                                lista_total_mapping = pickle.load(f)
                            os.remove(os.path.join(directorio, name_pickle))
                            name_pickle = 'partialspecialnodes' + str(n_large)
                            # name_pickle = 'specialnodes' + str(n)
                            with open(os.path.join(directorio, name_pickle), 'rb') as f:
                                lista_total_nodes_mapping = pickle.load(f)
                            os.remove(os.path.join(directorio, name_pickle))
                            # print(lista_total_mapping)
                            #### con multi
                            processes = []
                            contador_time_slots = 0
                            for i in range(len(lista_total_mapping)):
                                counter_evaluations = counter_evaluations + 1
                                elemento_a_evaluar = lista_total_mapping[i]
                                if isinstance(elemento_a_evaluar[0][0], bool):
                                    list_to_graph = [elemento_a_evaluar]
                                else:
                                    list_to_graph = elemento_a_evaluar
                                # we retrieve also the information about the special nodes
                                try:
                                    lista_nodos_especiales = lista_total_nodes_mapping[i]

                                except:
                                    lista_nodos_especiales = []
                                j = 4
                                name_debug = 'validacion-' + str(j)
                                # if j == 4:
                                #     selection_prints_during_perfo = 'none'
                                # else:
                                #     selection_prints_during_perfo = 'none'
                                nombre_debug_performance = 'bla' + str(j)
                                union_list = []
                                union_list.append(list_to_graph)
                                union_list.append(DG)
                                union_list.append(lista_nodos_especiales)
                                union_list.append(debugging_options)
                                union_list.append(nombre_debug_performance)
                                union_list.append(name_debug)
                                union_list.append(selection_prints_during_perfo)
                                union_list.append(debug_info)
                                union_list.append(dict_nodes_h)
                                union_list.append(dict_nodes_a)
                                union_list.append(dict_info_h)
                                union_list.append(dict_total_h)
                                union_list.append(dict_info_a)
                                union_list.append(DG_total_unroll)
                                union_list.append(AG_total)
                                union_list.append(method_evaluation)
                                union_list.append(AG)
                                union_list.append(LIMIT_TIME_SLOTS)
                                union_list.append(contador_time_slots)
                                t = multiprocessing.Process(target=perfo_multi_list, args=(union_list,))
                                processes.append(t)
                                t.start()

                            for one_process in processes:
                                one_process.join()

                            resulting_list = []
                            while not q.empty():
                                resulting_list.append(q.get())
                            performance_list = []
                            for j in range(len(resulting_list)):
                                performance_list.append(resulting_list[j][0])
                            # print(performance_list)
                            min_index = min(range(len(performance_list)), key=performance_list.__getitem__)
                            MAP_performance = resulting_list[min_index][0]
                            if MAP_performance != None:
                                if MAP_performance < latencia_resultado:
                                    latencia_resultado = MAP_performance

                                    lista_mapping_best = resulting_list[min_index][1].copy()
                                    lista_nodos_especiales_best = resulting_list[min_index][2].copy()

                    latency_evaluation, MAP, graph_total, MAP_performance, maximum_clock = \
                        performance_evaluation(
                            lista_mapping_best, DG,
                            lista_nodos_especiales_best,
                            debugging_options,
                            'bla', 'perfo', selection_prints, debug_info, dict_nodes_h, dict_nodes_a, DG_total_unroll,
                            dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll,
                            AG_total, method_evaluation, AG).perf_eval()



                    # after we perform again the evaluation we build the implementation graph
                    name_implementation_graph = "implementation_graph_list_" + str(number_of_pools) + "_" + \
                                                str(iteracion) + ".pdf"
                    vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                            dict_nodes_a, latency_evaluation,
                                                                                            maximum_clock,
                                                                                            MAP_performance,
                                                                                            os.path.join(directorio,
                                                                                                         name_implementation_graph),
                                                                                            os.path.join(directorio,
                                                                                                         'final_graph'),directorio)


                    if selection_prints == 'main':
                        print("the critical path is ", vector_longest)
                    print(f"the value of the overall latency is {MAP_performance} clock cycles")

                    d = datetime.now()
                    now = d.strftime("%H:%M:%S.%f")
                    e = d - b
                    timing_list_perfo.append(e)
                    print(
                        f"end of the performance evaluation, the number of evaluations is {counter_evaluations}, current time "
                        f"{now} the processing time is {e.seconds} seconds {e.microseconds} microseconds")
                    if selection_show_implementation_graph:
                        plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, name_implementation_graph),
                                                  shell=True)


                    g = d - k
                    print(
                        f"The overall processing time is {g.seconds} seconds {g.microseconds} microseconds")
                    timing_list_total.append(g)

            print(f"the average time of the list-based algorithm is "
                  f"{(sum(timing_list_map, timedelta()) / len(timing_list_map)).total_seconds()}")
            if selection_modules == 'total':
                print(f"the average time of the performance evaluation is "
                      f"{(sum(timing_list_perfo, timedelta()) / len(timing_list_perfo)).total_seconds()}")

                print(
                    f"the number of processes spawn is {number_of_pools}, the number of iterations is {number_iterations} "
                    f"and the average overall time "
                    f"is {(sum(timing_list_total, timedelta()) / len(timing_list_total)).total_seconds()}")




    else:
        for iteracion in range(number_iterations):
            b = datetime.now()
            print(f"start of the iteration {iteracion} in the list-based mapping approach, the time is "
                  f"",b.strftime("%H:%M:%S.%f"))
            test_final = list_map_v20.ListBasedMapping(DG, AG, datapaths, dict_nodes_h, dict_info_h, selection_prints,
                                               dict_nodes_a, selection_pause, dict_info_a, DG_total, AG_total, dict_total_h,
                                               debugging_options, lista_constraints, lista_tareas_constrains,
                                               all_topologicals,topological_app,topological_hw,list_selection,recomputation_enable)

            c = datetime.now()
            d = c - b
            timing_list_map.append(d)
            print(f"end of the list-based mapping, the processing time is {d.seconds} seconds "
                  f"{d.microseconds} microseconds, the current time is ",c.strftime("%H:%M:%S.%f"))

            if selection_prints == 'main':
                print("we are going to print the time slots of the implementation graph in the list-based approach, "
                      "the lenght of the mapping list is ", len(test_final.lista_final))
                for elemento in test_final.lista_final:
                    print("time slot  ", elemento)
                print(f"the special nodes are {test_final.lista_nodos_especiales}")



            if selection_modules == 'total':
                # modulo de evaluacion de desempeno
                b = datetime.now()
                print(f"start of iteration {iteracion} of the performance evaluation in "
                      f"the list-based approach",b.strftime("%H:%M:%S.%f"))
                if isinstance(test_final.lista_final[0][0][0], bool):
                    if selection_prints == 'main':
                        print("bug when we have just one instance from the first stage")
                    list_to_graph = test_final.lista_final[0]
                else:
                    list_to_graph = test_final.lista_final

                #####variable para debuggear ciertas partes de la evaluacion de performance
                debugging = True

                # evaluacion de desempeno
                longest, MAP, graph_total, MAP_performance, maximum_clock = \
                    performance_evaluation(test_final.lista_final, DG,
                                           test_final.lista_nodos_especiales,
                                           debugging_options,
                                           'bla', 'perfo', selection_prints, selection_pause,
                                           dict_nodes_h, dict_nodes_a, DG_total_unroll,
                                           dict_info_h, dict_total_h, dict_info_a,
                                           debugging, DG_total_unroll, AG_total,
                                           method_evaluation, AG).perf_eval()



                if selection_prints == 'main':
                    print(f"longest {longest}")


                name_implementation_graph = "implementation_graph_list_" + str(iteracion) + ".pdf"
                vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                        dict_nodes_a, longest, maximum_clock,
                                                                                        MAP_performance,
                                                                                        os.path.join(directorio,
                                                                                                     name_implementation_graph),
                                                                                        os.path.join(directorio, 'final_graph'),directorio)





                if selection_prints == 'main':
                    print("the critical path is ", vector_longest)

                print(f"the value of the overall latency is {MAP_performance} clock cycles")

                c = datetime.now()
                d = c - b
                timing_list_perfo.append(d)
                print(f"end of the iteration {iteracion} of the performance evaluation, the processing time is "
                      f"{d.seconds} seconds {d.microseconds} microseconds, the current time "
                      f"is ",c.strftime("%H:%M:%S.%f"))
                d = c - a
                timing_list_total.append(d)
                print(f"the overall processing time is {d.seconds} seconds {d.microseconds} microseconds")
                if selection_show_implementation_graph:
                    plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, name_implementation_graph), shell=True)

        print(f"the average time of the list-based mapping algorithm is "
              f"{(sum(timing_list_map, timedelta()) / len(timing_list_map)).total_seconds()}")
        if selection_modules == 'total':
            print(f"the average time of the performance evaluation is "
                  f"{(sum(timing_list_perfo, timedelta()) / len(timing_list_perfo)).total_seconds()}")

            print(f"The number of iterations is {number_iterations} "
                  f"and the average overall time "
                  f"is {(sum(timing_list_total, timedelta()) / len(timing_list_total)).total_seconds()}, "
                 f"the current time is", datetime.now().strftime("%H:%M:%S.%f"))





















if selection_algo == 'q-l':

    folder_txt = directorio + '/folder_result/'
    try:
        os.mkdir(folder_txt)
    except:
        pass
    try:
        text_file = open(os.path.join(folder_txt, "results.txt"), "x")
    except:
        os.remove(os.path.join(folder_txt, "results.txt"))
        text_file = open(os.path.join(folder_txt, "results.txt"), "x")
    text_file.write("-------------------------------------------------------------------\n")
    text_file.write("Q-learning approach \n")
    text_file.write("specifications of the test: hw: " + filepath_hw + ", app: " + filepath_app + ",\n")



    timing_list_ql_map = []
    timing_list_ql_perfo = []
    timing_list_ql_total = []
    a = datetime.now()

    print(f"General start of the q-learning approach", a.strftime("%H:%M:%S.%f"))
    try:
        with open(os.path.join(filepath_rewards, 'rewards_vector'), 'rb') as f:
            rewards_vector_original = pickle.load(f)
            text_file.write("the rewards path used is " + filepath_rewards + " with a number of iterations " + str(number_iterations) + "\n")
    except:
        print("No path to the rewards file is specified, we will use the default values")
        text_file.write("No reward path specified \n")
    text_file.close()
    # if len(rewards_vector) != number_iterations:
    #     print("Error in the number of rewards sets, is not equal to "
    #           "the number of iterations", len(rewards_vector), " != ", number_iterations)
    #     raise ValueError

    vector_training_rewards_resources = []
    vector_training_rewards_mapping = []
    vector_total_reward_resources = []
    vector_total_reward_mapping = []


    for iteracion in range(number_iterations):



        debugging = False
        pickle_name = [] # if there is a previous pickle
        b = datetime.now()
        print(f"start of iteration {iteracion} of the q-learning "
              f"mapping algorithm", b.strftime("%H:%M:%S.%f"))

        now = b.strftime("%H:%M:%S.%f")
        current_date = b.strftime("%d/%m")
        text_file = open(os.path.join(folder_txt, "results.txt"), "a")
        text_file.write("\nbegin of iteration " + str(iteracion) + ", current date: " + current_date + ", current time: " + now)
        # text_file.write("\nprocessing time is " + str(b.days) + " days " + str(b.seconds) + " seconds " + str(
        #     b.microseconds) + " microseconds")
        text_file.close()
        # print("the iteration number is ",iteracion)

        ################################MAPPING ALGORITHM
        # this print will be used for each episode, if we need to debug during that period we may change it,
        # but otherwise it is better to leave as none

        selection_prints_during_perfo = 'none'
        # total_mapping_reward = 0.4
        # verification_parameters_reward = 0.75
        # verification_of_data_dependence_reward = 0.80
        # verification_of_source_reward = 0.10
        # verification_of_actuator_reward = 0.10
        # latency_reward = 0.10
        # verification_degree_reward = 0.15
        # suc_and_prede_parameters = 0.20
        # performance_evaluation_reward = 0.5
        #
        # with open(os.path.join(filepath_rewards, 'rewards_vector'), 'rb') as f:
        #     rewards_vector = pickle.load(f)
        # print(rewards_vector)
        # rewards_vector = [total_mapping_reward,verification_parameters_reward,verification_of_data_dependence_reward,
        #                   verification_of_source_reward,verification_of_actuator_reward,latency_reward,
        #                   verification_degree_reward,suc_and_prede_parameters,performance_evaluation_reward]

        ############################REWARDS
        try:
            rewards_vector = rewards_vector_original[iteracion]
        except:
            rewards_vector = None

        qlearning_method = ql_map_v10.QLearning_V1(DG, AG, dict_nodes_h,
                                                     dict_info_h, selection_prints, dict_nodes_a, selection_pause,
                                                     dict_info_a, DG_total,
                                                     AG_total, dict_total_h, lista_constraints,
                                                     lista_tareas_constrains,pickle_name,debugging,directorio,debug_info,
                                                   debugging_options,selection_prints_during_perfo,
                                                   DG_total_unroll,method_evaluation,iteracion,folder_txt,
                                                   rewards=rewards_vector,
                                                   episodes_training=EPISODES_OFFLINE, start_of_decay_training=DECAY_START_OFFLINE,
                                                   end_decay_training=DECAY_END_OFFLINE, episodes_training_online=EPISODES_ONLINE,
                                                   start_of_decay_training_online=DECAY_START_ONLINE,
                                                   end_decay_training_online=DECAY_END_ONLINE)

        c = datetime.now()

        now = c.strftime("%H:%M:%S.%f")
        d = c - b

        print(
            f"end of the iteration {iteracion} of the q-learning approach , current time {now} the processing time is {d.seconds} seconds "
            f"{d.microseconds} microseconds")
        now = c.strftime("%H:%M:%S.%f")
        current_date = c.strftime("%d/%m")
        text_file = open(os.path.join(folder_txt, "results.txt"), "a")
        text_file.write(
            "\nend of iteration " + str(iteracion) + ", current date: " + current_date + ", current time: " + now)
        text_file.write("\nprocessing time is " + str(d.days) + " days " + str(d.seconds) + " seconds " + str(
            d.microseconds) + " microseconds")
        text_file.close()

        if selection_prints == 'main':
            print("de regreso a la funcion principal")
            print(qlearning_method.lista_mapping)

        if selection_modules == 'total':
            # modulo de evaluacion de desempeno
            g = datetime.now()
            print(f"start of the iteration {iteracion} of the performance evaluation in the q-learning process, time ", g.strftime("%H:%M:%S.%f"))
            now = g.strftime("%H:%M:%S.%f")
            current_date = g.strftime("%d/%m")
            text_file = open(os.path.join(folder_txt, "results.txt"), "a")
            text_file.write(
                "\nstart of the performance evaluation of  " + str(iteracion) + ", current date: " + current_date + ", current time: " + now)
            # text_file.write("\nprocessing time is " + str(d.days) + " days " + str(d.seconds) + " seconds " + str(
            #     d.microseconds) + " microseconds")
            text_file.close()


            if isinstance(qlearning_method.lista_mapping[0][0][0], bool):
                if selection_prints == 'main':
                    print("bug when we have just one instance from the first stage")
                list_to_graph = qlearning_method.lista_mapping[0]
            else:
                list_to_graph = qlearning_method.lista_mapping

            if selection_prints == 'basic':
                # print(qlearning_method.lista_nodos_especiales)
                print("WE ARE GOING TO START THE PERFORMANCE EVALUATION ")
                print("  ")

            #####variable para debuggear ciertas partes de la evaluacion de performance
            debugging = False
            selection_prints_during_perfo = selection_prints
            # evaluacion de desempeno
            longest, MAP, graph_total, MAP_performance, maximum_clock = \
                performance_evaluation(qlearning_method.lista_mapping, DG,
                                       qlearning_method.lista_nodos_especiales,
                                       debugging_options,
                                       'bla', 'perfo', selection_prints_during_perfo, selection_pause,
                                       dict_nodes_h, dict_nodes_a, DG_total_unroll,
                                       dict_info_h, dict_total_h, dict_info_a,
                                       debugging, DG_total_unroll, AG_total,
                                       method_evaluation, AG).perf_eval()

            if selection_prints == 'main':
                print(f"longest {longest}")

            name_implementation_graph = 'implementation_graph_ql_' + str(iteracion) + '.pdf'
            vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                    dict_nodes_a, longest, maximum_clock,
                                                                                    MAP_performance,
                                                                                    os.path.join(directorio,
                                                                                                 name_implementation_graph),
                                                                                    os.path.join(directorio, 'final_graph'),directorio)

            if selection_prints == 'main':
                print("the critical path is ", vector_longest)
            print(f"the value of the overall latency is {MAP_performance} clock cycles")
            c = datetime.now()

            now = c.strftime("%H:%M:%S.%f")
            d = c - g

            print(
                f"end of the iteration {iteracion} of the performance evaluation in the q-learning approach, current time {now} the processing "
                f"time is {d.seconds} seconds "
                f"{d.microseconds} microseconds")

            t = c - b

            print(f"the overall time is {t.seconds} seconds {t.microseconds} microseconds")

            now = c.strftime("%H:%M:%S.%f")
            current_date = c.strftime("%d/%m")
            text_file = open(os.path.join(folder_txt, "results.txt"), "a")
            text_file.write(
                "\nend of performance evaluation " + str(iteracion) + ", current date: " + current_date + ", current time: " + now)
            text_file.write("\nprocessing time is " + str(d.days) + " days " + str(d.seconds) + " seconds " + str(
                d.microseconds) + " microseconds")
            text_file.write("\nthe value of the overall latency is " + str(MAP_performance) + " clock cycles")
            text_file.write("\nthe overall processing time is " + str(t.days) + " days " + str(t.seconds) + " seconds " + str(
                t.microseconds) + " microseconds")
            text_file.close()
            # timing_list_heu_perfo.append(d)
            # t = c - b
            # timing_list_heu_total.append(t)
            # print(f"the overall time is {t.seconds} seconds {t.microseconds} microseconds")
            # para visualizar el pdf con los datos del grafo e informacion de la impementacion

            if selection_show_implementation_graph:
                plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, name_implementation_graph), shell=True)


        smooth_training_rewards_resources = gaussian_filter1d(qlearning_method.training_rewards_resources, sigma=2)
        smooth_training_rewards_mapping = gaussian_filter1d(qlearning_method.training_rewards_mapping, sigma=2)
        smooth_total_reward_resources = gaussian_filter1d(qlearning_method.total_reward_resources[0], sigma=2)
        smooth_total_reward_mapping = gaussian_filter1d(qlearning_method.total_reward_mapping[0], sigma=2)

        vector_training_rewards_resources.append(smooth_training_rewards_resources)
        vector_training_rewards_mapping.append(smooth_training_rewards_mapping)
        vector_total_reward_resources.append(smooth_total_reward_resources)
        vector_total_reward_mapping.append(smooth_total_reward_mapping)

    # print(qlearning_method.total_reward_mapping,qlearning_method.total_reward_resources)
    # fig, ax = plt.subplots(nrows=len(qlearning_method.total_reward_mapping)+0+len(qlearning_method.total_reward_resources),
    #                        ncols=1, figsize=(18, 5))


    # ax[0].plot(qlearning_method.training_rewards_mapping, label='reward training mapping')
    # ax[1].plot(qlearning_method.training_rewards_resources, label='reward training resources')
    # # plt.legend()
    # for n in range(0,len(qlearning_method.total_reward_mapping)):
    #     ax[n + 2].plot(qlearning_method.total_reward_mapping[n], label='rewards online mapping' + str(n))
    # if qlearning_method.total_reward_resources:

    # print(len(qlearning_method.total_reward_resources))
    # print(qlearning_method.training_rewards_resources)

    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # fig.suptitle('Horizontally stacked subplots')
    # smooth_training_rewards_resources = gaussian_filter1d(qlearning_method.training_rewards_resources, sigma=2)
    #
    # smooth_training_rewards_mapping = gaussian_filter1d(qlearning_method.training_rewards_mapping, sigma=2)
    # ax1.plot(smooth_training_rewards_resources)
    # ax2.plot(smooth_training_rewards_mapping)

    fig = plt.figure()

    # smooth_training_rewards_resources = gaussian_filter1d(qlearning_method.training_rewards_resources, sigma=2)
    # smooth_training_rewards_mapping = gaussian_filter1d(qlearning_method.training_rewards_mapping, sigma=2)
    # smooth_total_reward_resources = gaussian_filter1d(qlearning_method.total_reward_resources[0], sigma=2)
    # smooth_total_reward_mapping = gaussian_filter1d(qlearning_method.total_reward_mapping[0], sigma=2)

    # name_csv = 'testcsv'
    #
    # with open(os.path.join(directorio, name_csv), 'w', newline='') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    #     wr.writerow(smooth_total_reward_mapping)
    #     wr.writerow(smooth_training_rewards_mapping)

    # vector_training_rewards_resources.append(smooth_training_rewards_resources)
    # vector_training_rewards_mapping.append(smooth_training_rewards_mapping)
    # vector_total_reward_resources.append(smooth_total_reward_resources)
    # vector_total_reward_mapping.append(smooth_total_reward_mapping)
    # error antes de app03hw03
    test_name = 'app12hw09'

    plt.subplot(2, 2, 1,title='Offline training resources reward')
    # plt.suptitle('Offline training resources reward')
    name_csv = 'vector_training_rewards_resources' + test_name + '.csv'
    with open(os.path.join(directorio, name_csv), 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for iteration in range(number_iterations):
            if iteration == 0:
                color_plot = 'b'
            elif iteration == 1:
                color_plot = 'r'
            else:
                color_plot = 'g'
            plt.plot(vector_training_rewards_resources[iteration],color_plot)
            wr.writerow(vector_training_rewards_resources[iteration])
    # plt.plot(smooth_total_reward_resources)

    plt.subplot(2, 2, 2,title='Offline training total reward')
    # plt.suptitle('Offline training mapping reward')
    name_csv = 'vector_training_rewards_mapping' + test_name  + '.csv'
    with open(os.path.join(directorio, name_csv), 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for iteration in range(number_iterations):
            if iteration == 0:
                color_plot = 'b'
            elif iteration == 1:
                color_plot = 'r'
            else:
                color_plot = 'g'
            plt.plot(vector_training_rewards_mapping[iteration],color_plot)
            wr.writerow(vector_training_rewards_mapping[iteration])
    # plt.plot(smooth_training_rewards_mapping)

    plt.subplot(2, 2, 3,title='Online training resources reward')
    # plt.suptitle('Online training resources reward')
    name_csv = 'vector_total_reward_resources' + test_name + '.csv'
    with open(os.path.join(directorio, name_csv), 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for iteration in range(number_iterations):
            if iteration == 0:
                color_plot = 'b'
            elif iteration == 1:
                color_plot = 'r'
            else:
                color_plot = 'g'
            plt.plot(vector_total_reward_resources[iteration],color_plot)
            wr.writerow(vector_total_reward_resources[iteration])
    # plt.plot(smooth_total_reward_resources)

    plt.subplot(2, 2, 4,title='Online training total reward')
    # plt.suptitle('Online training mapping reward')
    name_csv = 'vector_total_reward_mapping' + test_name + '.csv'
    with open(os.path.join(directorio, name_csv), 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for iteration in range(number_iterations):
            if iteration == 0:
                color_plot = 'b'
            elif iteration == 1:
                color_plot = 'r'
            else:
                color_plot = 'g'
            plt.plot(vector_total_reward_mapping[iteration],color_plot)
            wr.writerow(vector_total_reward_mapping[iteration])
    # plt.plot(smooth_total_reward_mapping)

    plt.show()
    # name_plot = test_name + '.pdf'
    # plt.savefig(os.path.join(directorio, name_plot))

    #
    #
    # if len(qlearning_method.total_reward_resources) == 1:
    #     print("entrada ")
    #     # plt.figure(figsize=(9, 3))
    #     plt.plot(qlearning_method.total_reward_resources[0])
    #     plt.suptitle('Rewards')
    #     # plt.figure(figsize=(18, 5))
    #     plt.show()
    # else:
    #     fig, ax = plt.subplots(
    #         nrows=0 + 0 + len(qlearning_method.total_reward_resources),
    #         ncols=1, figsize=(18, 5))
    #     inicio = 1
    #
    #     for n in range(0,len(qlearning_method.total_reward_resources)):
    #         print(n)
    #         # ax[n + 2 + len(qlearning_method.total_reward_mapping)].plot(qlearning_method.total_reward_resources[n],
    #         #                                                             label='rewards online resources ' + str(n))
    #         ax[n].plot(qlearning_method.total_reward_resources[n],label='rewards online resources ' + str(n))
    #
    #
    #


        # plt.legend()
    # plt.show()


vector_of_already_know_good_mappings = [20345,33615,33623,33624,33625,33626,36933,36942,36943,36944,36949,36954,9805,
                                        34219,34222,34223,34224,40256,4204,10922,10925,1546]

if selection_algo == 'none' and selection_modules == 'total':
    iteracion = 0
    a = datetime.now()
    folder_txt = directorio + '/folder_result/'
    try:
        os.mkdir(folder_txt)
    except:
        pass
    try:
        text_file = open(os.path.join(folder_txt, "results.txt"), "x")
    except:
        os.remove(os.path.join(folder_txt, "results.txt"))
        text_file = open(os.path.join(folder_txt, "results.txt"), "x")
    text_file.write("Only performance evaluation")
    text_file.write("threads for the performance evaluation:  "
                    + str(pool_range_min) + "-" + str(pool_range_max))
    text_file.close()
    q = Queue()

    e = datetime.now()
    now = e.strftime("%H:%M:%S.%f")
    current_date = e.strftime("%d/%m")
    print(f"start of the performance evaluation without mapping algorithm, the current date {current_date}, current time is {now}")
    text_file = open(os.path.join(folder_txt, "results.txt"), "a")
    text_file.write(
        "\nstart of the performance evaluation, the current date is " + current_date + ", the current time is " + now)
    text_file.close()
    start_performance_benchmark = time.time()
    # We can select the type of verbosity during the performance evaluation, it is recommended to select none and
    # only change it if we are going to debug
    selection_prints_during_perfo = selection_prints
    #####################################################################
    ##############if we already started the process of iterating list by list we have a preliminar results txt,
    # so we read it and we will eliminate the already processed lists
    already_started_process = False
    path_of_the_preliminary_process = 'preliminary_results/results.txt'
    vector_preliminary_results = []
    if already_started_process:
        with open(path_of_the_preliminary_process) as myFile:
            text = myFile.read()
        result = text.split('\n')
        vector_preliminary_results = []
        for elemento in result:
            if elemento.startswith('the pickle'):
                # print(elemento)
                pedazos = elemento.split(' ')
                # print(pedazos[2])
                vector_preliminary_results.append(int(pedazos[2]))

    ######if we have already the number of the files we only need to load these numbers to the vector_preliminary_results
    # and enable the flag to skip the already read files, the pickle where the numbers are should be stored in the main
    # folder, and the name should be "list_of_copy_files"
    parallel_process_of_lists = True
    if parallel_process_of_lists:
        with open(os.path.join(dir_path, "list_of_copy_files"), 'rb') as f:
            vector_preliminary_results = pickle.load(f)
        already_started_process = True


    latencia_resultado = 1000000000000000000000000000000000000
    print(f"start of counting the pickles")
    number_pickles = 0
    final_node = None
    vector_numbers = []
    if os.path.exists(directorio):

        for file in os.listdir(directorio):
            if file.startswith('currentlist_'):

                try:
                    nombre_strip = str(file)
                    nombre_strip = nombre_strip.split('_')
                    if already_started_process:
                        if int(nombre_strip[2]) not in vector_preliminary_results:
                            vector_numbers.append(int(nombre_strip[2]))
                            number_pickles += 1
                    else:
                        vector_numbers.append(int(nombre_strip[2]))
                        number_pickles += 1
                    final_node = int(nombre_strip[1])
                except:
                    pass
        # print('expressmail')
        # print('Total files found:', number_pickles)
    # if we know the good mappings before hand
    number_pickles = len(vector_of_already_know_good_mappings) - 1
    vector_numbers = vector_of_already_know_good_mappings
    print(f"the total number of pickles is {number_pickles}, the last node mapped is {final_node}")
    e = datetime.now()
    now = e.strftime("%H:%M:%S.%f")
    current_date = e.strftime("%d/%m")
    text_file = open(os.path.join(folder_txt, "results.txt"), "a")
    text_file.write(
        "\nthe total number of pickles is " + str(number_pickles) + ", the current date is " + current_date + ", the current time is " + now)
    text_file.close()
    if number_pickles == 0 or final_node == None:
        print(f"Error : No preliminary mappings in the specified folder")
        raise ValueError

    contador_time_slots = [0 for n in range(len(AG.nodes))]
    aproximado_de_total_listas = number_pickles
    contador_time_slots_correctos = 0
    for number_of_pools in range(pool_range_min, pool_range_max):
        number_of_lists_processed = 0
        for n in range(0, number_pickles):
            e_begin = datetime.now()
            name_pickle = 'currentlist' + '_' + str(final_node) + '_' + str(vector_numbers[n])
            # name_pickle = 'partiallist' + str(n)
            with open(os.path.join(directorio, name_pickle), 'rb') as f:
                lista_total_mapping_large = pickle.load(f)
            name_pickle = 'specialnodes' + '_' + str(final_node) + '_' + str(vector_numbers[n])
            # name_pickle = 'specialnodes' + str(n)
            with open(os.path.join(directorio, name_pickle), 'rb') as f:
                lista_total_nodes_mapping_large = pickle.load(f)

            # the list could has up to 1000 lists, we need to divide it and then process it
            number_of_pickles_large = 0
            limit_number_list = number_of_pools
            number_of_lists = len(lista_total_mapping_large)
            inicio_lista = len(lista_total_mapping_large)
            # print(lista_total_mapping_large)
            print(f"the pickle {vector_numbers[n]} has {number_of_lists} lists")
            e = datetime.now()
            now = e.strftime("%H:%M:%S.%f")
            current_date = e.strftime("%d/%m")
            text_file = open(os.path.join(folder_txt, "results.txt"), "a")
            text_file.write(
                "\nthe pickle " + str(
                    vector_numbers[n]) +    " has " + str(number_of_lists)+" lists, the "
                                                                           "current date is " + current_date +
                ", the current time is " + now)
            text_file.close()
            no_zero = True
            while no_zero:
                if number_of_lists - limit_number_list > 0:
                    name_pickle = 'partiallist' + str(number_of_pickles_large)
                    # print(lista_total_mapping[0:1])
                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                        pickle.dump(lista_total_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                    name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                        pickle.dump(
                            lista_total_nodes_mapping_large[number_of_lists - limit_number_list:number_of_lists], f)
                    number_of_lists = number_of_lists - limit_number_list
                else:
                    name_pickle = 'partiallist' + str(number_of_pickles_large)
                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                        pickle.dump(lista_total_mapping_large[0:number_of_lists], f)
                    name_pickle = 'partialspecialnodes' + str(number_of_pickles_large)
                    with open(os.path.join(directorio, name_pickle), 'wb') as f:
                        pickle.dump(lista_total_nodes_mapping_large[0:number_of_lists], f)
                    no_zero = False
                number_of_pickles_large = number_of_pickles_large + 1

            lista_total_mapping_large = []
            lista_total_nodes_mapping_large = []

            # print(number_of_pickles_large)
            contador_time_slots_buffer = contador_time_slots[LIMIT_TIME_SLOTS]
            for n_large in range(0, number_of_pickles_large):
                name_pickle = 'partiallist' + str(n_large)
                # name_pickle = 'partiallist' + str(n)
                with open(os.path.join(directorio, name_pickle), 'rb') as f:
                    lista_total_mapping = pickle.load(f)
                os.remove(os.path.join(directorio, name_pickle))
                name_pickle = 'partialspecialnodes' + str(n_large)
                # name_pickle = 'specialnodes' + str(n)
                with open(os.path.join(directorio, name_pickle), 'rb') as f:
                    lista_total_nodes_mapping = pickle.load(f)
                os.remove(os.path.join(directorio, name_pickle))

                #### con multi
                processes = []
                number_of_lists_processed = number_of_lists_processed + len(lista_total_mapping)
                for i in range(len(lista_total_mapping)):
                    elemento_a_evaluar = lista_total_mapping[i]
                    if isinstance(elemento_a_evaluar[0][0], bool):
                        list_to_graph = [elemento_a_evaluar]
                    else:
                        list_to_graph = elemento_a_evaluar
                    # we retrieve also the information about the special nodes
                    try:
                        lista_nodos_especiales = lista_total_nodes_mapping[i]

                    except:
                        lista_nodos_especiales = []
                    j = 4
                    name_debug = 'validacion-' + str(j)
                    contador_time_slots[len(list_to_graph) - 1] = contador_time_slots[len(list_to_graph) - 1] + 1
                    # if j == 4:
                    #     selection_prints_during_perfo = 'none'
                    # else:
                    #     selection_prints_during_perfo = 'none'
                    nombre_debug_performance = 'bla' + str(j)
                    union_list = []
                    union_list.append(list_to_graph)
                    union_list.append(DG)
                    union_list.append(lista_nodos_especiales)
                    union_list.append(debugging_options)
                    union_list.append(nombre_debug_performance)
                    union_list.append(name_debug)
                    union_list.append(selection_prints_during_perfo)
                    union_list.append(debug_info)
                    union_list.append(dict_nodes_h)
                    union_list.append(dict_nodes_a)
                    union_list.append(dict_info_h)
                    union_list.append(dict_total_h)
                    union_list.append(dict_info_a)
                    union_list.append(DG_total_unroll)
                    union_list.append(AG_total)
                    union_list.append(method_evaluation)
                    union_list.append(AG)
                    union_list.append(LIMIT_TIME_SLOTS)
                    union_list.append(contador_time_slots_correctos)
                    t = multiprocessing.Process(target=perfo_multi, args=(union_list,))
                    processes.append(t)
                    t.start()

                for one_process in processes:
                    one_process.join()

                resulting_list = []
                while not q.empty():
                    resulting_list.append(q.get())
                performance_list = []
                vector_contador_time_slots_correctos = []
                for j in range(len(resulting_list)):
                    performance_list.append(resulting_list[j][0])
                    vector_contador_time_slots_correctos.append(resulting_list[j][3])
                # print(performance_list)
                max_contador_time_slots = max(range(len(vector_contador_time_slots_correctos)),
                                              key=vector_contador_time_slots_correctos.__getitem__)
                if contador_time_slots_correctos < max_contador_time_slots:
                    contador_time_slots_correctos = max_contador_time_slots
                min_index = min(range(len(performance_list)), key=performance_list.__getitem__)
                MAP_performance = resulting_list[min_index][0]
                if MAP_performance != None:
                    if MAP_performance < latencia_resultado:
                        latencia_resultado = MAP_performance

                        lista_mapping_best = resulting_list[min_index][1].copy()
                        lista_nodos_especiales_best = resulting_list[min_index][2].copy()

            e_2 = datetime.now()
            now = e_2.strftime("%H:%M:%S.%f")
            current_date = e_2.strftime("%d/%m")
            e_elapsed = e_2 - e_begin
            aproximado_de_proceso = (100 *  n) / aproximado_de_total_listas
            if contador_time_slots_buffer < contador_time_slots[LIMIT_TIME_SLOTS]:
                print(f"At least one preliminary mapping has the same or fewer than {LIMIT_TIME_SLOTS} time slots")
                text_file = open(os.path.join(folder_txt, "results.txt"), "a")
                text_file.write("\nThe pickle " + str(vector_numbers[n]) + " contains at least one preliminary mapping with the number of "
                                                                           "time slots smaller or equal to " + str(LIMIT_TIME_SLOTS))
                text_file.close()
            print(f"The percentage of already processed lists is {aproximado_de_proceso}, "
                  f"current date {current_date}, current time {now}, there are {contador_time_slots_correctos}"
                  f" mappings that have the good number of time slots ")
            print(f"the processing time for {inicio_lista} lists is {e_elapsed.days} days, {e_elapsed.seconds} seconds,"
                  f" {e_elapsed.microseconds} microseconds")


        # after passing through all the possible mappings we ended up with the best and this one we ultimate process
        # again, this seems like a but that we need to fix todo fix this thing

        latency_evaluation, MAP, graph_total, MAP_performance, maximum_clock = \
            perfomance_evaluation_exh(
                lista_mapping_best, DG,
                lista_nodos_especiales_best,
                debugging_options,
                'bla', 'perfo', selection_prints, debug_info, dict_nodes_h, dict_nodes_a, DG_total_unroll,
                dict_info_h, dict_total_h, dict_info_a, False, DG_total_unroll,
                AG_total, method_evaluation, AG).perf_eval()

        nombre_implementation_graph = "implementation_graph_exh_" + str(iteracion) + "_" + \
                                      str(number_of_pools) + ".pdf"
        nombre_final_graph = 'final_graph_' + str(iteracion) + '_' + str(number_of_pools)

        # after we perform again the evaluation we build the implementation graph
        vector_longest, graph = GraphVisualization.gen_implementation_graph_heu(graph_total, MAP, selection_prints,
                                                                                dict_nodes_a, latency_evaluation,
                                                                                maximum_clock,
                                                                                MAP_performance,
                                                                                os.path.join(directorio,
                                                                                             nombre_implementation_graph),
                                                                                os.path.join(directorio,
                                                                                             nombre_final_graph),
                                                                                directorio)

        end_performance_benchmark = time.time()
        time_benchmark_performance = end_performance_benchmark - start_performance_benchmark
        if selection_prints == 'main':
            print("the critical path is ", vector_longest)
        print(f"the value of the overall latency is {MAP_performance} clock cycles")
        print(f"the final counter of time slots is {contador_time_slots}")
        d = datetime.now()
        now = d.strftime("%H:%M:%S.%f")
        f = d - e

        current_date = d.strftime("%d/%m")
        print(
            f"end of the performance evaluation, current date {current_date}, current time {now} the processing time is {f.days} days {f.seconds} "
            f"seconds {f.microseconds} microseconds for {number_of_lists_processed} mapping lists")
        g = d - a
        print(
            f"The overall processing time is  {g.days} days  {g.seconds} seconds {g.microseconds} microseconds")
        if selection_show_implementation_graph:
            plot02 = subprocess.Popen("evince '%s'" % os.path.join(directorio, nombre_implementation_graph),
                                      shell=True)
        # timing_list_perfo.append(f)
        # timing_list_total.append(g)
        text_file = open(os.path.join(folder_txt, "results.txt"), "a")
        text_file.write("\nThe value of the overall latency is " + str(MAP_performance) + " clock cycles")
        for n_time_slot in range(len(contador_time_slots)):
            text_file.write("\nThe number of mappings with " + str(n_time_slot + 1) + "time slots is " + str(contador_time_slots[n_time_slot]))
        text_file.write(
            "\nEnd of the performance evaluation, current date is " + current_date + ", current time " + now)
        text_file.write("\nThe processing time is " + str(f.days) + " days, " + str(f.seconds) + " seconds, " + str(
            f.microseconds) + " microseconds")
        text_file.write("\nThe number of mapping list is " + str(number_of_lists_processed))
        text_file.write(
            "\nThe overall processing time is " + str(g.days) + " days, " + str(g.seconds) + " seconds, " + str(
                g.microseconds) + " microseconds")
        text_file.close()
        #####################################################################################
        # average_time_exh = (sum(timing_list_exh, timedelta()) / len(timing_list_exh)).total_seconds()
        # print(f"the average time of the exhaustive algorithm is "
        #       f"{average_time_exh}")

        # text_file = open(os.path.join(folder_txt, "results.txt"), "a")
        # text_file.write("\nThe average time of the exhaustive algorithm is " + str(average_time_exh))
        # text_file.close()














































