# import requests
#
# Replace with your own API key
# api_key = "YDOGQCOUWCOPJCM9"
# topics = "technology"
#
# url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={topics}&apikey={api_key}"
# response = requests.get(url)
# data = response.json()
#
# print(data)
# if "feed" in data:
#     ibm_sentiment = []
#
#     for article in data["feed"]:
#         for sentiment in article.get("ticker_sentiment", []):
#             if sentiment["ticker"] == ticker:
#                 ibm_sentiment.append({
#                     "Ticker": sentiment["ticker"],
#                     "Sentiment Score": sentiment["ticker_sentiment_score"],
#                     "Sentiment Category": sentiment["ticker_sentiment_label"]
#                 })
#
#     # Print IBM sentiment data
#     for item in ibm_sentiment:
#         print(item)
#
# else:
#     print("No sentiment data found")

import os
import pandas as pd
from backend.app import db, app
from sqlalchemy.orm import sessionmaker
from backend.models import Puzzle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, "data", "lichess_db_puzzle.csv")

# Batch size (adjustable)
BATCH_SIZE = 10000  # Insert 10,000 puzzles at a time

# Chunk size for reading CSV (prevents memory overload)
CHUNK_SIZE = 50000  # Load 50,000 rows at a time


def clean_data(chunk):
    """Clean the data by filtering invalid ratings and replacing NaN values."""
    # Convert Rating to integer (drop invalid values)
    chunk = chunk[pd.to_numeric(chunk["Rating"], errors="coerce").notna()]

    # Convert Rating and RatingDeviation to integers
    chunk["Rating"] = chunk["Rating"].astype(int)
    chunk["RatingDeviation"] = chunk["RatingDeviation"].fillna(0).astype(int)

    # Replace NaN values with empty strings
    chunk.fillna("", inplace=True)

    return chunk


def process_chunk(chunk):
    """Process a chunk of data and insert it into the database in batches."""
    chunk = clean_data(chunk)

    chunk.rename(columns={
        "FEN": "fen",
        "Moves": "solution",
        "Rating": "rating",
        "RatingDeviation": "rating_deviation",
        "Popularity": "popularity",
        "Themes": "themes",
        "GameUrl": "game_url",
        "OpeningTags": "opening_tags"
    }, inplace=True)

    # Convert Moves column (comma-separated solutions) to string format
    chunk["solution"] = chunk["solution"].apply(lambda x: ",".join(str(x).split()))

    # Convert dataframe to list of dictionaries
    puzzle_data = chunk.to_dict(orient="records")

    # Insert into database in batches
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        for i in range(0, len(puzzle_data), BATCH_SIZE):
            batch = puzzle_data[i:i + BATCH_SIZE]
            session.bulk_insert_mappings(Puzzle, batch)
            session.commit()  # Commit each batch
            print(f"✅ Inserted {i + len(batch)} puzzles...")

        session.close()


# Read CSV in chunks
print("📂 Starting puzzle import...")
chunk_iter = pd.read_csv(CSV_FILE_PATH, usecols=[
    "FEN", "Moves", "Rating", "RatingDeviation", "Popularity", "Themes", "GameUrl", "OpeningTags"
], chunksize=CHUNK_SIZE)

for chunk in chunk_iter:
    process_chunk(chunk)

print("🎉 Finished importing all puzzles!")