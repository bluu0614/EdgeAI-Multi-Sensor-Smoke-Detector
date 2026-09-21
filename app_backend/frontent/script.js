function getReadings() {
    console.log("Getting readings...");

    //uses the HTTP GET from the readings, GET = fetch() 
    fetch("/api/readings")
        //once it gets data, it converts the .json respnse to something it can read
        .then(response => response.json())
        //then once it converts data, do the rest of this
        .then(data => {
            //console.log is print in javasript, so prints received data
            console.log("Received:", data);

            //if nothing there, print that nothing was there
            if (data.length === 0) {
                console.log("No readings available.");
                return;
            }

            //gets newest reading, so by timestamp
            const latest = data[0];

            //puts the data received into the html
            document.getElementById("smoke").textContent = latest.smoke;
            document.getElementById("temperature").textContent = latest.temperature + " °C";
            document.getElementById("humidity").textContent = latest.humidity + " %";
            document.getElementById("battery").textContent = latest.battery + " %";
            document.getElementById("alarm").textContent = latest.alarm;
            document.getElementById("confidence").textContent = latest.confidence;
        });
}

getReadings();

setInterval(getReadings, 10000);