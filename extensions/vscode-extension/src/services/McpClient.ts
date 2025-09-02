import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface McpTool {
    name: string;
    description: string;
    inputSchema: any;
}

export interface McpToolCall {
    name: string;
    arguments: Record<string, any>;
}

export interface McpToolResult {
    status: 'success' | 'error' | 'timeout';
    data?: any;
    error?: string;
    execution_time: number;
    tool_name: string;
    timestamp: number;
}

export class McpClient {
    private client: AxiosInstance;
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 120000, // 2 minutes timeout
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                if (error.code === 'ECONNREFUSED') {
                    throw new Error(`Cannot connect to MCP server at ${baseUrl}. Make sure the server is running.`);
                }
                throw error;
            }
        );
    }

    async listTools(): Promise<McpTool[]> {
        try {
            const response = await this.client.get('/tools');
            return response.data;
        } catch (error: any) {
            throw new Error(`Failed to list MCP tools: ${error.message}`);
        }
    }

    async callTool(toolCall: McpToolCall): Promise<McpToolResult> {
        try {
            const response = await this.client.post('/call_tool', {
                name: toolCall.name,
                arguments: toolCall.arguments
            });
            return response.data;
        } catch (error: any) {
            throw new Error(`Failed to call MCP tool ${toolCall.name}: ${error.message}`);
        }
    }

    async chatWithModel(input: string, model?: string, userId?: string): Promise<McpToolResult> {
        return this.callTool({
            name: 'chat_with_model',
            arguments: {
                input,
                model,
                user_id: userId || 'vscode-user'
            }
        });
    }

    async listAvailableModels(includeDetails = false): Promise<McpToolResult> {
        return this.callTool({
            name: 'list_available_models',
            arguments: {
                include_details: includeDetails
            }
        });
    }

    async collaborativeChat(input: string, models: string[], maxRounds = 3, strategy = 'sequential'): Promise<McpToolResult> {
        return this.callTool({
            name: 'collaborative_chat',
            arguments: {
                input,
                models,
                max_rounds: maxRounds,
                strategy
            }
        });
    }

    async getServerHealth(): Promise<any> {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error: any) {
            throw new Error(`Failed to get server health: ${error.message}`);
        }
    }
}
