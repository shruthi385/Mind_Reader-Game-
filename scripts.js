function submitAndStartGame() {
    const playerName = document.getElementById('name').value;

    // Submit the name via AJAX
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "{{ url_for('store_name') }}", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Proceed to start the game after name is stored
            startCountdown(playerName);
        }
    };
    xhr.send("name=" + playerName);
}

function startCountdown(playerName) {
    const mainContent = document.getElementById("main-content");
    const countdownOverlay = document.getElementById("countdown-overlay");
    const countdownNumber = document.getElementById("countdown-number");

    // Blur the background
    mainContent.classList.add("blurred");

    // Show the countdown overlay
    countdownOverlay.classList.remove("d-none");

    let countdown = 3; // Starting number for countdown
    countdownNumber.textContent = countdown;

    // Play countdown sound
    const audio = new Audio("/static/images/countdown.mp3");
    audio.play();

    // Start countdown
    const interval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            countdownNumber.textContent = countdown; // Update the number
        } else if (countdown === 0) {
            countdownNumber.textContent = "Go👉"; // Show "Go"
        } else {
            clearInterval(interval); // Stop the interval
            countdownOverlay.classList.add("d-none"); // Hide countdown overlay
            audio.pause(); // Stop the countdown sound
            audio.currentTime = 0; // Reset the audio to the start
            redirectToGame(playerName); // Redirect to the game page with the name
        }
    }, 1000); // Update every second
}

function redirectToGame(playerName) {
    const gameUrl = "{{ url_for('games') }}";
    window.location.href = gameUrl + "?player_name=" + playerName; // Redirect to game with player name
}
