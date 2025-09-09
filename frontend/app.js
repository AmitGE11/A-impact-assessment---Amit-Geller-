const API_BASE = 'http://localhost:8000/api';

// DOM elements
const form = document.getElementById('businessForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const matchesContainer = document.getElementById('matchesContainer');
const reportSection = document.getElementById('reportSection');
const reportLoading = document.getElementById('reportLoading');
const reportContent = document.getElementById('reportContent');

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        // Get form data
        const formData = new FormData(form);
        const business = {
            size: formData.get('size'),
            seats: parseInt(formData.get('seats')) || 0, // Defensive: treat empty as 0
            area_sqm: parseInt(formData.get('area_sqm')) || 0,
            staff_count: parseInt(formData.get('staff_count')) || 0,
            features: formData.getAll('features')
        };

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'טוען...';
        
        // Show loading in results areas
        matchesContainer.innerHTML = '<div class="loading">טוען התאמות...</div>';
        reportContent.textContent = 'טוען דוח...';
        resultsSection.style.display = 'block';
        reportSection.style.display = 'block';

        // Call match API
        const matchResponse = await fetch(`${API_BASE}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(business)
        });

        if (!matchResponse.ok) {
            throw new Error(`HTTP error! status: ${matchResponse.status}`);
        }

        const matchData = await matchResponse.json();
        
        // Display matches
        displayMatches(matchData.matched);
        
        // Generate report
        await generateReport(business, matchData.matched);

    } catch (error) {
        console.error('Error:', error);
        alert('שגיאה בחיפוש דרישות רישוי. אנא נסה שוב.');
        // Show error in containers
        matchesContainer.innerHTML = '<div class="error">שגיאה בטעינת התאמות: ' + error.message + '</div>';
        reportContent.textContent = 'שגיאה ביצירת הדוח: ' + error.message;
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'קבל דוח';
    }
});

function displayMatches(matches) {
    if (matches.length === 0) {
        matchesContainer.innerHTML = '<p>לא נמצאו דרישות רישוי רלוונטיות.</p>';
    } else {
        matchesContainer.innerHTML = matches.map(match => `
            <div class="match-card priority-${match.priority.toLowerCase()}">
                <div class="match-header">
                    <h3>${match.title}</h3>
                    <span class="priority-badge priority-${match.priority.toLowerCase()}">${getPriorityText(match.priority)}</span>
                </div>
                <div class="match-category">${match.category}</div>
                <div class="match-description">${match.description}</div>
            </div>
        `).join('');
    }
    
    resultsSection.style.display = 'block';
}

async function generateReport(business, requirements) {
    try {
        reportLoading.style.display = 'block';
        reportContent.textContent = '';
        reportSection.style.display = 'block';

        const reportRequest = {
            business: business,
            requirements: requirements
        };

        const reportResponse = await fetch(`${API_BASE}/report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reportRequest)
        });

        if (!reportResponse.ok) {
            throw new Error(`HTTP error! status: ${reportResponse.status}`);
        }

        const reportData = await reportResponse.json();
        reportContent.textContent = reportData.report;

    } catch (error) {
        console.error('Error generating report:', error);
        reportContent.textContent = 'שגיאה ביצירת הדוח: ' + error.message;
    } finally {
        reportLoading.style.display = 'none';
    }
}

function getPriorityText(priority) {
    const priorityMap = {
        'High': 'גבוהה',
        'Medium': 'בינונית',
        'Low': 'נמוכה'
    };
    return priorityMap[priority] || priority;
}

// Health check on page load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (!response.ok) {
            console.warn('Backend health check failed');
        }
    } catch (error) {
        console.warn('Backend not available:', error);
    }
}

// Check backend health on page load
document.addEventListener('DOMContentLoaded', checkHealth);
