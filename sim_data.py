import numpy as np
import time

def sim_data():

    sim_nums = np.random.normal(loc=0, scale=3, size=3)
    scaled_nums = sim_nums * (10/5)
    return scaled_nums



