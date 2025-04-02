const loader = document.querySelector("#loader")

async function uploadFiles() {
    const jobFile = document.getElementById("jobFile").files[0];
    const resumeFiles = document.getElementById("resumeFiles").files;

    if (!jobFile || resumeFiles.length === 0) {
        alert("Please upload both the job description and resumes.");
        return;
    }

    let formData = new FormData();
    formData.append("job_file", jobFile);
    
    for (let file of resumeFiles) {
        formData.append("resumes", file);
    }

    try {
        loader.style.display = "block"
        const Host ="https://5732-34-16-144-117.ngrok-free.app/"
        const response = await fetch(`${Host}/upload`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        // console.log(result.shortlisted)
        loader.style.display = "none"
        displayResults(result);
    } catch (error) {
        loader.style.display = "none"
        console.error("Error:", error);
        alert("Error processing resumes.");
    }
}

function displayResults(result) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<h3>Shortlisted Candidates:</h3><ul>";

    result.shortlisted.forEach(candidate => {
        resultsDiv.innerHTML += `<li> <div class="card" id="jobCard">
        <h3>Job Title: <span id="jobTitle">${candidate.job_title}</span></h3>
        <p><strong>Email:</strong> <span id="email">${candidate.email}</span></p>
        <a id="resumeLink" class="resume-link" >${candidate.resume}</a>
    </div>
</li>`;
    });

    resultsDiv.innerHTML += "</ul>";
}
