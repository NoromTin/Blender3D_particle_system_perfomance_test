### recreate conclusion.csv (max cpu power) (../result/conclusion.csv ) from results csv (../result/*)
import os

from pandas import read_csv, merge
import numpy as np

src_dir = '../result/'
dst_dir = '../'
dst_filename = 'result_consolidated.csv'

dst_file_path = dst_dir + dst_filename

# remove old conclusion file
if os.path.exists(dst_file_path):
  os.remove(dst_file_path)

src_filename = os.listdir(src_dir)

group_by_field  = ['cpu', 'platform','platform_core_num', 'bench_env', 'os_type', 'os_release', 'os_version', 'blender_version','bench_version','bench_max_core_num','bench_hash','test_type', 'mp_type']
join_key       = group_by_field.copy()
join_key.append('cpu_rating')
join_field     = join_key.copy()
join_field.append('core_num')
need_header = True
for filename in src_filename:
    print(filename)
    df_src = read_csv(src_dir + filename)
    df_agregated = df_src.groupby( group_by_field
                    , as_index=False
                    ).agg( 
                        cpu_rating=('cpu_rating', np.max)    
                        )

    result = merge(df_agregated, df_src[join_field], how="left", on=join_key
                    ).rename(columns={'core_num': 'max_cpu_rating_core_num','cpu_rating': 'max_cpu_rating'}
                    ).to_csv(dst_file_path, index=False, header=need_header, mode = 'a')
    need_header = False
    
print('')
print(dst_filename)
