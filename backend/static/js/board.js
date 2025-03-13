var board;
var game = new Chess();
var currentSolution = [];
var moveHistory = [];
var timer;
var secondsElapsed = 0;

var puzzleID;
var inaccurateMoves = 0;
var hintsUsed = 0;

// not sure how useful the logs are, debugging i guess but they aren't in the terminal lol in the browser! ;)

document.addEventListener("DOMContentLoaded", function () {
     loadPersonalisationState(); loadPuzzle();

     localStorage.setItem("puzzleCounter", "0");
     updatePuzzleCounter();
});

function updatePuzzleCounter() {
    let counter = localStorage.getItem("puzzleCounter");
    document.getElementById("puzzleCounter").innerText = counter;
}

function startTimer() {
    clearInterval(timer); // Reset any existing timer
    secondsElapsed = 0;   // Reset time
    updateTimerDisplay(); // Reset UI

    timer = setInterval(() => {
        secondsElapsed++;
        updateTimerDisplay();
    }, 1000);


}

function updateTimerDisplay() {
    let minutes = Math.floor(secondsElapsed / 60);
    let seconds = secondsElapsed % 60;
    document.getElementById("timer").textContent =
        (minutes < 10 ? "0" : "") + minutes + ":" +
        (seconds < 10 ? "0" : "") + seconds;
}


function resetTimer() {
    clearInterval(timer);
    secondsElapsed = 0;
    updateTimerDisplay();
}

function stopTimer() {
    clearInterval(timer);
}



function loadPuzzle() {
     let isPersonalised = localStorage.getItem("personalisation") === "true"; // Read from localStorage
    console.log("🔄 Loading puzzle. Personalised:", isPersonalised);

    fetch(`/get_puzzle?personalised=${isPersonalised}`)
        .then(response => response.json())
        .then(data => {
            //console.log(" Loaded Puzzle:", data);
            if (data.error) {
                alert("Error loading puzzle: " + data.error);
                return;
            }

            let isBlackToMove = data.fen.split(" ")[1] === "b";
            let playerTurn = !isBlackToMove ? "Black" : "White";
            //console.log(" FEN:", data.fen);
             console.log(" Rating:", data.rating);
            // console.log(" Player should play as:", playerTurn);

            // Update the board orientation based on turn
            board = Chessboard('board', {
                draggable: true,
                position: data.fen,
                pieceTheme: '/static/img/chesspieces/{piece}.png',
                orientation: playerTurn.toLowerCase(), // Flip if Black
                onDrop: onDrop
            });

            game = new Chess(); // Reset game state
            game.load(data.fen);
            board.position(data.fen);
            currentSolution = [...data.solution];
            moveHistory = [];
            puzzleID = data.id;
            inaccurateMoves = 0;
            hintsUsed = 0;

            // console.log("processed :", currentSolution);
            // console.log("processed moveHistory :", moveHistory);

            let moveCount = currentSolution.length;
            let turnIndicator = document.querySelector('.puzzle-info');
            turnIndicator.innerHTML = `<span style="font-size: 20px; font-weight: bold; color: white;">Play as ${playerTurn}. <b>${Math.ceil(moveCount/2)}</b> best move(s)!</span>`;

            document.getElementById('result-message').innerText = "";
            document.querySelector(".button-next").style.display = "none"; // Hide Next button

            resetTimer();

            setTimeout(() => {
                applyOpponentMove();
                //console.log("🔹 Solution After Opponent Move:", currentSolution);
            }, 1200);

            startTimer();
        })
        .catch(error => {
            console.error(" Error fetching puzzle:", error);
        });
}

