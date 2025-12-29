"use strict";
// Autonomous Claude - Dashboard TypeScript
// ==================== STATE ====================
class DashboardState {
    constructor() {
        this.currentFilter = 'all';
        this.refreshInterval = null;
        this.isAgentRunning = false;
        this.apiUrl = '';
    }
    setFilter(filter) {
        this.currentFilter = filter;
    }
    setAgentRunning(running) {
        this.isAgentRunning = running;
    }
    setRefreshInterval(interval) {
        this.refreshInterval = interval;
    }
    clearRefreshInterval() {
        if (this.refreshInterval !== null) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}
const state = new DashboardState();
// ==================== API CLIENT ====================
class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    async call(endpoint, method = 'GET', body = null) {
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
            const response = await fetch(this.baseUrl + endpoint, options);
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            return data;
        }
        catch (error) {
            console.error('API Error:', error);
            const message = error instanceof Error ? error.message : 'Unknown error';
            ToastManager.show(message, 'error');
            throw error;
        }
    }
    async getStatus() {
        return this.call('/api/status');
    }
    async getRecentMemories(limit = 50) {
        return this.call(`/api/memories/recent?limit=${limit}`);
    }
    async searchMemories(type, limit = 50) {
        return this.call(`/api/memories/search?type=${type}&limit=${limit}`);
    }
    async getMemoryStats() {
        return this.call('/api/memories/stats');
    }
    async addMemory(type, content) {
        return this.call('/api/memories/add', 'POST', { type, content });
    }
    async setGoal(goal) {
        return this.call('/api/agent/goal', 'POST', { goal });
    }
    async startAgent() {
        return this.call('/api/agent/start', 'POST');
    }
    async stopAgent() {
        return this.call('/api/agent/stop', 'POST');
    }
    async chatgptThink(situation, context = {}) {
        return this.call('/api/chatgpt/think', 'POST', { situation, context });
    }
    async chatgptAnalyze(goal, observations) {
        return this.call('/api/chatgpt/analyze', 'POST', { goal, observations });
    }
    async chatgptLearn(experience, outcome) {
        return this.call('/api/chatgpt/learn', 'POST', { experience, outcome });
    }
    async clearDatabase() {
        return this.call('/api/database/clear', 'POST');
    }
}
const api = new ApiClient('');
// ==================== TOAST MANAGER ====================
class ToastManager {
    static initialize() {
        this.container = document.getElementById('toastContainer');
    }
    static show(message, type = 'info') {
        if (!this.container) {
            console.error('Toast container not found');
            return;
        }
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        this.container.appendChild(toast);
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (this.container) {
                    this.container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}
ToastManager.container = null;
// ==================== UI MANAGERS ====================
class StatusManager {
    async update() {
        try {
            const status = await api.getStatus();
            // Update iteration count
            this.updateElement('iterationCount', status.iteration.toString());
            // Update brain status
            this.updateElement('brainStatus', status.brain_available ? '✅' : '❌');
            // Update Qdrant status
            this.updateElement('qdrantStatus', status.qdrant_available ? '✅' : '❌');
            // Update status badge
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            if (statusDot && statusText) {
                if (status.running) {
                    statusDot.classList.add('active');
                    statusText.textContent = 'פעיל';
                    state.setAgentRunning(true);
                    AgentControls.update(true);
                }
                else {
                    statusDot.classList.remove('active');
                    statusText.textContent = 'מנוחה';
                    state.setAgentRunning(false);
                    AgentControls.update(false);
                }
            }
            // Update current goal
            if (status.current_goal) {
                const goalDiv = document.getElementById('currentGoal');
                if (goalDiv) {
                    goalDiv.textContent = `🎯 מטרה נוכחית: ${status.current_goal}`;
                    goalDiv.classList.add('active');
                }
            }
            // Update last decision
            if (status.last_decision) {
                DecisionDisplay.update(status.last_decision);
            }
        }
        catch (error) {
            console.error('Failed to load status:', error);
        }
    }
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
}
class MemoryManager {
    async load() {
        try {
            let memories;
            if (state.currentFilter === 'all') {
                memories = await api.getRecentMemories(50);
            }
            else {
                memories = await api.searchMemories(state.currentFilter, 50);
            }
            // Update memory count
            this.updateElement('memoryCount', memories.length.toString());
            // Render memories
            this.render(memories);
        }
        catch (error) {
            console.error('Failed to load memories:', error);
        }
    }
    render(memories) {
        const memoriesList = document.getElementById('memoriesList');
        if (!memoriesList)
            return;
        if (memories.length === 0) {
            memoriesList.innerHTML = '<div class="loading">אין זיכרונות</div>';
            return;
        }
        memoriesList.innerHTML = '';
        memories.reverse().forEach(memory => {
            const item = this.createMemoryItem(memory);
            memoriesList.appendChild(item);
        });
    }
    createMemoryItem(memory) {
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
            <div class="memory-content">${this.escapeHtml(memory.content)}</div>
        `;
        return div;
    }
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
class StatsManager {
    async load() {
        try {
            const stats = await api.getMemoryStats();
            const statsDiv = document.getElementById('memoryStats');
            if (!statsDiv)
                return;
            statsDiv.innerHTML = '';
            if (!stats.by_type || Object.keys(stats.by_type).length === 0) {
                statsDiv.innerHTML = '<div class="loading">אין סטטיסטיקות</div>';
                return;
            }
            this.render(statsDiv, stats);
        }
        catch (error) {
            console.error('Failed to load memory stats:', error);
        }
    }
    render(container, stats) {
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
            container.appendChild(bar);
        });
    }
}
class DecisionDisplay {
    static update(decision) {
        const decisionDiv = document.getElementById('lastDecision');
        if (!decisionDiv)
            return;
        if (decision.decision) {
            decisionDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                    ${new Date(decision.timestamp).toLocaleString('he-IL')}
                </div>
                <div>${this.escapeHtml(decision.decision)}</div>
            `;
        }
        else if (decision.analysis) {
            decisionDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                    ${new Date(decision.timestamp).toLocaleString('he-IL')}
                </div>
                <div><strong>פעולה:</strong> ${this.escapeHtml(decision.analysis.action)}</div>
                <div style="margin-top: 8px;"><strong>נימוק:</strong> ${this.escapeHtml(decision.analysis.reasoning)}</div>
                <div style="margin-top: 8px;"><strong>עדיפות:</strong> ${decision.analysis.priority}</div>
            `;
        }
    }
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
class AgentControls {
    static update(running) {
        const startBtn = document.getElementById('startAgentBtn');
        const stopBtn = document.getElementById('stopAgentBtn');
        if (startBtn && stopBtn) {
            if (running) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            }
            else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
    }
}
// ==================== EVENT HANDLERS ====================
class EventHandlers {
    static async setGoal() {
        const input = document.getElementById('goalInput');
        if (!input)
            return;
        const goal = input.value.trim();
        if (!goal) {
            ToastManager.show('נא להכניס מטרה', 'error');
            return;
        }
        try {
            await api.setGoal(goal);
            const goalDiv = document.getElementById('currentGoal');
            if (goalDiv) {
                goalDiv.textContent = `🎯 מטרה נוכחית: ${goal}`;
                goalDiv.classList.add('active');
            }
            input.value = '';
            ToastManager.show('מטרה הוגדרה בהצלחה!', 'success');
            // Refresh memories
            await new MemoryManager().load();
        }
        catch (error) {
            ToastManager.show('שגיאה בהגדרת מטרה', 'error');
        }
    }
    static async startAgent() {
        try {
            await api.startAgent();
            ToastManager.show('הסוכן התחיל לפעול!', 'success');
            AgentControls.update(true);
            const statusDiv = document.getElementById('agentStatus');
            if (statusDiv) {
                statusDiv.textContent = '⚡ הסוכן פועל...';
                statusDiv.classList.add('active');
            }
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'שגיאה בהפעלת הסוכן';
            ToastManager.show(message, 'error');
        }
    }
    static async stopAgent() {
        try {
            await api.stopAgent();
            ToastManager.show('הסוכן נעצר', 'info');
            AgentControls.update(false);
            const statusDiv = document.getElementById('agentStatus');
            if (statusDiv) {
                statusDiv.textContent = '⏸️ הסוכן עצר';
            }
        }
        catch (error) {
            ToastManager.show('שגיאה בעצירת הסוכן', 'error');
        }
    }
    static async chatgptThink() {
        const input = document.getElementById('chatgptInput');
        if (!input)
            return;
        const situation = input.value.trim();
        if (!situation) {
            ToastManager.show('נא להכניס שאלה ל-ChatGPT', 'error');
            return;
        }
        const responseDiv = document.getElementById('chatgptResponse');
        if (responseDiv) {
            responseDiv.textContent = '🤔 ChatGPT חושב...';
            responseDiv.classList.add('active');
        }
        try {
            const result = await api.chatgptThink(situation, {});
            if (responseDiv) {
                responseDiv.textContent = `💡 ${result.decision}`;
            }
            input.value = '';
            ToastManager.show('ChatGPT השיב!', 'success');
            // Refresh memories
            await new MemoryManager().load();
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'שגיאה לא ידועה';
            if (responseDiv) {
                responseDiv.textContent = `❌ שגיאה: ${message}`;
            }
            ToastManager.show('שגיאה בקבלת תשובה מ-ChatGPT', 'error');
        }
    }
    static async refreshAll() {
        ToastManager.show('מרענן נתונים...', 'info');
        await new StatusManager().update();
        await new MemoryManager().load();
        await new StatsManager().load();
    }
    static async clearMemory() {
        if (!confirm('האם אתה בטוח שברצונך למחוק את כל הזיכרונות?')) {
            return;
        }
        try {
            await api.clearDatabase();
            ToastManager.show('הזיכרון נוקה בהצלחה', 'success');
            // Refresh all data
            await EventHandlers.refreshAll();
        }
        catch (error) {
            ToastManager.show('שגיאה בניקוי הזיכרון', 'error');
        }
    }
    static setFilter(type) {
        state.setFilter(type);
        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            const button = btn;
            if (button.dataset.type === type) {
                button.classList.add('active');
            }
            else {
                button.classList.remove('active');
            }
        });
        // Reload memories
        new MemoryManager().load();
    }
}
// ==================== AUTO REFRESH ====================
class AutoRefresh {
    static start() {
        const interval = setInterval(async () => {
            // Only refresh if page is visible (performance optimization)
            if (!document.hidden) {
                await new StatusManager().update();
                // Only load memories and stats if agent is running
                if (state.isAgentRunning) {
                    await new MemoryManager().load();
                    await new StatsManager().load();
                }
            }
        }, 10000); // Every 10 seconds - optimized for better performance
        state.setRefreshInterval(interval);
    }
    static stop() {
        state.clearRefreshInterval();
    }
}
// ==================== INITIALIZATION ====================
function initializeEventListeners() {
    // Goal setting
    const setGoalBtn = document.getElementById('setGoalBtn');
    setGoalBtn?.addEventListener('click', () => EventHandlers.setGoal());
    // Agent control
    const startAgentBtn = document.getElementById('startAgentBtn');
    startAgentBtn?.addEventListener('click', () => EventHandlers.startAgent());
    const stopAgentBtn = document.getElementById('stopAgentBtn');
    stopAgentBtn?.addEventListener('click', () => EventHandlers.stopAgent());
    // ChatGPT
    const chatgptThinkBtn = document.getElementById('chatgptThinkBtn');
    chatgptThinkBtn?.addEventListener('click', () => EventHandlers.chatgptThink());
    // Quick actions
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn?.addEventListener('click', () => EventHandlers.refreshAll());
    const clearMemoryBtn = document.getElementById('clearMemoryBtn');
    clearMemoryBtn?.addEventListener('click', () => EventHandlers.clearMemory());
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.target;
            const type = target.dataset.type;
            if (type) {
                EventHandlers.setFilter(type);
            }
        });
    });
    // Enter key shortcuts
    const goalInput = document.getElementById('goalInput');
    goalInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            EventHandlers.setGoal();
        }
    });
    const chatgptInput = document.getElementById('chatgptInput');
    chatgptInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            EventHandlers.chatgptThink();
        }
    });
}
async function initialize() {
    console.log('🤖 Autonomous Claude Dashboard Loading...');
    // Initialize toast manager
    ToastManager.initialize();
    // Initialize event listeners
    initializeEventListeners();
    // Load initial data
    await new StatusManager().update();
    await new MemoryManager().load();
    await new StatsManager().load();
    // Start auto-refresh
    AutoRefresh.start();
    console.log('✅ Dashboard Ready!');
}
// ==================== MAIN ====================
document.addEventListener('DOMContentLoaded', () => {
    initialize().catch(error => {
        console.error('Initialization error:', error);
        ToastManager.show('שגיאה באתחול Dashboard', 'error');
    });
});
// Cleanup on unload
window.addEventListener('beforeunload', () => {
    AutoRefresh.stop();
});
// Error Handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    ToastManager.show('אירעה שגיאה לא צפויה', 'error');
});
//# sourceMappingURL=app.js.map