# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Sample Data (Replace with your actual API data)
# data = [
#     {"Ticker": "BA", "Sentiment Score": 0.052997, "Sentiment Category": "Neutral"},
#     {"Ticker": "BA", "Sentiment Score": 0.223339, "Sentiment Category": "Somewhat-Bullish"},
#     {"Ticker": "BA", "Sentiment Score": -0.155886, "Sentiment Category": "Somewhat-Bearish"},
#     {"Ticker": "BA", "Sentiment Score": 0.376046, "Sentiment Category": "Bullish"},
#     {"Ticker": "BA", "Sentiment Score": -0.12562, "Sentiment Category": "Neutral"},
#     {"Ticker": "BA", "Sentiment Score": -0.285908, "Sentiment Category": "Somewhat-Bearish"},
#     {"Ticker": "BA", "Sentiment Score": 0.468355, "Sentiment Category": "Bullish"},
#     {"Ticker": "BA", "Sentiment Score": 0.25966, "Sentiment Category": "Somewhat-Bullish"},
#     {"Ticker": "BA", "Sentiment Score": 0.170574, "Sentiment Category": "Somewhat-Bullish"},
# ]
#
# # Convert to DataFrame
# df = pd.DataFrame(data)
#
# # Summary Statistics
# avg_sentiment = df["Sentiment Score"].mean()
# category_counts = df["Sentiment Category"].value_counts()
#
# print(f"Average Sentiment Score: {avg_sentiment:.4f}")
# print("\nSentiment Category Distribution:")
# print(category_counts)
#
# # Plot Sentiment Score Distribution
# plt.hist(df["Sentiment Score"], bins=10, edgecolor='black')
# plt.title("Distribution of Sentiment Scores for BA")
# plt.xlabel("Sentiment Score")
# plt.ylabel("Frequency")
# plt.show()
#
# # Plot Sentiment Category Count
# category_counts.plot(kind="bar", title="Sentiment Category Distribution for BA")
# plt.ylabel("Count")
# #plt.show()
import numpy as np

# Number of random points to sample
N = 10000000  # Increase for better accuracy

# Define the bounding box (1x1x1 cube since 0 <= x,y,z <= 1)
x_samples = np.random.uniform(0, 1, N)
y_samples = np.random.uniform(0, 1, N)
z_samples = np.random.uniform(0, 1, N)

# Check if points satisfy the inequality sqrt(x) + y + z^2 <= 1
inside_region =     (np.sqrt(x_samples) + y_samples + z_samples**2) <= 1

# Estimated volume (fraction of points inside * cube volume)
volume_estimate = np.sum(inside_region) / N

# Display the result
print(volume_estimate)