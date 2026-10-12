# option-pricing

Black–Scholes option pricing and Greeks in Python, with analytical, finite-difference and Monte Carlo validation.

## Status

| Component | Status |
| --- | --- |
| Black–Scholes call and put prices | Done |
| Put-call parity and textbook checks | Done |
| Greeks: Delta, Gamma, Vega, Theta, Rho | Done |
| Finite-difference validation of the Greeks | Done |
| Monte Carlo validation | Planned |

## Model

For a European option on a non-dividend-paying stock:

```text
d1 = [ln(S/K) + (r + σ²/2) T] / (σ √T)
d2 = d1 − σ √T

Call = S N(d1) − K e^(−rT) N(d2)
Put  = K e^(−rT) N(−d2) − S N(−d1)
```

## Greeks

| Greek | Measures | Call | Put |
| --- | --- | --- | --- |
| Delta | ∂V/∂S | N(d1) | N(d1) − 1 |
| Gamma | ∂²V/∂S² | n(d1) / (S σ √T) | same as call |
| Vega | ∂V/∂σ | S n(d1) √T | same as call |
| Theta | change in value as time passes | −S n(d1) σ / (2√T) − rK e^(−rT) N(d2) | −S n(d1) σ / (2√T) + rK e^(−rT) N(−d2) |
| Rho | ∂V/∂r | K T e^(−rT) N(d2) | −K T e^(−rT) N(−d2) |

`n(·)` is the standard normal density. Vega and Rho are per unit change (divide by 100 for a one-percentage-point move); Theta is per year (divide by 365 for one calendar day).

For the Hull example: call Delta 0.779, put Delta −0.221, Gamma 0.0500, Vega 8.81, call Theta −4.56, put Theta −0.75, call Rho 13.98, put Rho −5.04.

## Validation

- **Textbook value:** Hull's Example 15.6 (S = 42, K = 40, T = 0.5, r = 10%, σ = 20%) gives a call of 4.76 and a put of 0.81.
- **Finite differences:** every analytical Greek is compared with a central difference of the pricing function (bump S, σ, r or T) across 24 parameter combinations, for calls and puts. This independent check caught an operator-precedence error in Theta during development: `x / 2 * sqrt(T)` puts √T in the numerator, and the put Theta came out positive.
- **Put-call parity:** `C − P = S − K e^(−rT)` holds to 1e-10 across a grid of prices, volatilities and maturities. Parity follows from no-arbitrage alone, so it catches sign errors in the put formula that would otherwise run without error. Differentiating it gives the Greek relations that are also tested: call Delta − put Delta = 1, and calls and puts share Gamma and Vega.

## Run it

```bash
pip install -r requirements.txt
pytest
```

```python
from pricing import bs_price, delta
bs_price(42, 40, 0.5, 0.10, 0.20, "call")   # 4.7594...
delta(42, 40, 0.5, 0.10, 0.20, "call")      # 0.7791...
```
