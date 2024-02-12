from sys import platform
import os
from time import time, sleep

from multiprocessing.connection import Listener, Client
from multiprocessing import set_start_method


################################# 
### config begin
###

# info strings, dont left it empty
hardware        = 'standart'
# hardware        = 'Mac Book Pro 2018 32GRam'
bench_env       = 'bare'
# bench_env = 'vm virtual box on Win10 host'
# bench_env = 'vm ec2'

# blender_path_Win = 'C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender'
blender_path_Win = 'C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender'
blender_path_Lnx = '/snap/blender/4300/blender'
blender_path_Mac = '/Applications/Blender.app/Contents/MacOS/Blender'
# test type, each have separate scene python file
# all scenes complexity scaled for around same cpu rating for a one core test
test_type_list = [
            'particle_movement'
            ,'particle_collision'
            ,'empty_play'
            ]

# Multiprocessing type used in bench
# 'mp' - Multi processing. Multiple workers(blender instances) every with 1 core, 
# 'th' - Threading. One blender instance, but start with different num of core. 
#  There is no middle setting for test, like 2 instance with 2 thread each. Think no case for that
mp_type_list = [
            'mp'
            ,'th'
            ]

# 'mp' cpu(core) num
mp_min      = 1
# As practice has shown, taking the number of cores by 1 more than the maximum really works and gives a small increase
mp_max      = 'auto' # 'auto' - Automatic os detect, incl hyper-threading PLUS ONE (!).  
# mp_max = 1

# 'th' cpu(core) num
tn_min      = 1
# tn_max can be limited by 8, because scalability 'th' for more then 4 core usualy is not effective. Preserving bench time for large multi-core systems, if needed
# As practice has shown, taking the number of cores by 1 more than the maximum really works and gives a small increase
tn_max    = 'auto' # 'auto' - Automatic os detect, incl hyper-threading PLUS ONE (!).
# tn_max      = 1


out_to_console  = True
out_to_csv      = True
csv_file_dir   = './result/'

is_gui_debug    = False # True - running with gui, false - without (default)

###
### config end
################################# 

bench_verion = '1_0_1'
IPC_base_port = 6100




# os detection
if platform == "linux" or platform == "linux2":
    os_type = 'Lnx'
elif platform == "darwin":
    os_type = 'Mac'
elif platform == "win32":
    os_type = 'Win'


##### for a workers process
if  __name__ != '__main__':

    import subprocess
    
    # blender path
    if os_type == 'Win':
        blender_path = blender_path_Win
        cmd_quote = '"'
    elif os_type == 'Lnx':
        blender_path = blender_path_Lnx
        cmd_quote = ''
    elif os_type == 'Mac':
        blender_path = blender_path_Mac
        cmd_quote = ''
    else:
        print('unknown os')
        exit()

    bench_dir = os.path.dirname(__file__)

def start_worker(*args):

    #starting blender separate instance, without GUI(default), with scene py file. Exit when the instance exit
    test_type  = args[0]
    t_num       = args[1]
    p_num       = args[2]
    gui_arg     = args[3]
    
    blender_args = gui_arg + ' -t ' + str(t_num) + ' -P "' + bench_dir +  '/scene/scene_' + test_type + '.py"' + ' -- -pn ' + str(p_num)
    cmd = cmd_quote +  '\"' + blender_path +'\" ' + blender_args + cmd_quote
    os.system(cmd)


