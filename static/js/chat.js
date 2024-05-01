// modified from https://github.com/docker/genai-stack/blob/main/front-end/src/lib/chat.store.js

document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.querySelector("#submit");
    const questionArea = document.querySelector("#question");
    const responseArea = document.querySelector("#response");
    const loadingDiv = document.querySelector("#loading");

    submitButton.addEventListener("click", () => {

        // Encode the question
        const question = encodeURI(questionArea.value);

        // Call the event stream
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
        evt.onerror = (e) => {
            // Stream will end with an error
            // and we want to close the connection on end (otherwise it will keep reconnecting)
            evt.close();
        };
    })
});