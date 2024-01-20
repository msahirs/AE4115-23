import pandas as pd
import itertools
import numpy as np
import datetime as dt

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
    
    def cull_0fs(self,tol = 1e-4):
        
        cull_indices = []

        
        for i, val in self.df.iterrows():
            if abs(val.iloc[2]) < tol and ((-tol < abs(val.iloc[-1]) - 5 < tol) or (-tol < val.iloc[-1]-10 < tol)):
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows():
            if not(val.iloc[1] == "L/cw-R/cw") and (-tol < abs(val.iloc[2]) < tol) :
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows():
            if not(-tol < val.iloc[0] + 10 < tol) and (-tol < abs(val.iloc[2]) < tol) and (-tol < abs(val.iloc[3]) < tol) :
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        cull_indices = []

        for i, val in self.df.iterrows():
            if (-tol < val.iloc[3] < tol) and not(val.iloc[1] == "L/cw-R/cw") :
                cull_indices.append(i)

        self.df = self.df.drop(index=cull_indices).reset_index(drop=True)
        self.d_ind = self.get_changed_indices()

        print(self.df)

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

        return self.df
            
n_factors = 5 # Not used just for keepsake

elev_def = [-10., 0., 10.] # Elevator Deflection in deg
# elev_def = [-10., 0., 10.] # Elevator Deflection in deg

prop_config =  ["L/cw-R/cw" ,
                "L/cw-R/ccw" ,
                "L/ccw-R/cw"] # Propellor orientation combos

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

ttm_approx = np.array([600,600,10,10,10])

identifier = "test_matrix_v1"
TM_1 = TestMatrix(identifier,factor_group,ttm_approx,base_col_names)

TM_1.cull_0fs()


# raise "error"

final_data = TM_1.compile_dataset()
final_data.to_csv(f"{TM_1.name}.csv",index = True)

with open(f"{TM_1.name}_table.txt", 'w') as file:
    file.write(final_data.to_latex(index=False,
                    formatters={"name": str.upper},
                    float_format="{:.1f}".format,
    ))



