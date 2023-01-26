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

    # Find the dice and the amount
    dice = []
    adv_dice = []  # [amount,dice,option]

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

        if option == '':
            # Save the dice into the array
            for n in range(amount):
                dice.append(die)
        else:
            adv_dice.append(amount)
            adv_dice.append(die)
            option_match = re.match(r'([a-z]+)([0-9]+)', option)
            if option_match.group(1) == "k" or option_match.group(1) == "kh" or option_match.group(1) == "dl":
                adv_dice.append(True)
            else:
                adv_dice.append(False)

        # remove the found dice from the modifiers string
        modifiers = modifiers.replace(f'{full_roll}', '')

    # In case there were no rolls in the message
    if len(dice) == 0 and len(adv_dice) == 0:
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

    # Calculate the statistical values for the rolls
    if len(adv_dice) == 0:  # In case it's a normal roll
        calcs = calc_dice(dice, roll_result)
    elif len(adv_dice) < 4:  # In case it's an advantage roll
        # Create an array of dice to keep
        keep_dice = [adv_dice[1] for _ in range(adv_dice[0])]
        calcs = calc_adv_dice(keep_dice, dice, roll_result, adv_dice[2])
        # The advantage roll also has to be put into the roll_input
        if adv_dice[2]:
            roll_input = f'{adv_dice[0]}d{adv_dice[1]}k1+'+roll_input
        else:
            roll_input = f'{adv_dice[0]}d{adv_dice[1]}d1+' + roll_input
    else:
        print("Cannot yet compute more than 1 advantage roll at a time")
        calcs = -1

    if calcs == -1:
        return -1
    else:
        return roll_input, roll_result + modifiers, calcs[0]+modifiers, calcs[1], calcs[2], calcs[3]


# Function for calculating the PMF and CDF of normal rolls
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

    # Calculate the cdf by adding up all the PMFs
    res_index = np.where(possible_vals == roll_result)[0][0]
    cdf = sum(pmf[0:res_index+1])
    inv_cdf = 1-sum(pmf[0:res_index])
    return mean, pmf[res_index], cdf, inv_cdf


# Function for calculating the PMF and CDF for advantage rolls
def calc_adv_dice(dice_to_keep, dice_to_roll, result, keep_highest):
    import itertools
    import fractions

    # Check if the cdf is manageable
    if len(dice_to_keep + dice_to_roll) > 50:
        print('too many dice')
        return -1

    pos_rolls = powerList(dice_to_keep + dice_to_roll)
    if pos_rolls > 150000:
        print('too many dice')
        return -1

    # Generate a list of ranges from the dice rolls
    dice_to_keep = [range(1, dice_to_keep[i] + 1) for i in range(len(dice_to_keep))]
    dice_to_roll = [range(1, dice_to_roll[i] + 1) for i in range(len(dice_to_roll))]

    # Generate a list of all possible outcomes of three dice rolls
    outcomes = [outcome for outcome in itertools.product(*dice_to_keep, *dice_to_roll)]

    if keep_highest:
        # Calculate the expected value, by taking the max value of keep dice, and the sum of dice to roll
        expected_value = sum(
            [max(outcome[0:len(dice_to_keep)]) + sum(outcome[len(dice_to_keep):]) for outcome in outcomes]) / len(
            outcomes)
    else:
        # Calculate the expected value, by taking the min value of keep dice, and the sum of dice to roll
        expected_value = sum(
            [min(outcome[0:len(dice_to_keep)]) + sum(outcome[len(dice_to_keep):]) for outcome in outcomes]) / len(
            outcomes)

    # Calculate the PMF
    pmf_table = {}
    for outcome in outcomes:
        # Find the sum of the options
        if keep_highest:
            sum_dice = max(outcome[0:len(dice_to_keep)]) + sum(outcome[len(dice_to_keep):])
        else:
            sum_dice = min(outcome[0:len(dice_to_keep)]) + sum(outcome[len(dice_to_keep):])
        # Figure out how many times the outcome occurs, and then get the fraction of that
        if sum_dice not in pmf_table:
            # If it's the first time we see the value we set the chance to the lowest 1/(possible outcomes)
            pmf_table[sum_dice] = fractions.Fraction(1 / len(outcomes)).limit_denominator(1000000)
        else:
            # If the dice already exists we add the chances together
            pmf_table[sum_dice] += fractions.Fraction(1 / len(outcomes)).limit_denominator(1000000)

    # Calculate the CDF
    cdf_table = {}
    cumulative_prob = 0
    for outcome in sorted(pmf_table.keys()):  # We simply add the PMFs together
        cumulative_prob += pmf_table[outcome]
        cdf_table[outcome] = cumulative_prob

    inv_cdf = {}
    cumulative_prob = 0
    for outcome in sorted(pmf_table.keys(), reverse=True):  # By doing the reverse I get the inverse CDF
        cumulative_prob += pmf_table[outcome]
        inv_cdf[outcome] = cumulative_prob

    # Return everything according to the results
    return expected_value, pmf_table[result], cdf_table[result], inv_cdf[result]


# Function used to figure out how hard it is to calculate
def powerList(myList):
    try:
        if len(myList) <= 1:
            return myList[0]
        # Take the power of elements one by one
        result = myList[0] ** (sum(myList[1:])/myList[0]+1)
        return result
    except Exception as e:
        print(e)
        print("cannot calculate the power of zero values")
        return 0


# Retrieve the pmf
def ret_pmf(dice):
    outcomes = ret_outcomes(dice)
    dice = np.abs(dice)
    # Using the fraction library, since this is usually more descriptive than floating numbers
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

    dice = [range(1, roll+1) if roll > 0 else range(roll, 0) for roll in rolls]
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
