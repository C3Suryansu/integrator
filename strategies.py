"""
Integration Strategies

This file is a booklet of strategies for
solving integration problems.

Each strategy is a subtype of IntegrationStrategy
and can apply itself to an expression.
"""

from elements import *

# add on integration uncertainty variable
def add_integration_constant(expr, original_intg):
  return Sum(expr, original_intg.var.vset.new_variable(suggest='C'))


def is_constant(expr, var) :
  """
  Test whether the expression is constant with respect to the variable.
  """
  if expr.is_a(Number) :
    return True
  elif expr.is_a(Variable) :
    return (expr != var)
  elif expr.is_a(Sum) or expr.is_a(Product):
    return is_constant(expr.a, var) and is_constant(expr.b, var)
  elif expr.is_a(Fraction):
    return is_constant(expr.numr, var) and is_constant(expr.denr, var)
  else :
    return False


class IntegrationStrategy(object):
  def __init__(self):
    raise "Strategy is an abstract class"

  def apply(exp):
    raise "apply not implemented"


class ConstantTerm(IntegrationStrategy):
  example = "int 4 dx = 4x + C"
  description = "integral of a constant term"

  @classmethod
  def applicable(self, intg):
    return is_constant(intg.exp, intg.var)

  @classmethod
  def apply(self, intg):
    exp = intg.exp.simplified()
    return add_integration_constant(Product(exp, intg.var), intg)


class ConstantFactor(IntegrationStrategy):
  example = "int 4x dx = 4 * int x dx"
  description = "integral with a constant factor"

  @classmethod
  def applicable(self, intg):
    exp = intg.simplified().exp
    return (exp.is_a(Product)
      and (is_constant(exp.a, intg.var)
        or is_constant(exp.b, intg.var)))

  @classmethod
  def apply(self, intg):
    exp = intg.simplified().exp
    integrand, constant_factor = sorted([exp.a, exp.b], key=lambda e: is_constant(e, intg.var) )
    return Product(constant_factor, Integral(integrand, intg.var))


class ConstantDivisor(IntegrationStrategy):
  example = "int x/4 dx = 1/4 * int x dx"
  description = "integral with a constant divisor"

  @classmethod
  def applicable(self, intg):
    exp = intg.simplified().exp
    return (exp.is_a(Fraction)
      and (is_constant(exp.denr, intg.var)))

  @classmethod
  def apply(self, intg):
    exp = intg.simplified().exp
    return Product(Fraction(Number(1), exp.denr), Integral(exp.numr, intg.var))


class SimpleIntegral(IntegrationStrategy):
  example = "int x dx = 1/2 x^2 + C"
  description = "integral of the integration variable occuring by itself"

  @classmethod
  def applicable(self, intg):
    expr = intg.simplified().exp
    return expr.is_a(Variable) and (expr is intg.var)

  @classmethod
  def apply(self, intg):
    expr = intg.simplified().exp
    half = Fraction(Number(1), Number(2))
    new_expr = Product(half, Power(expr, Number(2)))
    return add_integration_constant(new_expr, intg)


class ConstantPower(IntegrationStrategy):
  example = "int x^3 dx = 1/4 x^4 + C"
  description = "integral with a constant exponent"

  @classmethod
  def applicable(self, intg):
    expr = intg.simplified().exp
    return (expr.is_a(Power)
      and expr.base.is_a(Variable)
      and (expr.base.symbol == intg.var.symbol)
      and is_constant(expr.exponent, intg.var))

  @classmethod
  def apply(self, intg):
    expr = intg.simplified().exp
    # TODO: Do not use floating point reciprocal, use fraction instead.
    n_plus_one = Sum(expr.exponent, Number(1)).simplified()
    recip_n = n_plus_one.reciprocal()
    new_expr = Product(recip_n, Power(intg.var, n_plus_one))
    return add_integration_constant(new_expr, intg)


class DistributeAddition(IntegrationStrategy):
  example = "int x + x^2 dx = int x dx + int x^2 dx"
  description = "integral of sums to sum of integrals"

  @classmethod
  def applicable(self, intg):
    exp = intg.simplified().exp
    return exp.is_a(Sum)

  @classmethod
  def apply(self, intg):
    exp = intg.simplified().exp
    new_expr = Sum(Integral(exp.a, intg.var), Integral(exp.b, intg.var))
    return add_integration_constant(new_expr, intg)

class OneOverX(IntegrationStrategy):
  description = "The integral of 1/x is ln(x)."

  @classmethod
  def applicable(self, intg):
    exp = intg.simplified().exp
    return (exp.is_a(Fraction)
      and is_constant(exp.numr, intg.var)
      and (exp.denr == intg.var))

  @classmethod
  def apply(self, intg):
    return Product(intg.simplified().exp.numr, Logarithm(intg.var))


STRATEGIES = [ConstantTerm, ConstantFactor, ConstantDivisor, SimpleIntegral, ConstantPower, DistributeAddition, OneOverX]
