# Complete Mapping Framework for Software Programmable Streaming Coarse Grained Reconfigurable Architectures


## Overview

This repository contains a software tool developed for the easy reuse of Software Programmable Streaming Coarse-Grained Reconfigurable Architectures (SPS-CGRA). The complete overview is showed in the following figure.



![Mesa de trabajo 1](https://user-images.githubusercontent.com/35706145/117903432-27a61880-b295-11eb-870b-68d1b6d5b97a.png)



The inputs are a couple of specification files (application and hardware). The software tool consists of a parser, a set of mapping algorithms, a random graph generator, a performance evaluation, and a configuration context generator.

## Specification Files

The inputs of the tool are a couple of specification files. Some examples of these files are in the folder configfiles/.

General specifications for the files:
* All comments should start with #
* Each line should finish with a ;
* White spaces are not considered


### Application specification file

An example of a specification file is showed in the following figure.

![specificationfileapplication](https://user-images.githubusercontent.com/35706145/117912046-655e6d80-b2a4-11eb-8fdf-42699c0634ca.png)

In this simple example, the application consists of a sensor, an actuator, and a task connected in a pipeline. There is no limit to the number of tasks, parameters, or the number of output edges. The task's name should be without spaces and one single word that could contain letters, numbers, or special characters.

### Hardware specification file

An example of a specification file is showed in the following figure.

![specificationfilehardware](https://user-images.githubusercontent.com/35706145/117912704-94291380-b2a5-11eb-8b78-14ae32e1898b.png)

The specification file is divided into three sections: configuration functions and parameters, latency functions (input and computing latencies), and hardware resources description.

#### Configuration functions

This part should start with the word 

    configuration;
    
Next, we define the type of configuration, either sequential or parallel. In a sequential configuration, the configuration costs of all the hardware resources will be added. In a parallel configuration, the largest value of configuration cost of the hardware resources will be the one considered during the performance evaluation. Following the type, we describe the configuration cost functions of the hardware resources. These functions might consist of elementary operations (+,x,-,/) and their concatenations. Next, we describe the parameters that will be taken into account in computing the configuration cost functions.  This helps if we have a fixed parameter or a parameter related to a variable.
The order of the elements is not important.
#### Latency functions

This part should start with the word
 
    functions;
   
In this part, we should define the input and computing functions. We can use elementary operations (+,x,-,/) and their concatenations. Also, we may use keywords such as width (width of the input image) or height (height of the input image). Additionally, we may define the function as a constant. Both configuration functions and latency function's names will need to match the names specified in the description of the hardware resources.


#### Hardware resources description

This part should start with the word

    resources;
    
In this part, we describe the hardware resources and their features. An extract of a hardware specification file is showed in the following figure.

![specificationresource](https://user-images.githubusercontent.com/35706145/117990567-e3e9f800-b302-11eb-84dc-09db6bba5fb4.png)


Each hardware resource should start with the name. Then the following line defines the type of hardware resource and the output edges. The resources may be type rp (processing resource), rw (communication resource write operation), rr (communication resource read operation), ri (communication resource interface), rmux (communication resource multiplexer), rm (memory resource). Then in the following line, we define the configuration cost function of the hardware resource. We also may define some parameters in this field. The next line defines the operations that the hardware resource can perform. Each operation is described with the name of the operation, its parameters, the input latency function name, and the computing latency function name. These two names should be defined in the latency functions section. 


Allowed parameters:
* range , which represents a range of integer values. It should be defined as Parameter = [startvalue | endvalue]
* fixvalue, represents a fixed value. It should be defined as Parameter = [value]
* boolean, represents a boolean value (true or false). It should be defined as Parameter = [boolean]
* vectorvalues, represents a list of integer values. It should be defined as Parameter = [value0 ~ value1 ~ value2 ~ value3]
* vectorstring, represents a list of strings. It should be defined as Parameter = [string0 ~ string1 ~ string2]
* fixstring, represents a fixed string. It should be defined as Parameter = [string0]



## Command line and requirements

This software tool is developed in Python 3.6. The only external requirement is the GraphViz (version 0.13.2) library installed. Other libraries will be installed automatically. The software tool is executed through the command line, and several arguments need to be specified.

The main arguments are:

* -h : general help argument



* -app : defines the path of the application file, and it should include the name of the file. The file needs to be inside of the working directory or in a sub-folder of it. Example
    
         -app inputfiles/configurationfileapplication.txt
            
 the path is saved directly to args.AppFilepath and transfer to the variable "filepath\_app", this variable feeds  the configuration files parser. No path and random generator disable will raise an error.
* -hw : defines the path of the hardware file, it should include the name of the file. The file needs to be inside of the working directory or in a sub-folder of it. Example:
    
        -hw inputfiles/configurationfilehardware.txt
            
  the path is saved directly to args.HwFilepath and transfer to the variable "filepath\_hw", this variable feeds   the configuration files parser. No path and random generator disable will raise an error.
    
* -pr : defines the verbosity.  The argument is saved directly to args.Print. Example of input
    
       -pr noprint
            
    We have several options of verbosity, main options are main (information about the main script), eval (information about the performance evaluation script), exh (exhaustive algorithm script), heu (ta-map and bb-map scripts), ql (q-learning approach) and list (ss-map script).  Default value is 'noprint'.
* -mo :  we use this argument if we want or not execute the performance evaluation. The argument is saved to args.Total.
      This is used for the heuristic and the exhaustive, in the benchmark the performance evaluation is mandatory. Example:
      
      -mo total
      
     Options for this argument: total (execution of performance evaluation) and noperfo. Default value is 'noperfo'.
* -ta : argument for the type of mapping process that we want to perform.  Example
    
       -ta heu
    
The options are heu (ta-map and bb-map), list (ss-map), exh (exhaustive algorithm) and q-l (q-learning mapping algorithm)
* -sg : defines if we want to visualize the input graphs. Example
    
          -sg True
   Options are true or false
* -si : defines if we want to visualize the output graph (implementation graph). Options are true or false
* -con : argument for the path of the constrains file. It should include the name of the file. Example
  
          -con inputfiles/constrainsfile.txt
            
 The default value is an empty string which means no constrains. If we specify a path and the data of the file does not correspond to our input graphs but it can be used, the mapping will be wrong.
* -ran : random graph generator enable. Options are true or false.
* -gen :  argument for the path of the random generator specifications file. The random generator requires a certain number  of details to generate graphs. We specify the path of the file that contains all the details through this argument. Example
       
            -gen inputfiles/configurationforthegenerator.txt
            
 A empty string with argument -ran set to True will raise an error.
* -folder : argument to specify the path where we want to save our graphs and files. It will take as root the current path,
          where the python files are, and from there it will create the folders. For example, the top.py is in the
          following path:
          
            c:/users/name/mapping/top.py
            
   and we define the argument as
          
            -folder outputfiles
            
the final path of the output files will be
          
            c:/users/name/mapping/outputfiles/implementationgraph.pdf
            
Default value 'outputfiles'
* -listtype : defines the type of ss-map. Options are one (only one random topological sorting) or alltopo (all topological sortings)
* -iter : number of iterations of both the mapping and the performance evaluation 
* -heutype : type of the heuristic approach. Options are bayes (bb-map) and original (ta-map)
* -poolperfo : defines the number of threads that we want to spawn for the performance evaluation. 
* -byslatlmt : defines the limit of the number of elements of the latency groups for the bb-map
* -bysdislmt : defines the limit of the topological distance considered for the bb-map
* -onepisodes : defines the number of episodes of the online training (q-learning approach)
* -onestartdecay : defines the start of the decay of epsilon for the online training (q-learning approach)
* -oneenddecay : defines the end of the decay of epsilon for the online training (q-learning approach)
* -offepisodes : defines the number of episodes for the offline training (q-learning)
* -offstartdecay : defines the start of the decay of epsilon for the offline training (q-learning)
* -offenddecay : defines the end of the decay of epsilon for the offline training (q-learning)
* -rewardpath : defines the path of the rewards vector
* -limittimeslots : defines the limit of numnber of time slots for the exhaustive algorithm (limit the exploration design space)

## Mapping algorithms

This tool includes the following mapping algorithms : topology-aware mapping algorithm (TA-MAP), bayes-based mapping algorithm (BB-MAP), q-learning mapping algorithm, single-shot mapping algorithm (SS-MAP) and an exhaustive mapping algorithm. Each algorithm has its default values, however, they can change through the respective arguments.

### Topology-aware mapping algorithm

The ta-map is based on lookahead techniques and to be selected we use the following arguments:

    -ta heu -heutype original

### Bayes-Based mapping algorithm
 
 The BB-MAP requires the following arguments:
 
     -ta heu -heutype bayes 
     
   Aditional arguments may be used, -byslatlmt and -bysdislmt, both arguments only accepts integers.
 
 ### Q-Learning mapping algorithm
 
 The q-learning mapping algorithm requires to be specified: the number of episodes for the offline and the online training, and the specifications of the epsilon decay
 
      -ta q-l 
 
 ### Single-Shot Mapping Algorithm
 
 The SS-MAP requires the following argument:
 
     -ta list 
 
 and the version to be executed,
 
      -listtype one
 
 the options are one, using one random topological sorting, and alltopo using all topological sortings.
 
 ### Exhaustive mapping algorithm
 
 An exhaustive algorithm is included as a benchmark for the other algorithms.
 
    -ta exh
 
 
 
 
 ## Random graph generator
 
 
The pseudo-random graph generator allows  to produce synthetic graphs to verify the performance of the mapping algorithms.  The information to generate the graphs is obtained from a specification file.  This file is a .txt that should contain the following fields:



* Hardware graph specification
    * number_nodes, defines the maximum number of internal nodes of the graph.
    * node_input_degree, defines the maximum input degree of the graph.
    * node_output_degree, defines the maximum output degree of the graph.
    * number_actuators, defines the number of actuators or sinks of the hardware graph.
    * number_sensors, defines the number of sensors or source of the hardware graph.
    * number_rm, defines the maximum number of memory resources.
    * limit_address_space_rm, defines the maximum amount of memory address space for the memory resources.
    * limit_address_space_rc, defines the maximum amount of memory address space for the communication resources.
    * configuration_functions_list, defines the configuration functions. It  consist of a list of tuples.
    * input_latency_functions, defines the input latency functions. It consist of a list of tuples.
    * operations_list, defines the names of the operations that the resources may perform.
    * limit_parameters, defines the maximum number of parameters for each task.
    * limit_computing_latency, maximum number of clocks cycles for the computing latency of the communication resources.
    * computing_latency, defines the computing latency functions. It consist of a list of tuples.
    * limit_range, defines the possible range of the parameters that uses an integer range as input.
    * strings_list, defines the possible values of the parameters that uses a list of strings as input.
    * fixed_values, defines the possible values of the parameters that uses a list of integer values as input.
    * latency_copy, defines the latency of the copy operation.
    * mux_enable, defines if a multiplexer will be included to the hardware graph.

 * Application graph specification
    * number_applications, defines the number of applications that will be generated.
    * input_samples_range, defines the range of amount of input samples.
    * type_application, defines the type of application that will be generated.
    * resolutions, defines the possible resolutions of the input image that the generated application will use.
    * nodes_to_remove, defines the number of nodes that will be removed from the hardware graph.
    * limit_parallel_ins, define the number of possible parallel instances of the application.
    * limit_serial_ins, defines the number of possible serial instances of the application.
    
  * General specifications.
    * error_parameters, allows an error in the parameters of the application.

 
 The specification file is read by a parser and the data from this file is stored in several global variables to be used throughout the generation process. There is no standard order for the items. The comments should start with a #. Each line should end with a ;, and other lines beside  the ones described above are disregarded.
 
 
 ## Constrains specification file
 
 Another feauture of the tool is the capability of choosing an specific hardware resource for a given task. We are able to allocate manually tasks so the mapping algorithm will deal with the remaining tasks. This is done throug a constrains specification file (txt file) with the following format
 
 
![cons](https://user-images.githubusercontent.com/35706145/118012349-911a3b80-b316-11eb-96d7-005456ba689b.png)



The file starts with the keyword 
    
        mapping;
        
 Then the following lines should contain the tuples with the names of the task and the names of the hardware resources. The names should be the same as the ones of the hardware and application files. 
 
 ## Example
 
 A simple example of a command line is
 
        python main.py -app configfiles/app_homogenous_pipe/app00_01.txt -hw configfiles/hw_homogenous_pipe/hw_00.txt -ta heu -heutype bayes -mo total -sg true -si true -iter 3 -folder bayes_result 
        
  The last command line specifies an application specification file located inside the folder configfiles/app_homogenous_pipe/, inside of the current folder. The same as the hardware specification file. Next, we specified the type of algorithm, which is the BB-MAP, then we select the execution of the performance evaluation. Then we choose to visualize both the input and output graphs. Next, we specified that we want to execute three times the entire process (mapping plus performance evaluation). Finally, we define the folder where all the output files will be stored.
