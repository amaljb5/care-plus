function sendSOS() {

    document.getElementById("message").innerText =
        "Getting your location...";

    if (!navigator.geolocation) {

        alert("Location is not supported by this browser.");

        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;

            fetch("/sos", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    user_id: 1,

                    latitude: latitude,

                    longitude: longitude

                })

            })

            .then(response => response.json())

            .then(data => {

                document.getElementById("message").innerText =
                    "🚨 Emergency activated! Emergency ID: "
                    + data.emergency_id;

            });

        },

        function(error) {

            alert("Unable to get location.");

        }
    );
}







function startVoiceSOS() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        alert("Voice recognition is not supported.");

        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.start();

    document.getElementById("message").innerText =
        "Listening for emergency command...";

    recognition.onresult = function(event) {

        const command =
            event.results[0][0].transcript.toLowerCase();

        console.log(command);

        if (
            command.includes("sos") ||
            command.includes("emergency") ||
            command.includes("help")
        ) {

            sendSOS();

        } else {

            document.getElementById("message").innerText =
                "Emergency command not detected.";
        }
    };
}








const mapURL =
    "https://www.google.com/maps?q="
    + latitude
    + ","
    + longitude;

console.log(mapURL);








function bookCaregiver() {

    const service =
        document.getElementById("service").value;

    fetch("/booking", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            user_id: 1,

            caregiver_id: 1,

            service: service,

            booking_date: "2026-10-10"

        })

    })

    .then(response => response.json())

    .then(data => {

        alert(data.message);

    });
}









function registerVolunteer() {

    fetch("/volunteer", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            name:
                document.getElementById(
                    "volunteerName"
                ).value,

            phone:
                document.getElementById(
                    "volunteerPhone"
                ).value,

            service:
                document.getElementById(
                    "volunteerService"
                ).value

        })

    })

    .then(response => response.json())

    .then(data => {

        alert(data.message);

    });
}