// Verify that the script is running
alert("Script is running!");

// Add event listener to the form
document.getElementById("cta-form").addEventListener("submit", function (event) {
    event.preventDefault();  // Prevent the default form submission

    const email = document.getElementById("email").value;

    // Check if the email field is filled
    if (email) {
        alert("Thank you! We’ll keep you updated.");
        document.getElementById("cta-form").reset();  // Reset the form after submission
    } else {
        alert("Please enter a valid email.");
    }
});
