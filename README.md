# Blender3D_particle_system_perfomance_test
desc:
Perfomance test for Blender3D Particle subsystem.
Plain (without GUI).
Only updating particles coordinates (Play mode, not Render).

Has two main test:
1. Spreading in empty space
2. Collisions in compressed conditions

Quick start:
1. configure bench settings in file bench_start_win.py (! blender path) and check libs
2. run bench_start_win.py
3. read result in console

Result RAW structure:
1. os_type - string
2. bench_main_type - string
3. bench_mp_type - string
4. num_thread per instance - int (1 for bench_mp_type ='mp')
5. num instances - int (1 for bench_mp_type ='thread')
6. list of tuples (time_start, time_end) in seconds for every instance - float
 



todo:
1. Complete Main test type №2(Collisions)
2. Linux starter bench_start_linux.py or unify
3. Make online result collector, like : https://www.cgdirector.com/blender-benchmark-results-updated-scores/
4. csv export
5. solid and term refactoring
