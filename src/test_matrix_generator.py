import pandas as pd
from matplotlib import pyplot as plt
import itertools
import numpy as np
import datetime as dt




class TestMatrix():

    def __init__(self, param_lists, ttm, column_names = None) -> None:
        self.param_lists = param_lists
        self.ttm = ttm
        self.column_names = column_names

        self.df = self.generate_TM()

        
    def generate_TM(self):
        comb = [item for item in itertools.product(*self.param_lists)]
        return pd.DataFrame(comb, columns=self.column_names)
    
    def get_changed_indices(self):
        return self.df.ne(self.df.shift()).apply(lambda x: x.index[x].tolist())
    
    def get_timestamps(self, rem_lst_add_first = True):

        intervs = []
        
        d_ind = self.get_changed_indices()
        # print(d_ind)
        mask_ref = np.full(self.ttm.size, False)

        for key in range(self.df.shape[0]):
            mask = np.copy(mask_ref)

            for i in range(len(d_ind)):

                if key in d_ind.iloc[i]: mask[i] = True
                
            if key != 0:
                intervs.append(np.max(self.ttm[mask]))
            else:
                intervs.append(self.ttm[-1])

        if rem_lst_add_first:
            intervs = intervs[:-1]
            intervs.insert(0,0)
        # print(intervs)
        time_stamps = np.cumsum(intervs)
        time_stamps= [str(dt.timedelta(seconds = int(n))) for n in time_stamps]
        # time_stamps = pd.to_datetime(time_stamps_str)
        return intervs, time_stamps

    def compile_dataset(self, rem_lst_add_first = True):
        intervs, time_stamps = self.get_timestamps(rem_lst_add_first)
        self.df['period_s'] = intervs
        self.df['timestamp_hh-mm-ss'] = time_stamps

        return self.df
            

n_factors = 5

elev_def = [-10, 0, 10, 20]
prop_config =  ["L/cw-R/cw" , "L/cw-R/ccw" , "L/ccw-R/cw"]
AoA = [-5, 0 , 5, 10]
fs_vel = [0, 20, 40]
adv_ratio = [0, 1.6, 2, 2.5]

factor_group = [elev_def,
             prop_config,
             fs_vel,
             adv_ratio,
             AoA]

base_col_names = ["elev_def",
             "prop_config",
             "fs_vel",
             "adv_ratio",
             "AoA"]

ttm_approx = np.array([300,300,10,10,10])

TM_1 = TestMatrix(factor_group,ttm_approx,base_col_names)

final_data = TM_1.compile_dataset()
final_data.to_csv("test_matrix_v1.csv",index = True)
# print(d_ind)
# print(len(d_ind))
# print(t_s)


