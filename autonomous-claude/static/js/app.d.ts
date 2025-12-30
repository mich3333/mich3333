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
interface ApiResponse<T = any> {
    success?: boolean;
    error?: string;
    data?: T;
    [key: string]: any;
}
declare class DashboardState {
    currentFilter: string;
    refreshInterval: number | null;
    isAgentRunning: boolean;
    apiUrl: string;
    setFilter(filter: string): void;
    setAgentRunning(running: boolean): void;
    setRefreshInterval(interval: number): void;
    clearRefreshInterval(): void;
}
declare const state: DashboardState;
declare class ApiClient {
    private baseUrl;
    constructor(baseUrl?: string);
    call<T>(endpoint: string, method?: string, body?: any): Promise<T>;
    getStatus(): Promise<AgentStatus>;
    getRecentMemories(limit?: number): Promise<Memory[]>;
    searchMemories(type: string, limit?: number): Promise<Memory[]>;
    getMemoryStats(): Promise<MemoryStats>;
    addMemory(type: string, content: string): Promise<ApiResponse<{
        id: number;
    }>>;
    setGoal(goal: string): Promise<ApiResponse<{
        goal: string;
    }>>;
    startAgent(): Promise<ApiResponse<{}>>;
    stopAgent(): Promise<ApiResponse<{}>>;
    claudeThink(situation: string, context?: any): Promise<ApiResponse<{
        decision: string;
    }>>;
    claudeAnalyze(goal: string, observations: string[]): Promise<ApiResponse<{
        analysis: any;
    }>>;
    claudeLearn(experience: string, outcome: string): Promise<ApiResponse<{
        lesson: string;
    }>>;
    clearDatabase(): Promise<ApiResponse<{
        message: string;
    }>>;
}
declare const api: ApiClient;
declare class ToastManager {
    private static container;
    static initialize(): void;
    static show(message: string, type?: 'success' | 'error' | 'info'): void;
}
declare class StatusManager {
    update(): Promise<void>;
    private updateElement;
}
declare class MemoryManager {
    load(): Promise<void>;
    private render;
    private createMemoryItem;
    private updateElement;
    private escapeHtml;
    private formatTimestamp;
}
declare class StatsManager {
    load(): Promise<void>;
    private render;
}
declare class DecisionDisplay {
    static update(decision: LastDecision): void;
    private static formatTimestamp;
    private static escapeHtml;
}
declare class AgentControls {
    static update(running: boolean): void;
}
declare class EventHandlers {
    static setGoal(): Promise<void>;
    static startAgent(): Promise<void>;
    static stopAgent(): Promise<void>;
    static claudeThink(): Promise<void>;
    static refreshAll(): Promise<void>;
    static clearMemory(): Promise<void>;
    static setFilter(type: string): void;
}
declare class AutoRefresh {
    static start(): void;
    static stop(): void;
}
declare function initializeEventListeners(): void;
declare function initialize(): Promise<void>;
//# sourceMappingURL=app.d.ts.map