
from sys import platform

from time import time
from multiprocessing.connection import Listener, Client

IPC_base_port = 6000

IPC_addr_worker_ready   = ('localhost', IPC_base_port)
IPC_addr_worker_result  = ('localhost', IPC_base_port + 1)

# os detection
if platform == "linux" or platform == "linux2":
    os_type = 'lnx'
elif platform == "darwin":
    os_type = 'mac'
elif platform == "win32":
    os_type = 'win'



if  __name__ != '__main__':
    import os
    import subprocess
    
    # worker config

    if os_type == 'win':
        blender_path = 'C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender'
        # blender_path = 'C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender'
        
    elif os_type == 'lnx':
        blender_path = '/snap//blender/4300/4.0/'
        
    elif os_type == 'mac':
        blender_path = './Blender.app/Contents/MacOS/Blender'
        
    else:
        blender_path = './blender'

if __name__ == '__main__':

    # from os import cpu_count
    from psutil import cpu_count
    import os
    import sys
    
    
    from time import sleep
    from multiprocessing.pool import Pool
    from uuid import uuid4
    import csv
    
    from statistics import median
    from cpuinfo import get_cpu_info
    
    cpu_name = get_cpu_info()['brand_raw']
    
    


    
    ############################
    ### config start###
    
    ### mp config
    # multiprocessing scalibility test
    # there 2 mp_type: 'mp' and 'th'
    # 'mp' - multiprocessing, separate app instance for every cpu core with one core for each
    # 'th' - multithreading, one app instance with configured core num 
    #  There no middle setting test possibility, like 2 instance with 2 thread each. Think no case for that
    
    # number of worker - only for 'mp' test
    mp_min      = 1
    mp_max = 'auto' # 'auto' - Automatic os detect, incl hyper-threading
    # mp_max = 1
    # multiplier for overcore bench, for example 2 mean 24 threads for 12 logical cores. Experimental, mostly for incorrect logical cpu num detection 
    mp_factor   = 1    
    
    # threads per worker - only for 'thread' test
    tn_min      = 1         # recommended for mp test, but for 
    # 'auto' - Automatic os detect, incl hyper-threading. But tn_max limited by 8, because scalability for more then 4 core is not effective
    tn_max_limit = 8
    tn_max    = 'auto'     
    # tn_max      = 1
    # multiplier for overcore bench, for example 2 mean 24 threads for 12 logical cores. Experimental, mostly for incorrect logical cpu num detection 
    tn_factor   = 1 
    

    
    # mp_type used in bench
    # 'mp' - for workers(num of blender instances, every with 1 core, 
    # 'thread' - one instance of blender, but starts with different num of cpu. 
    mp_type_list = [
                'mp',
                'th'
                ]
                
    # test type, each have separate scene python file
    test_type_list = [
                'movement', 
                'collision'
                ]

    out_to_console  = True
    out_to_csv      = True
    csv_file_dir   = './result/'

    is_gui_debug    = False # True - running with gui, false - without

    ### config end
    ############################

def start_worker(*args):

    ### start blender separate instance, without GUI(default), with scene py file. Exit when instance exit

    test_type  = args[0]
    t_num       = args[1]
    p_num       = args[2]
    gui_arg     = args[3]
    
    # name of start script here
    blender_args = gui_arg + ' -t ' + str(t_num) + ' -P "./scene_' + test_type + '.py"' + ' -- -pn ' + str(p_num) 
    cmd = '\"\"' + blender_path +'\" ' + blender_args +'\"'
    # print(cmd)
    os.system(cmd)

    return None


if __name__ == '__main__':

    ### init params ###
    
    if mp_max == 'auto':
        mp_max = cpu_count() * mp_factor

    if tn_max == 'auto':
        tn_max = min(cpu_count() * tn_factor, tn_max_limit)

    if not is_gui_debug:
        gui_arg = '-b'
    else:
        gui_arg = ''
        
    i_bench = 1
    
    pool = Pool(processes=mp_max)
    
    # progress in console
    bench_num = len(test_type_list) *  ( (mp_max - mp_min + 1 if 'mp' in mp_type_list else 1) + (tn_max - tn_min + 1 if 'th' in mp_type_list else 1) )
    
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

    # analisys
    result_analisys = []
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
            
        # yep to dirty to get blender version from every run, but it simple, that made separeate process for
        blender_version = rec[1][0][0]
        agg_avg /= len(rec[1])
        agg_med = median(mp_time_list)
        cpu_rating = sum([ 1/mp_time for mp_time in mp_time_list])
        core_num = max(rec[0][2],rec[0][3])
        core_rating = cpu_rating / core_num
        
        result_analisys.append((rec[0][0],rec[0][1],blender_version,core_num,cpu_rating,core_rating,agg_avg,agg_med,agg_min,agg_max))
    
    if out_to_console:
        print('')
        print('result analisys')
        print(f'cpu : {cpu_name}  os : {os_type:4}  blender ver :{blender_version:8}')
        for test in result_analisys:
            print(f'test_type : {test[1]:9}  mp_type : {test[0]:3}  core_num : {test[3]}  cpu_rating : {test[4]:.4f}  core_rating : {test[5]:.4f}  avg_time : {test[6]:.4f}  med_time : {test[7]:.4f}  min_time : {test[8]:.4f}  max_time : {test[9]:.4f}')
            
    if out_to_csv:
        # additional unique mark for result files
        bench_hash = uuid4().hex[0:8]
        # raw
        csv_file_name = cpu_name.replace(" ", "_") + '__' + os_type + '__v' + blender_version.replace('.','_') + '__' + bench_hash + '.csv'
        with open(csv_file_dir + csv_file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile #, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL
                                    )
            # headers
            csv_writer.writerow(['cpu','os','blender_version','test_type','mp_type','core_num','cpu_rating','core_rating','avg_time','med_time','min_time','max_time'] )
            for test in result_analisys:
                csv_writer.writerow([cpu_name, os_type, blender_version, test[1][0:4],test[0],test[3],test[4],test[5],test[6],test[7],test[8],test[9]])