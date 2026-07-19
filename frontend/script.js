const saveBtn = document.getElementById("saveBtn");

saveBtn.addEventListener("click", function () {

    const name = document.getElementById("username").value;

    if(name === ""){
        alert("Please enter your name.");
        return;
    }

    localStorage.setItem("username", name);

    document.getElementById("welcomeMessage").innerHTML =
    `Welcome, ${name}:) Please paste your code below.`;
    document.getElementById("nameLabel").style.display = "none";
    document.getElementById("username").style.display = "none";
    document.getElementById("saveBtn").style.display = "none";
    document.querySelector(".hero").style.marginBottom = "10px";

});
const username = document.getElementById("username");

username.addEventListener("keypress", function(event){

    if(event.key === "Enter"){
        document.getElementById("saveBtn").click();
    }

});
const reviewBtn = document.getElementById("reviewBtn");

reviewBtn.addEventListener("click", async function () {

    const language = document.getElementById("language").value;
    const code = document.getElementById("code").value;

    const response = await fetch("https://ai-code-review-assistant-bdl5.onrender.com/review", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            language: language,
            code: code
        })

    });

    const data = await response.json();

    document.getElementById("result").innerHTML = data.review;

});
