document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const textForm = document.getElementById('text-form');
    const uploadBtn = document.getElementById('upload-btn');
    const textBtn = document.getElementById('text-btn');
    const uploadSpinner = document.getElementById('upload-spinner');
    const textSpinner = document.getElementById('text-spinner');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const errorAlert = document.getElementById('error-alert');

    const handleFetch = (url, options, btn, spinner) => {
        setLoading(btn, spinner, true);
        clearResults();

        fetch(url, options)
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return null; // Stop processing if redirected
                }
                return response.json();
            })
            .then(data => {
                if (!data) return; // Happens on redirect

                if (data.error) {
                    showError(data.error);
                } else {
                    // The data from the server is the full object
                    renderResults(data);
                }
            })
            .catch(err => {
                showError(`An unexpected error occurred. Please ensure you are logged in and try again.`);
            })
            .finally(() => {
                setLoading(btn, spinner, false);
            });
    };

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file-input');
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select a file to upload.');
                return;
            }
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            handleFetch('/upload_image', { method: 'POST', body: formData }, uploadBtn, uploadSpinner);
        });
    }

    if (textForm) {
        textForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const textInput = document.getElementById('text-input');
            const text = textInput.value;
            if (!text.trim()) {
                showError('Please enter some text to analyze.');
                return;
            }
            const options = {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            };
            handleFetch('/quick_analysis', options, textBtn, textSpinner);
        });
    }

    function setLoading(btn, spinner, isLoading) {
        if (isLoading) {
            btn.disabled = true;
            spinner.classList.remove('d-none');
        } else {
            btn.disabled = false;
            spinner.classList.add('d-none');
        }
    }

    function clearResults() {
        resultsContainer.classList.add('d-none');
        errorAlert.classList.add('d-none');
        resultsContent.innerHTML = '';
    }

    function showError(message) {
        resultsContainer.classList.remove('d-none');
        errorAlert.textContent = message;
        errorAlert.classList.remove('d-none');
        resultsContent.innerHTML = '';
    }

    function renderResults(data) {
        resultsContainer.classList.remove('d-none');
        errorAlert.classList.add('d-none');

        const { extraction, analysis, image_url } = data;

        if (!extraction || !analysis) {
            showError('The analysis response from the server was incomplete. Please try again.');
            return;
        }

        const trafficLightColor = {
            'Green': 'bg-success',
            'Yellow': 'bg-warning',
            'Red': 'bg-danger'
        }[analysis.traffic_light] || 'bg-secondary';

        let imageHtml = image_url ? `<img src="${image_url}" class="img-fluid rounded mb-3" alt="Product Image">` : '';

        let html = `
            <div class="row">
                <div class="col-md-4">
                    ${imageHtml}
                    <h4>${extraction.product_name || 'Product Analysis'}</h4>
                    <div class="d-flex align-items-center mb-3">
                        <div class="p-3 rounded-circle ${trafficLightColor}" style="width: 50px; height: 50px;"></div>
                        <div class="ms-3">
                            <h5 class="mb-0">Score: ${analysis.overall_safety_score}/100</h5>
                            <p class="mb-0"><strong>${analysis.traffic_light}</strong></p>
                        </div>
                    </div>
                    <p class="lead">${analysis.summary}</p>
                    <h5>Extracted Ingredients</h5>
                    <div class="mb-3 p-3 bg-light rounded">
                        ${extraction.ingredients.join(', ')}
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="accordion" id="analysisAccordion">
        `;

        if (analysis.harmful_ingredients && analysis.harmful_ingredients.length > 0) {
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingHarmful">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseHarmful" aria-expanded="true" aria-controls="collapseHarmful">
                            Harmful Ingredients
                        </button>
                    </h2>
                    <div id="collapseHarmful" class="accordion-collapse collapse show" aria-labelledby="headingHarmful">
                        <div class="accordion-body">
                            ${analysis.harmful_ingredients.map(item => `
                                <h6>${item.ingredient}</h6>
                                <p><strong>Reason:</strong> ${item.reason}</p>
                                <p><strong>Description:</strong> ${item.description}</p>
                                <p><strong>How to identify:</strong> ${item.identification}</p>
                                <hr>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        if (analysis.recommendations && analysis.recommendations.length > 0) {
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingRecs">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseRecs" aria-expanded="false" aria-controls="collapseRecs">
                            Recommendations
                        </button>
                    </h2>
                    <div id="collapseRecs" class="accordion-collapse collapse" aria-labelledby="headingRecs">
                        <div class="accordion-body">
                            <ul class="list-group list-group-flush">
                                ${analysis.recommendations.map(rec => `<li class="list-group-item">${rec}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        if (analysis.precautionary_tips && analysis.precautionary_tips.length > 0) {
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingTips">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTips" aria-expanded="false" aria-controls="collapseTips">
                            Precautionary Tips
                        </button>
                    </h2>
                    <div id="collapseTips" class="accordion-collapse collapse" aria-labelledby="headingTips">
                        <div class="accordion-body">
                             <ul class="list-group list-group-flush">
                                ${analysis.precautionary_tips.map(tip => `<li class="list-group-item">${tip}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        html += '</div></div></div>'; // Close accordion and columns

        resultsContent.innerHTML = html;
    }
});
