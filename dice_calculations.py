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
    print(roll_message.split("rolling ")[-1].split("("))
    #print(roll_input)
    roll_result = int(float(roll_message.split("=")[-1].split(" ")[0]))

    # Find the dice and the amount
    dice = []
    # Finding the index for each time the letter d is used
    d_place = find_indexes(roll_input, 'd')
    modifiers = roll_input  # Used for finding modifiers

    # Go through every d to figure out what kind of roll it is
    for i in d_place:
        # If it's not a die roll, continue
        if not roll_input[i + 1].isdigit():
            continue
        # Find the amount of dice
        amount = 1
        for n in range(1, 4):  # check to see if there's more than one die
            try:
                if roll_input[i - n].isdigit():
                    amount = int(roll_input[i - n:i])
            except:
                break
        # Find the die type
        for n in range(1, 4):
            try:
                if roll_input[i + n].isdigit():
                    die = int(roll_input[i + 1:i + n + 1])
            except:
                break
        # Save the dice into the sympy die class
        for n in range(amount):
            dice.append(die)
        # remove the found dice from the modifiers string
        modifiers = modifiers.replace(f'd{die}', '')

    # The players tend to try and break the program by writing an ungodly amount of dice
    if len(dice) >= 15:
        print("Too many dice")
        return

    # Find every case of "+ NUMBER" or "- NUMBER"
    modifiers1 = re.findall(r'[+\-*/] \d+', modifiers)
    modifiers2 = re.findall(r'[+\-*/]\d+', modifiers)

    # add the numbers together if there are any
    if len(modifiers1) != 0 or len(modifiers2) != 0:
        modifiers = eval(''.join(modifiers1)+''.join(modifiers2))
        #print(modifiers)
    else:
        modifiers = 0

    # Remove the modifier amount from the roll result
    roll_result = roll_result - modifiers

    means = ret_mean(dice)
    mean = sum(means)

    # Check if the cdf is manageable
    pos_rolls = powerList(dice)
    if pos_rolls > 8100:
        return roll_input, roll_result + modifiers, mean + modifiers, "unavailable", "unavailable"

    # Using the density and keys function I can extract all possible outcomes
    possible_vals, pmf = ret_pmf(dice)

    # Calculate the cdf by adding up all the pmfs
    res_index = np.where(possible_vals == roll_result)[0][0]
    cdf = sum(pmf[0:res_index])

    return roll_input, roll_result + modifiers, mean+modifiers, pmf[res_index], cdf


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
    outcomes = ret_outcomes(dice, len(dice), [])
    chance = Fraction(np.prod(1 / np.asarray(dice))).limit_denominator(10000)
    return outcomes[0], outcomes[1]*chance  # (possible rolls, pmf)


# Retrieving the mean of every dice
def ret_mean(dice):
    a = []
    for die in dice:
        a.append(np.mean(range(1, die+1)))
    return a


# retrieving each possible roll
def ret_outcomes(rolls, length,  out, last=0):

    for i in range(1, rolls[0] + 1):
        if length != 1:
            r = rolls[1:]
            ret_outcomes(r, length - 1, out, last=i + last)
        else:
            out.append(last + i)
    pos_outcomes = np.unique(np.asarray(out), return_counts=True)
    return pos_outcomes