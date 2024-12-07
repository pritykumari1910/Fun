document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // Show loading spinner
    document.getElementById('result').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
    formData.append('temperature', document.getElementById('temperature').value);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide loading spinner
        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').style.display = 'block';

        if (response.ok) {
            document.getElementById('category').textContent = data.category;
            document.getElementById('fruitname').textContent = data.fruitname;
            document.getElementById('shelf_life').textContent = data.shelf_life;
        } else {
            displayError(data.error || "An unexpected error occurred.");
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        displayError("An error occurred while making the prediction.");
    }
});

function displayError(errorMessage) {
    document.getElementById('error-text').textContent = errorMessage;
    document.getElementById('error-message').style.display = 'block';
}
