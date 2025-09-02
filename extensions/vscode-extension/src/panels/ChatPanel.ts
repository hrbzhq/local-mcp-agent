import * as vscode from 'vscode';
import { ApiClient, ChatRequest, ChatResponse, CollaborativeRequest, CollaborativeResponse } from '../services/ApiClient';

export class ChatPanel {
    public static currentPanel: ChatPanel | undefined;
    public static readonly viewType = 'localModelsChat';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private readonly _apiClient: ApiClient;
    private readonly _selectedModel: string;
    private readonly _collaborativeModels: string[];
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, apiClient: ApiClient, selectedModel: string, collaborativeModels: string[] = []) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._apiClient = apiClient;
        this._selectedModel = selectedModel;
        this._collaborativeModels = collaborativeModels;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'chat':
                        await this._handleChat(message.text);
                        break;
                    case 'collaborate':
                        await this._handleCollaborate(message.text);
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri, apiClient: ApiClient, selectedModel: string, collaborativeModels: string[] = []) {
        const column = vscode.window.activeTextEditor
            ? vscode.ViewColumn.Beside
            : undefined;

        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ChatPanel.viewType,
            `AI Chat${selectedModel !== 'auto' ? ` (${selectedModel})` : ''}`,
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri, apiClient, selectedModel, collaborativeModels);
    }

    public static revive(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, apiClient: ApiClient) {
        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri, apiClient, 'auto');
    }

    private async _handleChat(text: string) {
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "AI is thinking...",
                cancellable: false
            }, async (progress) => {
                const request: ChatRequest = {
                    input: text,
                    user_id: vscode.env.machineId,
                    model: this._selectedModel === 'auto' ? undefined : this._selectedModel
                };

                const response = await this._apiClient.chat(request);

                this._panel.webview.postMessage({
                    type: 'response',
                    userMessage: text,
                    aiResponse: response.output,
                    model: response.model,
                    latency: response.meta.latency_ms
                });
            });
        } catch (error: any) {
            vscode.window.showErrorMessage(`Chat failed: ${error.message}`);
            this._panel.webview.postMessage({
                type: 'error',
                message: error.message
            });
        }
    }

    private async _handleCollaborate(text: string) {
        if (this._collaborativeModels.length === 0) {
            vscode.window.showErrorMessage('No models selected for collaboration');
            return;
        }

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "AI collaboration in progress...",
                cancellable: false
            }, async (progress) => {
                const request: CollaborativeRequest = {
                    input: text,
                    models: this._collaborativeModels,
                    max_rounds: 3
                };

                const response = await this._apiClient.collaborativeChat(request);

                this._panel.webview.postMessage({
                    type: 'collaborativeResponse',
                    userMessage: text,
                    summary: response.collaboration_summary,
                    history: response.detailed_history
                });
            });
        } catch (error: any) {
            vscode.window.showErrorMessage(`Collaborative chat failed: ${error.message}`);
            this._panel.webview.postMessage({
                type: 'error',
                message: error.message
            });
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = `AI Chat${this._selectedModel !== 'auto' ? ` (${this._selectedModel})` : ''}`;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const nonce = getNonce();

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Chat</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    margin: 0;
                    padding: 20px;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                .chat-container {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    max-height: calc(100vh - 120px);
                }
                .messages {
                    flex: 1;
                    overflow-y: auto;
                    margin-bottom: 20px;
                    padding: 10px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                }
                .message {
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 8px;
                }
                .user-message {
                    background-color: var(--vscode-textBlockQuote-background);
                    border-left: 4px solid var(--vscode-textLink-foreground);
                }
                .ai-message {
                    background-color: var(--vscode-textCodeBlock-background);
                    border-left: 4px solid var(--vscode-charts-green);
                }
                .input-container {
                    display: flex;
                    gap: 10px;
                    align-items: flex-end;
                }
                .input-field {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 4px;
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    font-family: inherit;
                    resize: vertical;
                    min-height: 40px;
                }
                .send-button {
                    padding: 10px 20px;
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .send-button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                .model-info {
                    font-size: 0.9em;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 5px;
                }
                .error-message {
                    background-color: var(--vscode-inputValidation-errorBackground);
                    border: 1px solid var(--vscode-inputValidation-errorBorder);
                    color: var(--vscode-inputValidation-errorForeground);
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div id="messages" class="messages"></div>
                <div class="input-container">
                    <textarea
                        id="input"
                        class="input-field"
                        placeholder="Type your message here..."
                        rows="2"
                    ></textarea>
                    <button id="sendButton" class="send-button">Send</button>
                    ${this._collaborativeModels.length > 0 ? '<button id="collaborateButton" class="send-button">Collaborate</button>' : ''}
                </div>
            </div>

            <script nonce="${nonce}">
                const vscode = acquireVsCodeApi();
                const messagesDiv = document.getElementById('messages');
                const inputField = document.getElementById('input');
                const sendButton = document.getElementById('sendButton');
                const collaborateButton = document.getElementById('collaborateButton');

                sendButton.addEventListener('click', () => {
                    const text = inputField.value.trim();
                    if (text) {
                        vscode.postMessage({ type: 'chat', text });
                        inputField.value = '';
                    }
                });

                inputField.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendButton.click();
                    }
                });

                if (collaborateButton) {
                    collaborateButton.addEventListener('click', () => {
                        const text = inputField.value.trim();
                        if (text) {
                            vscode.postMessage({ type: 'collaborate', text });
                            inputField.value = '';
                        }
                    });
                }

                window.addEventListener('message', event => {
                    const message = event.data;

                    switch (message.type) {
                        case 'response':
                            addMessage('user', message.userMessage);
                            addMessage('ai', message.aiResponse, message.model, message.latency);
                            break;
                        case 'collaborativeResponse':
                            addMessage('user', message.userMessage);
                            addCollaborativeResponse(message.summary, message.history);
                            break;
                        case 'error':
                            addErrorMessage(message.message);
                            break;
                    }
                });

                function addMessage(sender, text, model = '', latency = 0) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = \`message \${sender}-message\`;

                    const contentDiv = document.createElement('div');
                    contentDiv.textContent = text;
                    messageDiv.appendChild(contentDiv);

                    if (model || latency) {
                        const infoDiv = document.createElement('div');
                        infoDiv.className = 'model-info';
                        infoDiv.textContent = \`\${model} (\${latency}ms)\`;
                        messageDiv.appendChild(infoDiv);
                    }

                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }

                function addCollaborativeResponse(summary, history) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ai-message';

                    const summaryDiv = document.createElement('div');
                    summaryDiv.innerHTML = \`<strong>Collaborative Result:</strong><br>\${summary.final_output}\`;
                    messageDiv.appendChild(summaryDiv);

                    const infoDiv = document.createElement('div');
                    infoDiv.className = 'model-info';
                    infoDiv.textContent = \`Models: \${summary.models_involved.join(', ')} | Rounds: \${summary.total_rounds}\`;
                    messageDiv.appendChild(infoDiv);

                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }

                function addErrorMessage(message) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = \`Error: \${message}\`;
                    messagesDiv.appendChild(errorDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            </script>
        </body>
        </html>`;
    }

    public dispose() {
        ChatPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
