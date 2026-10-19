# CFD Framework — Development Postmortem

## 1. Project Background

I started this project to build on the experience I gained from developing my previous database engine project. I wanted to develop further programming skills by working on a simulation that involved representing mathematical equations, modelling a physical system and observing how its state evolved over time.

Computational fluid dynamics provided an opportunity to combine programming with numerical methods and physics. Rather than simply processing or storing data, the framework needed to calculate how a simulated fluid changed in response to its surroundings, including the presence of solid obstacles.

The project gradually expanded from a basic flow simulation into a more substantial framework with multiple geometries, different numerical methods, a graphical interface, flow visualisation and data-export capabilities.

## 2. Development Process

I began with a basic uniform flow and developed the simulation incrementally, adding geometries and slip-wall boundary treatments as the project progressed. This approach allowed the framework to grow from a relatively simple starting point into a system capable of representing more varied flow configurations.

One of the largest changes in scope was the addition of a graphical user interface (GUI). The GUI was not part of the original plan, but it developed into an important part of the project. It made the simulator more accessible and allowed users to change settings and inspect the computed flow fields without interacting exclusively through code.

Another major step was extending the implementation from the Euler equations to the Navier–Stokes equations. This represented a significant increase in scope because the framework needed to accommodate viscous effects in addition to the inviscid flow model.

As the project developed, the work extended beyond implementing the numerical solver. Organising the code, managing configuration and connecting the GUI to the simulation became substantial parts of the development process.

## 3. Technical Challenges

### 3.1 Project Organisation

Packaging the project into a clear and organised structure was one of the main challenges. As more functionality was added, it became increasingly important to separate responsibilities and make the codebase easier to navigate.

This highlighted that a project involving numerical simulation requires more than a working solver. The surrounding infrastructure, including geometry generation, visualisation, configuration and data export, also needs a structure that remains manageable as the project grows.

### 3.2 Configuration Management

Another challenge was designing the configuration system that passes information between the GUI and the simulator.

The interface needs to expose useful settings while ensuring that the simulation receives the appropriate values. Managing this interaction required careful consideration of how configuration data is represented and transferred between the two parts of the framework.

This was an important architectural problem because changes to the interface should not unnecessarily complicate the numerical implementation.

### 3.3 GUI Complexity

The Tkinter interface grew into a large file that became difficult to read and maintain. As more controls and functionality were added, the amount of code in a single location made the interface increasingly difficult to navigate.

This demonstrated the limitations of allowing a graphical interface to grow without sufficiently separating its responsibilities. A more modular structure would make individual interface components easier to understand, modify and test.

## 4. Unexpected Numerical Behaviour

Several unexpected behaviours were observed during development. I investigated them, but their causes remain unresolved, so I cannot confidently attribute them to specific implementation errors or numerical-method limitations.

### 4.1 Freestream Velocity Discrepancy

The ambient flow speed reaches only approximately half the specified inflow velocity under the tested conditions. This is a significant limitation because the resulting flow field does not reproduce the intended freestream conditions as expected.

The discrepancy has not been resolved. Its cause is unknown, and further investigation is needed before the simulation can be relied upon for quantitative aerodynamic predictions.

### 4.2 Flow Near Solid Boundaries

I also observed fluid flowing towards solid boundaries rather than remaining parallel to them as I had expected. This behaviour raised questions about the implementation of the solid-wall treatment and the resulting flow field.

Although I investigated the behaviour, I did not establish its cause. It therefore remains uncertain whether it results from a bug, an interaction between numerical components or another aspect of the implementation.

### 4.3 HLL and HLLC Flux Methods

The HLL and HLLC flux methods produced results with sharp and unnatural-looking features compared with the behaviour I expected.

I investigated these results but did not identify or resolve their cause. Without further testing against suitable reference cases, I cannot determine whether the behaviour is caused by an implementation issue, the numerical method's behaviour under the chosen conditions or another limitation of the solver.

These experiences reinforced the importance of distinguishing between a simulation that produces convincing visualisations and one whose numerical results have been demonstrated to be correct.

## 5. Architecture and Design Decisions

One of the most successful design decisions was keeping the simulator separate from the GUI.

The simulation can run independently of the graphical interface, allowing the numerical implementation to remain usable without requiring the GUI to be active. This separation also made the main simulation loop clearer: the code responsible for advancing the simulation each frame is distinct from the code responsible for presenting it to the user.

I found this separation particularly valuable because the numerical solver and graphical interface have different responsibilities. The solver manages the evolving flow state, while the GUI provides controls and visual feedback.

The project also developed a useful degree of customisation. Users can explore different geometries, visualisation options and numerical settings without being presented with an unnecessarily overwhelming interface.

In retrospect, maintaining this separation while expanding the project's capabilities was one of the stronger aspects of the design.

## 6. Testing and Validation

The framework has been exercised through geometry experiments, airfoil simulations and performance benchmarks. These experiments helped me observe its behaviour under different configurations and investigate aspects of its computational performance.

However, the simulated results have not been verified against existing research data, analytical solutions or trusted reference simulations. Consequently, the visual similarity between my results and those produced by professional CFD software should not be interpreted as evidence of equivalent accuracy.

