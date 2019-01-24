from math import lgamma
from numba import jit
import numpy as np
import matplotlib.pyplot as plt


@jit
def h(a, b, c, d):
    """
    This is the equation number 3 of the article

    :param a:
    :param b:
    :param c:
    :param d:
    :return:
    """
    num = lgamma(a + c) + lgamma(b + d) + lgamma(a + b) + lgamma(c + d)
    den = lgamma(a) + lgamma(b) + lgamma(c) + lgamma(d) + lgamma(a + b + c + d)
    return np.exp(num - den)


@jit
def g0(a, b, c):
    """
    This is the first equation of chapter 2

    :param a:
    :param b:
    :param c:
    :return:
    """
    return np.exp(lgamma(a + b) + lgamma(a + c) - (lgamma(a + b + c) + lgamma(a)))


@jit
def hiter(a, b, c, d):
    """
    This function iterate using the recurrence equations (page 3) until it reaches the case of the first equation
    of chapter 2

    :param a:
    :param b:
    :param c:
    :param d:
    :return:
    """
    while d > 1:
        d -= 1
        yield h(a, b, c, d) / d


def g(a, b, c, d):
    """
    This is the equation...

    :param a:
    :param b:
    :param c:
    :param d:
    :return:
    """
    return g0(a, b, c) + sum(hiter(a, b, c, d))


def calc_prob_between(beta1, beta2) -> float:
    """
    This function calculate the probability for beta1 to be greater than beta2.
    In this function the beta functions (scipy.stats.beta) are needed only for extracting the arguments

    The output will be a number. 0.5 means the distributions are the same,
    more than 0.5 means that beta1 is better than beta2, less than 0.5 means the opposite.

    For having an affordable result, that probability should be greater than 0.95.

    Details about the math: https://www.johndcook.com/UTMDABTR-005-05.pdf

    :param beta1: the first beta distribution
    :param beta2: the second beta distribution
    :return: the probability.
    """
    return g(beta1.args[0], beta1.args[1], beta2.args[0], beta2.args[1])


def calc_beta_mode(a: int, b: int) -> float:
    """
    This function calculate the mode (i.e. the peak) of the beta distribution.

    :param a: First shape parameter of the Beta distribution
    :param b: Second shape parameter of the Beta distribution
    :return: The mode
    """
    return (a-1)/(a+b-2)


def plot_beta(betas, names, linf=0, lsup=0.01):
    """
    This function plots the Beta distribution(s)
    
    :param betas: a list containing the beta distributions
    :param names: a list of the same size of `betas`, with the names associated to the samples as strings
    :param linf: the left limit for the horizontal (`x`) axis.
    :param lsup: the right limit for the horizontal (`x`) axis.
    :return: nothing, just plot the beta(s)
    """""
    x = np.linspace(linf, lsup, 100)
    for f, name in zip(betas, names):
        y = f.pdf(x)
        y_mode = calc_beta_mode(f.args[0], f.args[1])
        y_var = f.var()
        plt.plot(x, y, label=f"{name}, peak @ {y_mode:0.1E}, var = {y_var:0.1E}")
        plt.yticks([])
    plt.legend()
    plt.show()
