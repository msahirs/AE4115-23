import pandas as pd
import itertools
import numpy as np
import datetime as dt

def partition(values, indices):
    idx = 0

    for index in indices:
        sublist = []
        while idx < len(values) and values[idx] < index:
            sublist.append(values[idx])
            idx += 1
        if sublist:
            yield sublist

class TestMatrix():

    def __init__(self, identifier, param_lists, ttm,
                 column_names = None) -> None:
        self.name = identifier
        
        self.param_lists = param_lists
        self.ttm = ttm
        self.column_names = column_names

        self.df = self.generate_TM() # Create data frame
        self.d_ind = self.get_changed_indices()
        
    def generate_TM(self): # Dataframe is a combination of values being varied
        comb = [item for item in itertools.product(*self.param_lists)]
        return pd.DataFrame(comb, columns=self.column_names)
    
    def get_changed_indices(self): # Get values being changed to get time to change variables
        # This does some wacky dataframe manipulation
        return self.df.ne(self.df.shift()).apply(lambda x: x.index[x].tolist())
    
    def cull(self,tol = 1e-3):
        
        cull_indices = []

        for i, val in self.df.iterrows(): # Remove angle of attack variation with zero fs
            if abs(val.iloc[2]) < tol and ((-tol < abs(val.iloc[-1]) - 5 < tol) or (-tol < val.iloc[-1]-10 < tol)):
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows(): #Only test one prop config for free stream variation
            if not(val.iloc[1] == "L/cw-R/cw") and (-tol < abs(val.iloc[2]) < tol) :
                cull_indices.append(i)

        # print(self.df.iloc[cull_indices])

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows(): # test zero fs and zero adv ratio for one elev deflect
            if not(-tol < val.iloc[0] + 10 < tol) and (-tol < abs(val.iloc[2]) < tol) and (-tol < abs(val.iloc[3]) < tol) :
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows(): #Only test 0 advance ratios for just one prop config
            if (-tol < val.iloc[3] < tol) and not(val.iloc[1] == "L/cw-R/cw") :
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows(): # Change all but one adv ratio of 0 to prop off
            if (-tol < val.iloc[3] < tol) and not(-tol < val.iloc[0] + 10 < tol and -tol < val.iloc[2] < tol) :
                cull_indices.append(i)
        

        self.df.loc[cull_indices, ['prop_config']] = 'OFF'
        # print(self.df)

        # Collect and concantenate "OFF" to between propellor changes per elevator deflection
        
        sort_mask = self.d_ind.iloc[0] + [self.df.shape[0]] # Add last element to close off boundary
        split_data = list(partition(cull_indices,sort_mask))
        prop_split = list(partition(self.d_ind.iloc[1],sort_mask))

        conc_net = []
        for i, values in enumerate(split_data):
            # print(prop_split[i][1])
            # print(self.df[prop_split[i][0]:prop_split[i][1]].drop(index=values))
            # print(self.df[prop_split[i][1]:sort_mask[i+1]])
            conc_net.append(self.df[prop_split[i][0]:prop_split[i][1]].drop(index=values))
            conc_net.append(self.df.iloc[values])
            conc_net.append(self.df[prop_split[i][1]:sort_mask[i+1]])
            
        self.df = pd.concat(conc_net,ignore_index=True)
        self.d_ind = self.get_changed_indices()

        # sort according to yoari's suggestion:
        b_1_sort = {"L/cw-R/cw":0 , "L/cw-R/ccw":1 , "OFF":2, "L/ccw-R/cw":3}
        b_1 = self.df[sort_mask[0]:sort_mask[1]].sort_values(by=['prop_config'], key=lambda x: x.map(b_1_sort))
        
        b_2_sort = {"L/ccw-R/cw":0,"L/cw-R/cw":1, "OFF":2,
                "L/cw-R/ccw":3}
        b_2 = self.df[sort_mask[1]:sort_mask[2]].sort_values(by=['prop_config'], key=lambda x: x.map(b_2_sort))
        b_3_sort ={"L/cw-R/ccw" :0,
                "L/cw-R/cw":1 ,
                "L/ccw-R/cw":2, "OFF":3}
        b_3 = self.df[sort_mask[2]:sort_mask[3]].sort_values(by=['prop_config'], key=lambda x: x.map(b_3_sort))
        
        self.df = pd.concat([b_1,b_2,b_3],ignore_index=True)
        self.d_ind = self.get_changed_indices()
        

    def get_timestamps(self): # Evaluate intervals and timestamps

        intervs = []
        
        # print(d_ind)
        mask_ref = np.full(self.ttm.size, False) # comparison class

        for key in range(self.df.shape[0]):
            mask = np.copy(mask_ref)

            for i in range(len(self.d_ind)):

                if key in self.d_ind.iloc[i]: mask[i] = True # Made in a modular way for future changes
                
            if key != 0:
                intervs.append(np.max(self.ttm[mask]))

            else: # Used as technically all variables change at the first row
                intervs.append(self.ttm[-1]) # So we default to last value in ttm
 
        time_stamps = np.cumsum(intervs) - self.ttm[-1] # accumlate values and remove bias term being ttm[-1]
        
        time_stamps = [str(dt.timedelta(seconds = int(n))) for n in time_stamps]
        
        return intervs, time_stamps

    def compile_dataset(self):
        intervs, time_stamps = self.get_timestamps()
        self.df['period_s'] = intervs
        self.df['timestamp_hh-mm-ss'] = time_stamps
        self.df['adv_ratio'] = self.df['adv_ratio'].astype(str) + " ("+ self.get_rps_from_J_fs().map('{:,.1f}'.format) + ") "

        # print(self.get_rps_from_J_fs())
        return self.df
    

    def get_rps_from_J_fs(self, prop_len = 0.2032):
        return (self.df["fs_vel"]/(self.df["adv_ratio"] * prop_len)).replace([np.inf,np.nan],0)
            
n_factors = 5 # Not used just for keepsake

elev_def = [-10., 0., 10.] # Elevator Deflection in deg
# elev_def = [-10., 0., 10.] # Elevator Deflection in deg

prop_config =  ["L/cw-R/cw" ,
                "L/cw-R/ccw" ,
                "L/ccw-R/cw", "OFF"] # Propellor orientation combos

# AoA = [-5., 0. , 5.] # Angle of Attack in deg
AoA = [-5., 0. , 5.,] # Angle of Attack in deg

fs_vel = [0., 20., 40.] # Freestream Velocity in m/s

adv_ratio = [0, 1.6, 2.5] # Yoari suggestion
# adv_ratio = [0, 1.6, 2, 2.5] # Advance Ratio

factor_group = [elev_def,
             prop_config,
             fs_vel,
             adv_ratio,
             AoA] # Order defines order of change in combinations produces

base_col_names = ["elev_def",
             "prop_config",
             "fs_vel",
             "adv_ratio",
             "AoA"] # Used for csv/dataframe headers

ttm_approx = np.array([600,600,15,15,15])

identifier = "test_matrix_bad"
TM_1 = TestMatrix(identifier,factor_group,ttm_approx,base_col_names)

# TM_1.cull()


# raise "error"

final_data = TM_1.compile_dataset()
final_data.to_csv(f"{TM_1.name}.csv",index = True)

with open(f"{TM_1.name}_table.txt", 'w') as file:
    file.write(final_data.to_latex(index=True,
                    formatters={"name": str.upper},
                    float_format="{:.1f}".format,
    ))



