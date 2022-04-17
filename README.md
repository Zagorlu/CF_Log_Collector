# CF_Log_Collector
CF log controller for Windows
Firstly this code very old and quick&dirty for usage, because of that please read the explanations. On the logging and gathering all of result was very hard to get it on the Windows OS. So dedicated part is creating the simple gui application and more user friendly. According to useage of the cloud foundry cli, realtime logs very difficult to capture it, especially for the real time documentations. Furter more not usefull for the operators and the developer. I'm including developers because hard to understanding for the bugs and investigations. Rarely, crusial points are missing on the checklists of the developers. As a result this project was created, but probably doesnt work properly. Except those it was used for the dummy variables. Please be carefull for usage.

In my plan was capturing multiply sessions from other orgs or fields, so in this case was needed to use multi threading. On the background all threads working for capturing logs from different threads, so app consumes too much resources, but it could be optimizeable. 

App has been developed by python 2.7.x. So some of the parts quite old and not compatiable for other OS. Basiclly you can moddeling from here(if necessary to copy that, but I dont guess). 
