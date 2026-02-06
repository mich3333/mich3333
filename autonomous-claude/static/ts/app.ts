// Autonomous Claude - Dashboard TypeScript

// ==================== INTERFACES ====================

interface Memory {
    id: number;
    type: 'goal' | 'thought' | 'action' | 'observation';
    content: string;
    timestamp: string;
}

interface AgentStatus {
    running: boolean;
    current_goal: string | null;
    iteration: number;
    last_decision: LastDecision | null;
    brain_available: boolean;
    anthropic_key_set: boolean;
    qdrant_available: boolean;
}

interface LastDecision {
    situation?: string;
    decision?: string;
    goal?: string;
    analysis?: {
        action: string;
        reasoning: string;
        priority: string;
    };
    timestamp: string;
}

interface MemoryStats {
    total: number;
    by_type: Record<string, number>;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface ApiResponse<T = any> {
    success?: boolean;
    error?: string;
    data?: T;
    [key: string]: any;
}

// ==================== UTILITY FUNCTIONS ====================

function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: number | null = null;
    return (...args: Parameters<T>) => {
        if (timeout !== null) {
            clearTimeout(timeout);
        }
        timeout = window.setTimeout(() => func(...args), wait);
    };
}

function throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle: boolean = false;
    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ==================== STATE ====================

class DashboardState {
    currentFilter: string = 'all';
    refreshInterval: number | null = null;
    isAgentRunning: boolean = false;
    apiUrl: string = '';
    lastActivity: number = Date.now();
    consecutiveErrors: number = 0;
    isOnline: boolean = navigator.onLine;

    setFilter(filter: string): void {
        this.currentFilter = filter;
        this.updateActivity();
    }

    setAgentRunning(running: boolean): void {
        this.isAgentRunning = running;
        this.updateActivity();
    }

    setRefreshInterval(interval: number): void {
        this.refreshInterval = interval;
    }

    clearRefreshInterval(): void {
        if (this.refreshInterval !== null) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    updateActivity(): void {
        this.lastActivity = Date.now();
    }

    isActive(): boolean {
        // Consider inactive after 5 minutes of no activity
        return Date.now() - this.lastActivity < 300000;
    }

    incrementErrors(): void {
        this.consecutiveErrors++;
    }

    resetErrors(): void {
        this.consecutiveErrors = 0;
    }

    setOnlineStatus(online: boolean): void {
        this.isOnline = online;
    }
}

const state = new DashboardState();

// ==================== API CLIENT ====================

class ApiClient {
    private baseUrl: string;
    private abortControllers: Map<string, AbortController> = new Map();
    private requestCache: Map<string, { data: any; timestamp: number }> = new Map();
    private readonly CACHE_TTL = 5000; // 5 seconds cache

    constructor(baseUrl: string = '') {
        this.baseUrl = baseUrl;
    }

