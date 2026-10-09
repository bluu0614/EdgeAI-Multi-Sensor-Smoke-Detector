function getLatestReading() {
    console.log("Getting latest readings...");

    //uses the HTTP GET from the readings, GET = fetch() 
    fetch("/api/latest")
        //once it gets data, it converts the .json respnse to something it can read
        .then(response => response.json())
        //then once it converts data, do the rest of this
        .then(data => {
            //console.log is print in javasript, so prints received data
            console.log("Received:", data);

            //if nothing there, print that nothing was there
            if (data.message) {
                console.log(data.message);
                return;
            }


            //puts the data received into the html
            document.getElementById("smoke").textContent = data.smoke;
            document.getElementById("temperature").textContent = data.temperature + " °C";
            document.getElementById("humidity").textContent = data.humidity + " %";
            document.getElementById("co").textContent = data.co + " ppm";
            document.getElementById("battery").textContent = data.battery + " %";
            document.getElementById("alarm").textContent = data.alarm === 1 ? "Active": "Inactive";
            document.getElementById("confidence").textContent = data.confidence;
        });
}

getLatestReading();

setInterval(getLatestReading, 10000);
