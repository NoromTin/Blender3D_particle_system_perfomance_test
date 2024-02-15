import sys
from time import perf_counter

import argparse
from multiprocessing.connection import Listener, Client

parser = argparse.ArgumentParser(description='process some integers.')
parser.add_argument('-pn', '--process_num', default='1')
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
process_num = int(args.process_num)

IPC_base_port = 15000

import bpy
import blend_render_info

blender_version = bpy.app.version_string

# scene settings, better dont change for shared benchmark
frame_part_born     = 0
subdiv              = 7
scene_frame_end     = 107 #  105 - 1(init frames) = 104 active frames
part_velocity       = 1.0

ps_timestep = 1/1000

srcRadius = 1.0
src_location = [0.0,0.0,0.0]
src_rotation = [0.0,0.0,0.0]
src_scale    = [1.0,1.0,1.0]

### scene creation
scene = bpy.context.scene
for obj in scene.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.scene.frame_end = scene_frame_end
bpy.types.Scene(bpy.context.scene).use_gravity = False
bpy.types.Scene(bpy.context.scene).gravity = (0, 0, 0)

### source mesh
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv,radius=srcRadius, calc_uvs=False, enter_editmode=False
                                        , align='WORLD', location=src_location, rotation=src_rotation, scale=src_scale)
obj = bpy.context.active_object
obj.name    =   'src_obj'
obj.show_instancer_for_render = False
obj.show_instancer_for_viewport = False
src_vertex_num = len(bpy.data.objects[obj.name].data.vertices)

### particle system
obj.modifiers.new("part", type='PARTICLE_SYSTEM')
ps = obj.particle_systems[0]
settings = ps.settings
settings.emit_from          = 'VERT'
settings.use_emit_random    = False
settings.physics_type       = 'NEWTON'
settings.integrator         = 'RK4'
settings.render_type        = 'OBJECT'
settings.particle_size      = 0.001
settings.display_method     = 'CROSS'
settings.subframes = 0
settings.timestep = ps_timestep
settings.use_adaptive_subframes = True
settings.normal_factor = part_velocity


settings.display_percentage = 100
settings.display_size       = 0.01
settings.display_color      = 'NONE'
settings.count              = src_vertex_num
settings.lifetime           = scene_frame_end + 1
settings.frame_start        = frame_part_born
settings.frame_end          = frame_part_born

# camera only for debug
camera_data = bpy.data.cameras.new(name='Camera')
camera_object = bpy.data.objects.new('Camera', camera_data)
bpy.context.scene.collection.objects.link(camera_object)
camera_object.location = [0,0,12]
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
bpy.context.scene.camera = camera_object

# skip emission and 1st work frame for proper init
bpy.context.scene.frame_set(1)


# bench
# messaging 
IPC_RECEIVER_START_TIME_MESSAGE = Listener(('localhost', IPC_base_port + 3 + process_num))
IPC_SENDER_WORKER_READY    = Client(('localhost', IPC_base_port))
IPC_SENDER_WORKER_READY.close()
conn = IPC_RECEIVER_START_TIME_MESSAGE.accept()
bench_start_time = conn.recv()
conn.close()
IPC_RECEIVER_START_TIME_MESSAGE.close()

# check bench_start_time to early to this worker
if bench_start_time < perf_counter():
    print('time start to early for worker!! increase [signal_gap_worker_start], exit')
    exit(1)

# waiting for the start time and warming up
while bench_start_time > perf_counter():
    a = 1.0
    a *= 3.1415

# bench test
# "playing"
for i in range(2, scene_frame_end + 1):
    bpy.context.scene.frame_set(i)
    
bench_end_time = perf_counter()

# debug frieze emulation
# import random
# if bool(random.getrandbits(1)):
    # if bool(random.getrandbits(1)):
        # if bool(random.getrandbits(1)):
            # from time import sleep
            # print('worker freeze ',process_num) 
            # sleep(1660.0)


# sending result
IPC_SENDER_RESULT           = Client(('localhost', IPC_base_port + 2))
IPC_SENDER_RESULT.send((blender_version, bench_start_time, bench_end_time))
IPC_SENDER_RESULT.close()

bpy.ops.wm.quit_blender()