    async call<T>(
        endpoint: string,
        method: string = 'GET',
        body: any = null,
        options: { retry?: boolean; timeout?: number; cache?: boolean } = {}
    ): Promise<T> {
        const { retry = true, timeout = 10000, cache = false } = options;

        // Check cache for GET requests
        if (method === 'GET' && cache) {
            const cached = this.getCached(endpoint);
            if (cached) return cached as T;
        }

        // Cancel previous request to same endpoint
        this.cancelRequest(endpoint);

        // Create new abort controller
        const controller = new AbortController();
        this.abortControllers.set(endpoint, controller);

        // Setup timeout
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await this.fetchWithRetry<T>(
                endpoint,
                {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: body ? JSON.stringify(body) : null,
                    signal: controller.signal
                },
                retry ? 3 : 1
            );

            clearTimeout(timeoutId);
            this.abortControllers.delete(endpoint);

            // Cache successful GET requests
            if (method === 'GET' && cache) {
                this.setCache(endpoint, response);
            }

            return response;
        } catch (error) {
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

    private async fetchWithRetry<T>(
        endpoint: string,
        options: RequestInit,
        maxRetries: number
    ): Promise<T> {
        let lastError: Error | null = null;

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

                return data as T;
            } catch (error) {
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

    private cancelRequest(endpoint: string): void {
        const controller = this.abortControllers.get(endpoint);
        if (controller) {
            controller.abort();
            this.abortControllers.delete(endpoint);
        }
    }

    private getCached(key: string): any | null {
        const cached = this.requestCache.get(key);
        if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
            return cached.data;
        }
        this.requestCache.delete(key);
        return null;
    }

    private setCache(key: string, data: any): void {
        this.requestCache.set(key, { data, timestamp: Date.now() });
    }

    private getErrorMessage(error: Error): string {
        if (!navigator.onLine) {
            return 'אין חיבור לאינטרנט';
        }
        if (error.message.includes('timeout')) {
            return 'הבקשה לקחה יותר מדי זמן';
        }
        return error.message || 'שגיאה לא ידועה';
    }

    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async getStatus(): Promise<AgentStatus> {
        return this.call<AgentStatus>('/api/status', 'GET', null, { cache: true });
    }

    async getRecentMemories(limit: number = 50): Promise<Memory[]> {
        return this.call<Memory[]>(`/api/memories/recent?limit=${limit}`, 'GET', null, { cache: true });
    }

    async searchMemories(type: string, limit: number = 50): Promise<Memory[]> {
        return this.call<Memory[]>(`/api/memories/search?type=${type}&limit=${limit}`, 'GET', null, { cache: true });
    }

    async getMemoryStats(): Promise<MemoryStats> {
        return this.call<MemoryStats>('/api/memories/stats', 'GET', null, { cache: true });
    }

    async addMemory(type: string, content: string): Promise<ApiResponse<{ id: number }>> {
        return this.call('/api/memories/add', 'POST', { type, content });
    }

    async setGoal(goal: string): Promise<ApiResponse<{ goal: string }>> {
        return this.call('/api/agent/goal', 'POST', { goal });
    }

    async startAgent(): Promise<ApiResponse<{}>> {
        return this.call('/api/agent/start', 'POST');
    }

    async stopAgent(): Promise<ApiResponse<{}>> {
        return this.call('/api/agent/stop', 'POST');
    }

    async claudeThink(situation: string, context: any = {}): Promise<ApiResponse<{ decision: string }>> {
        return this.call('/api/claude/think', 'POST', { situation, context });
    }

    async claudeAnalyze(goal: string, observations: string[]): Promise<ApiResponse<{ analysis: any }>> {
        return this.call('/api/claude/analyze', 'POST', { goal, observations });
    }

    async claudeLearn(experience: string, outcome: string): Promise<ApiResponse<{ lesson: string }>> {
        return this.call('/api/claude/learn', 'POST', { experience, outcome });
    }

    async clearDatabase(): Promise<ApiResponse<{ message: string }>> {
        return this.call('/api/database/clear', 'POST');
    }
}

const api = new ApiClient('');

// ==================== TOAST MANAGER ====================

class ToastManager {
    private static container: HTMLElement | null = null;

    static initialize(): void {
        this.container = document.getElementById('toastContainer');
    }

