import pandas as pd
from sympy import *
import uncertainties


def alex_lazy_format(value, sigma_value):
    #return '$' + {:eL}'.format(uncertainties.ufloat(float(value), float(sigma_value))) + '$'
    if float(sigma_value) > 0 :
        correct_digs = str(uncertainties.ufloat(float(value), float(sigma_value))).replace('(', '').replace(')','').split('+/-')
        return '\SI{' + correct_digs[0] + ' \pm ' + correct_digs[1] + ' }{}'
    else :
        return '\SI{' + str(value) + '}{}'

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
    # Also makes sure it converts the strings to latex form for replacement,
    # e.g latexify will turn theta into \theta

    latex_expression = latex(expression)

    # replace sigma values first to make sure we dont replace their subscripts
    variables = sorted(expression.free_symbols, key=lambda thing: 'sigma_' not in str(thing))
    for variable in variables:
        latex_expression = str.replace(latex_expression, ' '+latex(variable), ' \\left(\\SI{' + str(csv.iloc[row][str(variable)]) + '}{' + str(csv.iloc[0][str(variable)]).replace('nan','') + '}\\right)')
        latex_expression = str.replace(latex_expression, '('+latex(variable), '(\\left(\\SI{' + str(csv.iloc[row][str(variable)]) + '}{' + str(csv.iloc[0][str(variable)]).replace('nan','') + '}\\right)')
        latex_expression = str.replace(latex_expression, '{'+latex(variable), '{\\left(\\SI{' + str(csv.iloc[row][str(variable)]) + '}{' + str(csv.iloc[0][str(variable)]).replace('nan','') + '}\\right)')

    return latex_expression


# Inputs : a sympy expression, a csv, and which row of that csv to act on
# Returns? A sympy expression I believe.
def evaluate_equation(expression, csv, row):
    for variable in expression.free_symbols:
        expression = expression.subs(variable, csv.iloc[row][str(variable)])

    return expression


def gen_error_example(quantity, equation_string):
    return '\\begin{align} \\sigma_{' + latex(sympify(quantity)) + '}&=' +  structure_line(equation_string) + '\\\\\\sigma_{' + latex(sympify(quantity)) + '}&=' + latex(error_equation(equation_string)) + '\\end{align}'


def table_header(expresion, quantity, csv) :
    # Make the headers
    row_text = latex(sympify(quantity)) + ' (\\SI{}{' + csv.iloc[0]['Equation'] + '})'
    for variable in expresion.free_symbols :
        row_text = row_text + '&' + latex(variable) + ' (\\SI{}{' + str(csv.iloc[0][str(variable)]).replace('nan','') + '})'

    return row_text + '\\\\'


def table_row(expresion, value, sigma_value, csv, row):
    # Make the headers
    row_text = alex_lazy_format(value,sigma_value)
    for variable in expresion.free_symbols:
        row_text += '&' + alex_lazy_format(csv.iloc[row][str(variable)], csv.iloc[row]['sigma_'+str(variable)])

    return row_text + '\\\\'

def make_table(expression, error_expression, quantity, csv):
    column_string = ''
    for i in range(0, len(expression.free_symbols)+1):
        column_string += 'l'

    table_string = '\\begin{tabular}{' + column_string + '}' + table_header(expression, quantity, csv)

    result = 31415926 # Placeholder? super hacky, shame on me.
    i = 1
    while N(result) != nan:
        result = evaluate_equation(expression, csv, i)
        sigma_result = evaluate_equation(error_expression, csv, i)
        if result != nan:
            table_string += table_row(expression, result.evalf(), sigma_result.evalf(),  csv, i)
        i += 1

    return table_string + '\\end{tabular}'


if __name__ == '__main__':
    test = pd.read_csv('lauethero.csv')

    # The equation string from the csv
    equation = test.iloc[1]['Equation']

    # Everything before the equals sign
    quantity = equation[:equation.find('=')]

    # Everything after the equals sign
    formula = equation[equation.find('=')+1:]


    formula_text = '\\begin{align} ' + latex(sympify(quantity)) +\
        '&=' + latex(sympify(formula)) + '\\\\ '+\
        '&=' + sub_values(sympify(formula), test, 1) + '\\\\'+\
        '&= \\SI{' + str(evaluate_equation(sympify(formula), test, 1).evalf()) + '}{' + test.iloc[0]['Equation'] + '}\\end{align}'

    error_text = '\\begin{align} \\sigma_{' + latex(sympify(quantity)) + '}'+\
        '&=' + structure_line(formula) + '\\\\ '+\
        '&=' + latex(error_equation(formula)) + '\\\\ '+\
        '&=' + sub_values(error_equation(formula), test, 1) + '\\\\'+\
        '&= \\SI{' + str(evaluate_equation(error_equation(formula), test, 1).evalf()) + '}{' + test.iloc[0]['Equation'] + '}\\end{align}'


    table_text = make_table(sympify(formula), error_equation(formula), quantity, test)

    # Replacements, theres going to need to be a lot more of these in the future
    replacements = {'lamb':'\lambda', '\operatorname{asin}':'\\arcsin', '\operatorname{acos}':'\\arccos', '\operatorname{atan}':'\\arctan'}

    for key in replacements.keys():
        formula_text = formula_text.replace(key, replacements[key])
        error_text = error_text.replace(key, replacements[key])
        table_text = table_text.replace(key, replacements[key])

    print(formula_text)
    print(error_text)
    print(table_text)


