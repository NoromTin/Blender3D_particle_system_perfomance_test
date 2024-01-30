
from time import time

from multiprocessing.connection import Listener, Client

IPC_base_port = 6000

IPC_addr_worker_ready   = ('localhost', IPC_base_port)
IPC_addr_worker_result  = ('localhost', IPC_base_port + 1)

if  __name__ != '__main__':
    import os
    import subprocess
    blender_path = 'C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender'

if __name__ == '__main__':

    from os import cpu_count
    import os
    import sys
    
    from time import sleep
    from multiprocessing.pool import Pool
    
    ############################
    ### config start###
    
    # number of worker - only for 'mp' test
    mp_min      = 1
    # mp_max = 'auto' # 'auto' - Automatic os detect, incl hyper-threading
    mp_max      = 1    
    mp_factor   = 1    # multiplier for overcore bench, for example 2 mean 24 threads for 12 logical cores
    
    # threads per worker - only for 'thread' test
    tn_min      = 1         # recommended for mp test, but for 
    tn_max      = 1    # 'auto' - Automatic os detect, incl hyper-threading
    tn_factor   = 1         # multiplier for overthread bench
    
    os_type = 'windows' # i known it is dirty, need some solid refactoring
    
    # bench list . Bench type process are separate
    # 'mp' - for workers(num of blender instances, every with 1 core, 
    # 'thread' - one instance of blender, but starts with different num of cpu. 
    bench_type_list = [
                'mp',
                'thread'
                ]
    # test type. for every - separate scene python file
    bench_name_list = [
                'movement', 
                #'collision'
                ]

    out_to_console  = False
    out_to_csv      = True

    is_gui_debug    = False # True - running with gui, false - without

    ### config end
    ############################

def start_worker(*args):

    # os_type     = args[0]
    bench_name  = args[1]
    # bench_type  = args[2]
    t_num       = args[3]
    p_num       = args[4]
    gui_arg     = args[5]
    
    # name of start script here
    blender_args = gui_arg + ' -t ' + str(t_num) + ' -P "./scene_' + bench_name + '.py"' + ' -- -pn ' + str(p_num) 
    cmd = '\"\"' + blender_path +'\" ' + blender_args +'\"'
    # print(cmd)
    os.system(cmd)

    return None


if __name__ == '__main__':

    ### init params ###
    
    if mp_max == 'auto':
        mp_max = cpu_count() * mp_factor

    if tn_max == 'auto':
        tn_max = cpu_count() * tn_factor

    if not is_gui_debug:
        gui_arg = '-b'
    else:
        gui_arg = ''
        
    i_bench = 1
    
    pool = Pool(processes=mp_max)
    
    bench_num = len(bench_name_list) *  ( (mp_max - mp_min + 1 if 'mp' in bench_type_list else 1) + (tn_max - tn_min + 1 if 'thread' in bench_type_list else 1) )
    
    def start_pool(args_list):
    
        global i_bench
        print(f'bench {i_bench} of  {bench_num}')
        
        IPC_READY_recv       = Listener(IPC_addr_worker_ready)
        
        r = pool.starmap_async(start_worker, args_list)
        
        # IPC READY msg from workers
        for i in range (len(args_list)):
            msg = IPC_READY_recv.accept()
        sleep(3)
        
        # IPC START message to workers
        IPC_START_sender_arr = [Client(('localhost', IPC_base_port + 2 + i)) for i in range(1, len(args_list) + 1)]
        
        for IPC_START_sender in IPC_START_sender_arr:
            IPC_START_sender.send('')
        
        # IPC RESULT get from workers
        IPC_RESULT_recv = Listener(IPC_addr_worker_result)
        calc_result = []
        for i in range (len(args_list)):
            calc_result.append(IPC_RESULT_recv.accept().recv())

        r.wait()
        return calc_result
        
    ### start bench
    result = []
    
    for bench_name in bench_name_list:
        for bench_type in bench_type_list:
     
            if bench_type == 'mp':
                for mp_num in range(mp_min, mp_max + 1):
                    args_list = [ (os_type, bench_name,bench_type, 1 ,mp_n, gui_arg) for mp_n in range(mp_min, mp_num + 1)]
                    result.append( (args_list, start_pool(args_list) ) )
                    i_bench +=1
                    
            elif bench_type == 'thread':
                for tn_num in range(tn_min, tn_max + 1):
                    args_list = [ (os_type, bench_name, bench_type, tn_num , 1, gui_arg) ]
                    result.append( (args_list, start_pool(args_list) ) )
                    i_bench +=1

    # result RAW
    print('result raw:')
    for rec in result:
        print(rec)

    ### analisys
    print('')
    print('result analisys')
    for rec in result:
        print(f'os:{rec[0][0]}, main type:{rec[0][1]}, mp type:{rec[0][2]}, cpu num:{max(rec[0][3],rec[0][4])}')