function applyOpponentMove(){
    if (currentSolution.length > 0) {
        //console.log("🟡 [Before] Full Solution List:", [...currentSolution]);
        let firstMove = currentSolution[0];

        console.log("♟️ Opponent's Move:", firstMove);
        //console.log("🟢 [After] Solution List:", [...currentSolution]);

        let opponentMoveObj = game.move({
            from: firstMove.substring(0, 2),
            to: firstMove.substring(2, 4),
            promotion: 'q'
        });

        if (opponentMoveObj) {
            board.position(game.fen());
            moveHistory.push(opponentMoveObj.san);
            console.log("Opponent played:", opponentMoveObj.san);
            console.log("move his and current sol:",moveHistory.length, currentSolution.length)
        } else {
            console.error(" Opponent's move was invalid:", firstMove);
        }
    }
}


// move validation
function onDrop(source, target) {
    if (source === target) {
        console.log("🔄 Piece clicked but not moved, ignoring.");
        return;
    }

    let move = {
        from: source,
        to: target,
        promotion: 'q'
    };

    let userMoveNotation = source + target; // Example: "e2e4"

    // Ensure pawn promotions are accounted for
    if (game.get(source).type === "p" && (target[1] === "8" || target[1] === "1")) {
        userMoveNotation += "q";
    }

    console.log("🔍 Expected Move:", currentSolution[moveHistory.length]);
    console.log("✅ User Attempt:", userMoveNotation);

    if (userMoveNotation !== currentSolution[moveHistory.length]) {
        console.log("❌ Incorrect move! Try again.");
        showError(" Incorrect move! Try again.", target);
        inaccurateMoves++;
        return 'snapback';
    }

    let userMove = game.move(move);

    if (!userMove) {
        console.log("❌ Illegal move attempted:", move);

        // Get all legal moves from Chess.js
        let legalMoves = game.moves({ verbose: true });

        // Compare what you tried vs. what Chess.js expects
        let legalMoveFormats = legalMoves.map(m => ({
            from: m.from,
            to: m.to,
            promotion: m.promotion || null,
            moveInUCI: m.san  // Standard Algebraic Notation
        }));

        console.log("🔍 Legal Moves (Verbose Format):", legalMoveFormats);

        // Highlight error and reset piece
        highlightSquareError(target, "red");
        return 'snapback';
    }


    moveHistory.push(userMoveNotation);
    console.log(" Correct move:", userMoveNotation);

    // Check if there is an opponent's response move
    if (moveHistory.length < currentSolution.length) {
        let opponentMove = currentSolution[moveHistory.length]; // Next move in the sequence
        console.log("🤖 Opponent Move:", opponentMove);

        setTimeout(() => {
            let opponentMoveObj = game.move({
                from: opponentMove.substring(0, 2),
                to: opponentMove.substring(2, 4),
                promotion: 'q'
            });

            if (!opponentMoveObj) {
                console.error(" Opponent move was invalid:", opponentMove);
                return;
            }

            board.position(game.fen()); // Update board
            moveHistory.push(opponentMove); // Add to move history
            console.log("️ Opponent played:", opponentMove);
        }, 1000);
    }


    // if solved
    if (moveHistory.length === currentSolution.length) {
        console.log(" Puzzle solved!");
        stopTimer();

        let counter = parseInt(localStorage.getItem("puzzleCounter"), 10) || 0;
        counter++;
        localStorage.setItem("puzzleCounter", counter);
        updatePuzzleCounter();

        let timeTaken = secondsElapsed;
        let wrongMoves = inaccurateMoves;
        let hints = hintsUsed;
        let puzzleId = puzzleID;


        let resultMessage = document.getElementById('result-message');
        resultMessage.innerHTML = "<span style='font-weight: bold; font-size: 18px; color: green;'>✅ Puzzle solved!</span>";

        // Force final board update and clear selection
        setTimeout(() => {
            board.position(game.fen());
            board.resize(); // Fixes visual glitches
        }, 300);




        fetch('/submit_puzzle_result', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                puzzle_id: puzzleId,
                time_taken: timeTaken,
                number_wrong_moves: wrongMoves,
                hints_used: hints,
                solved: true,
                personalised: localStorage.getItem("personalisation") === "true"
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("📌 Rating Update:", data);
            //alert(`New Rating: ${data.new_rating} (Change: ${data.rating_change})`);
        })
        .catch(error => console.error("❌ Error submitting puzzle result:", error));

        // Show "Next" button
        document.querySelector('.button-next').style.display = "inline-block";

        return;
    }
}

