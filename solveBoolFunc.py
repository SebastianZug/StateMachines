# Evaluates the coffee maschine example

# | 2_s | 100_s |  FF2  | FF1  |  FF2' | FF1' |
# |  0  |  0    |   0   |   0  |   0   |   0  |
# |  0  |  0    |   0   |   1  |   0   |   1  |
# |  0  |  0    |   1   |   0  |   1   |   0  |
# |  0  |  0    |   1   |   1  |   1   |   1  |
# |  0  |  1    |   0   |   0  |   0   |   0  |
# |  0  |  1    |   0   |   1  |   0   |   1  |
# |  0  |  1    |   1   |   0  |   1   |   1  |
# |  0  |  1    |   1   |   1  |   1   |   1  |
# |  1  |  0    |   0   |   0  |   0   |   1  |
# |  1  |  0    |   0   |   1  |   1   |   0  |
# |  1  |  0    |   1   |   0  |   1   |   0  |


from sympy.logic import SOPform
from sympy import symbols

x3, x2, x1, x0 = symbols('2s 100s FF2 FF1')

FF1_minterms = [[0, 0, 0, 1],
                [0, 0, 1, 1],
                [0, 1, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 0],]
result = SOPform([x3, x2, x1, x0], FF1_minterms)
print "FF1 = " + str(result)

FF2_minterms = [[0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 1, 0],]
result = SOPform([x3, x2, x1, x0], FF2_minterms)
print "FF2 = " + str(result)
