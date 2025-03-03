from flask_sqlalchemy import SQLAlchemy
#from backend.app import db

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)  # Storing plain text passwords
    rating = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        return f"<User {self.username}>"


class Puzzle(db.Model):
    __tablename__ = "puzzles"

    id = db.Column(db.Integer, primary_key=True)
    fen = db.Column(db.String(100), nullable=False)  # Board state
    solution = db.Column(db.String(255), nullable=False)  # Solution moves (comma-separated)
    rating = db.Column(db.Integer, nullable=False)  # Puzzle difficulty based on rating
    rating_deviation = db.Column(db.Float, nullable=False)  # Rating uncertainty
    popularity = db.Column(db.Integer, nullable=True)  # Number of plays
    themes = db.Column(db.String(255), nullable=True)  # Puzzle themes
    game_url = db.Column(db.String(255), nullable=True)  # Link to the original game
    opening_tags = db.Column(db.String(255), nullable=True)  # Opening classification

    def __repr__(self):
        return f"<Puzzle {self.id} - {self.rating}>"


class UserPuzzle(db.Model):
    __tablename__ = "user_puzzles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    puzzle_id = db.Column(db.Integer, db.ForeignKey("puzzles.id"), nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # Time in seconds
    number_wrong_moves = db.Column(db.Integer, default=0, nullable=False)  # Mistakes before solving
    hints_used = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    solved = db.Column(db.Boolean, default=False)  # If the puzzle was solved correctly
    date_attempted = db.Column(db.DateTime, default=db.func.current_timestamp())  # Timestamp
    user_rating_change = db.Column(db.Integer, default=0, nullable=True)  # Rating adjustment

    user = db.relationship("User", backref="solved_puzzles")
    puzzle = db.relationship("Puzzle", backref="attempts")

    def __repr__(self):
        return f"<User {self.user_id} - Puzzle {self.puzzle_id} - Solved: {self.solved}>"


