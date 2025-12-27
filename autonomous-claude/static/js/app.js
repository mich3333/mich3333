// Autonomous Claude - Dashboard JavaScript

// State
let currentFilter = 'all';
let refreshInterval = null;
let isAgentRunning = false;

// API Base URL
const API_URL = '';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 Autonomous Claude Dashboard Loading...');

    // Initialize event listeners
    initializeEventListeners();

    // Load initial data
    loadStatus();
    loadMemories();
    loadMemoryStats();

    // Start auto-refresh
    startAutoRefresh();

    console.log('✅ Dashboard Ready!');
});

// Event Listeners
function initializeEventListeners() {
    // Goal setting
    document.getElementById('setGoalBtn').addEventListener('click', setGoal);

    // Agent control
    document.getElementById('startAgentBtn').addEventListener('click', startAgent);
    document.getElementById('stopAgentBtn').addEventListener('click', stopAgent);

    // ChatGPT
    document.getElementById('chatgptThinkBtn').addEventListener('click', chatgptThink);

    // Quick actions
    document.getElementById('refreshBtn').addEventListener('click', refreshAll);
    document.getElementById('clearMemoryBtn').addEventListener('click', clearMemory);

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const type = e.target.dataset.type;
            setFilter(type);
        });
    });

    // Enter key shortcuts
    document.getElementById('goalInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            setGoal();
        }
    });

    document.getElementById('chatgptInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            chatgptThink();
        }
    });
}

