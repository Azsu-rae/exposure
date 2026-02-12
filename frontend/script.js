form = document.getElementById("moyenneForm")
form.addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(form);
    console.log("before: ${formData}")
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/save-result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data) // Turn the object into a string
        });

        const result = await response.json();
        console.log('Server says:', result);

        // Your existing UI logic
        const resultArea = document.getElementById("resultArea");
        const status = finalMoyenne >= 10 ? "Admis!" : "Ajourné.";
        resultArea.innerHTML = `<p>${status} Moyenne: <strong>${finalMoyenne.toFixed(2)}</strong></p>`;

    } catch (error) {
        console.error('Error sending data:', error);
    }
});
