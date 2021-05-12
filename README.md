# Complete Mapping Framework for Software Programmable Streaming Coarse Grained Reconfigurable Architectures


## Overview

This repository contains a software tool developed for the easy reuse of Software Programmable Streaming Coarse Grained Reconfigurable Architectures (SPS-CGRA). The complete overview is showed in the following figure



![Mesa de trabajo 1](https://user-images.githubusercontent.com/35706145/117903432-27a61880-b295-11eb-870b-68d1b6d5b97a.png)



The inputs are a couple of specification files (application and hardware). The software tool consists of a parser, a set of mapping algorithms, a random graph generator, a performance evaluation and a configuration context generator.

## Specification Files

The inputs of the tool are a couple of specification file. Some examples of this are in the folder configfiles/

### Application specification file

An example of a specification file is showed in the following figure

![specificationfileapplication](https://user-images.githubusercontent.com/35706145/117912046-655e6d80-b2a4-11eb-8fdf-42699c0634ca.png)


In this simple example the application consists of a sensor, an actuator and a task, all conected in a pipeline.

### Hardware specification file

An example of a specification file is showed in the following figure

![specificationfilehardware](https://user-images.githubusercontent.com/35706145/117912704-94291380-b2a5-11eb-8b78-14ae32e1898b.png)

The specification file is divided into three sections: configuration functions and parameters, latency functions (input and computing latencies) and hardware resources description.


## Command line and requirements

This software tool is developed in Python 3.6. The only external requirement is the GraphViz library installed, other libraries will be installed automatically. The software tool is executed throught the command line and several arguments need to be specified.

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

This tool includes the following mapping algorithms : topology-aware mapping algorithm (TA-MAP), bayes-based mapping algorithm (BB-MAP), q-learning mapping algorithm, single-shot mapping algorithm (SS-MAP) and an exhaustive mapping algorithm.

## Topology-aware mapping algorithm

The ta-map is based on lookahead techniques and to be selected we use the following arguments:

-ta heu -heutype original

## Bayes-Based mapping algorithm
 
 The BB-MAP requires the following arguments:
 
 -ta heu -heutype bayes -byslatlmt INTEGER -bysdislmt INTEGER
 
 ## Q-Learning mapping algorithm
 
 The q-learning mapping algorithm requires to be specified: the number of episodes for the offline and the online training, and the specifications of the epsilon decay
 
 ## Single-Shot Mapping Algorithm
 
 The SS-MAP requires the following arguments:
 
 -ta list 
 
 in the case of -listtype we can define either one or alltopo
 
 ## Exhaustive mapping algorithm
 
 An exhaustive algorithm is included as a benchmark for the other algorithms.
 
 
