// Nathan Hartzler
// CSC790-SP24-Project
// modified from https://github.com/docker/genai-stack/blob/main/front-end/src/lib/chat.store.js

// Start the function when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    // Get the html objects from the dom
    const submitButton = document.querySelector("#submit");
    const questionArea = document.querySelector("#question");
    const responseArea = document.querySelector("#response");
    const loadingDiv = document.querySelector("#loading");

    // Call the function with the Submit button is clicked
    submitButton.addEventListener("click", () => {
        // Clear the previous response
        responseArea.textContent = '';
        responseArea.style.display = 'none';

        // Encode the question
        const question = encodeURI(questionArea.value);

        // Call the event stream server
        const evtSource = new EventSource("/query-stream?text=" + question);
        evtSource.onmessage = (e) => {
            if (e.data) {
                const data = JSON.parse(e.data);
                if (data.init) {
                    console.log("Using", data.model);
                    // Show the loading gif
                    loadingDiv.style.display = '';
                    return;
                } 
                // Hide the loading gif
                loadingDiv.style.display = 'none';
                // Show the response
                responseArea.style.display = '';
                responseArea.textContent += data.token;
            }
        };
        evtSource.onerror = (e) => {
            // Stream will end with an error
            // and we want to close the connection on end (otherwise it will keep reconnecting)
            evtSource.close();
            loadingDiv.style.display = 'none';
        };
    })
});