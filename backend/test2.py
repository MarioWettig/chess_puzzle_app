import pandas as pd
import matplotlib.pyplot as plt

# Sample Data (Replace with your actual API data)
data = [
    {"Ticker": "BA", "Sentiment Score": 0.052997, "Sentiment Category": "Neutral"},
    {"Ticker": "BA", "Sentiment Score": 0.223339, "Sentiment Category": "Somewhat-Bullish"},
    {"Ticker": "BA", "Sentiment Score": -0.155886, "Sentiment Category": "Somewhat-Bearish"},
    {"Ticker": "BA", "Sentiment Score": 0.376046, "Sentiment Category": "Bullish"},
    {"Ticker": "BA", "Sentiment Score": -0.12562, "Sentiment Category": "Neutral"},
    {"Ticker": "BA", "Sentiment Score": -0.285908, "Sentiment Category": "Somewhat-Bearish"},
    {"Ticker": "BA", "Sentiment Score": 0.468355, "Sentiment Category": "Bullish"},
    {"Ticker": "BA", "Sentiment Score": 0.25966, "Sentiment Category": "Somewhat-Bullish"},
    {"Ticker": "BA", "Sentiment Score": 0.170574, "Sentiment Category": "Somewhat-Bullish"},
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Summary Statistics
avg_sentiment = df["Sentiment Score"].mean()
category_counts = df["Sentiment Category"].value_counts()

print(f"Average Sentiment Score: {avg_sentiment:.4f}")
print("\nSentiment Category Distribution:")
print(category_counts)

# Plot Sentiment Score Distribution
plt.hist(df["Sentiment Score"], bins=10, edgecolor='black')
plt.title("Distribution of Sentiment Scores for BA")
plt.xlabel("Sentiment Score")
plt.ylabel("Frequency")
plt.show()

# Plot Sentiment Category Count
category_counts.plot(kind="bar", title="Sentiment Category Distribution for BA")
plt.ylabel("Count")
#plt.show()