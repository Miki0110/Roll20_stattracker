import numpy as np
from fractions import Fraction

# Simpel index list function
def find_indexes(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# function for retrieving the dice rolls
def ret_rolls(roll_message):
    import re
    # Using the structure of the string to extract the rolled dice and result of rolling
    roll_input = roll_message.split("rolling ")[-1].split("(")[0]
    roll_result = int(float(roll_message.split("=")[-1].split(" ")[0]))
    print(roll_message)

    # Find the dice and the amount
    dice = []
    # Finding the rolls through the setup [amount]d[die][options]
    rolls = re.finditer(r'(-)?(\d*)?d(\d+)(\w*)', roll_input)

    modifiers = roll_input  # Used for finding modifiers

    # Go through every d to figure out what kind of roll it is
    for roll in rolls:
        # Collect the data retrieved
        full_roll = roll.group(0)
        amount = int(roll.group(2)) if roll.group(2) != '' else 1
        if roll.group(1) is None:
            die = int(roll.group(3))
        else:
            die = int(roll.group(1)+roll.group(3))
        option = roll.group(4)

        # Just in case someone rolls with zeros
        if die == 0 or amount == 0:
            print('zero is not manageable')
            continue

        if option != '':
            # Since we cannot look directly at the output for the result of adv dice
            in_between = roll_message.replace(full_roll, "").split("=")[0]
            roll_results = re.findall(r'\d+', in_between)
            result = max(map(int, roll_results))
            mean, pmf, cdf, inv_cdf = calc_adv_dice(amount, die, result, option)
            # Until I figure out how to save the statistics of an advantage roll this stays
            amount = 1

        # Save the dice into the array
        for n in range(amount):
            dice.append(die)
        # remove the found dice from the modifiers string
        modifiers = modifiers.replace(f'{full_roll}', '')

    if len(dice) == 0:
        return -1
    # Find every case of "+ NUMBER" or "- NUMBER"
    modifiers1 = re.findall(r'[+\-*/] \d+', modifiers)
    modifiers2 = re.findall(r'[+\-*/]\d+', modifiers)

    # add the numbers together if there are any
    if len(modifiers1) != 0 or len(modifiers2) != 0:
        modifiers = eval(''.join(modifiers1)+''.join(modifiers2))
    else:
        modifiers = 0

    # Remove the modifier amount from the roll result
    roll_result = roll_result - modifiers

    # Rewrite the input so that it can be cleaned and reprinted
    roll_input = ''
    d, c = np.unique(np.asarray(dice), return_counts=True)
    for i in range(len(d)):
        roll_input = roll_input+f'{c[i]}d{d[i]}+'
    roll_input = roll_input+f'{modifiers}'

    print(dice)
    calcs = calc_dice(dice, roll_result)
    if calcs == -1:
        return -1
    else:
        return roll_input, roll_result + modifiers, calcs[0]+modifiers, calcs[1], calcs[2], calcs[3]


def calc_dice(dice, roll_result):
    # Retrieve mean
    means = ret_mean(dice)
    mean = sum(means)

    # Check if the cdf is manageable
    if len(dice) > 50:
        print('too many dice')
        return -1

    pos_rolls = powerList(dice)
    if pos_rolls > 50000:
        pmf, cdf, inv_cdf = trail_and_error(dice, roll_result)
        return mean, pmf, cdf, inv_cdf

    # Using the density and keys function I can extract all possible outcomes
    possible_vals, pmf = ret_pmf(dice)

    # Calculate the cdf by adding up all the pmfs
    res_index = np.where(possible_vals == roll_result)[0][0]
    cdf = sum(pmf[0:res_index+1])
    inv_cdf = 1-sum(pmf[0:res_index])
    return mean, pmf[res_index], cdf, inv_cdf


def calc_adv_dice(amount_of_dice, die, roll_result, option):
    # Check if the cdf is manageable
    if amount_of_dice > 50:
        print('too many dice')
        return -1

    # Using the density and keys function I can extract all possible outcomes
    if option == "kh1" or option == 'dl1' or option == "kh":
        possible_vals, pmf = ret_pmf_HL_die(die, amount_of_dice, True)
    else:
        possible_vals, pmf = ret_pmf_HL_die(die, amount_of_dice, False)
    # Expected value
    mean = np.dot(possible_vals, pmf)

    # Find the possible values and the calculate the CDF and inv-CDF
    res_index = np.where(possible_vals == roll_result)[0][0]
    cdf = sum(pmf[0:res_index + 1])
    inv_cdf = 1 - sum(pmf[0:res_index])
    return mean, pmf[res_index], cdf, inv_cdf


# Function used to figure out how hard it is to calculate
def powerList(myList):
    try:
        if len(myList) <= 1:
            return myList[0]
        # Take the power of elements one by one
        result = myList[0] ** (sum(myList[1:])/myList[0]+1)
        return result
    except:
        return 0


# Retrieve the pmf
def ret_pmf(dice):
    print(dice)
    outcomes = ret_outcomes(dice)
    dice = np.abs(dice)
    chance = Fraction(np.prod(1 / dice)).limit_denominator(1000000)
    return outcomes[0], outcomes[1]*chance  # (possible rolls, pmf)


# Retrieving the mean of every dice
def ret_mean(dice):
    a = []
    for die in dice:
        if die > 0:
            a.append(np.mean(range(1, die+1)))
        else:
            a.append(np.mean(range(die, 0)))
    return a


# retrieving each possible roll
def ret_outcomes(rolls):
    import itertools

    dice = [range(1,roll+1) if roll > 0 else range(roll, 0) for roll in rolls]
    out = [sum(x) for x in itertools.product(*dice)]

    pos_outcomes = np.unique(np.asarray(out), return_counts=True)
    return pos_outcomes


# This is a way to estimate results of many dice rolls
def trail_and_error(dice, result):
    from random import choices

    length = 1000000  # Reasons for this number is simply that around 1-10 seconds used on calculations is manageable

    res = np.zeros(length, dtype='uint16')  # Numpy array for summarizing the results
    for die in dice:
        res = np.add(res, (choices(range(1, die + 1), k=length)))
    value, count = np.unique(np.asarray(res), return_counts=True)

    res_index, = np.where(value == result)[0]

    prob = count / length
    cdf = sum(prob[0:res_index+1])
    inv_cdf = 1-sum(prob[0:res_index])
    return prob[res_index], cdf, inv_cdf


# Function for retrieving the PMF of a keep highest or keep lowest roll
def ret_pmf_HL_die(num_sides, num_dice, keep_highest):
    outcomes = np.random.randint(1, num_sides+1, size=(num_dice, 1000000))
    if keep_highest:
        max_outcome = np.amax(outcomes, axis=0)
    else:
        max_outcome = np.amin(outcomes, axis=0)
    unique, counts = np.unique(max_outcome, return_counts=True)
    pmf = counts/len(max_outcome)
    return unique, pmf
