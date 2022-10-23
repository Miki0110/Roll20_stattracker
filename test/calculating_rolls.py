import numpy as np
import dice_calculations as dc
from fractions import Fraction
dice = [20]

means = dc.ret_mean(dice)
mean = sum(means)

# Using the density and keys function I can extract all possible outcomes
possible_vals, pmf = dc.ret_pmf(dice)

# Calculate the cdf by adding up all the pmfs
res_index = np.where(possible_vals == 1)[0][0]
cdf = sum(pmf[0:res_index+1])
print(cdf)
print(mean)


# for roll in rolls:
#     def go_through(rolls, length, last=0, out=[]):
#         for i in range(1, rolls[0] + 1):
#             if length != 1:
#                 r = rolls[1:]
#                 go_through(r, length - 1, last=i + last, out = out)
#             else:
#                 out.append(last + i)
#         return np.unique(np.asarray(out), return_counts=True)
#
#     # Retrieving the mean of every dice
#     def ret_mean(dice):
#         a = []
#         for die in dice:
#             a.append(np.mean(range(1, die+1)))
#         return a
#
#
#     length = len(roll)
#
#     print(ret_mean(roll))
#
#     outcomes = go_through(roll, length)
#     chance = Fraction(np.prod(1/np.asarray(roll))).limit_denominator(10000)
#     print(chance)
#
#     chances = outcomes[1]*chance
#     outcomes = outcomes[0]
#
#     print(outcomes, chances)
#
#     cdf = sum(chances[0:np.where(outcomes == 12)[0][0]])
#
#     print(cdf)
