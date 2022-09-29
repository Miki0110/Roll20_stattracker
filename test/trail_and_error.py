import numpy as np
import dice_calculations as dc
from random import randint, choices
import time


dice = [20,20,20,20,20,20,20,20,20,20,20,20]

rmax = sum(dice)
rmin = len(dice)
res_index = range(rmin, rmax+1).index(50)

start_time = time.time()


length = 1000000
res = np.zeros(length, dtype='uint16')

for die in dice:
    #print(res)
    res = np.add(res, (choices(range(1, die+1), k=length)))
value, count = np.unique(res, return_counts=True)

prob = count/length

cdf = sum(prob[0:res_index])
print(f'new cdf = {cdf}')

elapsed_time_1 = time.time() - start_time
print(f'elapsed time calc = {elapsed_time_1}')
exit()

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


res = []
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
