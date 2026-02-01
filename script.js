function getWeather() {
    console.log("Button clicked");

    const city = document.getElementById("city").value;

    if(city===""){
        alert("Enter City Name");
        return;
    }

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city: city })
    })
    .then(response => response.json())
    .then(data => {
        console.log("server Data:",data);
        
        document.getElementById("result").style.display="block";
        document.getElementById("temp").innerText = data.current_temp;
        document.getElementById("humidity").innerText = data.humidity;
        document.getElementById("condition").innerText = data.condition;
        document.getElementById("rain").innerText = data.rain;
        document.getElementById("activity").innerText = data.activity;
        document.getElementById("feels").innerText = data.feels_like;
        document.getElementById("wind_speed").innerText = data.wind_speed;
        document.getElementById("wind_direction").innerText = data.wind_direction;

        // Change background based on rain
        const video = document.getElementById("bgVideo");

        if (data.rain.toLowerCase() === "yes" || data.condition.toLowerCase().includes("rain")) {
            video.src = "/static/videos/rains.mp4";
        } else {
            video.src = "/static/videos/no_rain.mp4";
        }
        


    })
    .catch(error => alert("Invalid city or API error"));
}