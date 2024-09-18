// Verify that the script is running
alert("Script is running!");

// Add event listener to the form
document.getElementById("cta-form").addEventListener("submit", function (event) {
    event.preventDefault();  // Prevent the default form submission

    const email = document.getElementById("email").value;
    const message = document.getElementById("message").value;

    // Check if the email field is filled
    if (email) {
        // Prepare the form data
        const formData = new FormData();
        formData.append("email", email);
        formData.append("message", message);

        // Send the form data to Formspree
        fetch("https://formspree.io/f/mrbzjywo", {
            method: "POST",
            body: formData,  // Send the form data as FormData, not JSON
            headers: {
                "Accept": "application/json"
            }
        }).then(response => {
            if (response.ok) {
                alert("Thank you! We’ll keep you updated.");
                document.getElementById("cta-form").reset();  // Reset the form after successful submission
            } else {
                alert("Something went wrong. Please try again.");
            }
        }).catch(error => {
            alert("There was an error submitting the form. Please try again later.");
            console.error("Form submission error:", error);
        });
    } else {
        alert("Please enter a valid email.");
    }
});
