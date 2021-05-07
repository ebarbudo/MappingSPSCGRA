
from graphviz import Digraph
from fpdf import FPDF
from PyPDF2 import PdfFileMerger

import os


class GraphRep:
    def __init__(self, DG, AG, resultado, type_representation, name_file,nodes_enable,color_01,color_02,shape):
        self.DG = DG
        self.AG = AG
        self.resultado = resultado
        self.nodos_especiales_flag = None  #####indica si se va a agregar los nodos especiales o no
        #######valores basicos, estos tal vez se puedan indicar desde fuera de la funcion
        self.nodes_enable = nodes_enable
        self.color_01 = color_01
        self.color_02 = color_02
        self.shape = shape
        self.size_node = '3.5'
        self.font_node = '10'
        self.penwidth_node = '4'
        self.pendwidth_edge = '4'
        self.name_file = name_file
        self.nodos_especiales = None
        ###COLOCAR UN SWITCH AQUI
        if type_representation == 'app':
            self.bandera_op = True
            self.representacion_de_una_grafica_cualquiera_app()
        elif type_representation == 'hw':
            self.bandera_op = True
            self.representacion_de_una_grafica_cualquiera_hw()


    def representacion_de_una_grafica_cualquiera_hw(self):
        nodos = self.DG.nodes
        arcos = self.DG.edges
        self.f = Digraph('implementation graph', filename=self.name_file,format='png')
        self.f.attr(rankdir='LR', size=self.size_node)
        contador_instancia = 0
        for nodo in nodos:
            if self.bandera_op:
                if True in self.nodes_enable[nodo]:
                    nombre = 'r' + str(contador_instancia + nodo)
                    self.f.node(nombre, color=self.color_01, style='solid', shape=self.shape,
                                fontsize=self.font_node, fontname='bold', penwidth=self.penwidth_node)
                    test = list(self.DG.edges(nodo))
                    if test:
                        for arcos in range(0, len(test)):
                            nombre_edge_01 = 'r' + str(test[arcos][0] + contador_instancia)
                            nombre_edge_02 = 'r' + str(test[arcos][1] + contador_instancia)
                            self.f.edge(nombre_edge_01, nombre_edge_02,
                                        penwidth=self.pendwidth_edge)
                else:
                    nombre = 'r' + str(contador_instancia + nodo)
                    self.f.node(nombre, color='black', style='solid', shape='square',
                                fontsize=self.font_node, fontname='bold', penwidth=self.penwidth_node)
                    test = list(self.DG.edges(nodo))
                    if test:
                        for arcos in range(0, len(test)):
                            nombre_edge_01 = 'r' + str(test[arcos][0] + contador_instancia)
                            nombre_edge_02 = 'r' + str(test[arcos][1] + contador_instancia)
                            self.f.edge(nombre_edge_01, nombre_edge_02,
                                        penwidth=self.pendwidth_edge)
        self.f.attr(fontsize='40')

    def representacion_de_una_grafica_cualquiera_app(self):
        nodos = self.AG.nodes
        arcos = self.AG.edges
        self.f = Digraph('implementation graph', filename=self.name_file,format='png')
        self.f.attr(rankdir='LR', size=self.size_node)
        contador_instancia = 0
        # print("LA LISTA DE CANDIDATOS DENTRO DE LA FUNCION", self.nodes_enable)
        vector_edges = []
        for nodo in nodos:
            # we create the node
            # first the name
            # print(nodo,self.AG.nodes[nodo])
            nombre = self.AG.nodes[nodo]['name']
            self.f.node(str(nodo), label = nombre,color='black', shape=self.shape,
                                fontsize=self.font_node, fontname='bold', penwidth=self.penwidth_node)
            # we add the predecessors
            predecesores = self.AG.predecessors(nodo)
            for prede in predecesores:
                dummy = (str(prede), str(nodo))
                # dummy = (self.AG.nodes[prede]['name'], nombre)
                if dummy in vector_edges:
                    pass
                else:
                    self.f.edge(str(prede), str(nodo),
                                                penwidth=self.pendwidth_edge)

                    vector_edges.append(dummy)
            # next we add the successors
            sucesores = self.AG.successors(nodo)
            for suc in sucesores:
                dummy = (str(nodo),str(suc))
                # dummy = (nombre, self.AG.nodes[suc]['name'])
                if dummy in vector_edges:
                    pass
                else:
                    self.f.edge(str(nodo),str(suc), penwidth=self.pendwidth_edge)

                    vector_edges.append(dummy)



