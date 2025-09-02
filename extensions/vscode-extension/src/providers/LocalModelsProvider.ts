import * as vscode from 'vscode';
import { ApiClient, ModelInfo } from '../services/ApiClient';

export class LocalModelsProvider implements vscode.TreeDataProvider<ModelItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ModelItem | undefined | null | void> = new vscode.EventEmitter<ModelItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ModelItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private apiClient: ApiClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ModelItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: ModelItem): Promise<ModelItem[]> {
        if (element) {
            // Return capabilities for a specific model
            return element.capabilities.map(cap => new ModelItem(cap, cap, vscode.TreeItemCollapsibleState.None, 'capability'));
        } else {
            // Return list of models
            try {
                const models = await this.apiClient.listModels();
                return models.map(model => new ModelItem(
                    model.name,
                    model.description || model.name,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'model',
                    model.capabilities || []
                ));
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to load models: ${error}`);
                return [new ModelItem('Error', 'Failed to load models', vscode.TreeItemCollapsibleState.None, 'error')];
            }
        }
    }
}

class ModelItem extends vscode.TreeItem {
    constructor(
        override readonly label: string,
        override readonly tooltip: string,
        override readonly collapsibleState: vscode.TreeItemCollapsibleState,
        override readonly contextValue: string,
        public readonly capabilities: string[] = []
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltip;
        this.contextValue = contextValue;

        // Set icon based on type
        if (contextValue === 'model') {
            this.iconPath = new vscode.ThemeIcon('robot');
            this.command = {
                command: 'localModels.chat',
                title: 'Chat with this model',
                arguments: [label]
            };
        } else if (contextValue === 'capability') {
            this.iconPath = new vscode.ThemeIcon('symbol-property');
        } else if (contextValue === 'error') {
            this.iconPath = new vscode.ThemeIcon('error');
        }

        // Set description for models
        if (contextValue === 'model' && capabilities.length > 0) {
            this.description = capabilities.join(', ');
        }
    }
}
