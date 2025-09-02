import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface ChatRequest {
    input: string;
    user_id?: string;
    model?: string;
}

export interface ChatResponse {
    model: string;
    output: string;
    meta: {
        latency_ms: number;
        model_call_ms: number;
    };
}

export interface ModelInfo {
    name: string;
    capabilities?: string[];
    description?: string;
}

export interface CollaborativeRequest {
    input: string;
    models: string[];
    max_rounds?: number;
}

export interface CollaborativeResponse {
    collaboration_summary: {
        initial_input: string;
        models_involved: string[];
        total_rounds: number;
        final_output: string;
    };
    detailed_history: any[];
}

export class ApiClient {
    private client: AxiosInstance;
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: vscode.workspace.getConfiguration('localModels').get<number>('timeout', 120) * 1000,
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                if (error.code === 'ECONNREFUSED') {
                    throw new Error(`Cannot connect to API server at ${baseUrl}. Make sure the server is running.`);
                }
                throw error;
            }
        );
    }

    async chat(request: ChatRequest): Promise<ChatResponse> {
        try {
            const response = await this.client.post<ChatResponse>('/chat', request);
            return response.data;
        } catch (error: any) {
            throw new Error(`Chat request failed: ${error.message}`);
        }
    }

    async listModels(): Promise<ModelInfo[]> {
        try {
            const response = await this.client.get('/models');
            // Parse the raw output to extract model names
            const rawOutput = response.data.models_raw || '';
            const models: ModelInfo[] = [];

            // Simple parsing of ollama list output
            const lines = rawOutput.split('\n').filter((line: string) => line.trim());
            for (const line of lines) {
                const parts = line.trim().split(/\s+/);
                if (parts.length >= 1) {
                    const modelName = parts[0];
                    models.push({
                        name: modelName,
                        description: `Local model: ${modelName}`
                    });
                }
            }

            return models;
        } catch (error: any) {
            throw new Error(`Failed to list models: ${error.message}`);
        }
    }

    async collaborativeChat(request: CollaborativeRequest): Promise<CollaborativeResponse> {
        try {
            const response = await this.client.post<CollaborativeResponse>('/mcp/tools/collaborative_chat', request);
            return response.data;
        } catch (error: any) {
            throw new Error(`Collaborative chat failed: ${error.message}`);
        }
    }

    async listMcpTools(): Promise<any[]> {
        try {
            const response = await this.client.get('/mcp/tools');
            return response.data.tools || [];
        } catch (error: any) {
            throw new Error(`Failed to list MCP tools: ${error.message}`);
        }
    }

    async callMcpTool(toolName: string, args: any = {}): Promise<any> {
        try {
            const response = await this.client.post(`/mcp/tools/${toolName}`, args);
            return response.data;
        } catch (error: any) {
            throw new Error(`MCP tool call failed: ${error.message}`);
        }
    }

    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.data.status === 'ok';
        } catch (error) {
            return false;
        }
    }

    updateBaseUrl(newUrl: string) {
        this.baseUrl = newUrl;
        this.client.defaults.baseURL = newUrl;
    }
}
