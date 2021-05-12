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
* -app : defines the application specification file path
* -hw : defines the hardware specification file path
* -pr : defines the verbosity, main options are main (information about the main script), eval (information about the performance evaluation script), exh (exhaustive algorithm script), heu (ta-map and bb-map scripts), ql (q-learning approach) and list (ss-map script)
* -mo : defines if we will execute only the mapping or also the performance evaluation. The options are noperfo and total
* -ta : defines the type of mapping algorithm. The options are heu (ta-map and bb-map), list (ss-map), exh (exhaustive algorithm) and q-l (q-learning mapping algorithm)
* -sg : defines if we want to visualize the input graphs. Options are true or false
* -si : defines if we want to visualize the output graph (implementation graph). Options are true or false
* -con : defines the constrains file path.
* -ran : random graph generator enable. Options are true or false.
* -gen : defines the constrains file for the random graph generator
* -folder : defines where we want to save the output files 
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

