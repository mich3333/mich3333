"use strict";
// Autonomous Claude - Dashboard TypeScript
// ==================== UTILITY FUNCTIONS ====================
function debounce(func, wait) {
    let timeout = null;
    return (...args) => {
        if (timeout !== null) {
            clearTimeout(timeout);
        }
        timeout = window.setTimeout(() => func(...args), wait);
    };
}
function throttle(func, limit) {
    let inThrottle = false;
    return (...args) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
// ==================== STATE ====================
class DashboardState {
    constructor() {
        this.currentFilter = 'all';
        this.refreshInterval = null;
        this.isAgentRunning = false;
        this.apiUrl = '';
        this.lastActivity = Date.now();
        this.consecutiveErrors = 0;
        this.isOnline = navigator.onLine;
    }
    setFilter(filter) {
        this.currentFilter = filter;
        this.updateActivity();
    }
    setAgentRunning(running) {
        this.isAgentRunning = running;
        this.updateActivity();
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
    updateActivity() {
        this.lastActivity = Date.now();
    }
    isActive() {
        // Consider inactive after 5 minutes of no activity
        return Date.now() - this.lastActivity < 300000;
    }
    incrementErrors() {
        this.consecutiveErrors++;
    }
    resetErrors() {
        this.consecutiveErrors = 0;
    }
    setOnlineStatus(online) {
        this.isOnline = online;
    }
}
const state = new DashboardState();
// ==================== API CLIENT ====================
class ApiClient {
    constructor(baseUrl = '') {
        this.abortControllers = new Map();
        this.requestCache = new Map();
        this.CACHE_TTL = 5000; // 5 seconds cache
        this.baseUrl = baseUrl;
    }
    async call(endpoint, method = 'GET', body = null, options = {}) {
        const { retry = true, timeout = 10000, cache = false } = options;
        // Check cache for GET requests
        if (method === 'GET' && cache) {
            const cached = this.getCached(endpoint);
            if (cached)
                return cached;
        }
        // Cancel previous request to same endpoint
        this.cancelRequest(endpoint);
        // Create new abort controller
        const controller = new AbortController();
        this.abortControllers.set(endpoint, controller);
        // Setup timeout
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        try {
            const response = await this.fetchWithRetry(endpoint, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: body ? JSON.stringify(body) : null,
                signal: controller.signal
            }, retry ? 3 : 1);
            clearTimeout(timeoutId);
            this.abortControllers.delete(endpoint);
            // Cache successful GET requests
            if (method === 'GET' && cache) {
                this.setCache(endpoint, response);
            }
            return response;
        }
        catch (error) {
            clearTimeout(timeoutId);
            this.abortControllers.delete(endpoint);
            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Request timeout');
                }
                console.error('API Error:', error);
                ToastManager.show(this.getErrorMessage(error), 'error');
            }
            throw error;
        }
    }
    async fetchWithRetry(endpoint, options, maxRetries) {
        let lastError = null;
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const response = await fetch(this.baseUrl + endpoint, options);
                const data = await response.json();
                if (!response.ok) {
                    // Don't retry client errors (4xx)
                    if (response.status >= 400 && response.status < 500) {
                        throw new Error(data.error || `Request failed with status ${response.status}`);
                    }
                    // Retry server errors (5xx)
                    throw new Error(data.error || 'Server error');
                }
                return data;
            }
            catch (error) {
                lastError = error instanceof Error ? error : new Error('Unknown error');
                // Don't retry on abort
                if (lastError.name === 'AbortError') {
                    throw lastError;
                }
                // Exponential backoff before retry
                if (attempt < maxRetries - 1) {
                    const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
                    await this.sleep(delay);
                }
            }
        }
        throw lastError || new Error('Request failed');
    }
    cancelRequest(endpoint) {
        const controller = this.abortControllers.get(endpoint);
        if (controller) {
            controller.abort();
            this.abortControllers.delete(endpoint);
        }
    }
    getCached(key) {
        const cached = this.requestCache.get(key);
        if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
            return cached.data;
        }
        this.requestCache.delete(key);
        return null;
    }
    setCache(key, data) {
        this.requestCache.set(key, { data, timestamp: Date.now() });
    }
    getErrorMessage(error) {
        if (!navigator.onLine) {
            return 'אין חיבור לאינטרנט';
        }
        if (error.message.includes('timeout')) {
            return 'הבקשה לקחה יותר מדי זמן';
        }
        return error.message || 'שגיאה לא ידועה';
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    async getStatus() {
        return this.call('/api/status', 'GET', null, { cache: true });
    }
    async getRecentMemories(limit = 50) {
        return this.call(`/api/memories/recent?limit=${limit}`, 'GET', null, { cache: true });
    }
    async searchMemories(type, limit = 50) {
        return this.call(`/api/memories/search?type=${type}&limit=${limit}`, 'GET', null, { cache: true });
    }
    async getMemoryStats() {
        return this.call('/api/memories/stats', 'GET', null, { cache: true });
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
    async claudeThink(situation, context = {}) {
        return this.call('/api/claude/think', 'POST', { situation, context });
    }
    async claudeAnalyze(goal, observations) {
        return this.call('/api/claude/analyze', 'POST', { goal, observations });
    }
    async claudeLearn(experience, outcome) {
        return this.call('/api/claude/learn', 'POST', { experience, outcome });
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
    constructor() {
        this.lastMemories = [];
        this.renderScheduled = false;
    }
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
            // Only re-render if data changed
            if (this.hasChanged(memories)) {
                this.lastMemories = memories;
                this.scheduleRender(memories);
            }
        }
        catch (error) {
            console.error('Failed to load memories:', error);
        }
    }
    hasChanged(newMemories) {
        if (newMemories.length !== this.lastMemories.length) {
            return true;
        }
        // Quick check: compare last item
        if (newMemories.length > 0 && this.lastMemories.length > 0) {
            const lastNew = newMemories[newMemories.length - 1];
            const lastOld = this.lastMemories[this.lastMemories.length - 1];
            return lastNew.id !== lastOld.id || lastNew.content !== lastOld.content;
        }
        return false;
    }
    scheduleRender(memories) {
        if (this.renderScheduled)
            return;
        this.renderScheduled = true;
        requestAnimationFrame(() => {
            this.render(memories);
            this.renderScheduled = false;
        });
    }
    render(memories) {
        const memoriesList = document.getElementById('memoriesList');
        if (!memoriesList)
            return;
        if (memories.length === 0) {
            memoriesList.innerHTML = '<div class="loading">אין זיכרונות</div>';
            return;
        }
        // Use DocumentFragment for better performance
        const fragment = document.createDocumentFragment();
        memories.slice().reverse().forEach(memory => {
            const item = this.createMemoryItem(memory);
            fragment.appendChild(item);
        });
        memoriesList.innerHTML = '';
        memoriesList.appendChild(fragment);
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
        const timestamp = this.formatTimestamp(memory.timestamp);
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
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            // Check if date is valid
            if (isNaN(date.getTime())) {
                return timestamp; // Return original if invalid
            }
            return date.toLocaleString('he-IL', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        catch (error) {
            console.error('Date parsing error:', error);
            return timestamp; // Fallback to original timestamp
        }
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
        const formattedTime = this.formatTimestamp(decision.timestamp);
        if (decision.decision) {
            decisionDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                    ${formattedTime}
                </div>
                <div>${this.escapeHtml(decision.decision)}</div>
            `;
        }
        else if (decision.analysis) {
            decisionDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                    ${formattedTime}
                </div>
                <div><strong>פעולה:</strong> ${this.escapeHtml(decision.analysis.action)}</div>
                <div style="margin-top: 8px;"><strong>נימוק:</strong> ${this.escapeHtml(decision.analysis.reasoning)}</div>
                <div style="margin-top: 8px;"><strong>עדיפות:</strong> ${decision.analysis.priority}</div>
            `;
        }
    }
    static formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            if (isNaN(date.getTime())) {
                return timestamp;
            }
            return date.toLocaleString('he-IL', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        catch (error) {
            console.error('Date parsing error:', error);
            return timestamp;
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
    static async claudeThink() {
        const input = document.getElementById('claudeInput');
        if (!input)
            return;
        const situation = input.value.trim();
        if (!situation) {
            ToastManager.show('נא להכניס שאלה ל-Claude', 'error');
            return;
        }
        const responseDiv = document.getElementById('claudeResponse');
        if (responseDiv) {
            responseDiv.textContent = '🤔 Claude חושב...';
            responseDiv.classList.add('active');
        }
        try {
            const result = await api.claudeThink(situation, {});
            if (responseDiv) {
                responseDiv.textContent = `💡 ${result.decision}`;
            }
            input.value = '';
            ToastManager.show('Claude השיב!', 'success');
            // Refresh memories
            await new MemoryManager().load();
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'שגיאה לא ידועה';
            if (responseDiv) {
                responseDiv.textContent = `❌ שגיאה: ${message}`;
            }
            ToastManager.show('שגיאה בקבלת תשובה מ-Claude', 'error');
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
        // Reload memories with debounce
        this.debouncedLoadMemories();
    }
}
EventHandlers.debouncedLoadMemories = debounce(() => {
    new MemoryManager().load();
}, 300);
// ==================== AUTO REFRESH ====================
class AutoRefresh {
    static start() {
        this.scheduleNext();
    }
    static scheduleNext() {
        const interval = setTimeout(async () => {
            await this.refresh();
            this.scheduleNext();
        }, this.currentInterval);
        state.setRefreshInterval(interval);
    }
    static async refresh() {
        // Skip if page is hidden or user is inactive
        if (document.hidden || !state.isActive()) {
            return;
        }
        // Skip if offline
        if (!state.isOnline) {
            this.increaseInterval();
            return;
        }
        try {
            await new StatusManager().update();
            // Only load memories and stats if agent is running
            if (state.isAgentRunning) {
                await Promise.all([
                    new MemoryManager().load(),
                    new StatsManager().load()
                ]);
            }
            // Success - reset error count and interval
            state.resetErrors();
            this.currentInterval = this.baseInterval;
        }
        catch (error) {
            console.error('Auto-refresh error:', error);
            state.incrementErrors();
            // Exponential backoff on consecutive errors
            if (state.consecutiveErrors >= 3) {
                this.increaseInterval();
            }
        }
    }
    static increaseInterval() {
        this.currentInterval = Math.min(this.currentInterval * 1.5, this.maxInterval);
    }
    static stop() {
        state.clearRefreshInterval();
    }
}
AutoRefresh.baseInterval = 10000; // 10 seconds
AutoRefresh.maxInterval = 60000; // 60 seconds
AutoRefresh.currentInterval = AutoRefresh.baseInterval;
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
    // Claude
    const claudeThinkBtn = document.getElementById('claudeThinkBtn');
    claudeThinkBtn?.addEventListener('click', () => EventHandlers.claudeThink());
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
    const claudeInput = document.getElementById('claudeInput');
    claudeInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            EventHandlers.claudeThink();
        }
    });
}
async function initialize() {
    console.log('🤖 Autonomous Claude Dashboard Loading...');
    // Initialize toast manager
    ToastManager.initialize();
    // Initialize event listeners
    initializeEventListeners();
    // Setup network monitoring
    setupNetworkMonitoring();
    // Load initial data with error handling
    try {
        await Promise.all([
            new StatusManager().update(),
            new MemoryManager().load(),
            new StatsManager().load()
        ]);
    }
    catch (error) {
        console.error('Failed to load initial data:', error);
        ToastManager.show('שגיאה בטעינת נתונים ראשוניים', 'error');
    }
    // Start auto-refresh
    AutoRefresh.start();
    console.log('✅ Dashboard Ready!');
}
function setupNetworkMonitoring() {
    // Monitor online/offline events
    window.addEventListener('online', () => {
        state.setOnlineStatus(true);
        state.resetErrors();
        ToastManager.show('חיבור אינטרנט חזר', 'success');
        EventHandlers.refreshAll();
    });
    window.addEventListener('offline', () => {
        state.setOnlineStatus(false);
        ToastManager.show('אין חיבור לאינטרנט', 'error');
    });
    // Monitor visibility changes
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            state.updateActivity();
        }
    });
    // Track user activity
    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    const throttledActivity = throttle(() => state.updateActivity(), 5000);
    activityEvents.forEach(event => {
        document.addEventListener(event, throttledActivity, { passive: true });
    });
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
