from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import random
import chess
import os
import redis
from flask_migrate import Migrate
from flask_session import Session

from backend.config import SQLALCHEMY_DATABASE_URI
from backend.models import db, User, Puzzle, UserPuzzle
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "fallback_secret_key")

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # if you want to sign session cookies
app.config['SESSION_REDIS'] = redis.from_url(os.environ.get("REDIS_URL"))


Session(app)


db.init_app(app)
migrate = Migrate(app, db)


import time
TOTAL_PUZZLES = 4679273

@app.route('/session_debug')
def session_debug():
    if "user_id" not in session:
        session["user_id"] = random.randint(1000, 9999)  # Assign a test ID
        return jsonify({"message": "New session created", "user_id": session["user_id"]})

    return jsonify({"message": "Session exists", "user_id": session["user_id"]})


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
            Puzzle.rating.between(user_rating - 70, user_rating + 70)
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
    is_personalised = data.get("personalised", False)

    puzzle = Puzzle.query.get(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle does not exist"}), 400

    rating_at_attempt = user.rating

    # --- ELO-inspired rating update ---
    K = 47

    # Calculate expected score (ELO system)
    print(puzzle.rating)
    expected = 1 / (1 + 10 ** ((puzzle.rating - user.rating) / 400))

    total_moves = len(puzzle.solution.split(","))
    total_user_moves = max(1, total_moves // 2)  # at least 1 (avoid division by zero)
    hint_efficiency = hints_used / total_user_moves # 0-1 percentage of hints to moves
    time_efficiency = time_taken / total_user_moves # time per move
    move_efficiency = number_wrong_moves / total_user_moves # mistakes per move

    print("time eff: ", time_efficiency, ". Move eff: ", move_efficiency, ". Hint eff: ", hint_efficiency, ". is Perso: ", is_personalised)

    if solved:
        if hint_efficiency > 0.95:  # Used hints for almost all moves, didn't really solve it
            actual = 0.1
        elif time_efficiency <= 8 and move_efficiency == 0 and hint_efficiency == 0.0:
            actual = 1.0  # Perfect solve: solved quickly with no mistakes/hints
        elif ((time_efficiency <= 10 and move_efficiency <= 0.34) or (time_efficiency <= 15 and move_efficiency == 0.0)) and hint_efficiency == 0.0:
            actual = 0.85  # Very good solve
        elif time_efficiency <= 15 and move_efficiency <= 0.34 and hint_efficiency == 0.0:
            actual = 0.75  # Good solve
        elif time_efficiency <= 15 and move_efficiency <= 0.5 and hint_efficiency <= 0.3:
            actual = 0.65  # Above average solve
        elif time_efficiency <= 25 and move_efficiency <= 0.2  and hint_efficiency <= 0.3:
            actual = 0.55  # pretty good solve, but took too long
        elif move_efficiency <= 1.5 and hint_efficiency <= 0.3:
            actual = 0.4  # solved but took too long, and/or made many mistakes, but didn't rely heavily too on hints
        elif move_efficiency <= 1 and 0.5 < hint_efficiency < 0.7:
            actual = 0.35
        elif move_efficiency <= 1 and 0.7 < hint_efficiency < 0.8:
            actual = 0.25  # Solved but used way too many hints
        else:
            actual = 0.15  # very below average solve
    else:
        actual = 0.1

    if actual <= 0.3:
        solved = False


    print(actual, " actuallll", expected, "expectedddd")
    user_change = round(K * (actual - expected))

    # Additional penalty for hints
    hint_penalty = round(hint_efficiency * 5)
    hint_penalty = min(15, hint_penalty)
    user_change -= hint_penalty


    print("prior user rating", user.rating)
    user.rating = max(300, user.rating + user_change)
    print("changed user rating",user.rating)

    user_puzzle = UserPuzzle(
        user_id=user_id,
        puzzle_id=puzzle_id,
        puzzle_rating=puzzle.rating,
        time_taken=time_taken,
        number_wrong_moves=number_wrong_moves,
        hints_used=hints_used,
        rating=rating_at_attempt,
        solved=solved,
        user_rating_change=user_change,
        random = not is_personalised
    )

    db.session.add(user_puzzle)
    db.session.commit()

    return jsonify({
        "message": "Puzzle result recorded",
        "new_rating": user.rating,
        "rating_change": user_change,
        "hint_penalty": hint_penalty
    })

@app.route('/reset_rating', methods=['POST'])
def reset_rating():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "User not found in session"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User does not exist"}), 400

    # Reset rating to 1000
    user.rating = 1000
    db.session.commit()

    print(f"✅ User {user.username} (ID: {user.id}) rating reset to 1000")

    return jsonify({"message": "User rating reset", "new_rating": user.rating})



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
    print(f"📌 Connected to: {SQLALCHEMY_DATABASE_URI}")
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
        guest_user = User(username=guest_username, email=None, password="guest", rating=1000)
        db.session.add(guest_user)
        db.session.commit()

        session["user_id"] = guest_user.id  # Store user ID
        session["is_guest"] = True  # Mark as guest

        print(f"✅ Guest Created: {guest_user.username} (ID: {guest_user.id})")

    print(f"📌 Session User ID: {session.get('user_id')}")  # Debugging line

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

@app.route('/debug_users')
def debug_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "rating": u.rating} for u in users])



if __name__ == '__main__':
    app.run(debug=True)
