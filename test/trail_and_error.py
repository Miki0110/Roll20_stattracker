import numpy as np
import dice_calculations as dc
from random import randint
import time

start_time = time.time()

dice = [6,6,6,6,6,6,6,6,6]

# Retrieve mean
# means = dc.ret_mean(dice)
# mean = sum(means)
#
# # Using the density and keys function I can extract all possible outcomes
# possible_vals, pmf = dc.ret_pmf(dice)
#
# # Calculate the cdf by adding up all the pmfs
# res_index = np.where(possible_vals == 15)[0][0]
# cdf = sum(pmf[0:res_index])
#
# print(f'calculated dice:\nMean={mean}\nCDF = {float(cdf)}')
elapsed_time_1 = time.time() - start_time

start_time = time.time()

rmax = sum(dice)
rmin = len(dice)
res_index = range(rmin, rmax+1).index(10)

res = []
length = 500000
for i in range(length):
    rd = []
    for die in dice:
        rd.append(randint(1, die))
    res.append(sum(rd))
value, count = np.unique(np.asarray(res), return_counts=True)

prob = count/length

cdf = sum(prob[0:res_index])
print(f'new cdf = {cdf}')

elapsed_time_2 = time.time() - start_time

print(f'elapsed time calc = {elapsed_time_1}\nelapsed time trail = {elapsed_time_2}')
