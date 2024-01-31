# Blender3D_particle_system_perfomance_test
Perfomance test for Blender3D Particle subsystem.
Check speed of updating particles coordinates (like Play button, without GUI, without rendering).
MP scalability stats.

Has two main test:
1. Movement - Spreading in empty space
2. Collision - Spreading and continously reflecting in compressed conditions (sphere)

Quick start:
1. c:\Program Files\Blender Foundation\Blender 3.5\3.5\python\bin\python -m pip install ....... (libs for scene_[].py
2. configure bench settings in file bench_start_win.py (blender app path, etc) and check libs
3. run bench_start_win.py
4. read result in console or csv

Result RAW structure:
1. os_type - string
2. bench_main_type - string
3. bench_mp_type - string
4. num_thread per instance - int (1 for bench_mp_type ='mp')
5. num instances - int (1 for bench_mp_type ='thread')
6. list of tuples (time_start, time_end) in seconds for every instance - float

Result analisys structure:
1. cpu_name - string
2. os - string ('win','lnx','mac')
3. test_type - string('movement','collision')
4. mp_type   - string('mp','mt')
5. core_num  - int
6. cpu_rating - float (compute(cpu) rating for current core_num)
7. core_rating - float (core efficiency)
8. avg_time     - float (average test time)
9. med_time     - mediana
10. min_time    - float
11. max_time    - float

todo:
1. Complete Main test type №2 file(Collisions)
2. Linux starter bench_start_linux.py or unified
3. MacOS starter
3. Make online result collector, like : https://www.cgdirector.com/blender-benchmark-results-updated-scores/
4. READY csv export
5. solid and term refactoring
6. List to dict, pythonic way