The unresolved numerical behaviours described above make this distinction particularly important. A plausible pressure or velocity distribution is not sufficient to establish that the underlying numerical solution is correct.

A key lesson from this project is that implementation, debugging and validation are separate stages of numerical software development. A framework can successfully execute its algorithms and produce useful visualisations while still containing unresolved numerical problems.

Future validation work would need to compare appropriate test cases against established reference results and investigate discrepancies systematically.

## 7. Performance and Optimisation

One of the most surprising findings was how quickly the numerical calculations could execute, even for relatively large computational grids.

The performance experiments indicated that rendering could account for the overwhelming majority of total runtime at larger grid sizes. This meant that the visualisation pipeline, rather than the numerical calculations alone, was a major bottleneck in the complete simulation workflow.

This changed how I would approach optimisation. Improving the solver's calculation time would have limited impact on overall runtime if rendering continued to dominate the execution cost.

One possible future direction would be to investigate a different rendering architecture. For example, SDL3 and a custom rendering engine could provide an alternative to the existing Pygame-based approach, potentially allowing more efficient rendering and GPU-accelerated visualisation.

However, this would require implementation and benchmarking before any performance improvement could be established. A custom rendering engine would also introduce additional complexity, so its benefits would need to justify the development effort.

## 8. Most Successful Aspects

I am particularly pleased with the visual presentation and the range of functionality achieved. The framework produces clean flow visualisations and supports a variety of geometries and simulation settings.

The resulting images often look qualitatively similar to those produced by professional CFD software, which makes the framework useful for exploring flow-field behaviour and comparing configurations. However, this is a visual observation rather than a quantitative validation of the numerical results.

I am also satisfied with the balance between customisation and usability. The user can alter important aspects of the simulation without having to work directly with every internal implementation detail.

Finally, the separation between the simulator and GUI provides a clearer structure for continued development. Together, these aspects make the framework a useful foundation for further numerical and software-engineering work.

## 9. What I Would Do Differently

If I were to begin the project again, I would place greater emphasis on code organisation and validation strategy from an earlier stage.

In particular, I would aim to keep the GUI modular as its functionality expands, rather than allowing a large interface file to become difficult to maintain. I would also give more attention to how configuration data flows between the interface and the simulator, so that the boundaries between components remain clear.

I would also establish a more systematic approach to numerical validation. Unexpected behaviour should be investigated using small, controlled test cases wherever possible, making it easier to isolate the component responsible. Comparisons against suitable analytical or reference solutions would provide stronger evidence than visual inspection alone.

Finally, I would measure the performance of the numerical and rendering components separately from an earlier stage. The existing benchmarks showed the value of separating these costs, and doing so sooner could have helped guide architectural decisions before the visualisation system became a major performance bottleneck.

## 10. Future Improvements

The most impactful improvements would address the current performance bottleneck and the unresolved numerical limitations.

### 10.1 Rendering Performance

Optimising rendering is a priority because the benchmarks showed that it dominates runtime for large grids. Potential approaches include reducing unnecessary drawing operations, improving the rendering pipeline or investigating a GPU-accelerated implementation.

Any replacement should be evaluated against the existing renderer using comparable workloads to establish whether it provides a meaningful improvement.

### 10.2 Numerical Validation

The solver needs further investigation and validation before its results can be treated as reliable aerodynamic predictions. This includes investigating the freestream-velocity discrepancy, the unexpected flow near solid boundaries and the behaviour observed with HLL and HLLC flux methods.

These issues should be addressed through controlled experiments and comparison with appropriate reference solutions, rather than by assuming a particular cause.

### 10.3 Aerodynamic Force Calculations

Adding a method for calculating lift would make the airfoil experiments more informative. It would provide a quantitative measure to investigate alongside the existing pressure and velocity visualisations.

Such a feature would need to be implemented and checked carefully, and its results would depend on the reliability of the underlying flow solution.

### 10.4 Three-Dimensional Simulation

Extending the framework to three dimensions would allow the investigation of more realistic geometries and flow configurations that cannot be represented in a two-dimensional model.

However, this would be a substantial undertaking. It would increase the computational and visualisation requirements and require changes to the solver, geometry representation and data structures. A more efficient rendering pipeline and a validated two-dimensional solver would be sensible priorities before pursuing this extension.

## 11. Conclusion

Developing this framework gave me experience extending a software project from a basic numerical simulation into a more complete application with a graphical interface, multiple geometries, data collection and performance analysis.

The project also demonstrated the challenges of numerical software development. Producing visually convincing results is only one part of the task; understanding unexpected behaviour, structuring the code for maintainability and establishing numerical validity are equally important.

The most useful lessons were the value of separating the simulation from the GUI, the importance of managing configuration and code complexity, and the need to measure performance rather than assume where the bottlenecks lie.

Although several numerical limitations remain unresolved, the framework provides a foundation for further investigation. My priorities for future development would be to improve rendering performance, establish stronger numerical validation and then extend the simulator's quantitative analysis capabilities.