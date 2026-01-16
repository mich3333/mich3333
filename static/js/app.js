// Multi-Agent System - Frontend with WebSockets Real-Time Streaming

class MultiAgentUI {
    constructor() {
        this.apiBase = '';
        this.executing = false;
        this.socket = null;
        this.init();
    }

    async init() {
        // Initialize Socket.IO
        this.initWebSocket();

        // Load agents
        await this.loadAgents();

        // Check status
        await this.checkStatus();

        // Setup event listeners
        document.getElementById('executeBtn').addEventListener('click', () => this.executeTask());

        // Enter key in textarea
        document.getElementById('taskInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.executeTask();
            }
        });
    }

    initWebSocket() {
        // Connect to Socket.IO server
        this.socket = io();

        // Connection events
        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
            this.updateConnectionStatus(false);
        });

        // Real-time execution events
        this.socket.on('execution_start', (data) => {
            console.log('🚀 Execution started:', data.task);
            this.clearExecutionLog();
            this.clearResults();
        });

        this.socket.on('agent_update', (data) => {
            console.log(`🤖 ${data.agent}: ${data.status}`);
            this.addLogEntry(data.agent, data.status, data.message);
            this.highlightAgent(data.agent, data.status === 'working');
        });

        this.socket.on('execution_complete', (data) => {
            console.log('✅ Execution complete');
            this.displayResults(data);
            this.setExecuting(false);
        });

        this.socket.on('error', (data) => {
            console.error('❌ Error:', data.message);
            this.showError(data.message);
            this.setExecuting(false);
        });
    }

    updateConnectionStatus(connected) {
        const badge = document.getElementById('statusBadge');
        const dot = badge.querySelector('.status-dot');
        const text = badge.querySelector('.status-text');

        if (connected) {
            dot.classList.remove('offline');
            text.textContent = 'Online - WebSocket Connected';
        } else {
            dot.classList.add('offline');
            text.textContent = 'Disconnected';
        }
    }

    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();

            const badge = document.getElementById('statusBadge');
            const dot = badge.querySelector('.status-dot');
            const text = badge.querySelector('.status-text');

            if (data.status === 'online' && data.anthropic_key_set) {
                dot.classList.remove('offline');
                text.textContent = 'Online - Ready (WebSocket)';
            } else {
                dot.classList.add('offline');
                text.textContent = data.anthropic_key_set ? 'Offline' : 'API Key Missing';
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }

    async loadAgents() {
        try {
            const response = await fetch(`${this.apiBase}/api/agents`);
            const data = await response.json();

            const grid = document.getElementById('agentsGrid');
            const agentColors = {
                'manager': 'from-amber-500 to-orange-500',
                'researcher': 'from-blue-500 to-cyan-500',
                'coder': 'from-green-500 to-emerald-500',
                'reviewer': 'from-purple-500 to-violet-500',
                'reporter': 'from-pink-500 to-rose-500'
            };

            grid.innerHTML = data.agents.map(agent => `
                <div class="agent-card glass p-4 rounded-xl border-2 border-white/10 hover:border-${agent.name.toLowerCase() === 'manager' ? 'orange' : agent.name.toLowerCase() === 'researcher' ? 'cyan' : agent.name.toLowerCase() === 'coder' ? 'emerald' : agent.name.toLowerCase() === 'reviewer' ? 'violet' : 'rose'}-500/50 transition-all duration-300 hover:scale-105 cursor-pointer group" data-agent="${agent.name.toLowerCase()}">
                    <div class="text-center">
                        <div class="w-14 h-14 mx-auto mb-3 rounded-xl bg-gradient-to-br ${agentColors[agent.name.toLowerCase()]} flex items-center justify-center text-2xl transform group-hover:scale-110 transition-transform">
                            ${agent.emoji}
                        </div>
                        <div class="font-bold text-sm mb-1">${agent.name}</div>
                        <div class="text-xs text-gray-400 leading-tight">${agent.role.split(' ').slice(0, 2).join(' ')}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    }

    executeTask() {
        if (this.executing) return;

        const taskInput = document.getElementById('taskInput');
        const task = taskInput.value.trim();

        if (!task) {
            alert('Please enter a task!');
            return;
        }

        this.executing = true;
        this.setExecuting(true);

        // Execute via WebSocket for real-time updates
        this.socket.emit('start_task', { task: task });
    }

    setExecuting(executing) {
        const btn = document.getElementById('executeBtn');
        const btnText = document.getElementById('btnText');
        const btnLoader = document.getElementById('btnLoader');

        btn.disabled = executing;

        if (executing) {
            btnText.textContent = '⚡ Executing (Real-time)...';
            btnLoader.style.display = 'inline-block';
        } else {
            btnText.textContent = '🚀 Execute Task';
            btnLoader.style.display = 'none';
        }
    }

    clearExecutionLog() {
        const log = document.getElementById('executionLog');
        log.innerHTML = '<div class="empty-state">⚡ Executing with real-time streaming...</div>';
    }

    clearResults() {
        const results = document.getElementById('results');
        results.innerHTML = '<div class="empty-state">⚡ Processing...</div>';
    }

    addLogEntry(agent, status, message) {
        const log = document.getElementById('executionLog');

        // Remove empty state if present
        const emptyState = log.querySelector('.text-center');
        if (emptyState && emptyState.textContent.includes('No task running')) {
            emptyState.remove();
        }

        const agentColors = {
            'manager': 'border-orange-500/50 bg-orange-500/5',
            'researcher': 'border-cyan-500/50 bg-cyan-500/5',
            'coder': 'border-emerald-500/50 bg-emerald-500/5',
            'reviewer': 'border-violet-500/50 bg-violet-500/5',
            'reporter': 'border-rose-500/50 bg-rose-500/5'
        };

        const statusColors = {
            'working': 'bg-yellow-500/20 text-yellow-300',
            'completed': 'bg-green-500/20 text-green-300',
            'analyzing': 'bg-blue-500/20 text-blue-300',
            'error': 'bg-red-500/20 text-red-300'
        };

        const logEntry = document.createElement('div');
        logEntry.className = `glass p-4 rounded-xl border-l-4 ${agentColors[agent] || 'border-purple-500/50'} animate-slide-in-right`;
        logEntry.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                    <span class="text-xl">${this.getAgentEmoji(agent)}</span>
                    <span class="font-semibold capitalize">${agent}</span>
                </div>
                <span class="text-xs px-2 py-1 rounded-full ${statusColors[status] || 'bg-gray-500/20 text-gray-300'}">${status}</span>
            </div>
            <div class="text-sm text-gray-300 leading-relaxed">${this.truncateMessage(message, 300)}</div>
        `;
        log.appendChild(logEntry);

        // Scroll to bottom
        log.scrollTop = log.scrollHeight;
    }

    displayResults(data) {
        const results = document.getElementById('results');
        results.innerHTML = '';

        // Final Report
        const reportSection = document.createElement('div');
        reportSection.className = 'result-section';
        reportSection.innerHTML = `
            <h3>📊 Final Report</h3>
            <div class="result-content">${this.formatMarkdown(data.final_report)}</div>
        `;
        results.appendChild(reportSection);

        // Execution log from result
        if (data.result && data.result.execution_log) {
            const logSection = document.createElement('div');
            logSection.className = 'result-section';
            logSection.innerHTML = `
                <h3>📝 Execution Summary</h3>
                <div class="result-content">
                    ${data.result.execution_log.length} steps completed
                </div>
            `;
            results.appendChild(logSection);
        }
    }

    highlightAgent(agentName, active) {
        const agentCard = document.querySelector(`[data-agent="${agentName}"]`);
        if (agentCard) {
            if (active) {
                agentCard.classList.add('ring-2', 'ring-purple-500', 'scale-110', 'neon-glow');
            } else {
                setTimeout(() => {
                    agentCard.classList.remove('ring-2', 'ring-purple-500', 'scale-110', 'neon-glow');
                }, 1000);
            }
        }
    }

    getAgentEmoji(agentName) {
        const emojis = {
            'manager': '🎯',
            'researcher': '🔍',
            'coder': '💻',
            'reviewer': '✅',
            'reporter': '📊'
        };
        return emojis[agentName.toLowerCase()] || '🤖';
    }

    truncateMessage(message, maxLength) {
        if (message.length <= maxLength) return message;
        return message.substring(0, maxLength) + '...';
    }

    formatMarkdown(text) {
        // Basic markdown formatting
        return text
            .replace(/```([^`]+)```/g, '<pre>$1</pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    showError(message) {
        const log = document.getElementById('executionLog');
        log.innerHTML = `
            <div class="log-entry error">
                <div class="log-header">
                    <span>❌</span>
                    <span>Error</span>
                    <span class="log-status error">failed</span>
                </div>
                <div class="log-message">${message}</div>
            </div>
        `;

        const results = document.getElementById('results');
        results.innerHTML = `
            <div class="empty-state">
                ❌ Task execution failed. Check the logs for details.
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MultiAgentUI();
});
