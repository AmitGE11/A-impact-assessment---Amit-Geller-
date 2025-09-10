// Function to get API base URL
function getApiBase() {
    if (window.API_BASE) {
        return window.API_BASE;
    }
    const stored = localStorage.getItem("API_BASE");
    if (stored) {
        return stored;
    }
    return "http://localhost:8000";
}

// DOM elements
const form = document.getElementById('businessForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const matchesContainer = document.getElementById('matchesContainer');
const reportSection = document.getElementById('reportSection');
const reportLoading = document.getElementById('reportLoading');
const reportContent = document.getElementById('reportContent');

// Statistics and filter elements
const statsSection = document.getElementById('statsSection');
const totalMatchesEl = document.getElementById('totalMatches');
const highPriorityCountEl = document.getElementById('highPriorityCount');
const mediumPriorityCountEl = document.getElementById('mediumPriorityCount');
const lowPriorityCountEl = document.getElementById('lowPriorityCount');
const priorityChartEl = document.getElementById('priorityChart');
const filterSection = document.getElementById('filterSection');
const severityFilter = document.getElementById('severityFilter');
const categoryFilter = document.getElementById('categoryFilter');
const featureFilter = document.getElementById('featureFilter');
const clearFiltersBtn = document.getElementById('clearFilters');

// Global variables for filtering
let allMatches = [];
let filteredMatches = [];
let priorityChart = null;

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
        const matchResponse = await fetch(`${getApiBase()}/api/match`, {
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
        
        // Store all matches and display them
        allMatches = matchData.matched;
        displayMatches(allMatches);
        updateStatistics(allMatches);
        updateFilterOptions(allMatches);
        
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
    filteredMatches = matches;
    
    if (matches.length === 0) {
        matchesContainer.innerHTML = '<p>לא נמצאו דרישות רישוי רלוונטיות.</p>';
    } else {
        matchesContainer.innerHTML = matches.map(match => `
            <div class="match-card priority-${match.priority.toLowerCase()}" data-priority="${match.priority}" data-category="${match.category}">
                <div class="match-header">
                    <h3>${match.title}</h3>
                    <span class="priority-badge priority-${match.priority.toLowerCase()}">${getPriorityText(match.priority)}</span>
                </div>
                <div class="match-category">${match.category}</div>
                <div class="match-description">${match.description}</div>
                ${match.reasons && match.reasons.length > 0 ? `
                    <div class="match-reasons">
                        <h4>סיבות להתאמה:</h4>
                        <ul class="reasons">
                            ${match.reasons.map(reason => `<li>${formatHebrewArrows(reason)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    resultsSection.style.display = 'block';
    statsSection.style.display = 'block';
    filterSection.style.display = 'block';
}

// Update statistics
function updateStatistics(matches) {
    const total = matches.length;
    const high = matches.filter(m => m.priority === 'High').length;
    const medium = matches.filter(m => m.priority === 'Medium').length;
    const low = matches.filter(m => m.priority === 'Low').length;
    
    totalMatchesEl.textContent = total;
    highPriorityCountEl.textContent = high;
    mediumPriorityCountEl.textContent = medium;
    lowPriorityCountEl.textContent = low;
    
    // Update chart
    updateChart(high, medium, low);
}

// Update chart
function updateChart(high, medium, low) {
    if (priorityChart) {
        priorityChart.destroy();
    }
    
    const ctx = priorityChartEl.getContext('2d');
    priorityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['גבוהה', 'בינונית', 'נמוכה'],
            datasets: [{
                data: [high, medium, low],
                backgroundColor: ['#ff4444', '#ff8800', '#00cc44'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const priorityMap = ['High', 'Medium', 'Low'];
                    const selectedPriority = priorityMap[elementIndex];
                    
                    // Update the severity filter
                    severityFilter.value = selectedPriority;
                    
                    // Apply the filter
                    filterMatches();
                }
            },
            onHover: (event, elements) => {
                // Change cursor to pointer when hovering over chart segments
                event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

// Update filter options
function updateFilterOptions(matches) {
    // Update category filter
    const categories = [...new Set(matches.map(m => m.category))].sort();
    categoryFilter.innerHTML = '<option value="all">הכל</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
    
    // Update feature filter
    const features = new Set();
    matches.forEach(match => {
        if (match.reasons) {
            match.reasons.forEach(reason => {
                if (reason.includes('מאפיין זוהה :')) {
                    const feature = reason.replace('מאפיין זוהה : ', '');
                    features.add(feature);
                }
            });
        }
    });
    
    featureFilter.innerHTML = '<option value="all">הכל</option>';
    [...features].sort().forEach(feature => {
        const option = document.createElement('option');
        option.value = feature;
        option.textContent = feature;
        featureFilter.appendChild(option);
    });
}

// Filter matches
function filterMatches() {
    const severityValue = severityFilter.value;
    const categoryValue = categoryFilter.value;
    const featureValue = featureFilter.value;
    
    let filtered = allMatches;
    
    if (severityValue !== 'all') {
        filtered = filtered.filter(match => match.priority === severityValue);
    }
    
    if (categoryValue !== 'all') {
        filtered = filtered.filter(match => match.category === categoryValue);
    }
    
    if (featureValue !== 'all') {
        filtered = filtered.filter(match => {
            if (!match.reasons) return false;
            return match.reasons.some(reason => 
                reason.includes('מאפיין זוהה :') && reason.includes(featureValue)
            );
        });
    }
    
    displayMatches(filtered);
    updateStatistics(filtered);
}

// Clear filters
function clearFilters() {
    severityFilter.value = 'all';
    categoryFilter.value = 'all';
    featureFilter.value = 'all';
    displayMatches(allMatches);
    updateStatistics(allMatches);
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

        const reportResponse = await fetch(`${getApiBase()}/api/report`, {
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

function formatHebrewArrows(text) {
    // Helper to pretty-print Hebrew arrows (≥ ≤)
    return text
        .replace(/≥/g, '<span class="arrow">≥</span>')
        .replace(/≤/g, '<span class="arrow">≤</span>');
}

// Health check on page load
async function checkHealth() {
    const statusDiv = document.getElementById('apiBaseStatus');
    
    try {
        const response = await fetch(`${getApiBase()}/api/health`);
        if (response.ok) {
            showServerStatus('השרת פעיל', 'success');
            if (statusDiv) {
                statusDiv.textContent = 'השרת זמין!';
                statusDiv.style.color = '#4CAF50';
            }
        } else {
            showServerStatus('השרת לא זמין', 'error');
            if (statusDiv) {
                statusDiv.textContent = 'השרת לא זמין';
                statusDiv.style.color = '#f44336';
            }
        }
    } catch (error) {
        console.warn('Backend not available:', error);
        showServerStatus('השרת לא זמין', 'error');
        if (statusDiv) {
            statusDiv.textContent = 'שגיאה בחיבור לשרת';
            statusDiv.style.color = '#f44336';
        }
    }
}

// Show server status
function showServerStatus(message, type) {
    let statusBanner = document.getElementById('serverStatus');
    if (!statusBanner) {
        statusBanner = document.createElement('div');
        statusBanner.id = 'serverStatus';
        statusBanner.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px 15px;
            border-radius: 5px;
            font-weight: bold;
            z-index: 1000;
            max-width: 200px;
        `;
        document.body.appendChild(statusBanner);
    }
    
    statusBanner.textContent = message;
    statusBanner.style.backgroundColor = type === 'success' ? '#4CAF50' : '#f44336';
    statusBanner.style.color = 'white';
    
    // Show API base selector if server is not available
    if (type === 'error') {
        showApiBaseSelector();
    } else {
        hideApiBaseSelector();
    }
}

// Show API base selector
function showApiBaseSelector() {
    let selector = document.getElementById('apiBaseSelector');
    if (!selector) {
        selector = document.createElement('div');
        selector.id = 'apiBaseSelector';
        selector.style.cssText = `
            position: fixed;
            top: 60px;
            right: 10px;
            background: white;
            border: 2px solid #ccc;
            border-radius: 5px;
            padding: 15px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-width: 250px;
        `;
        
        const currentBase = getApiBase();
        selector.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #333;">הגדר כתובת שרת</h4>
            <input type="text" id="apiBaseInput" placeholder="http://localhost:8000" value="${currentBase}"
                   style="width: 100%; padding: 5px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px;">
            <button onclick="setApiBase()" style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">שמור</button>
            <div id="apiBaseStatus" style="margin-top: 5px; font-size: 12px; color: #666;"></div>
        `;
        
        // Add Enter key handler
        const input = document.getElementById('apiBaseInput');
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    setApiBase();
                }
            });
        }
        
        document.body.appendChild(selector);
    }
    selector.style.display = 'block';
}

// Hide API base selector
function hideApiBaseSelector() {
    const selector = document.getElementById('apiBaseSelector');
    if (selector) {
        selector.style.display = 'none';
    }
}

// Set API base
function setApiBase() {
    const input = document.getElementById('apiBaseInput');
    const statusDiv = document.getElementById('apiBaseStatus');
    const newBase = input.value.trim();
    
    if (newBase) {
        localStorage.setItem("API_BASE", newBase);
        console.log('API base set to:', newBase);
        
        // Show status
        if (statusDiv) {
            statusDiv.textContent = 'שומר...';
            statusDiv.style.color = '#007bff';
        }
        
        // Re-run health check
        checkHealth();
    } else {
        console.log('No API base provided');
        if (statusDiv) {
            statusDiv.textContent = 'אנא הזן כתובת שרת';
            statusDiv.style.color = '#f44336';
        }
    }
}

// Make setApiBase globally accessible
window.setApiBase = setApiBase;

// Add event listeners for filters
severityFilter.addEventListener('change', filterMatches);
categoryFilter.addEventListener('change', filterMatches);
featureFilter.addEventListener('change', filterMatches);
clearFiltersBtn.addEventListener('click', clearFilters);

// Check backend health on page load
document.addEventListener('DOMContentLoaded', checkHealth);
