"""Cox–Ross–Rubinstein binomial tree for European and American options on a non-dividend-paying stock."""
import numpy as np


def binomial_price(S, K, T, r, sigma, option_type="call", n=500, american=False):
    """Price an option on an n-step CRR tree.

    Each step of length dt = T/n moves the stock up by u = e^(σ√dt) or down by d = 1/u.
    The risk-neutral up probability p = (e^(r dt) − d) / (u − d) makes the expected
    stock price grow at the risk-free rate. Working backwards from expiry, each node is
    the discounted expectation of its two children; an American option is also worth at
    least its immediate exercise value at every node.
    """
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    disc = np.exp(-r * dt)
    p = (np.exp(r * dt) - d) / (u - d)
    if not 0 < p < 1:
        raise ValueError("risk-neutral probability outside (0, 1): increase n")

    def payoff(S_nodes):
        if option_type == "call":
            return np.maximum(S_nodes - K, 0)
        return np.maximum(K - S_nodes, 0)

    # Stock prices at expiry: S u^j d^(n−j) for j = 0..n up moves.
    j = np.arange(n + 1)
    V = payoff(S * u**j * d**(n - j))
    for step in range(n - 1, -1, -1):
        V = disc * (p * V[1:] + (1 - p) * V[:-1])
        if american:
            j = np.arange(step + 1)
            V = np.maximum(V, payoff(S * u**j * d**(step - j)))
    return float(V[0])
