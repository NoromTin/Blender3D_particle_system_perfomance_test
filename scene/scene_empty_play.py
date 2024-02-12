import sys
from time import time

import argparse
parser = argparse.ArgumentParser(description='process some integers.')
parser.add_argument('-pn', '--process_num', default='1')
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
process_num = int(args.process_num)

from multiprocessing.connection import Listener, Client

IPC_base_port = 6100

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

### warm up ~ 1.5 sec
IPC_RECEIVER_START_WARM_UP = Listener(('localhost', IPC_base_port + 3 + process_num))
IPC_SENDER_WARM_UP_READY    = Client(('localhost', IPC_base_port))
IPC_RECEIVER_START_WARM_UP.accept()
a = 1.0
for i in range(7500000):
    a *= 3.1415
    a /= 3.14149

# bench
IPC_RECEIVER_START_BENCH = Listener(('localhost', IPC_base_port + 6003 + process_num)) # 6000 - manual offset (nondirect limit for core num)
IPC_SENDER_BENCH_READY      = Client(('localhost', IPC_base_port + 1))
IPC_RECEIVER_START_BENCH.accept()
# skip emission and 1st work frame for proper init
bpy.context.scene.frame_set(1)
# "playing"
time_start = time()
for i in range(2, scene_frame_end + 1):
    bpy.context.scene.frame_set(i)
time_end = time()

# sending result
IPC_SENDER_RESULT           = Client(('localhost', IPC_base_port + 2))
IPC_SENDER_RESULT.send((blender_version, time_start, time_end))

# closштп connections
IPC_SENDER_WARM_UP_READY.close()
IPC_SENDER_BENCH_READY.close()
IPC_SENDER_RESULT.close()
IPC_RECEIVER_START_WARM_UP.close()
IPC_RECEIVER_START_BENCH.close()

bpy.ops.wm.quit_blender()