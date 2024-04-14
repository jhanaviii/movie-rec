document.getElementById("movieForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission
    
    var formData = new FormData(this); // Get form data
    
    fetch("/", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.recommendations) {
            var table = "<table><tr><th>Movie Title</th><th>Similarity Score</th></tr>";
            data.recommendations.forEach(function(item) {
                table += "<tr><td>" + item[0] + "</td><td>" + item[1] + "</td></tr>";
            });
            table += "</table>";
            document.getElementById("recommendations").innerHTML = table; // Append table to recommendations div
        } else {
            document.getElementById("recommendations").innerHTML = "No recommendations found.";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("recommendations").innerHTML = "An error occurred while fetching recommendations.";
    });
});
