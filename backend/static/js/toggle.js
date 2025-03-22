// Function to handle toggle switch
function togglePersonalisation() {
    let toggle = document.getElementById("personalisationToggle");
    let isPersonalised = toggle.checked;

    // Save to localStorage
    localStorage.setItem("personalisation", isPersonalised ? "true" : "false");

    console.log("📌 Personalisation set to:", isPersonalised);
}


function loadPersonalisationState() {
    let toggle = document.getElementById("personalisationToggle");
    let savedState = localStorage.getItem("personalisation");

    if (savedState === null) {
        // Assign random personalisation on first visit
        let isPersonalised = Math.random() < 0.5; // 50% chance
        localStorage.setItem("personalisation", isPersonalised ? "true" : "false");
        toggle.checked = isPersonalised;
        console.log("🔄 Randomised Personalisation:", isPersonalised);
    } else {
        toggle.checked = savedState === "true";
    }
    togglePersonalisation();
}

// Call function when the page loads
document.addEventListener("DOMContentLoaded", loadPersonalisationState);
