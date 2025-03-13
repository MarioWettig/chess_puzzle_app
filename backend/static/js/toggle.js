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

   if (savedState === null || savedState === "true") {
        // Force reset to false on first visit
        localStorage.setItem("personalisation", "false");
        toggle.checked = false;
    } else {
        toggle.checked = savedState === "true";
    }
}

// Call function when the page loads
document.addEventListener("DOMContentLoaded", loadPersonalisationState);