    static show(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
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

// ==================== UI MANAGERS ====================

class StatusManager {
    async update(): Promise<void> {
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
                } else {
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

        } catch (error) {
            console.error('Failed to load status:', error);
        }
    }

    private updateElement(id: string, content: string): void {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
}

class MemoryManager {
    private lastMemories: Memory[] = [];
    private renderScheduled: boolean = false;

    async load(): Promise<void> {
        try {
            let memories: Memory[];

            if (state.currentFilter === 'all') {
                memories = await api.getRecentMemories(50);
            } else {
                memories = await api.searchMemories(state.currentFilter, 50);
            }

            // Update memory count
            this.updateElement('memoryCount', memories.length.toString());

            // Only re-render if data changed
            if (this.hasChanged(memories)) {
                this.lastMemories = memories;
                this.scheduleRender(memories);
            }

        } catch (error) {
            console.error('Failed to load memories:', error);
        }
    }

    private hasChanged(newMemories: Memory[]): boolean {
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

    private scheduleRender(memories: Memory[]): void {
        if (this.renderScheduled) return;

        this.renderScheduled = true;
        requestAnimationFrame(() => {
            this.render(memories);
            this.renderScheduled = false;
        });
    }

    private render(memories: Memory[]): void {
        const memoriesList = document.getElementById('memoriesList');
        if (!memoriesList) return;

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

    private createMemoryItem(memory: Memory): HTMLDivElement {
        const div = document.createElement('div');
        div.className = 'memory-item';
        div.dataset.type = memory.type;

        const icons: Record<string, string> = {
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

    private updateElement(id: string, content: string): void {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    private formatTimestamp(timestamp: string): string {
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
        } catch (error) {
            console.error('Date parsing error:', error);
            return timestamp; // Fallback to original timestamp
        }
    }
}

class StatsManager {
    async load(): Promise<void> {
        try {
            const stats = await api.getMemoryStats();

            const statsDiv = document.getElementById('memoryStats');
            if (!statsDiv) return;

            statsDiv.innerHTML = '';

            if (!stats.by_type || Object.keys(stats.by_type).length === 0) {
                statsDiv.innerHTML = '<div class="loading">אין סטטיסטיקות</div>';
                return;
            }

            this.render(statsDiv, stats);

        } catch (error) {
            console.error('Failed to load memory stats:', error);
        }
    }

    private render(container: HTMLElement, stats: MemoryStats): void {
        const total = stats.total;
        const types: Record<string, string> = {
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
    static update(decision: LastDecision): void {
        const decisionDiv = document.getElementById('lastDecision');
        if (!decisionDiv) return;

        const formattedTime = this.formatTimestamp(decision.timestamp);

        if (decision.decision) {
            decisionDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-secondary); font-size: 0.9em;">
                    ${formattedTime}
                </div>
                <div>${this.escapeHtml(decision.decision)}</div>
            `;
        } else if (decision.analysis) {
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

    private static formatTimestamp(timestamp: string): string {
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
        } catch (error) {
            console.error('Date parsing error:', error);
            return timestamp;
        }
    }

    private static escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

class AgentControls {
    static update(running: boolean): void {
        const startBtn = document.getElementById('startAgentBtn') as HTMLButtonElement;
        const stopBtn = document.getElementById('stopAgentBtn') as HTMLButtonElement;

        if (startBtn && stopBtn) {
            if (running) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
    }
}

// ==================== EVENT HANDLERS ====================

class EventHandlers {
    static async setGoal(): Promise<void> {
        const input = document.getElementById('goalInput') as HTMLTextAreaElement;
        if (!input) return;

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

        } catch (error) {
            ToastManager.show('שגיאה בהגדרת מטרה', 'error');
        }
    }

    static async startAgent(): Promise<void> {
        try {
            await api.startAgent();

            ToastManager.show('הסוכן התחיל לפעול!', 'success');
            AgentControls.update(true);

            const statusDiv = document.getElementById('agentStatus');
            if (statusDiv) {
                statusDiv.textContent = '⚡ הסוכן פועל...';
                statusDiv.classList.add('active');
            }

        } catch (error) {
            const message = error instanceof Error ? error.message : 'שגיאה בהפעלת הסוכן';
            ToastManager.show(message, 'error');
        }
    }

    static async stopAgent(): Promise<void> {
        try {
            await api.stopAgent();

            ToastManager.show('הסוכן נעצר', 'info');
            AgentControls.update(false);

            const statusDiv = document.getElementById('agentStatus');
            if (statusDiv) {
                statusDiv.textContent = '⏸️ הסוכן עצר';
            }

        } catch (error) {
            ToastManager.show('שגיאה בעצירת הסוכן', 'error');
        }
    }

    static async claudeThink(): Promise<void> {
        const input = document.getElementById('claudeInput') as HTMLTextAreaElement;
        if (!input) return;

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

        } catch (error) {
            const message = error instanceof Error ? error.message : 'שגיאה לא ידועה';
            if (responseDiv) {
                responseDiv.textContent = `❌ שגיאה: ${message}`;
            }
            ToastManager.show('שגיאה בקבלת תשובה מ-Claude', 'error');
        }
    }

    static async refreshAll(): Promise<void> {
        ToastManager.show('מרענן נתונים...', 'info');
        await new StatusManager().update();
        await new MemoryManager().load();
        await new StatsManager().load();
    }

    static async clearMemory(): Promise<void> {
        if (!confirm('האם אתה בטוח שברצונך למחוק את כל הזיכרונות?')) {
            return;
        }

        try {
            await api.clearDatabase();
            ToastManager.show('הזיכרון נוקה בהצלחה', 'success');

            // Refresh all data
            await EventHandlers.refreshAll();

        } catch (error) {
            ToastManager.show('שגיאה בניקוי הזיכרון', 'error');
        }
    }

    static setFilter(type: string): void {
        state.setFilter(type);

        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            const button = btn as HTMLButtonElement;
            if (button.dataset.type === type) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        // Reload memories with debounce
        this.debouncedLoadMemories();
    }

    private static debouncedLoadMemories = debounce(() => {
        new MemoryManager().load();
    }, 300);
}

// ==================== AUTO REFRESH ====================

class AutoRefresh {
    private static baseInterval: number = 10000; // 10 seconds
    private static maxInterval: number = 60000; // 60 seconds
    private static currentInterval: number = AutoRefresh.baseInterval;

    static start(): void {
        this.scheduleNext();
    }

    private static scheduleNext(): void {
        const interval = setTimeout(async () => {
            await this.refresh();
            this.scheduleNext();
        }, this.currentInterval);

        state.setRefreshInterval(interval);
    }

    private static async refresh(): Promise<void> {
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

        } catch (error) {
            console.error('Auto-refresh error:', error);
            state.incrementErrors();

            // Exponential backoff on consecutive errors
            if (state.consecutiveErrors >= 3) {
                this.increaseInterval();
            }
        }
    }

    private static increaseInterval(): void {
        this.currentInterval = Math.min(
            this.currentInterval * 1.5,
            this.maxInterval
        );
    }

    static stop(): void {
        state.clearRefreshInterval();
    }
}

// ==================== INITIALIZATION ====================

function initializeEventListeners(): void {
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
            const target = e.target as HTMLButtonElement;
            const type = target.dataset.type;
            if (type) {
                EventHandlers.setFilter(type);
            }
        });
    });

    // Enter key shortcuts
    const goalInput = document.getElementById('goalInput');
    goalInput?.addEventListener('keypress', (e) => {
        if ((e as KeyboardEvent).key === 'Enter' && (e as KeyboardEvent).ctrlKey) {
            EventHandlers.setGoal();
        }
    });

    const claudeInput = document.getElementById('claudeInput');
    claudeInput?.addEventListener('keypress', (e) => {
        if ((e as KeyboardEvent).key === 'Enter' && (e as KeyboardEvent).ctrlKey) {
            EventHandlers.claudeThink();
        }
    });
}

async function initialize(): Promise<void> {
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
    } catch (error) {
        console.error('Failed to load initial data:', error);
        ToastManager.show('שגיאה בטעינת נתונים ראשוניים', 'error');
    }

    // Start auto-refresh
    AutoRefresh.start();

    console.log('✅ Dashboard Ready!');
}

function setupNetworkMonitoring(): void {
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
