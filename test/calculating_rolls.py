import numpy as np
import dice_calculations as dc
from scipy.stats import binom
from fractions import Fraction

dice = [20,-4]
result = 13

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


def calc_adv_dice(amount_of_dice, die, roll_result, option):
    # Check if the cdf is manageable
    if amount_of_dice > 50:
        print('too many dice')
        return -1

    # Using the density and keys function I can extract all possible outcomes
    if option == "kh1" or option == 'dl1':
        possible_vals, pmf = dc.ret_pmf_HL_die(die, amount_of_dice, True)
    else:
        possible_vals, pmf = dc.ret_pmf_HL_die(die, amount_of_dice, False)

    mean = np.dot(possible_vals, pmf)

    # Find the possible values and the calculate the CDF and inv-CDF
    res_index = np.where(possible_vals == roll_result)[0][0]
    cdf = sum(pmf[0:res_index + 1])
    inv_cdf = 1 - sum(pmf[0:res_index])
    return mean, pmf[res_index], cdf, inv_cdf

outcome = calc_adv_dice([6,6,6], 3, 'kl1')
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