class GenerationGraphPdf:

    def __init__(self,cell_size,cell_lenght,font_title,font_text,type,fusion,
                 graph,view_graph,name_graph,name_pdf,name_complete,dict_info_h, DG_total, dict_total_h):
        self.lista_vacia = []
        self.cell_size = cell_size
        self.cell_lenght = cell_lenght
        self.font_title = font_title
        self.font_text = font_text
        self.type = type
        self.fusion = fusion
        self.graph = graph
        self.view_graph = view_graph
        self.name_graph = name_graph
        self.name_pdf = name_pdf
        self.name_complete = name_complete
        #########only for the hardware
        self.dict_info_h = dict_info_h
        self.dict_total_h = dict_total_h
        self.DG_total = DG_total


        if self.type == 'app':
            self.application_generation()
        elif self.type == 'hw':
            self.hardware_generation()


    def application_generation(self):
        lista_app  = [[False, False, False] for n in range(0, len(self.graph.nodes))]
        graph_visual_00 = GraphRep([], self.graph, self.lista_vacia, 'app', self.name_graph, lista_app, 'red', 'black',
                                                      'circle')
        graph_visual_00.f.render(view=False)
        graph_visual_00.f.render(view=self.view_graph, format='pdf')

        if self.fusion:
            pdf1 = FPDF(format='A4')
            pdf1.add_page()
            pdf1.set_font("Arial", size=self.font_title)
            texto = "Application graph"

            pdf1.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="C")
            pdf1.cell(self.cell_lenght, self.cell_size, txt='', ln=1, align="C")
            pdf1.cell(self.cell_lenght, self.cell_size, txt='', ln=1, align="C")
            pdf1.set_font("Arial", size=self.font_text)
            for nodo in self.graph:
                texto = "task :  " + self.graph.nodes[nodo]['name'] + "        type : " + self.graph.nodes[nodo]['op']
                pdf1.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                text02 = " parameters : " + str(self.graph.nodes[nodo]['par'])
                pdf1.cell(self.cell_lenght, self.cell_size, txt=text02, ln=1, align="L")
                pdf1.cell(self.cell_lenght, self.cell_size, txt='', ln=1, align="L")
            pdf1.output(self.name_pdf)
            name_graph = self.name_graph + '.pdf'
            pdfs = [name_graph, self.name_pdf]
            merger1 = PdfFileMerger()
            for pdf in pdfs:
                merger1.append(pdf)
            merger1.write(self.name_complete)
            merger1.close()



    def hardware_generation(self):
        lista_hw = [[False, False, False] for n in range(0, len(self.graph.nodes))]

        graph_visual_02 = GraphRep([], self.graph, self.lista_vacia, 'app', self.name_graph, lista_hw, 'red',
                                                      'black',
                                                      'circle')
        graph_visual_02.f.render(view=False)
        graph_visual_02.f.render(view=self.view_graph, format='pdf')
        if self.fusion:
            pdf2 = FPDF(format='A4')
            pdf2.add_page()
            pdf2.set_font("Arial", size=self.font_title)
            texto = "Hardware graph"
            pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="C")
            pdf2.cell(self.cell_lenght, self.cell_size, txt='', ln=1, align="L")
            pdf2.set_font("Arial", size=self.font_text)
            for nodo in self.DG_total:
                # print(nodo, self.DG_total.nodes[nodo])
                texto = "resource : " + self.DG_total.nodes[nodo]['name'] + "   type :  " + self.DG_total.nodes[nodo]['type']

                pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                try:
                    formula = None
                    for elemento in self.dict_info_h['functions_cfg']:
                        # print(elemento,self.dict_total_h[nodo]['fun_lat']['formula'])
                        if elemento == self.dict_total_h[nodo]['fun_lat']['formula']:
                            formula = self.dict_info_h['functions_cfg'][elemento]
                    parametros_buffer = []
                    for elemento in self.dict_total_h[nodo]['fun_lat']:
                        if elemento != 'formula':
                            temporal = elemento, self.dict_total_h[nodo]['fun_lat'][elemento]
                            string_temporal = elemento + ' = ' + str(self.dict_total_h[nodo]['fun_lat'][elemento])
                            parametros_buffer.append(string_temporal)
                    texto = "configuration - cost function : " + str(formula)
                    texto01 = "configuration - parameters : " + str(parametros_buffer)
                except:
                    texto = "configuration - cost function : None"
                    texto01 = "configuration - parameters : None"

                pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                pdf2.cell(self.cell_lenght, self.cell_size, txt=texto01, ln=1, align="L")
                # print("DENTRO DEL MODULO")
                # print(nodo,self.dict_total_h[nodo])
                # for n,data in self.dict_total_h.items():
                #     print(n,data)
                try:
                    for oper in self.dict_total_h[nodo]['ops']:
                        texto = "task type : " + oper
                        pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                        texto = "parameters : " + str(self.dict_total_h[nodo]['ops'][oper])
                        pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                except:
                    nombre_nodo = self.DG_total.nodes[nodo]['name']
                    for n_interno,data in self.dict_total_h.items():
                        if data['name'] == nombre_nodo:
                            for oper in self.dict_total_h[n_interno]['ops']:
                                texto = "task type : " + oper
                                pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")
                                texto = "parameters : " + str(self.dict_total_h[n_interno]['ops'][oper])
                                pdf2.cell(self.cell_lenght, self.cell_size, txt=texto, ln=1, align="L")

                pdf2.cell(self.cell_lenght, self.cell_size, txt='', ln=1, align="L")
            pdf2.output(self.name_pdf)
            name_graph = self.name_graph + '.pdf'
            pdfs = [name_graph, self.name_pdf]
            merger2 = PdfFileMerger()
            for pdf in pdfs:

                merger2.append(pdf)
            merger2.write(self.name_complete)

            merger2.close()



