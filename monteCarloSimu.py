import numpy as np
import matplotlib.pyplot as plt

# Parameters
S0 = 100        # Initial stock price
mu = 0.07       # Expected return
sigma = 0.2     # Volatility
T = 1           # Time in years
dt = 1/252      # Daily steps
N = int(T/dt)   # Number of time steps
M = 100         # Number of simulations

# Simulation
np.random.seed(42)
paths = np.zeros((N + 1, M))
paths[0] = S0

for t in range(1, N + 1):
    Z = np.random.standard_normal(M)
    paths[t] = paths[t - 1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(paths)
plt.title("Monte Carlo Simulation of Stock Price Paths ")
plt.xlabel("Time Steps (Days)")
plt.ylabel("Stock Price:")
plt.grid(True)
plt.show()