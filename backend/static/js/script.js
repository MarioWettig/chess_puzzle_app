var board;
var game = new Chess();
var currentSolution = [];
var moveHistory = [];

var timer;
var secondsElapsed = 0;

// not sure how useful the logs are, debugging i guess but they aren't in the terminal lol in the browser! ;)

document.addEventListener("DOMContentLoaded", function () {
    loadPuzzle();
});



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
    fetch('/get_puzzle')
        .then(response => response.json())
        .then(data => {
            console.log(" Loaded Puzzle:", data);
            if (data.error) {
                alert("Error loading puzzle: " + data.error);
                return;
            }

            let isBlackToMove = data.fen.split(" ")[1] === "b";
            let playerTurn = !isBlackToMove ? "Black" : "White";

            console.log(" FEN:", data.fen);
            console.log(" Player should play as:", playerTurn);

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

            console.log("processed :", currentSolution);

            let moveCount = currentSolution.length;
            let turnIndicator = document.querySelector('.puzzle-info');
            turnIndicator.innerHTML = `<span style="font-size: 20px; font-weight: bold; color: white;">Play as ${playerTurn}. <b>${Math.ceil(moveCount/2)}</b> best move(s)!</span>`;


            document.getElementById('result-message').innerText = "";
            document.querySelector(".button-next").style.display = "none"; // Hide Next button

            resetTimer();

            setTimeout(() => {
                applyOpponentMove();
                console.log("🔹 Solution After Opponent Move:", currentSolution);
            }, 1200);

            startTimer();
        })
        .catch(error => {
            console.error(" Error fetching puzzle:", error);
        });
}

function applyOpponentMove(){
    if (currentSolution.length > 0) {
        let firstMove = currentSolution.shift();
        console.log("♟️ Opponent's Move:", firstMove);

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
    let userMove = game.move({
        from: source,
        to: target,
        promotion: 'q' // Auto promote to queen if needed
    });

    if (!userMove) {
        console.log(" Illegal move!");
        highlightSquareError(target, "red");
        //console.log(game.fen())
        return 'snapback'; // Reset piece
    }

    let userMoveNotation = source + target; // "e2e4"
    console.log(" User Move :", userMoveNotation);

    if (userMoveNotation !== currentSolution[moveHistory.length]) {
        console.log(" Incorrect move! Try again.");
        showError(" Incorrect move! Try again.", target);
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

    let resultMessage = document.getElementById('result-message');
    resultMessage.innerHTML = "<span style='font-weight: bold; font-size: 18px; color: green;'>✅ Puzzle solved!</span>";

    // Force final board update and clear selection
    setTimeout(() => {
        board.position(game.fen());
        board.resize(); // Fixes visual glitches
    }, 300);

    // Show "Next" button
    document.querySelector('.button-next').style.display = "inline-block";

    return;
    }
}

function showError(message, targetSquare) {
    let resultMessage = document.getElementById('result-message');
    resultMessage.innerText = message;
    resultMessage.style.color = "red";

    highlightSquare(targetSquare, "red");

    setTimeout(() => {
        resultMessage.innerText = "";
    }, 4000);
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
    var lastMove =  game.undo();
    moveHistory.pop();

    if (lastMove) {
        board.position(game.fen()); // Update board to reflect the undone move
        console.log(" Move undone:", lastMove);
        currentSolution.unshift(lastMove.san); // Put the undone move back into solution list
    } else {
        console.log(" No moves to undo!");
    }
}


function showHint(){
    if (moveHistory.length >= currentSolution.length) {
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
}


function highlightSquare(square, color) {
    $(`#board .square-${square}`).css("background", color);
}

// Helper function to remove highlight
function removeHighlight(square) {
    $(`#board .square-${square}`).css("background", "");
}





