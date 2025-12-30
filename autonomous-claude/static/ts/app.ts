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

// ==================== STATE ====================

class DashboardState {
    currentFilter: string = 'all';
    refreshInterval: number | null = null;
    isAgentRunning: boolean = false;
    apiUrl: string = '';

    setFilter(filter: string): void {
        this.currentFilter = filter;
    }

    setAgentRunning(running: boolean): void {
        this.isAgentRunning = running;
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
}

const state = new DashboardState();

// ==================== API CLIENT ====================

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = '') {
        this.baseUrl = baseUrl;
    }

    async call<T>(
        endpoint: string,
        method: string = 'GET',
        body: any = null
    ): Promise<T> {
        try {
            const options: RequestInit = {
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

            return data as T;
        } catch (error) {
            console.error('API Error:', error);
            const message = error instanceof Error ? error.message : 'Unknown error';
            ToastManager.show(message, 'error');
            throw error;
        }
    }

    async getStatus(): Promise<AgentStatus> {
        return this.call<AgentStatus>('/api/status');
    }

    async getRecentMemories(limit: number = 50): Promise<Memory[]> {
        return this.call<Memory[]>(`/api/memories/recent?limit=${limit}`);
    }

    async searchMemories(type: string, limit: number = 50): Promise<Memory[]> {
        return this.call<Memory[]>(`/api/memories/search?type=${type}&limit=${limit}`);
    }

    async getMemoryStats(): Promise<MemoryStats> {
        return this.call<MemoryStats>('/api/memories/stats');
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

            // Render memories
            this.render(memories);

        } catch (error) {
            console.error('Failed to load memories:', error);
        }
    }

    private render(memories: Memory[]): void {
        const memoriesList = document.getElementById('memoriesList');
        if (!memoriesList) return;

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

        // Reload memories
        new MemoryManager().load();
    }
}

// ==================== AUTO REFRESH ====================

class AutoRefresh {
    static start(): void {
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
