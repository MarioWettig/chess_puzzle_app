from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import json
import random
import chess
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from fontTools.misc.cython import returns

from backend.config import SQLALCHEMY_DATABASE_URI
from backend.models import db, User, Puzzle, UserPuzzle
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)


db.init_app(app)
migrate = Migrate(app, db)


import time
TOTAL_PUZZLES = 4679273

# Load puzzles from JSON
def load_random_puzzle():
    print("Loading random puzzle.")
    try:
        # start_time = time.time()

        random_id = random.randint(2, TOTAL_PUZZLES)
        # id_time = time.time()

        puzzle = Puzzle.query.filter(Puzzle.id == random_id).first()
        # fetch_time = time.time()

        if not puzzle:
            return None

        # end_time = time.time()

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


def load_personalised_puzzle(user_id):
    print('personalised puzzle')
    try:
        user = User.query.get(user_id)
        if not user:
            print("❌ User not found! Using default rating.")
            user_rating = 1000  # Default rating for unknown users
        else:
            user_rating = user.rating

        # Fetch a puzzle within ±100 rating of the user
        puzzle = Puzzle.query.filter(
            Puzzle.rating.between(user_rating - 100, user_rating + 100)
        ).order_by(db.func.random()).first()

        if not puzzle:
            return None  # Return None if no puzzle found

        # Convert puzzle object to dictionary
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
        print(f"❌ Error fetching personalized puzzle: {e}")
        return None



# API to get a random puzzle
@app.route('/get_puzzle', methods=['GET'])
def get_puzzle():
    start_time = time.time()  # Start measuring time
    is_personalised = request.args.get("personalised", "false").lower() == "true"
    user_id = session.get("user_id")  # Get user ID from session

    print(f"✅ personalised = {is_personalised}")
    print(f"👤 User ID from session: {user_id}")

    if is_personalised:
        puzzle = load_personalised_puzzle(user_id) if user_id else load_random_puzzle()
    else:
        puzzle = load_random_puzzle()


    if puzzle is None:
        return jsonify({"error": "No puzzles found"}), 500

    end_time = time.time()
    print(f"⏱ Puzzle API response time: {end_time - start_time:.4f} seconds")

    return jsonify(puzzle)


@app.route('/submit_puzzle_result', methods=['POST'])
def submit_puzzle_result():
    data = request.json
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "User not found in session"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User does not exist"}), 400

    puzzle_id = data.get("puzzle_id")
    time_taken = data.get("time_taken", 0)
    number_wrong_moves = data.get("number_wrong_moves", 0)
    hints_used = data.get("hints_used", 0)  # Get hints count
    solved = data.get("solved", False)

    puzzle = Puzzle.query.get(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle does not exist"}), 400

    rating_at_attempt = user.rating

    # --- ELO-inspired rating update ---
    K = 40

    # Calculate expected score (ELO system)
    expected = 1 / (1 + 10 ** ((puzzle.rating - user.rating) / 400))

    if solved:
        if time_taken < 45 and number_wrong_moves == 0 and hints_used == 0:
            actual = 1.0   #  Perfect solve: fast, no mistakes, no hints
        elif time_taken < 75 and number_wrong_moves <= 1 and hints_used <= 1:
            actual = 0.8   #  Good solve: decent time, minor errors, at most 1 hint
        elif hints_used > 2:
            actual = 0.3   #  Solved but used too many hints
        else:
            actual = 0.5   # ️ Average solve
    else:
        actual = 0.0       #  Failed to solve

    print(actual, " actuallll", expected, "expectedddd")
    user_change = round(K * (actual - expected))

    # Additional penalty for hints
    hint_penalty = hints_used * 3
    user_change -= hint_penalty

    print("prior user rating", user.rating)
    user.rating = max(300, user.rating + user_change)
    print("changed user rating",user.rating)

    user_puzzle = UserPuzzle(
        user_id=user_id,
        puzzle_id=puzzle_id,
        time_taken=time_taken,
        number_wrong_moves=number_wrong_moves,
        hints_used=hints_used,
        rating=rating_at_attempt,
        solved=solved,
        user_rating_change=user_change
    )

    db.session.add(user_puzzle)
    db.session.commit()

    return jsonify({
        "message": "Puzzle result recorded",
        "new_rating": user.rating,
        "rating_change": user_change,
        "hint_penalty": hint_penalty
    })


# API to validate a move
@app.route('/validate', methods=['POST'])
def validate_move():
    data = request.json
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
    if "user_id" not in session:
        guest_username = f"guest_{random.randint(1000, 9999)}"
        guest_user = User(
            username=guest_username,
            email=None,
            password="guest",
            rating=1000
        )
        db.session.add(guest_user)
        db.session.commit()

        session["user_id"] = guest_user.id  # Store guest user ID in session
        session["is_guest"] = True  # Mark as guest

        print(f"✅ Guest Created: {guest_user.username} (ID: {guest_user.id})")
        print(f"📌 Session Data: {session}")  # Check what's stored

    else:
        print(f"👤 Existing User Session: {session['user_id']}")
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
