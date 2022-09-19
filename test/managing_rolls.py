from sympy import stats
import playerClass as func
import re

rolls = ["rolling 3d20\n(\n14\n)\n=50", "August 29, 2022 6:35PM\nElona Winterbreeze:rolling d6 + 4 Magic damage\n(\n1\n)+4\n=5","Miki P. (GM):rolling d20+5+d8+d10\n(\n5\n)+5+(\n1\n)+(\n8\n)\n=19"]


# Simpel index list function
def find_indexes(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


for roll in rolls:
    roll_inp, result, mean, pmf, cdf = func.ret_stats(roll)
    print(f'roll_input = {roll_inp}\nmean = {mean}\ncdf={cdf}')
    continue
    # average roll
    # cdf of given value
    roll_input = roll.split("rolling ")[-1].split("\n")[0]

    print(f'roll_input = {roll_input}')
    roll_result = int(roll.split("=")[-1])

    # Find the dice and the amount
    dice = []
    d_place = find_indexes(roll_input, 'd')
    modifiers = roll_input
    for i in d_place:
        if not roll_input[i+1].isdigit():
            continue
        amount = 1
        for n in range(1,4): # check to see if there's more than one die
            try:
                if roll_input[i-n].isdigit():
                    amount = int(roll_input[i-n:i])
            except:
                break
        for n in range(1,4):
            try:
                if roll_input[i+n].isdigit():
                    die = int(roll_input[i+1:i+n+2])
            except:
                break
        for n in range(amount):
            dice.append(stats.Die(f'Die_{i}_{n+1}', die))
        modifiers = modifiers.replace(f'd{die}+', '').replace(f'd{die}', '')

    modifiers = re.findall(r'[+\-*/] \d', modifiers).append(re.findall(r'[+\-*/]\d', modifiers))
    if modifiers != None:
        modifiers = eval(''.join(modifiers))
    else:
        modifiers = 0

    roll_result = roll_result - modifiers
    expected_value = stats.E(sum(dice))

    pmf = stats.density(sum(dice))
    # Casting the values into ints so that I can use 'em
    if len(dice) == 1:
        possible_vals = range(1,die+1)
    else:
        possible_vals = [int(k) for k in pmf.keys()]

    cdf = 0
    for n in range(possible_vals.index(roll_result)+1):
        cdf += pmf[possible_vals[n]]
    print(1-cdf)


    print(f'expected value = {expected_value}')