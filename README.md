# Blender UI no GUI perfomance benchmark v1_0_2
1. Perfomance test for Blender (www.blender.org) UI without GUI (mainly for particle subsystem).
2. Multiprocessing core scalability. Linux, Windows, Mac compatible.
3. Results are collected in "./result/*".
4. Consolidated result in the file "./result_consolidated.csv:
5. Can be adopted for diiferent tools.
6. Old results can be find in the relevant branches

Project advantages:
1. Extenssibility. You can add your personal test that can be written with Python.
2. Not ordinary scalability test. For huge scenes, you'll get point of view how effective concrete instrument.
3. CPU scalibility result. Some time all core usage bring worst result instead of limitet number of threads.
4. Result is analitical oriented (csv). So you able to play with pivot table.

Now contains these tests:
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
   [blender dir] \ [blender ver] \python\bin\python -m pip install [libs for scene_*.py],
   for Win: "c:\Program Files\Blender Foundation\Blender 3.5\3.5\python\bin\python -m pip install [libs for scene_*.py]
3. configure bench settings in file bench_start.py (blender path, MP usage, info string vars for result file)
4. run bench_start.py
5. read result in console or csv
6. you could send result to aninelo@gmail.com with "blender bench" subject (i'll share it) OR push it to this rep with your branch

*****Ubuntu without desktop shell Blender installation  process:
1. apt-get install -y libxrender-dev libxxf86vm-dev libxfixes-dev libxi6 libxkbcommon-dev libsm6 libgl1-mesa-glx 
2. snap install blender --classic

Wanted results data for:
1. AMD Threadripper, Intel Xeons, AMD Ryzen, Apple CPUs, Exotic CPUs, and others


What does this benchmark do:
1. Prepares synchronization
2. Launch a pool of blender instances without a GUI (the number depends on the number of cores at the current iteration)
3. Each blender:
    runs the *.py script passed to it,
        Builds a scene,
        Waits for a start signal from the main thread,
        Does measurable work,
        Send measurements,
    exit Blender
4. Prepare the next iteration and run the pool again.

Why this might be interesting:
1. Check the performance scalability of the UX modules.
2. Check Performance development between blender versions. 
3. Compare processor performance for UX.

Why is this interesting to the author:
1. Collecting results for different types of processors
2. Comparing them with the results of my special modified version of Blender.
3. Comparing it with famous CPU tests such as GeekBench, Cinebench.
4. Perform calculations and make decisions for my computing stack (well parallelized scientific calculations)


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
6. cpu_rating   - float  [cpu compute rating in this test]          (calculated)
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

WHATS NEW
1. 1.0.2.2   - ability to turn ON core affinity (could be factor for a large core systems)
2. 1.0.2.1 - timeout improvement
3. 1.0.2 - IPC sync signal replaced by scheduling, warm up improve
4. 1.0.1 - IPC, sync, worm up impruvment and refactoring. Tests time was decreased for ~two times (because better sync)

HISTORY(WHY):

I did some Blender modification for my scientific calculation.
Main modified part is particle system.
(logging, some precalculations, FLOAT --> DOUBLE, simplifying structures, cleaning, disable heavy functions that I don't need, fixes, etc..)
My calculations are very CPU-hungry, and this is not one-time project.
So I started developing my home computing stack.
And you know it is an economic problem.
Part of Blender code, that i made and i interest for, don't contain most of the modern CPU instructions. So common benchmarks do not fit this goal.
And i wrote this one. 
I think it turned out to be a good universal tool

