# Blender UI no GUI perfomance benchmark
Perfomance test for Blender (www.blender.org) UI without GUI (mainly for particle subsystem)
Multiprocessing core scalability. Linux, Windows, Mac compatible
Results are collected in ./result

Contain tests:
1. particle_movement    - Spreading particles in empty space
2. particle_collision   - Spreading and continously reflecting in compressed conditions (sphere)
3. empty_play           - just playing in empty scene

Requirements:
1. .py file editing experience
2. installed Blender app (tested on Blender v3.5, v4.0)
3. 400mb ram per logical core (num of cores used in test can be limited with configuration, but all cores access running is prefferable)

Quick start:
1. check os python 3 libs
   Win: pip install psutil py-cpuinfo
   Linux: apt install python3-pip && pip install psutil py-cpuinfo
2. check blender python libs
   [blender dir] \ [blender ver] \python\bin\python -m pip install [libs for scene_*.py]
   Win: "c:\Program Files\Blender Foundation\Blender 3.5\3.5\python\bin\python -m pip install [libs for scene_*.py]
3. configure bench settings in file bench_start.py (blender path, MP usage, info string vars for result file)
4. run bench_start.py
5. read result in console or csv
6. you could send result to aninelo@gmail.com with "blender bench" subject (i'll share it) OR push it to this rep with your branch

Wanted result data for:
1. AMD Threadripper, Intel Xeons, AMD Ryzen, Apple CPUs, Exotic CPUs, and others)


What does this benchmark do:
1. Prepares synchronization
2. Launch a pool of blender instances without a GUI (the number depends on the number of cores at the current iteration)
3. Each blender:
      runs the *.py script passed to it
          Builds a scene,
          Waits for a start signal from the main thread,
          Does measurable work,
          Send measurements,
      exit Blender
4. Prepare the next iteration and run the pool again.

Why this might be interesting:
1. Check the performance scalability of the UI modules.
2. Check Performance development between blender versions. 
3. Compare processor performance for UX.

Why is this interesting to the author:
1. Collecting results for different types of processors
2. Comparing them with the results of my special modified version of Blender.
3. Comparing it with famous CPU tests such as GeekBench, Cinebench.
4. Perform calculations and make decisions for my Beowolf cluster (well parallelized scientific calculations)


Result RAW structure:
1. os_type                  - string
2. test_type                - string
3. mp_type                  - string
4. num_thread per instance  - int (1 for bench_mp_type ='mp')
5. num instances            - int (1 for bench_mp_type ='thread')
6. list of tuples           - float [(time_start, time_end),] in seconds for every instance

Result analysis structure:
1. cpu_name     - string [large cpu name]                           (autodetected, from cpuinfo import get_cpu_info)
2. hardware     - string [hardware platform (brand, mb, ram etc.)]  (added manually, hardware var in bench_start.py)
3. bench_env    - string ['bare','vm*']                             (added manually, 'bare' for real host, 'vm [brand] [hypervisor os] [hypervisor cpu if needed]' )
4. os_type      - string ['Win','Lnx','Mac']                        (autodetected, from sys import platform)
5. os_release   - string [Major os version]                         (autodetected, import platform, platform.release())
6. os_version   - string [Detailed os version]                      (autodetected, import platform, platform.version())
7. blender_version - string [Blender app major version]             (autodetected, scene*.py file, import bpy, bpy.app.version_string)
8. test_type    - string ['particle_movement','particle_collision','empty_play'] (autodetected, test_type_list)
4. mp_type      - string ['mp','mt']                                (autodetected, mp_type_list)
5. core_num     - int    [number of cores used in current test]     (autodetected, HT included logical cores)
6. cpu_rating   - float  [cpu compute rating in this test]          (calculated, all tests complexity needed to be scale for around the same one core cpu power)
7. core_rating  - float  [core efficiency]                          (calculated)
8. avg_time     - float  [average time, sec]                        (calculated)
9. med_time     - float  [mediana time, sec]                        (calculated)
10. min_time    - float  [minimal time, sec]                        (calculated)
11. max_time    - float  [maximum time, sec]                        (calculated)


TODO:
1. TODO solid and term refactoring
2. TODO Make online result collector, like : https://www.cgdirector.com/blender-benchmark-results-updated-scores/
3. TODO List to dict, pythonic way
 
COMPLETED:
1. Linux starter bench_start_linux.py or unified
2. Complete Main test type №2 file(Collisions)
3. MacOS starter
4. READY csv export
5. Warming up cpu to get more honest result
6. Conclusion analysys
7. Blender version

HISTORY(WHY):

I did some Blender modification for my scientific calculation.
Main modified part is particle system.
(logging, some precalculations, FLOAT --> DOUBLE, simplifiing structures, cleaning, disable heavy functions I don't need, fixes, etc..)
My calculations are very CPU-hungry, and this is not one-time project.
So I started developing my home supercomputer (Beowolf cluster).
And you know it is an economic problem.
Part of Blender code, that i made and i interest for, don't contain most of the modern CPU instructions. So common benchmarks do not fit this goal.
So i wrote this one!)  
I think it turned out to be a good universal tool)

