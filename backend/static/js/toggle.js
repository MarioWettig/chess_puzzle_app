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

    if (savedState === "true") {
        toggle.checked = true;
    } else {
        toggle.checked = false;
    }
}

// Call function when the page loads
document.addEventListener("DOMContentLoaded", loadPersonalisationState);