### for the main process
if __name__ == '__main__':

    import sys
    from time import sleep
    from multiprocessing.pool import Pool
    set_start_method('spawn')
    
    from psutil import cpu_count
    from uuid import uuid4
    
    import csv
    from statistics import median
    from cpuinfo import get_cpu_info
    import platform
    
    cpu_name = get_cpu_info()['brand_raw']
    os_release = platform.release()
    os_version = platform.version()
    # additional unique mark for the result
    bench_hash = uuid4().hex[0:16]

    ### cooking vars ###
    
    if mp_max == 'auto':
        mp_max = cpu_count() + 1
    if tn_max == 'auto':
        tn_max = cpu_count() + 1

    if not is_gui_debug:
        gui_arg = '-b'
    else:
        gui_arg = ''

    pool = Pool(processes=mp_max)
    
    i_bench = 1
    # progress in console
    bench_num = len(test_type_list) *  ( (mp_max - mp_min + 1 if 'mp' in mp_type_list else 1) + (tn_max - tn_min + 1 if 'th' in mp_type_list else 1) )
    
    def start_pool(args_list):
    
        global i_bench
        print(f'bench {i_bench} of  {bench_num}')
        
        worker_num = len(args_list)
        
        def wait_workers_ready_signal(listener_arr):
            for i in range (worker_num):
                msg = listener_arr.accept()

        # preparing listeners and senser
        IPC_RECEIVER_WARM_UP_READY = Listener(('localhost', IPC_base_port))
        IPC_RECEIVER_BENCH_READY   = Listener(('localhost', IPC_base_port + 1))
        IPC_RECEIVER_RESULT        = Listener(('localhost', IPC_base_port + 2))

        # running workers
        r = pool.starmap_async(start_worker, args_list)

        ### warm up
        wait_workers_ready_signal(IPC_RECEIVER_WARM_UP_READY)
        IPC_SENDER_START_WARM_UP_arr = [Client(('localhost', IPC_base_port + 3 + i)) for i in range(1, worker_num + 1)]

        ### bench
        wait_workers_ready_signal(IPC_RECEIVER_BENCH_READY)
        IPC_SENDER_START_BENCH_arr = [Client(('localhost', IPC_base_port + 6003 + i)) for i in range(1, worker_num + 1)]
        
        # get RESULT from workers
        calc_result = []
        for i in range (worker_num):
            calc_result.append(IPC_RECEIVER_RESULT.accept().recv())
        r.wait()

        IPC_RECEIVER_WARM_UP_READY.close()
        IPC_RECEIVER_BENCH_READY.close()
        IPC_RECEIVER_RESULT.close()
        
        for IPC_SENDER in IPC_SENDER_START_WARM_UP_arr:
            IPC_SENDER.close()
        for IPC_SENDER in IPC_SENDER_START_BENCH_arr:
            IPC_SENDER.close()

        return calc_result
        
    ### starting pool for every bench combinations
    result = []
    
    for test_type in test_type_list:
        for mp_type in mp_type_list:
     
            if mp_type == 'mp':
                for mp_num in range(mp_min, mp_max + 1):
                    args_list = [ (test_type, 1 ,mp_n, gui_arg) for mp_n in range(mp_min, mp_num + 1)]
                    result.append( ((mp_type,) + args_list[-1], tuple(start_pool(args_list) )) )
                    i_bench +=1
                    
            elif mp_type == 'th':
                for tn_num in range(tn_min, tn_max + 1):
                    args_list = [ (test_type, tn_num , 1, gui_arg) ]
                    result.append( ((mp_type,) + args_list[-1], tuple(start_pool(args_list) )) )
                    i_bench +=1

    # result RAW
    if out_to_console:
        print('result raw:')
        for rec in result:
            print(rec)

    # analysis
    result_analysis = []
    for rec in result:
        # average
        agg_avg = 0.0
        agg_min = float('+inf')
        agg_max = 0.0
        agg_med = None
        mp_time_list = []
        for result_rec in rec[1]:
            mp_time = result_rec[2] - result_rec[1]
            mp_time_list.append(mp_time)
            agg_avg += mp_time
            agg_min = min(agg_min, mp_time)
            agg_max = max(agg_max, mp_time)
            
        # yep to dirty to get blender version from every run, but it's simple than made separeate process for
        blender_version = rec[1][0][0]
        agg_avg /= len(rec[1])
        agg_med = median(mp_time_list)
        cpu_rating = sum([ 1/mp_time for mp_time in mp_time_list])
        core_num = max(rec[0][2],rec[0][3])
        core_rating = cpu_rating / core_num
        
        result_analysis.append((rec[0][0],rec[0][1],blender_version,core_num,cpu_rating,core_rating,agg_avg,agg_med,agg_min,agg_max))
    
    if out_to_console:
        print('')
        print('result analysis')
        print(f'cpu : {cpu_name}  os : {os_type:4}  blender ver :{blender_version:8}')
        for test in result_analysis:
            print(f'test_type : {test[1]:9}  mp_type : {test[0]:3}  core_num : {test[3]}  cpu_rating : {test[4]:.4f}  core_rating : {test[5]:.4f}  avg_time : {test[6]:.4f}  med_time : {test[7]:.4f}  min_time : {test[8]:.4f}  max_time : {test[9]:.4f}')
            
    if out_to_csv:
        csv_file_name = cpu_name.replace(" ", "_") + '__' + os_type + '__v' + blender_version.replace('.','_') + '__' + bench_hash + '.csv'
        with open(csv_file_dir + csv_file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile #, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL
                                    )
            # headers
            csv_writer.writerow(['cpu', 'hardware','bench_env', 'os_type', 'os_release', 'os_version', 'blender_version','bench_verion','bench_hash','test_type', 'mp_type', 'core_num', 'cpu_rating','core_rating','avg_time','med_time','min_time','max_time'] )
            for test in result_analysis:
                csv_writer.writerow([cpu_name, hardware, bench_env, os_type, os_release, os_version , blender_version ,bench_verion, bench_hash, test[1],test[0],test[3],test[4],test[5],test[6],test[7],test[8],test[9]])
        print('csv result file: ',csv_file_name)
    
