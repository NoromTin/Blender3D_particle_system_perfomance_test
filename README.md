# Blender3D_particle_system_perfomance_test
desc:
Perfomance test for Blender3D Particle subsystem.
Only plain (without GUI).
Only updating particles coordinates (Play mode, not Render).
One thread per one app instance.

Has two main test:
1. Spreading in empty space
2. Collisions in compressed conditions

Quick start:
1. configure bench settings in file bench_start_win.py (! blender path) and check libs
2. run bench_start_win.py
3. read result in console

Result RAW structure:
os_type - string
bench_main_type - string
bench_mp_type - string
num_thread per instance - int (1 for bench_mp_type ='mp')
num instances - int (1 for bench_mp_type ='thread')
list of tuples (time_start, time_end) in seconds for every instance - float
 



todo:
1. Main test type №2(Collisions)
2. Linux .sh starter
3. Make online result collector, like : https://www.cgdirector.com/blender-benchmark-results-updated-scores/
4. csv export
