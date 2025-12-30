// Multi-Agent System - Frontend JavaScript

class MultiAgentUI {
    constructor() {
        this.apiBase = '';
        this.executing = false;
        this.init();
    }

    async init() {
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

    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();

            const badge = document.getElementById('statusBadge');
            const dot = badge.querySelector('.status-dot');
            const text = badge.querySelector('.status-text');

            if (data.status === 'online' && data.anthropic_key_set) {
                dot.classList.remove('offline');
                text.textContent = 'Online - Ready';
            } else {
                dot.classList.add('offline');
                text.textContent = data.anthropic_key_set ? 'Offline' : 'API Key Missing';
            }
        } catch (error) {
            console.error('Status check failed:', error);
            const badge = document.getElementById('statusBadge');
            const dot = badge.querySelector('.status-dot');
            const text = badge.querySelector('.status-text');
            dot.classList.add('offline');
            text.textContent = 'Offline';
        }
    }

    async loadAgents() {
        try {
            const response = await fetch(`${this.apiBase}/api/agents`);
            const data = await response.json();

            const grid = document.getElementById('agentsGrid');
            grid.innerHTML = data.agents.map(agent => `
                <div class="agent-card" data-agent="${agent.name.toLowerCase()}">
                    <div class="agent-emoji">${agent.emoji}</div>
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-role">${agent.role}</div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    }

    async executeTask() {
        if (this.executing) return;

        const taskInput = document.getElementById('taskInput');
        const task = taskInput.value.trim();

        if (!task) {
            alert('Please enter a task!');
            return;
        }

        this.executing = true;
        this.setExecuting(true);

        // Clear previous results
        this.clearExecutionLog();
        this.clearResults();

        try {
            const response = await fetch(`${this.apiBase}/api/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ task })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResults(data);
                this.displayExecutionLog(data.execution_log);
            } else {
                this.showError(data.error || 'Execution failed');
            }
        } catch (error) {
            console.error('Execution error:', error);
            this.showError(`Error: ${error.message}`);
        } finally {
            this.executing = false;
            this.setExecuting(false);
        }
    }

    setExecuting(executing) {
        const btn = document.getElementById('executeBtn');
        const btnText = document.getElementById('btnText');
        const btnLoader = document.getElementById('btnLoader');

        btn.disabled = executing;

        if (executing) {
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-block';
        } else {
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    }

    clearExecutionLog() {
        const log = document.getElementById('executionLog');
        log.innerHTML = '<div class="empty-state">Executing task...</div>';
    }

    clearResults() {
        const results = document.getElementById('results');
        results.innerHTML = '<div class="empty-state">Processing...</div>';
    }

    displayExecutionLog(logEntries) {
        const log = document.getElementById('executionLog');
        log.innerHTML = '';

        logEntries.forEach((entry, index) => {
            setTimeout(() => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry ${entry.agent}`;
                logEntry.innerHTML = `
                    <div class="log-header">
                        <span>${this.getAgentEmoji(entry.agent)}</span>
                        <span>${entry.agent.charAt(0).toUpperCase() + entry.agent.slice(1)}</span>
                        <span class="log-status ${entry.status}">${entry.status}</span>
                    </div>
                    <div class="log-message">${this.truncateMessage(entry.message, 500)}</div>
                `;
                log.appendChild(logEntry);

                // Highlight active agent
                this.highlightAgent(entry.agent, entry.status === 'working');

                // Scroll to bottom
                log.scrollTop = log.scrollHeight;
            }, index * 100);
        });
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

        // Subtask Results (optional, collapsed)
        if (data.subtask_results && Object.keys(data.subtask_results).length > 0) {
            const subtasksSection = document.createElement('div');
            subtasksSection.className = 'result-section';
            subtasksSection.innerHTML = `
                <h3>🔍 Detailed Agent Results</h3>
            `;

            for (const [agent, result] of Object.entries(data.subtask_results)) {
                const agentResult = document.createElement('div');
                agentResult.className = 'result-section';
                agentResult.innerHTML = `
                    <h4>${this.getAgentEmoji(agent)} ${agent.charAt(0).toUpperCase() + agent.slice(1)}</h4>
                    <div class="result-content">${this.truncateMessage(result, 1000)}</div>
                `;
                subtasksSection.appendChild(agentResult);
            }

            results.appendChild(subtasksSection);
        }
    }

    highlightAgent(agentName, active) {
        const agentCard = document.querySelector(`[data-agent="${agentName}"]`);
        if (agentCard) {
            if (active) {
                agentCard.classList.add('active');
            } else {
                setTimeout(() => {
                    agentCard.classList.remove('active');
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
