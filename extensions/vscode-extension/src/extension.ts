import * as vscode from 'vscode';
import { LocalModelsProvider } from './providers/LocalModelsProvider';
import { ChatPanel } from './panels/ChatPanel';
import { ApiClient } from './services/ApiClient';
import { McpClient } from './services/McpClient';

let localModelsProvider: LocalModelsProvider;
let apiClient: ApiClient;
let mcpClient: McpClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('Local Multi-Model Gateway extension is now active!');

    // Initialize API client
    const config = vscode.workspace.getConfiguration('localModels');
    const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
    const mcpUrl = config.get<string>('mcpUrl', 'http://localhost:8000/mcp');
    
    apiClient = new ApiClient(apiUrl);
    mcpClient = new McpClient(mcpUrl);

    // Initialize providers
    localModelsProvider = new LocalModelsProvider(apiClient);
    vscode.window.registerTreeDataProvider('localModelsView', localModelsProvider);

    // Register existing commands
    context.subscriptions.push(
        vscode.commands.registerCommand('localModels.chat', async (model?: string) => {
            const selectedModel = model || await selectModel();
            if (selectedModel) {
                ChatPanel.createOrShow(context.extensionUri, apiClient, selectedModel);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('localModels.collaborate', async () => {
            const models = await selectMultipleModels();
            if (models && models.length > 0) {
                ChatPanel.createOrShow(context.extensionUri, apiClient, 'auto', models);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('localModels.refresh', () => {
            localModelsProvider.refresh();
        })
    );

    // Register new MCP commands
    context.subscriptions.push(
        vscode.commands.registerCommand('mcp.listTools', async () => {
            try {
                const tools = await mcpClient.listTools();
                const quickPick = vscode.window.createQuickPick();
                quickPick.title = 'MCP Tools Available';
                quickPick.placeholder = 'Select a tool to learn more about it';
                quickPick.items = tools.map(tool => ({
                    label: tool.name,
                    description: tool.description,
                    detail: `Schema: ${JSON.stringify(tool.inputSchema.properties || {}, null, 2)}`
                }));
                quickPick.show();
                
                quickPick.onDidAccept(() => {
                    const selected = quickPick.selectedItems[0];
                    if (selected) {
                        vscode.window.showInformationMessage(`Tool: ${selected.label}\n${selected.description}`);
                    }
                    quickPick.dispose();
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to list MCP tools: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('mcp.askTool', async () => {
            try {
                const tools = await mcpClient.listTools();
                const toolNames = tools.map(t => t.name);
                
                const selectedTool = await vscode.window.showQuickPick(toolNames, {
                    placeHolder: 'Select an MCP tool to use'
                });
                
                if (!selectedTool) return;
                
                if (selectedTool === 'chat_with_model') {
                    const input = await vscode.window.showInputBox({
                        prompt: 'Enter your message for the AI model',
                        placeHolder: 'What would you like to ask the AI?'
                    });
                    
                    if (input) {
                        const model = await vscode.window.showInputBox({
                            prompt: 'Enter model name (leave empty for auto-selection)',
                            placeHolder: 'e.g., llama3.2:3b or leave empty'
                        });
                        
                        vscode.window.withProgress({
                            location: vscode.ProgressLocation.Notification,
                            title: 'Calling AI model...',
                            cancellable: false
                        }, async () => {
                            try {
                                const result = await mcpClient.chatWithModel(input, model || undefined);
                                if (result.status === 'success') {
                                    const response = result.data;
                                    const panel = vscode.window.createWebviewPanel(
                                        'mcpResult',
                                        'AI Response',
                                        vscode.ViewColumn.One,
                                        {}
                                    );
                                    panel.webview.html = `
                                        <html>
                                        <body>
                                            <h2>AI Model: ${response.model}</h2>
                                            <h3>Your Input:</h3>
                                            <p style="background:#f0f0f0; padding:10px; border-radius:5px;">${response.input}</p>
                                            <h3>AI Response:</h3>
                                            <div style="background:#e8f4f8; padding:15px; border-radius:5px; white-space:pre-wrap;">${response.output}</div>
                                            <hr>
                                            <small>Execution time: ${result.execution_time.toFixed(2)}s</small>
                                        </body>
                                        </html>
                                    `;
                                } else {
                                    vscode.window.showErrorMessage(`Tool call failed: ${result.error}`);
                                }
                            } catch (error) {
                                vscode.window.showErrorMessage(`Error: ${error}`);
                            }
                        });
                    }
                } else if (selectedTool === 'list_available_models') {
                    vscode.window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Fetching available models...',
                        cancellable: false
                    }, async () => {
                        try {
                            const result = await mcpClient.listAvailableModels(true);
                            if (result.status === 'success') {
                                const models = result.data.models;
                                const modelList = models.join('\n• ');
                                vscode.window.showInformationMessage(`Available Models (${models.length}):\n• ${modelList}`, { modal: true });
                            } else {
                                vscode.window.showErrorMessage(`Failed to list models: ${result.error}`);
                            }
                        } catch (error) {
                            vscode.window.showErrorMessage(`Error: ${error}`);
                        }
                    });
                } else if (selectedTool === 'collaborative_chat') {
                    const input = await vscode.window.showInputBox({
                        prompt: 'Enter your question for collaborative AI discussion',
                        placeHolder: 'What topic should the AI models discuss?'
                    });
                    
                    if (input) {
                        const models = await selectMultipleModels();
                        if (models && models.length > 0) {
                            vscode.window.withProgress({
                                location: vscode.ProgressLocation.Notification,
                                title: 'Starting collaborative chat...',
                                cancellable: false
                            }, async () => {
                                try {
                                    const result = await mcpClient.collaborativeChat(input, models);
                                    if (result.status === 'success') {
                                        const panel = vscode.window.createWebviewPanel(
                                            'collaborativeResult',
                                            'Collaborative AI Discussion',
                                            vscode.ViewColumn.One,
                                            {}
                                        );
                                        
                                        const data = result.data;
                                        let historyHtml = '';
                                        if (data.detailed_history) {
                                            historyHtml = data.detailed_history.map((round: any, index: number) => 
                                                `<h4>Round ${index + 1} - ${round.model}</h4>
                                                 <div style="background:#f9f9f9; padding:10px; margin:10px 0; border-left:3px solid #007ACC;">${round.output}</div>`
                                            ).join('');
                                        }
                                        
                                        panel.webview.html = `
                                            <html>
                                            <body>
                                                <h2>Collaborative AI Discussion</h2>
                                                <h3>Topic:</h3>
                                                <p style="background:#f0f0f0; padding:10px; border-radius:5px;">${input}</p>
                                                <h3>Models Involved:</h3>
                                                <p>${models.join(', ')}</p>
                                                <h3>Final Consensus:</h3>
                                                <div style="background:#e8f4f8; padding:15px; border-radius:5px; white-space:pre-wrap;">${data.collaboration_summary?.final_output || 'No final output available'}</div>
                                                <h3>Discussion History:</h3>
                                                ${historyHtml}
                                                <hr>
                                                <small>Total rounds: ${data.collaboration_summary?.total_rounds || 0} | Execution time: ${result.execution_time.toFixed(2)}s</small>
                                            </body>
                                            </html>
                                        `;
                                    } else {
                                        vscode.window.showErrorMessage(`Collaborative chat failed: ${result.error}`);
                                    }
                                } catch (error) {
                                    vscode.window.showErrorMessage(`Error: ${error}`);
                                }
                            });
                        }
                    }
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to execute MCP tool: ${error}`);
            }
        })
    );

    // Register webview panel serializer for chat panels
    context.subscriptions.push(
        vscode.window.registerWebviewPanelSerializer(ChatPanel.viewType, {
            async deserializeWebviewPanel(webviewPanel: vscode.WebviewPanel, state: any) {
                ChatPanel.revive(webviewPanel, context.extensionUri, apiClient);
            }
        })
    );

    // Show welcome message
    vscode.window.showInformationMessage(
        'Local Multi-Model Gateway is ready! Use Ctrl+Shift+P and search for "MCP" or "Local Models" to get started.',
        'Show MCP Tools', 'Open Chat'
    ).then(selection => {
        if (selection === 'Show MCP Tools') {
            vscode.commands.executeCommand('mcp.listTools');
        } else if (selection === 'Open Chat') {
            vscode.commands.executeCommand('localModels.chat');
        }
    });
}

export function deactivate() {
    console.log('Local Multi-Model Gateway extension is now deactivated!');
}

async function selectModel(): Promise<string | undefined> {
    try {
        const models = await apiClient.listModels();
        const modelNames = models.map((m: any) => m.name || m);

        const selected = await vscode.window.showQuickPick(
            ['auto', ...modelNames],
            {
                placeHolder: 'Select a model or choose auto for smart routing',
                matchOnDescription: true
            }
        );

        return selected;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to load models: ${error}`);
        return undefined;
    }
}

async function selectMultipleModels(): Promise<string[] | undefined> {
    try {
        const models = await apiClient.listModels();
        const modelNames = models.map((m: any) => m.name || m);

        const selected = await vscode.window.showQuickPick(
            modelNames,
            {
                canPickMany: true,
                placeHolder: 'Select models for collaboration'
            }
        );

        return selected;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to load models: ${error}`);
        return undefined;
    }
}
