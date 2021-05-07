from GraphGenerator import GraphGeneration

def arguments(parser):

    parser.add_argument("-app", "--AppFilepath", help="Defines the application file path")
    parser.add_argument("-hw", "--HwFilepath", help="Defines the hardware file path")


    parser.add_argument("-pr", "--Print", help="Defines the verbosity, options:  "
                                               "debug: all, "
                                               "basic: main prints for debug,  "
                                               "noprint: nothing,  "
                                               "iter:  mapping info, "
                                               "eval : performance evaluation info, "
                                               "bench : benchmark information, "
                                               "main: debug information in the main module, "
                                               "exh : exhaustive mapping debug, "
                                               "exhdebug : exhaustive mapping debug high verbosity, "
                                               "heu : heuristic mapping debug, "
                                               "heudebug : heuristic mapping debug high verbosity, "
                                               "list : list mapping debug, "
                                               "listdebug : list mapping debug high verbosity, "
                                               "ql : q-learning mapping debug, "
                                               "qldebug : q-learning mapping debug high verbosity ")

    parser.add_argument("-mo", "--Total", help="Defines if only mapping or also performance evaluation, "
                                               "options: noperfo , total")
    parser.add_argument("-ta", "--Algo", help="Defines the type of algorithm, options: heu, exh, q-l, list, none")
    parser.add_argument("-nn", "--Node", help="Defines the presence of special nodes and configuration node in the "
                                              "visualization, options: True, False ")
    parser.add_argument("-pa", "--Pause", help="Defines if we pause the code or no, options: True, False")
    parser.add_argument("-sg", "--Showgraph", help="If we  want to show the input graphs, options: True, False")
    parser.add_argument("-si", "--ShowImplementation", help="If we  want to show the output graph (implementation graphs)"
                                                            ", options: True, False")
    parser.add_argument("-debug", "--DebugVariables", help=" This argument enables to print some information about the process"
                                                           " options: total, remove, memory, final, none ")
    parser.add_argument("-deperfo","--DebugPerformance", help="This argument enables to print some information of the "
                                                              "performance evaluation, options: True, False" )
    parser.add_argument("-con", "--ConFilepath", help="Defines the constrains file path")
    parser.add_argument("-ran", "--RandomGen", help="Random generator enable")
    parser.add_argument("-gen", "--GenFilepath", help="Defines the path of the constrains file for the random generator")
    parser.add_argument("-hwbench", "--HwBenchmark", help="Defines the number of hardware graphs for the benchmark")
    parser.add_argument("-appbench", "--AppBenchmark", help="Defines the number of application graphs for the benchmark")
    parser.add_argument("-save", "--SaveInfo", help="We can select if we want to save some of the information, "
                                                    "options : store_exh, store_perfo")
    parser.add_argument("-metperfo", "--MethodPerfo", help="We can select what method we want for the performance "
                                                           "evaluation, options: longest, simple")
    parser.add_argument("-folder", "--SaveFolder", help="Where we want to save the output files of the graph generator "
                                                        "and the performance evaluation")
    parser.add_argument("-listtype", "--ListApproachType", help="Type of implementation of the list-based approach, "
                                                        "if we want one topological sorting or all, options : alltopo, one")
    parser.add_argument("-iter", "--NumberIterations", help="Defines the number of iterations of a processing method")
    # parser.add_argument("-pool", "--RangePool", help="Defines the range of number of performance evaluation we want "
    #                                                  "to spawn")
    parser.add_argument("-exhtype", "--ExhaustiveType", help="If we want to use the option of multiprocessing for "
                                                             "the exhaustive algorithm,multi or serial")
    parser.add_argument("-heutype", "--HeuristicType", help="Type of implementation of the heuristic approach, if we "
                                                            "want the bayes approach or the mapping success, options : "
                                                            "bayes, original")

    # parser.add_argument("-poolexh", "--RangePoolexh", help="Defines the range of number of processes that we spawn "
    #                                                     "for the exhaustive mapping (number of lists that we process "
    #                                                     "in parallel")
    parser.add_argument("-poolperfo", "--RangePoolPerfo", help="Defines the range of number of processes that we for the "
                                                          "performance evaluation (number of possible mappings that we "
                                                          "evaluate in parallel (for list and exhaustive")


    parser.add_argument("-exhstrlist", "--ExhStoreListPickle", help="Number of possible mappings that a single pickle "
                                                                    "file will store in the exhaustive mapping")
    parser.add_argument("-exhpcslist", "--ExhProcessList", help="Number of threads that we will spawn in the "
                                                                "exhaustive mapping")

    parser.add_argument("-byslatlmt", "--BayesLatLimit", help="Defines the limit of latency groups for the "
                                                              "bayes approach")

    parser.add_argument("-bysdislmt", "--BayesDisLimit", help="Defines the limit of the distance "
                                                              "groups (topological distance) for the bayes approach")

    parser.add_argument("-onepisodes", "--OnlineEpisodes", help="Defines the number of episodes for the online "
                                                                "training (exclusive for the q-l approach")

    parser.add_argument("-onestartdecay", "--OnlineStartDecay", help="Defines the start of the decay of epsilon for the online "
                                                                "training (exclusive for the q-l approach")
    parser.add_argument("-oneenddecay", "--OnlineEndDecay",
                        help="Defines the end of the decay of epsilon for the online "
                             "training (exclusive for the q-l approach")

    parser.add_argument("-offepisodes", "--OfflineEpisodes", help="Defines the number of episodes for the offline "
                                                                "training (exclusive for the q-l approach")
    parser.add_argument("-offstartdecay", "--OfflineStartDecay", help="Defines the start of the decay of epsilon for the offline "
                                                                "training (exclusive for the q-l approach")

    parser.add_argument("-offenddecay", "--OfflineEndDecay",
                        help="Defines the end of the decay of epsilon for the offline "
                             "training (exclusive for the q-l approach")

    parser.add_argument("-rewardpath", "--RewardFilepath",
                        help="Defines the path of the rewards vector")

    parser.add_argument("-limittimeslots","--LimitTimeSlots",help="Defines the limit number of "
                                                                  "time slots for the exhaustive algorithm")

    args = parser.parse_args()



    ######FILEPATHS##############################################################################
    # hardware
    filepath_hw = args.HwFilepath
    # application
    filepath_app = args.AppFilepath
    # constrains
    filepath_con = args.ConFilepath
    # random generator parameters
    filepath_gen = args.GenFilepath
    # save
    if args.SaveFolder:
        filepath_savefolder = args.SaveFolder
    else:
        filepath_savefolder = 'outputfiles'
    # rewards vector
    filepath_rewards = args.RewardFilepath
    ######GENERAL INFORMATION ####################################################################

    # selection of the algorithm
    selection_algo = 'none'
    if args.Algo:
        if args.Algo == 'exh' or args.Algo == 'heu' or args.Algo == 'none' or args.Algo == 'q-l' \
                or args.Algo == 'bench' or args.Algo == 'list' or args.Algo == 'sarsa':
            selection_algo = args.Algo
        else:
            print(f"Error : Input {args.Algo} for -ta field is not valid")
            raise ValueError

    #selection of the verbosity
    selection_prints = 'noprint'
    if args.Print:
        if args.Print == 'debug' or args.Print == 'basic' or args.Print == 'noprint' or args.Print == 'iter' \
                or args.Print == 'eval' \
                or args.Print == 'bench' or args.Print == 'main' \
                or args.Print == 'exh' or args.Print == 'testexh' or args.Print == 'debugexh' \
                or args.Print == 'heu' or args.Print == 'list' or args.Print == 'q-l' or args.Print == 'qliter' \
                or args.Print == 'graphgenerator' or args.Print == 'qldebug' or args.Print == 'heudebug' or \
                args.Print == 'heuiter' or args.Print == 'heulow' or args.Print == 'ql' or args.Print == 'qldebug'\
                or args.Print == 'listdebug' or args.Print == 'exhdebug' or args.Print == 'generatordebug':
            selection_prints = args.Print
        else:
            print(f"Error : Input {args.Print} for -pr field is not valid")
            raise ValueError

    # selection if we want the performance evaluation
    selection_modules = 'noperfo'
    if args.Total:
        if args.Total == 'total' or args.Total == 'noperfo':
            selection_modules = args.Total
        else:
            print(f"Error : Input {args.Total} for -mo field is not valid")
            raise ValueError

    # selection of the range of threads that we are going to spawn of the performance evaluation
    pool_range_min = 5
    pool_range_max = 6
    if args.RangePoolPerfo:
        try:
            values = args.RangePoolPerfo.split('-')
            pool_range_min = int(values[0])
            pool_range_max = int(values[1])
            if pool_range_min == pool_range_max:
                pool_range_max = pool_range_min + 1
        except:
            print(f"Error : Input {args.RangePoolPerfo} for -poolperfo field is not valid, "
                  f"the structure should be int-int")
            raise ValueError
        if pool_range_min > pool_range_max:
            print(
                f"Error : Input {args.RangePoolPerfo} for -poolperfo field is not valid, the "
                f"first value should be less or equal"
                f" than the second")
            raise ValueError

    # number of the iterations that we are going to process
    number_iterations = 1
    if args.NumberIterations:
        try:
            number_iterations = int(args.NumberIterations)
        except:
            print(f"Error : Input {args.NumberIterations} for -iter field is not valid, int only accepted")
            raise ValueError

    # selection of the method of the performance evaluation
    method_evaluation = 'longest'
    if args.MethodPerfo:
        if args.MethodPerfo == 'simple' or args.MethodPerfo == 'longest':
            method_evaluation = args.MethodPerfo
        else:
            print(f"Error : Input {args.MethodPerfo} for -metperfo field is not valid")
            raise ValueError

    # debug options
    debug_info = None
    if args.DebugVariables:
        if args.DebugVariables == 'total' or args.DebugVariables == 'remove' or args.DebugVariables == 'memory' \
                or args.DebugVariables == 'none' or args.DebugVariables == 'final' or args.DebugVariables == 'graphs':
            debug_info = args.DebugVariables
        else:
            print(f"Error :  Input {args.DebugVariables} for -debug field is not valid")
            raise ValueError

    # enable of the pause during the processes
    selection_pause = False
    if args.Pause:
        if args.Pause == 'True' or args.Pause == 'False':
            if args.Pause == 'True':
                selection_pause = True
            else:
                selection_pause = False
        else:
            print(f"Error : Input {args.Pause} for -pa field is not valid")
            raise ValueError


    # enable of some debugging options
    debugging_options = False
    if args.DebugPerformance:
        if args.DebugPerformance == 'True' or args.DebugPerformance == 'False':
            if args.DebugPerformance == 'True':
                debugging_options = True
            else:
                debugging_options = False
        else:
            print(f"Error : Input {args.DebugPerformance} for -deperfo field is not valid")
            raise ValueError

    # we enable the storing of some information in here
    save_info = None
    if args.SaveInfo:
        if args.SaveInfo == 'store_exh' or args.SaveInfo == 'store_heu':
            save_info = args.SaveInfo
        else:
            print(f"Error : Input {args.SaveInfo} for -save field is not valid")
            raise ValueError

    ######################VISUALIZATION##################################################################


    # visualization of the input graphs
    selection_show = False
    if args.Showgraph:
        if args.Showgraph == 'True' or args.Showgraph == 'False' or args.Showgraph == 'true' \
                or args.Showgraph == 'TRUE' or args.Showgraph == 'false' or args.Showgraph == 'FALSE':
            if args.Showgraph == 'True' or args.Showgraph == 'true' or args.Showgraph ==  'TRUE':
                selection_show = True
            else:
                selection_show = False
        else:
            print(f"Error : Input {args.Showgraph} for -sg field is not valid")
            raise ValueError

    # visualization of the implementation graph
    selection_show_implementation_graph = False
    if args.ShowImplementation:
        if args.ShowImplementation == 'True' or args.ShowImplementation == 'False' \
                or args.ShowImplementation == 'false' or args.ShowImplementation == 'FALSE' \
                or args.ShowImplementation == 'TRUE' or args.ShowImplementation == 'true':
            if args.ShowImplementation == 'True' or args.ShowImplementation == 'true' or \
                    args.ShowImplementation == 'TRUE':
                selection_show_implementation_graph = True
            else:
                selection_show_implementation_graph = False
        else:
            print(f"Error : Input {args.ShowImplementation} for -si field is not valid")
            raise ValueError

    # if we dont want certain nodes in the graphs
    selection_no_nodes = False
    if args.Node:
        if args.Node == 'True' or args.Node == 'False':
            if args.Node == 'True':
                selection_no_nodes = True
            else:
                selection_no_nodes = False
        else:
            print(f"Error : Input {args.Node} for -nn field is not valid")
            raise ValueError

    #########################RANDOM GENERATOR OPTIONS



    # ENABLE OF THE RANDOM GENERATOR
    random_generator = False
    if args.RandomGen:
        if args.RandomGen == 'True' or args.RandomGen == 'False' or args.RandomGen == 'false' or \
                args.RandomGen == 'FALSE' or args.RandomGen == 'TRUE' or args.RandomGen == 'true':
            if args.RandomGen == 'True' or args.RandomGen == 'TRUE' or args.RandomGen == 'true':
                random_generator = True
            else:
                random_generator = False
        else:
            print(f"Error : Input {args.RandomGen} for -ran field is not valid")
            raise ValueError

    # Number of the hardware graphs that we are going to create
    HwBenchmark = 0
    if args.HwBenchmark:
        try:
            HwBenchmark = int(args.HwBenchmark)
        except:
            print(f"Error : Input {args.HwBenchmark} for -hwbench field is not valid, int only accepted")
            raise ValueError

    # Number of the application graphs that we are going to create
    AppBenchmark = 0
    if args.AppBenchmark:
        try:
            AppBenchmark = int(args.AppBenchmark)
        except:
            print(f"Error : Input {args.AppBenchmark} for -appbench field is not valid, int only accepted")
            raise ValueError

    # if the random generator is enable we call the generator function
    graph_generator = None
    if random_generator:
        if filepath_savefolder:
            filepath_final = '/' + filepath_savefolder + '/'
            graph_generator = GraphGeneration(filepath_gen, folderpath=filepath_final, s_prints=selection_prints,
                                              debug=debug_info)
        else:
            graph_generator = GraphGeneration(filepath_gen)




    #######OPTIONS FOR THE ALGORITHMS

    ########EXHAUSTIVE
    # Selection of the type of exhaustive algorithm
    exh_multi = 'multi'
    if args.ExhaustiveType:
        if args.ExhaustiveType == 'multi' or args.ExhaustiveType == 'serial':
            exh_multi = args.ExhaustiveType
        else:
            print(f"Error : Input {args.ExhaustiveType} for -exhtype field is not valid")
            raise ValueError

    # number of preliminar mappings that we store in a single pickle
    LIMIT_STORE_LIST = 8000
    if args.ExhStoreListPickle:
        try:
            LIMIT_STORE_LIST = int(args.ExhStoreListPickle)
        except:
            print(f"Error : Input {args.ExhStoreListPickle} for -exhstrlist field is not valid, int only accepted")
            raise ValueError

    # number of processes that we spawn in the exhaustive approach
    LIMIT_PROCESS_LIST = 8
    if args.ExhProcessList:
        try:
            LIMIT_PROCESS_LIST = int(args.ExhProcessList)
        except:
            print(f"Error : Input {args.ExhProcessList} for -exhpcslist field is not valid, int only accepted")
            raise ValueError


    LIMIT_TIME_SLOTS = None
    if args.LimitTimeSlots:
        try:
            LIMIT_TIME_SLOTS = int(args.LimitTimeSlots)
        except:
            print(f"Error :  Input {args.LimitTimeSlots} for -limittimeslots field is not valid, int only accepted")
            raise ValueError


    ##############HEURISTIC
    # Selection of the type of heuristic algorithm
    heu_type = 'original'
    if args.HeuristicType:
        if args.HeuristicType == 'bayes' or args.HeuristicType == 'original':
            heu_type = args.HeuristicType
        else:
            print(f"Error : Input {args.HeuristicType} for -heutype field is not valid")
            raise ValueError

    # limit number of the latency list, in other words, for the bayes approach we define a limit for the selection of
    # the best candidates according to the latency, eg BAYES_LATENCY = 3 will select the best 3 resources
    BAYES_LATENCY = 10
    if args.BayesLatLimit:
        try:
            BAYES_LATENCY = int(args.BayesLatLimit)
        except:
            print(f"Error : Input {args.BayesLatLimit} for -byslatlmt field is not valid, int only accepted")
            raise ValueError

    # limit distance for the bayes approach, we select a group of resources that are within this distance to be the
    # best candidates, eg if we select BAYES_DISTANCE = 1, the group will be all the resources that are within a
    # topological distance of 1
    BAYES_DISTANCE = 10
    if args.BayesDisLimit:
        try:
            BAYES_DISTANCE = int(args.BayesDisLimit)
        except:
            print(f"Error : Input {args.BayesDisLimit} for -bysdislmt field is not valid, int only accepted")
            raise ValueError


    ################LIST-BASED
    # Selection of the type of list algorithm
    list_type = 'one'
    if args.ListApproachType:
        if args.ListApproachType == 'one' or args.ListApproachType == 'alltopo':
            list_type = args.ListApproachType
        else:
            print(f"Error : Input {args.ListApproachType} for -listtype field is not valid")
            raise ValueError



    ##############Q LEARNING



    # number of episodes of the offline training
    EPISODES_OFFLINE = 10000
    if args.OfflineEpisodes:
        try:
            EPISODES_OFFLINE = int(args.OfflineEpisodes)
        except:
            print(f"Error : Input {args.OfflineEpisodes} for -offepisodes field is not valid, int only accepted")
            raise ValueError

   # start of the decay of epsilon for the offline training
    DECAY_START_OFFLINE = 1500
    if args.OfflineStartDecay:
        try:
            DECAY_START_OFFLINE = int(args.OfflineStartDecay)
        except:
            print(f"Error : Input {args.OfflineStartDecay} for -offstartdecay field is not valid, int only accepted")
            raise ValueError

    # end of the decay of epsilon for the offline training
    DECAY_END_OFFLINE = 7000
    if args.OfflineEndDecay:
        try:
            DECAY_END_OFFLINE = int(args.OfflineEndDecay)
        except:
            print(f"Error : Input {args.OfflineEndDecay} for -offenddecay field is not valid, int only accepted")
            raise ValueError

    # number of episodes of the online training
    EPISODES_ONLINE = 10000
    if args.OnlineEpisodes:
        try:
            EPISODES_ONLINE = int(args.OnlineEpisodes)
        except:
            print(f"Error : Input {args.OnlineEpisodes} for -onepisodes field is not valid, int only accepted")
            raise ValueError

    # start of the decay of epsilon for the online training
    DECAY_START_ONLINE = 1500
    if args.OnlineStartDecay:
        try:
            DECAY_START_ONLINE = int(args.OnlineStartDecay)
        except:
            print(f"Error : Input {args.OnlineStartDecay} for -onestartdecay field is not valid, int only accepted")
            raise ValueError

    # end of the decay of epsilon for the online training
    DECAY_END_ONLINE = 7000
    if args.OnlineEndDecay:
        try:
            DECAY_END_ONLINE = int(args.OnlineEndDecay)
        except:
            print(f"Error : Input {args.OnlineEndDecay} for -oneenddecay field is not valid, int only accepted")
            raise ValueError


    return  filepath_hw,filepath_app,filepath_con,filepath_gen,filepath_savefolder,selection_algo,selection_prints,\
            selection_modules,pool_range_min,pool_range_max,number_iterations,method_evaluation,debug_info,\
            selection_pause,debugging_options,save_info,selection_show,selection_show_implementation_graph,\
            selection_no_nodes,random_generator,HwBenchmark,AppBenchmark,graph_generator,exh_multi,LIMIT_STORE_LIST,\
            LIMIT_PROCESS_LIST,heu_type,BAYES_LATENCY,BAYES_DISTANCE,list_type,EPISODES_OFFLINE,DECAY_START_OFFLINE,\
            EPISODES_ONLINE,DECAY_START_ONLINE,filepath_rewards,DECAY_END_ONLINE,DECAY_END_OFFLINE,LIMIT_TIME_SLOTS



