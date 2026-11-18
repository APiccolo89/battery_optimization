Add design notes for the optimisation routine
 
Deciding whether to use a plain function or a class. The easiest solution is having a set of functions that produce the result. However, having a solver object could be a design choice that could be more sensible.
-> Object class: creating a class containing the set-up functions is functional, and since I can introduce the battery class within it, without having a memory overhead, it could be a sensible choice. But this choice is too advanced for the problem at hand, and it may imply a future project about it.
-> A direct function that uses the markets may not give the flexibility. I need to check whether or not I can set up a separate formulation for each market and then merge them into one problem, which is solved once.
i.e.:
=> From the configuration input file, it gives the information about the markets that needs to be fed into the system.
=> For each market, it produces the PuLP configuration.
=> In the solution, it adds each market's configuration to the final constraints.
--- Need to verify