// Auto Refresh
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadStatus();
        loadMemories();
        loadMemoryStats();
    }, 3000); // Every 3 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// API Calls
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(API_URL + endpoint, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Load Status
async function loadStatus() {
    try {
        const status = await apiCall('/api/status');

        // Update iteration count
        document.getElementById('iterationCount').textContent = status.iteration || 0;

        // Update brain status
        const brainStatus = document.getElementById('brainStatus');
        brainStatus.textContent = status.brain_available ? '✅' : '❌';

        // Update Qdrant status
        const qdrantStatus = document.getElementById('qdrantStatus');
        qdrantStatus.textContent = status.qdrant_available ? '✅' : '❌';

        // Update status badge
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');

        if (status.running) {
            statusDot.classList.add('active');
            statusText.textContent = 'פעיל';
            isAgentRunning = true;
            updateAgentControls(true);
        } else {
            statusDot.classList.remove('active');
            statusText.textContent = 'מנוחה';
            isAgentRunning = false;
            updateAgentControls(false);
        }

        // Update current goal
        if (status.current_goal) {
            const goalDiv = document.getElementById('currentGoal');
            goalDiv.textContent = `🎯 מטרה נוכחית: ${status.current_goal}`;
            goalDiv.classList.add('active');
        }

        // Update last decision
        if (status.last_decision) {
            updateLastDecision(status.last_decision);
        }

    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

// Load Memories
async function loadMemories() {
    try {
        let endpoint = '/api/memories/recent?limit=50';
        if (currentFilter !== 'all') {
            endpoint = `/api/memories/search?type=${currentFilter}&limit=50`;
        }

        const memories = await apiCall(endpoint);

        // Update memory count
        document.getElementById('memoryCount').textContent = memories.length;

        // Render memories
        const memoriesList = document.getElementById('memoriesList');
        if (memories.length === 0) {
            memoriesList.innerHTML = '<div class="loading">אין זיכרונות</div>';
            return;
        }

        memoriesList.innerHTML = '';
        memories.reverse().forEach(memory => {
            const item = createMemoryItem(memory);
            memoriesList.appendChild(item);
        });

    } catch (error) {
        console.error('Failed to load memories:', error);
    }
}

// Create Memory Item
function createMemoryItem(memory) {
    const div = document.createElement('div');
    div.className = 'memory-item';
    div.dataset.type = memory.type;

    const icons = {
        'goal': '🎯',
        'thought': '💭',
        'action': '⚡',
        'observation': '👁️'
    };

    const icon = icons[memory.type] || '•';
    const timestamp = new Date(memory.timestamp).toLocaleString('he-IL');

    div.innerHTML = `
        <div class="memory-header">
            <span class="memory-type">${icon} ${memory.type}</span>
            <span class="memory-time">${timestamp}</span>
        </div>
        <div class="memory-content">${escapeHtml(memory.content)}</div>
    `;

    return div;
}

// Load Memory Stats
async function loadMemoryStats() {
    try {
        const stats = await apiCall('/api/memories/stats');

        const statsDiv = document.getElementById('memoryStats');
        statsDiv.innerHTML = '';

        if (!stats.by_type || Object.keys(stats.by_type).length === 0) {
            statsDiv.innerHTML = '<div class="loading">אין סטטיסטיקות</div>';
            return;
        }

        const total = stats.total;
        const types = {
            'goal': '🎯 מטרות',
            'thought': '💭 מחשבות',
            'action': '⚡ פעולות',
            'observation': '👁️ תצפיות'
        };

        Object.entries(stats.by_type).forEach(([type, count]) => {
            const percentage = (count / total * 100).toFixed(1);
            const label = types[type] || type;

            const bar = document.createElement('div');
            bar.className = 'stat-bar';
            bar.innerHTML = `
                <div class="stat-bar-header">
                    <span>${label}</span>
                    <span>${count} (${percentage}%)</span>
                </div>
                <div class="stat-bar-progress">
                    <div class="stat-bar-fill" style="width: ${percentage}%"></div>
                </div>
            `;
            statsDiv.appendChild(bar);
        });

    } catch (error) {
        console.error('Failed to load memory stats:', error);
    }
}

// Set Goal
async function setGoal() {
    const input = document.getElementById('goalInput');
    const goal = input.value.trim();

    if (!goal) {
        showToast('נא להכניס מטרה', 'error');
        return;
    }

    try {
        await apiCall('/api/agent/goal', 'POST', { goal });

        const goalDiv = document.getElementById('currentGoal');
        goalDiv.textContent = `🎯 מטרה נוכחית: ${goal}`;
        goalDiv.classList.add('active');

        input.value = '';
        showToast('מטרה הוגדרה בהצלחה!', 'success');

        // Refresh memories
        await loadMemories();

    } catch (error) {
        showToast('שגיאה בהגדרת מטרה', 'error');
    }
}

// Start Agent
async function startAgent() {
    try {
        await apiCall('/api/agent/start', 'POST');

        showToast('הסוכן התחיל לפעול!', 'success');
        updateAgentControls(true);

        const statusDiv = document.getElementById('agentStatus');
        statusDiv.textContent = '⚡ הסוכן פועל...';
        statusDiv.classList.add('active');

    } catch (error) {
        showToast(error.message || 'שגיאה בהפעלת הסוכן', 'error');
    }
}

// Stop Agent
async function stopAgent() {
    try {
        await apiCall('/api/agent/stop', 'POST');

        showToast('הסוכן נעצר', 'info');
        updateAgentControls(false);

        const statusDiv = document.getElementById('agentStatus');
        statusDiv.textContent = '⏸️ הסוכן עצר';

    } catch (error) {
        showToast('שגיאה בעצירת הסוכן', 'error');
    }
}

// Update Agent Controls
function updateAgentControls(running) {
    const startBtn = document.getElementById('startAgentBtn');
    const stopBtn = document.getElementById('stopAgentBtn');

    if (running) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// ChatGPT Think
async function chatgptThink() {
    const input = document.getElementById('chatgptInput');
    const situation = input.value.trim();

    if (!situation) {
        showToast('נא להכניס שאלה ל-ChatGPT', 'error');
        return;
    }

    const responseDiv = document.getElementById('chatgptResponse');
    responseDiv.textContent = '🤔 ChatGPT חושב...';
    responseDiv.classList.add('active');

    try {
        const result = await apiCall('/api/chatgpt/think', 'POST', {
            situation,
            context: {}
        });

        responseDiv.textContent = `💡 ${result.decision}`;
        input.value = '';
        showToast('ChatGPT השיב!', 'success');

        // Refresh memories
        await loadMemories();

    } catch (error) {
        responseDiv.textContent = `❌ שגיאה: ${error.message}`;
        showToast('שגיאה בקבלת תשובה מ-ChatGPT', 'error');
    }
}

// Set Filter
function setFilter(type) {
    currentFilter = type;

    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        if (btn.dataset.type === type) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Reload memories
    loadMemories();
}

// Refresh All
function refreshAll() {
    showToast('מרענן נתונים...', 'info');
    loadStatus();
    loadMemories();
    loadMemoryStats();
}

// Clear Memory
async function clearMemory() {
    if (!confirm('האם אתה בטוח שברצונך למחוק את כל הזיכרונות?')) {
        return;
    }

    try {
        await apiCall('/api/database/clear', 'POST');
        showToast('הזיכרון נוקה בהצלחה', 'success');

        // Refresh all data
        await refreshAll();

    } catch (error) {
        showToast('שגיאה בניקוי הזיכרון', 'error');
    }
}

// Update Last Decision
function updateLastDecision(decision) {
    const decisionDiv = document.getElementById('lastDecision');

    if (decision.decision) {
        decisionDiv.innerHTML = `
            <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                ${new Date(decision.timestamp).toLocaleString('he-IL')}
            </div>
            <div>${escapeHtml(decision.decision)}</div>
        `;
    } else if (decision.analysis) {
        decisionDiv.innerHTML = `
            <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                ${new Date(decision.timestamp).toLocaleString('he-IL')}
            </div>
            <div><strong>פעולה:</strong> ${escapeHtml(decision.analysis.action)}</div>
            <div style="margin-top: 8px;"><strong>נימוק:</strong> ${escapeHtml(decision.analysis.reasoning)}</div>
            <div style="margin-top: 8px;"><strong>עדיפות:</strong> ${decision.analysis.priority}</div>
        `;
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Error Handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    showToast('אירעה שגיאה לא צפויה', 'error');
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
