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
// Old report section elements removed - now using modal only


// Smart Report Modal elements
const smartReportBtn = document.getElementById('smartReportBtn');
const smartReportModal = document.getElementById('smartReportModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalLoading = document.getElementById('modalLoading');
const modalReportContent = document.getElementById('modalReportContent');
const modalModelBadge = document.getElementById('modalModelBadge');
const modalCopyBtn = document.getElementById('modalCopyBtn');
const modalDownloadBtn = document.getElementById('modalDownloadBtn');

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
            business_name: formData.get('business_name'),
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
        resultsSection.style.display = 'block';

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

    } catch (error) {
        console.error('Error:', error);
        alert('שגיאה בחיפוש דרישות רישוי. אנא נסה שוב.');
        // Show error in containers
        matchesContainer.innerHTML = '<div class="error">שגיאה בטעינת התאמות: ' + error.message + '</div>';
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
        
        // API base updated
    } else {
        console.log('No API base provided');
        if (statusDiv) {
            statusDiv.textContent = 'אנא הזן כתובת שרת';
            statusDiv.style.color = '#f44336';
        }
    }
}

// Format report content for better display
function formatReportContent(reportText) {
    // Convert markdown-like formatting to HTML
    return reportText
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gims, '<ul>$1</ul>')
        .replace(/---/g, '<hr>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}


// Smart Report Modal Functions
function openSmartReportModal() {
    smartReportModal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
    
    // Generate smart report
    generateSmartReport();
}

function closeSmartReportModal() {
    smartReportModal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
    
    // Reset modal content
    modalReportContent.innerHTML = '';
    modalModelBadge.style.display = 'none';
    modalCopyBtn.style.display = 'none';
    modalDownloadBtn.style.display = 'none';
}

async function generateSmartReport() {
    try {
        // Show loading state
        modalLoading.style.display = 'flex';
        modalReportContent.innerHTML = '';
        modalModelBadge.style.display = 'none';
        modalCopyBtn.style.display = 'none';
        modalDownloadBtn.style.display = 'none';

        // Get form data
        const formData = new FormData(form);
        const business = {
            business_name: formData.get('business_name'),
            size: formData.get('size'),
            seats: parseInt(formData.get('seats')) || 0,
            area_sqm: parseInt(formData.get('area_sqm')) || 0,
            staff_count: parseInt(formData.get('staff_count')) || 0,
            features: formData.getAll('features')
        };

        // First get matches
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
        
        // Generate report
        const reportRequest = {
            business: business,
            requirements: matchData.matched
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
        
        // Display the report with proper formatting
        modalReportContent.innerHTML = formatReportContent(reportData.report);
        
        // Show model badge and action buttons
        if (reportData.metadata) {
            modalModelBadge.textContent = `מודל בשימוש: ${reportData.metadata.model || 'Mock'}`;
            modalModelBadge.style.display = 'inline-block';
        }
        
        modalCopyBtn.style.display = 'inline-flex';
        modalDownloadBtn.style.display = 'inline-flex';

    } catch (error) {
        console.error('Error generating smart report:', error);
        modalReportContent.innerHTML = '<div class="error">שגיאה ביצירת הדוח החכם: ' + error.message + '</div>';
    } finally {
        modalLoading.style.display = 'none';
    }
}

// Copy modal report to clipboard
async function copyModalReportToClipboard() {
    try {
        const reportText = modalReportContent.textContent || modalReportContent.innerText;
        await navigator.clipboard.writeText(reportText);
        
        // Show success feedback
        const originalText = modalCopyBtn.textContent;
        modalCopyBtn.textContent = '✅ הועתק!';
        modalCopyBtn.style.background = '#28a745';
        
        setTimeout(() => {
            modalCopyBtn.textContent = originalText;
            modalCopyBtn.style.background = '#28a745';
        }, 2000);
    } catch (error) {
        console.error('Failed to copy report:', error);
        alert('שגיאה בהעתקת הדוח. אנא נסה שוב.');
    }
}

// Download modal report as text file
function downloadModalReportAsText() {
    try {
        const reportText = modalReportContent.textContent || modalReportContent.innerText;
        const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `דוח_חכם_רישוי_עסק_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        // Show success feedback
        const originalText = modalDownloadBtn.textContent;
        modalDownloadBtn.textContent = '✅ הורד!';
        modalDownloadBtn.style.background = '#17a2b8';
        
        setTimeout(() => {
            modalDownloadBtn.textContent = originalText;
            modalDownloadBtn.style.background = '#17a2b8';
        }, 2000);
    } catch (error) {
        console.error('Failed to download report:', error);
        alert('שגיאה בהורדת הדוח. אנא נסה שוב.');
    }
}

// Make setApiBase globally accessible
window.setApiBase = setApiBase;

// Add event listeners for filters
severityFilter.addEventListener('change', filterMatches);
categoryFilter.addEventListener('change', filterMatches);
featureFilter.addEventListener('change', filterMatches);
clearFiltersBtn.addEventListener('click', clearFilters);

// Old report action listeners removed - now using modal only

// Add event listeners for smart report modal
smartReportBtn.addEventListener('click', openSmartReportModal);
modalCloseBtn.addEventListener('click', closeSmartReportModal);
modalBackdrop.addEventListener('click', closeSmartReportModal);
modalCopyBtn.addEventListener('click', copyModalReportToClipboard);
modalDownloadBtn.addEventListener('click', downloadModalReportAsText);

// Close modal on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && smartReportModal.style.display === 'flex') {
        closeSmartReportModal();
    }
});

// Page loaded
document.addEventListener('DOMContentLoaded', function() {
    // Page initialization complete
});
