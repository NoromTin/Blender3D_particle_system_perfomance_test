import sys
from time import time

import argparse
parser = argparse.ArgumentParser(description='process some integers.')
parser.add_argument('-pn', '--process_num', default='1')
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
process_num = int(args.process_num)

from multiprocessing.connection import Listener, Client

IPC_base_port = 6000

IPC_READY_sender = Client(('localhost', IPC_base_port))

import bpy
import blend_render_info


# scene settings, better dont change for shared benchmark
frame_part_born     = 0
subdiv              = 7
scene_frame_end     = 502 #  502 - 2(init frames) = 500 active frames
part_velocity       = 1.0

ps_timestep = 1/1000

srcRadius = 1.0
src_location = [0.0,0.0,0.0]
src_rotation = [0.0,0.0,0.0]
src_scale    = [1.0,1.0,1.0]

### scene
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

# print('worker connect', ('localhost', 6001 + process_num))
IPC_START_recv = Listener(('localhost', IPC_base_port + 2 + process_num))

# IPC READY send to coordinator
IPC_READY_sender.send(process_num)

# IPC START waiting from coordinator
msg = IPC_START_recv.accept()

# skip emission and 1st work frame for proper init
bpy.context.scene.frame_set(1)
bpy.context.scene.frame_set(2)

# play 
time_start = time()

for i in range(3, scene_frame_end + 1):
    bpy.context.scene.frame_set(i)
time_end = time()

# IPC RESULT send to coordinator
IPC_RESULT_sender  = Client(('localhost', IPC_base_port + 1))
IPC_RESULT_sender.send((time_start, time_end))

bpy.ops.wm.quit_blender()
