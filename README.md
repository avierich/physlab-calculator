# physlab-calculator

This script is meant to accept a .csv containing an equation, and experimentally obtained values for each variable in the equation.

The script will then output a sample calculation of the first row of values and output that in LaTeX for you to put in your report.

Most significantly however this will also find the error formula from the given formula and then output it explicitly with the equation and a sample calculation in LaTeX.

It will also output a tabular LaTeX block containing all of the calculated values, formatted with proper units and errors.

# Gotchas and Pitfalls
Note that this uses sympy to parse the input equation to use. For example, make sure you use asin instead of arcsin to avoid weird crashes. See the sympy gotchas and pitfalls page here : http://docs.sympy.org/latest/gotchas.html

Make sure you import the amsmath package into your LaTeX document, but you should be using it anyways because it is amazing.

Note that you may have to manually add linebreaks to the equations if they extend off the page, \right. and \left. can help you break the lines without adding errors.
