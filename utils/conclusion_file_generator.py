### recreate conclusion.csv (max cpu power) (../result/conclusion.csv ) from results csv (../result/*)
import os

from pandas import read_csv
import numpy as np

src_dir = '../result/'
dst_dir = '../result/'
dst_filename = 'conclusion.csv'

dst_file_path = dst_dir + dst_filename

# remove old conclusion file
if os.path.exists(dst_file_path):
  os.remove(dst_file_path)

src_filename = os.listdir(src_dir)

  
need_header = True
for filename in src_filename:
    print(filename)
    df = read_csv(src_dir + filename)
    df.groupby(['cpu','hardware','bench_env','os_type','os_release','os_version','blender_version','bench_hash','test_type','mp_type'], as_index=False).agg(
                    max_core_num=('core_num', np.max),
                    max_cpu_rating=('cpu_rating', np.max)
                ).to_csv(dst_file_path, index=False, header=need_header, mode = 'a')
    need_header = False