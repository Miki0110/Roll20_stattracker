import numpy as np
import dice_calculations as dc
from scipy.stats import binom
from fractions import Fraction
import itertools

import itertools
import fractions




# Define the number of sides on each die
num_sides_dice1 = 20
num_sides_dice2 = 20
num_sides_dice3 = 6
print(dc.calc_adv_dice([20,20], [8], 20, True))
# Generate a list of all possible outcomes of three dice rolls
outcomes = [outcome for outcome in itertools.product(range(1, num_sides_dice1 + 1), range(1, num_sides_dice2 + 1), range(1, num_sides_dice3 + 1))]

# Calculate the expected value
expected_value = sum([max(outcome[0],outcome[1]) + outcome[2] for outcome in outcomes]) / len(outcomes)
print("Expected value:", expected_value)

# Calculate the PMF
pmf = {}
for outcome in outcomes:
    sum_highest_two = max(outcome[0],outcome[1]) + outcome[2]
    if sum_highest_two not in pmf:
        pmf[sum_highest_two] = 1 / len(outcomes)
    else:
        pmf[sum_highest_two] += 1 / len(outcomes)
print("PMF:", pmf)

# Calculate the CDF
cdf = {}
cumulative_prob = 0
for outcome in sorted(pmf.keys()):
    cumulative_prob += pmf[outcome]
    cdf[outcome] = cumulative_prob
print("CDF:", cdf)

outcome = dc.calc_adv_dice(2, 20, 20, 'kh')
print(outcome[0]+3.5)

exit()
dice = [20,20]
result = -3

res = dc.calc_dice(dice, result)
print(res)
exit()


#
result = 3
# Number of dice
n = 3

#number to keep
n_keep = 1

# Number of sides on each die
sides = 20



print(outcome)


# Compute the expected value by taking the dot product of the outcomes and probabilities


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