def gen_implementation_graph_heu(graph_total,MAP,selection_prints,dict_nodes_a,longest,maximum_clock,
                                 MAP_performance,name_implementation,name_graph,directorio):
    #variables para el grafo dot
    size_node = '4.5'
    font_node = '40'
    penwidth_node = '3'
    pendwidth_edge = '13'
    ######inicializacion del grafo
    # estos valores idealmente deberian de ser modificables, pero se deja para otra actualizacion
    graph = Digraph('implementation graph', filename=name_graph, format='pdf')
    graph.attr(rankdir='LR', size=size_node)
    #variables para el pdf
    cell_size = 5
    cell_lenght = 300
    font_titulo = 20
    font_texto = 8


    #######inicio de creacion de nodos
    vector_edges = []
    # bandera_nodos_especiales = flag_special_nodes
    contador_nodos_grafo = 0

    contador_instancias = 0
    primera_vez = True
    #####los nodos especiales, de memoria y de configuracion se numeraran a partir del numero de nodos normales
    vector_nodos_en_instancia = []
    vector_buffer = []
    #######por cada una de las instancias dentro de la lista de entrada
    if selection_prints == 'basic' or selection_prints == 'debug':
        print("enter the function that transforms the list into a graph")
    # if selection_prints == 'debug':
    #     print(mapping_list)
    # print(mapping_list)
    # print(len(mapping_list))
    test = []
    # graph_total
    # graph_total = MAP
    for nodo in graph_total:
        # print(nodo, graph_total.nodes[nodo])
        # if selection_prints == 'basic':
        #     print("iniciaremos el proceso de generacion de grafo")
        if selection_prints == 'basic':
            print(graph_total.nodes[nodo])
        if graph_total.nodes[nodo]['map']:

            if graph_total.nodes[nodo]['op'] != 'config':
                if graph_total.nodes[nodo]['task'] != None:
                    # nombre = 't' + str(graph_total.nodes[nodo]['task']) + '\n ' + graph_total.nodes[nodo]['name']+ '_' + str(nodo)

                    nombre = dict_nodes_a[graph_total.nodes[nodo]['task']]['name'] + '\n ' + graph_total.nodes[nodo][
                        'name'] + '_' + str(nodo)
                    graph.node(nombre, color='red', style='solid', shape='square', fontsize=font_node,
                               fontname='bold', penwidth=penwidth_node)
                else:
                    if graph_total.nodes[nodo]['op'] == 'ri':
                        try:
                            nombre = str(graph_total.nodes[nodo]['assign']) + '\n' + graph_total.nodes[nodo][
                                'name'] + '_' + str(nodo)
                        except:
                            nombre = graph_total.nodes[nodo][
                                         'name'] + '_' + str(nodo)
                        graph.node(nombre, color='green', style='solid', shape='circle', fontsize=font_node,
                                   fontname='bold', penwidth=penwidth_node)
                    elif graph_total.nodes[nodo]['op'] == 'copy':
                        nombre = 'copy' + '\n ' + graph_total.nodes[nodo]['name'] + '_' + str(nodo)
                        graph.node(nombre, color='red', style='solid', shape='circle', fontsize=font_node,
                                   fontname='bold', penwidth=penwidth_node)
                    else:
                        nombre = graph_total.nodes[nodo]['name'] + '_' + str(nodo)
                        graph.node(nombre, color='black', style='solid', shape='circle', fontsize=font_node,
                                   fontname='bold', penwidth=penwidth_node)
            else:
                nombre = graph_total.nodes[nodo]['name'] + '_' + str(nodo)
                graph.node(nombre, color='blue', style='solid', shape='square', fontsize=font_node,
                           fontname='bold', penwidth=penwidth_node)
        else:
            nombre = graph_total.nodes[nodo]['name'] + '_' + str(nodo)
            graph.node(nombre, color='black', style='solid', shape='square', fontsize=font_node,
                       fontname='bold', penwidth=penwidth_node)
        # print("nombre del edge", nombre)
        predecesores = graph_total.predecessors(nodo)
        for predecesor in predecesores:
            # print("predecesor",predecesor,graph_total.nodes[predecesor]['op'])
            if graph_total.nodes[predecesor]['map']:
                if graph_total.nodes[predecesor]['op'] != 'config':
                    if graph_total.nodes[predecesor]['task'] != None:

                        nombre_1 = dict_nodes_a[graph_total.nodes[predecesor]['task']]['name'] + '\n ' + \
                                   graph_total.nodes[predecesor]['name'] + '_' + str(predecesor)
                        # nombre_1 = 't' + str(graph_total.nodes[predecesor]['task']) + '\n ' + graph_total.nodes[predecesor]['name']+ '_' + str(predecesor)
                    else:
                        if graph_total.nodes[predecesor]['op'] == 'ri':
                            try:
                                nombre_1 = str(graph_total.nodes[predecesor]['assign']) + '\n' + \
                                           graph_total.nodes[predecesor][
                                               'name'] + '_' + str(predecesor)
                            except:
                                nombre_1 = graph_total.nodes[predecesor][
                                               'name'] + '_' + str(predecesor)

                            # nombre_1 = str(graph_total.nodes[nodo]['assign']) + '\n' + graph_total.nodes[predecesor]['name']+ '_' + str(predecesor)
                        elif graph_total.nodes[predecesor]['op'] == 'copy':
                            nombre_1 = 'copy' + '\n ' + graph_total.nodes[predecesor]['name'] + '_' + str(predecesor)
                        else:
                            nombre_1 = graph_total.nodes[predecesor]['name'] + '_' + str(predecesor)
                else:
                    nombre_1 = graph_total.nodes[predecesor]['name'] + '_' + str(predecesor)
            else:
                nombre_1 = graph_total.nodes[predecesor]['name'] + '_' + str(predecesor)

            if not [nombre_1, nombre] in vector_edges and nombre != nombre_1:
                graph.edge(nombre_1, nombre,
                           penwidth=pendwidth_edge)
                # print("npmbre y edge", nombre_1,nombre)
                edges_buffer = [nombre_1, nombre]
                vector_edges.append(edges_buffer)

        successors = graph_total.successors(nodo)
        # print("successors",nodo,list(graph_total.successors(nodo)))
        for successor in successors:
            if graph_total.nodes[successor]['map']:
                if graph_total.nodes[successor]['op'] != 'config':
                    if graph_total.nodes[successor]['task'] != None:

                        nombre_1 = dict_nodes_a[graph_total.nodes[successor]['task']]['name'] + '\n ' + \
                                   graph_total.nodes[successor]['name'] + '_' + str(successor)
                        # nombre_1 = 't' + str(graph_total.nodes[successor]['task']) + '\n ' + graph_total.nodes[successor]['name']+ '_' + str(successor)
                    else:
                        if graph_total.nodes[successor]['op'] == 'ri':
                            try:
                                nombre_1 = str(graph_total.nodes[successor]['assign']) + '\n' + \
                                           graph_total.nodes[successor][
                                               'name'] + '_' + str(successor)
                            except:
                                nombre_1 = graph_total.nodes[successor][
                                               'name'] + '_' + str(successor)

                            # nombre_1 = str(graph_total.nodes[nodo]['assign']) + '\n' + graph_total.nodes[successor]['name']+ '_' + str(successor)
                        elif graph_total.nodes[successor]['op'] == 'copy':
                            nombre_1 = 'copy' + '\n ' + graph_total.nodes[successor]['name'] + '_' + str(successor)
                        else:
                            nombre_1 = graph_total.nodes[successor]['name'] + '_' + str(successor)
                else:
                    nombre_1 = graph_total.nodes[successor]['name'] + '_' + str(successor)
            else:
                nombre_1 = graph_total.nodes[successor]['name'] + '_' + str(successor)

            if not [nombre, nombre_1] in vector_edges and nombre_1 != nombre:
                graph.edge(nombre, nombre_1,
                           penwidth=pendwidth_edge)
                # print("test ddd",nombre,nombre_1,successor)
                edges_buffer = [nombre, nombre_1]
                vector_edges.append(edges_buffer)

    # end_performance_benchmark = time.time()
    # time_benchmark_performance = end_performance_benchmark - start_performance_benchmark
    longest_names = []
    for nodo in longest:
        longest_names.append(MAP.nodes[nodo]['name'])
    if selection_prints == 'printper':
        print("the critical path is ", longest_names)
    # print(f"the value of the overall latency is {MAP_performance} clock cycles")
    # print(f"end of the performance evaluation, the processing time is {time_benchmark_performance} seconds")


    vector_longest = longest_names
    # print(latency_evaluation)


    pdf2 = FPDF(format='A4')
    pdf2.add_page()
    pdf2.set_font("Arial", size=font_titulo)
    texto = "Implementation graph"
    pdf2.cell(cell_lenght, cell_size, txt=texto, ln=1, align="C")
    pdf2.cell(cell_lenght, cell_size, txt='', ln=1, align="L")
    pdf2.set_font("Arial", size=font_texto)
    texto = "The critical path is " + str(vector_longest) + " and the computing latency per pixel is " + str(
        maximum_clock)
    pdf2.cell(cell_lenght, cell_size, txt=texto, ln=1, align="L")
    pdf2.cell(cell_lenght, cell_size, txt='', ln=1, align="L")
    texto = "The overall latency is " + str(MAP_performance)
    pdf2.cell(cell_lenght, cell_size, txt=texto, ln=1, align="L")
    pdf2.cell(cell_lenght, cell_size, txt='', ln=1, align="L")
    # for nodo in graph_total:
    #     print(graph_total.nodes[nodo],nodo)

    for nodo in longest:

        # print(nodo, MAP.nodes[nodo])
        # print(nodo,DG_total.nodes[nodo])
        try:
            nodo_name = MAP.nodes[nodo]['name'] + '_' + str(nodo)
            latencia_resultante = MAP.nodes[nodo]['latencia_resultante']
            latencia_de_nodo = MAP.nodes[nodo]['latencia_de_nodo']

            texto = "resource : " + nodo_name + "   resource latency :  " + str(
                latencia_de_nodo) + " overall latency up this resource : " + str(latencia_resultante)

            pdf2.cell(cell_lenght, cell_size, txt=texto, ln=1, align="L")

            pdf2.cell(cell_lenght, cell_size, txt='', ln=1, align="L")
        except:
            pass

    name_temporal_pdf = os.path.join(directorio, "implementation_info_nt.pdf")
    pdf2.output(name_temporal_pdf)
    # finally we are going to merge both pdfs
    graph.render(view=False)
    temporal_name = name_graph + '.pdf'
    # print(temporal_name,name_implementation
    #       )
    pdfs = [temporal_name, name_temporal_pdf]
    merger2 = PdfFileMerger()
    for pdf in pdfs:
        merger2.append(pdf)
    # print("tetste",name_implementation)
    merger2.write(name_implementation)

    # os.system('hw_complete.pdf')
    merger2.close()
    return vector_longest, graph


