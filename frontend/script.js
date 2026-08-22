const reviewBtn = document.getElementById("reviewBtn");

reviewBtn.addEventListener("click", async function () {

    const language = document.getElementById("language").value;
    const code = document.getElementById("code").value;
    const result = document.getElementById("result");

    // Check if code was entered
    if (code.trim() === "") {
        result.innerHTML = "Please enter some code to review.";
        return;
    }

    // Show loading message
    result.innerHTML = "Reviewing your code...";

    try {
        const response = await fetch("https://ai-code-review-assistant-1-7ctp.onrender.com/review", 
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    language: language,
                    code: code
                })
            }
        );

        const data = await response.json();

        // Handle backend errors
        if (data.error) {
            result.innerHTML = "Error: " + data.error;
            return;
        }

        // Display AI review
        result.innerHTML = data.review;

    } catch (error) {
        result.innerHTML =
            "Unable to connect to the backend. Please try again.";
        console.error(error);
    }
});