import sys
from time import perf_counter, time

import argparse
parser = argparse.ArgumentParser(description='process some integers.')
parser.add_argument('-pn', '--process_num', default='1')
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
process_num = int(args.process_num)

from multiprocessing.connection import Listener, Client

IPC_base_port = 15000

import bpy
import blend_render_info

blender_version = bpy.app.version_string

# scene settings, better dont change for shared benchmark
frame_part_born     = 0
subdiv              = 7
scene_frame_end     = 1332501 #  1032501 - 1(init frame) = 1032500 active frames  ~ 3 second benchmark
part_velocity       = 1.0

ps_timestep = 1/1000

srcRadius = 1.0
src_location = [0.0,0.0,0.0]
src_rotation = [0.0,0.0,0.0]
src_scale    = [1.0,1.0,1.0]

# scene creation
scene = bpy.context.scene
for obj in scene.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.scene.frame_end = scene_frame_end
bpy.types.Scene(bpy.context.scene).use_gravity = False
bpy.types.Scene(bpy.context.scene).gravity = (0, 0, 0)

# skip emission and 1st work frame for proper init
bpy.context.scene.frame_set(1)



# bench
# messaging 

def send_result(msg):
    IPC_SENDER_RESULT           = Client(('localhost', IPC_base_port + 2))
    IPC_SENDER_RESULT.send(msg)
    IPC_SENDER_RESULT.close()

IPC_RECEIVER_START_TIME_MESSAGE = Listener(address=('localhost', IPC_base_port + 3 + process_num), backlog=1)
IPC_SENDER_WORKER_READY    = Client(('localhost', IPC_base_port))
IPC_SENDER_WORKER_READY.close()
conn = IPC_RECEIVER_START_TIME_MESSAGE.accept()
bench_schedule_start_time = conn.recv()
conn.close()
IPC_RECEIVER_START_TIME_MESSAGE.close()

# check bench_start_time to early to this worker
if bench_schedule_start_time < time():
    send_result('err_timestart')
    exit()

# waiting for the start time and warming up
while bench_schedule_start_time > time():
    a = 1.0
    a *= 3.1415

# bench test
# "playing"
bench_start_time = perf_counter()
for i in range(2, scene_frame_end + 1):
    bpy.context.scene.frame_set(i)
    
bench_end_time = perf_counter()

# debug frieze emulation
# import random
# if bool(random.getrandbits(1)):
    # if bool(random.getrandbits(1)):
        # if bool(random.getrandbits(1)):
            # if bool(random.getrandbits(1)):
                # from time import sleep
                # print('worker freeze ',process_num) 
                # sleep(1660.0)


# sending result
send_result((blender_version, bench_start_time, bench_end_time))

bpy.ops.wm.quit_blender()