function showError(message, targetSquare) {
    let resultMessage = document.getElementById('result-message');
    resultMessage.innerText = message;
    resultMessage.style.color = "red";

    highlightSquareError(targetSquare, "red");

    setTimeout(() => {
        resultMessage.innerText = "";
    }, 3000);
}


// Highlight incorrect moves
function highlightSquareError(square, color) {
    let squareEl = document.querySelector(`.square-${square}`);
    if (squareEl) {
        squareEl.style.backgroundColor = color;
        setTimeout(() => {
            squareEl.style.backgroundColor = '';
        }, 750);
    }
}


function undoMove() {
    if (moveHistory.length === 0) {
        console.log("⚠️ No moves to undo!");
        return;
    }

    var lastMove = game.undo();  // Undo last move
    if (!lastMove) return; // Safety check

    moveHistory.pop(); // Remove last move from history
    board.position(game.fen()); // Update board

    console.log("🔄 Move undone:", lastMove.san);

    // Check if we just undid an opponent's move (Even index = opponent move)
    let isOpponentMove = moveHistory.length % 2 === 0;

    if (isOpponentMove) {
        console.log("♟️ Opponent move was undone. Replaying...");

        setTimeout(() => {
            let opponentMove = currentSolution[moveHistory.length]; // Next expected move
            let opponentMoveObj = game.move({
                from: opponentMove.substring(0, 2),
                to: opponentMove.substring(2, 4),
                promotion: 'q'
            });

            if (!opponentMoveObj) {
                console.error("❌ Error replaying opponent move:", opponentMove);
                return;
            }

            board.position(game.fen()); // Sync board
            moveHistory.push(opponentMove); // Restore opponent move
            console.log("♟️ Opponent replayed move:", opponentMove);
        }, 1000); // Delay for smoother UX
    }
}




function showHint(){
    if (moveHistory.length > currentSolution.length) {
            console.log(" Puzzle already solved, no hint needed.");
            return;
        }

        let nextMove = currentSolution[moveHistory.length];
        let fromSquare = nextMove.substring(0, 2);
        let toSquare = nextMove.substring(2, 4);

        console.log(` Hint: Move from ${fromSquare} to ${toSquare}`);

        highlightSquare(fromSquare, "yellow");
        highlightSquare(toSquare, "yellow");

        setTimeout(() => {
            removeHighlight(fromSquare);
            removeHighlight(toSquare);
        }, 1500);

        hintsUsed++;
}


function highlightSquare(square, color) {
    $(`#board .square-${square}`).css("background", color);
}

// Helper function to remove highlight
function removeHighlight(square) {
    $(`#board .square-${square}`).css("background", "");
}


// Function to handle toggle switch
function togglePersonalisation() {
    let toggle = document.getElementById("personalisationToggle");
    let isPersonalised = toggle.checked;

    // Save to localStorage
    localStorage.setItem("personalisation", isPersonalised ? "true" : "false");

    console.log("📌 Personalisation set to:", isPersonalised);

    fetch('/reset_rating', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("🔄 User rating reset:", data);
        loadPuzzle();  // Reload puzzle after reset
    })
    .catch(error => console.error("❌ Error resetting rating:", error));
}


function loadPersonalisationState() {
    let toggle = document.getElementById("personalisationToggle");
    let savedState = localStorage.getItem("personalisation");

    if (savedState === null || savedState === "true") {
        // Force reset to false on first visit
        localStorage.setItem("personalisation", "false");
        toggle.checked = false;
    } else {
        toggle.checked = savedState === "true";
    }
}





