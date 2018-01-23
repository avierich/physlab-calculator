import pandas as pd
from sympy import *


def structure_line(equation_string):
    expression = sympify(equation_string)
    error_expression = ''
    for variable in expression.free_symbols:
        error_expression = error_expression + ' + \\left(\\frac{\\partial \\left(' + latex(expression) + '\\right) }{\\partial ' + latex(variable) + '}\\right)^2 \\sigma_{' + latex(variable) + '}^2'

    # Hackily get rid of first plus sign
    error_expression = error_expression[2:]
    return '\\left( ' + error_expression + '\\right)^{\\frac{1}{2}}'


def error_equation(equation_string):
    expression = sympify(equation_string)
    error_expression = 0
    for variable in expression.free_symbols:
        error_expression = error_expression + diff(expression, variable)**2*sympify('sigma_'+str(variable))**2

    return error_expression**(1/2)

# Inputs : a sympy expression, a csv, and which row of that csv to act on
def sub_values(expression, csv, row):
    latex_expression = latex(expression)
    for variable in expression.free_symbols:
        latex_expression = str.replace(latex_expression, ' '+latex(variable), '\\left(\\SI{' + str(csv.iloc[row][str(variable)]) + '}{' + str(csv.iloc[0][str(variable)]) + '}\\right)')

    return latex_expression

# Inputs : a sympy expression, a csv, and which row of that csv to act on
def evaluate_equation(expression, csv, row):
    for variable in expression.free_symbols:
        expression = expression.subs(variable, csv.iloc[row][str(variable)])

    return expression

def gen_error_example(quantity, equation_string):
    return '\\begin{align} \\sigma_{' + latex(sympify(quantity)) + '}&=' +  structure_line(equation_string) + '\\\\\\sigma_{' + latex(sympify(quantity)) + '}&=' + latex(error_equation(equation_string)) + '\\end{align}'


if __name__ == '__main__':
    test = pd.read_csv('main_test.csv')

    # The equation string from the csv
    equation = test.iloc[1]['Equation']

    # Everything before the equals sign
    quantity = equation[:equation.find('=')]

    # Everything after the equals sign
    formula = equation[equation.find('=')+1:]


    formula_text = '\\begin{align} ' + latex(sympify(quantity)) +\
        '&=' + latex(sympify(formula)) + '\\\\ '+\
        '&=' + sub_values(sympify(formula), test, 1) + '\\\\'+\
        '&= \\SI{' + latex(evaluate_equation(sympify(formula), test, 1).evalf()) + '}{' + test.iloc[0]['Equation'] + '}\\end{align}'

    error_text = '\\begin{align} \\sigma_{' + latex(sympify(quantity)) + '}'+\
        '&=' + structure_line(formula) + '\\\\ '+\
        '&=' + latex(error_equation(formula)) + '\\\\ '+\
        '&=' + sub_values(error_equation(formula), test, 1) + '\\\\'+\
        '&= \\SI{' + latex(evaluate_equation(error_equation(formula), test, 1).evalf()) + '}{' + test.iloc[0]['Equation'] + '}\\end{align}'

    print(formula_text)
    print(error_text)


