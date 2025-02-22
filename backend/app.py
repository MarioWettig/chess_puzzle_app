from flask import Flask, jsonify, request, render_template, redirect, url_for
import json
import random
import chess
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.config import SQLALCHEMY_DATABASE_URI
from backend.models import db, User, Puzzle, UserPuzzle
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


import time
TOTAL_PUZZLES = 4679273

# Load puzzles from JSON
def load_puzzles():
    try:
        # start_time = time.time()

        random_id = random.randint(2, TOTAL_PUZZLES)
        # id_time = time.time()

        puzzle = Puzzle.query.filter(Puzzle.id == random_id).first()
        # fetch_time = time.time()

        if not puzzle:
            return None

        # end_time = time.time()
        #
        # print(f"📌 Query Timings:")
        # print(f"  ✅ Fetch Puzzle by ID: {fetch_time - id_time:.4f} sec")
        # print(f"  ✅ Total Query Time: {end_time - start_time:.4f} sec")

        # print(f"📌 Loaded Puzzle ID: {puzzle.id}")
        # print(f"🔹 FEN: {puzzle.fen}")
        # print(f"🔹 Solution: {puzzle.solution}")
        # print(f"🔹 Rating: {puzzle.rating}")
        # print(f"🔹 Rating Deviation: {puzzle.rating_deviation}")

        return {
            "id": puzzle.id,
            "fen": puzzle.fen,
            "solution": puzzle.solution.split(","),  # Convert to a list
            "rating": puzzle.rating,
            "rating_deviation": puzzle.rating_deviation,
            "popularity": puzzle.popularity,
            "themes": puzzle.themes,
            "game_url": puzzle.game_url,
            "opening_tags": puzzle.opening_tags
        }
    except Exception as e:
        print(f"❌ Error fetching puzzle: {e}")
        return None




# API to get a random puzzle
@app.route('/get_puzzle', methods=['GET'])
def get_puzzle():
    start_time = time.time()  # Start measuring time
    puzzle = load_puzzles()

    if puzzle is None:
        return jsonify({"error": "No puzzles found"}), 500

    end_time = time.time()  # End measuring time
    print(f"⏱ Puzzle API response time: {end_time - start_time:.4f} seconds")

    return jsonify(puzzle)




# API to validate a move
@app.route('/validate', methods=['POST'])
def validate_move():
    data = request.json  # Get data from frontend
    board = chess.Board(data['fen'])  # FEN is a way to represent the board
    move = chess.Move.from_uci(data['move'])  # Convert user move

    if move in board.legal_moves:
        board.push(move)  # Apply move if valid
        return jsonify({"valid": True, "new_fen": board.fen()})
    else:
        return jsonify({"valid": False})


@app.route('/')
def home():
    return render_template('home.html')


# Login screen
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Basic authentication logic (replace with database later)
        if username == 'admin' and password == 'password':
            return redirect(url_for('chessboard'))  # Redirect to the chessboard screen
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/chessboard')
def index():
    return render_template("chessboard.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validation (you can later replace this with database logic)
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        # Store user details (for now, just redirect)
        return redirect(url_for('login'))  # Redirect to login after signup
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
