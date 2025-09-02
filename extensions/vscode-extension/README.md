# Local Multi-Model AI Gateway - VSCode Extension

This VSCode extension provides seamless integration with your local multi-model AI gateway, allowing you to chat with AI models directly from VSCode.

## Features

- 🤖 **Model Explorer**: Browse and manage your local AI models
- 💬 **AI Chat**: Chat with individual models or use smart routing
- 👥 **Collaborative Chat**: Multiple models working together on complex tasks
- 🔧 **MCP Integration**: Full Model Context Protocol support
- ⚡ **Real-time Communication**: Direct connection to your local API server

## Prerequisites

1. **Local Multi-Model Gateway**: Make sure your API server is running
   ```bash
   cd /path/to/your/gateway
   .\service_launcher.ps1 -StartAPI
   ```

2. **Ollama Models**: Ensure your models are available
   ```bash
   .\service_launcher.ps1 -PullModels
   ```

## Installation

1. Clone or download this extension
2. Run `npm install` in the `vscode-extension` directory
3. Run `npm run compile` to build the extension
4. Open VSCode and go to Extensions → Install from VSIX
5. Select the generated `.vsix` file

## Configuration

Configure the extension in VSCode settings:

```json
{
  "localModels.apiUrl": "http://localhost:8000",
  "localModels.defaultModel": "auto",
  "localModels.timeout": 120,
  "localModels.maxTokens": 2048
}
```

## Usage

### Model Explorer
- Open the Explorer panel
- Find "Local AI Models" section
- Browse available models and their capabilities
- Right-click on a model to start chatting

### AI Chat
- Use Command Palette: `Ctrl+Shift+P` → "Local Models: Chat with AI Model"
- Select a model or choose "auto" for smart routing
- Type your message and get AI responses

### Collaborative Chat
- Use Command Palette: `Ctrl+Shift+P` → "Local Models: Collaborative Chat"
- Select multiple models for collaboration
- Ask complex questions that benefit from multiple AI perspectives

## Commands

| Command | Description |
|---------|-------------|
| `localModels.chat` | Start a chat with a specific model |
| `localModels.collaborate` | Start collaborative chat with multiple models |
| `localModels.refresh` | Refresh the model list |

## Troubleshooting

### Connection Issues
- Ensure your API server is running on the configured URL
- Check firewall settings
- Verify the API endpoint is accessible

### Model Not Found
- Run `.\service_launcher.ps1 -PullModels` to ensure models are downloaded
- Check Ollama service is running
- Verify model names in the API response

### Extension Not Loading
- Check VSCode developer console for errors
- Ensure all dependencies are installed
- Try reloading VSCode window

## Development

### Building
```bash
npm run compile
npm run watch  # For development
```

### Testing
```bash
npm run test
```

### Debugging
1. Open the extension in VSCode
2. Press `F5` to launch extension development host
3. Test features in the new window

## Architecture

```
VSCode Extension
├── extension.ts          # Main extension entry point
├── services/
│   └── ApiClient.ts      # HTTP client for API communication
├── providers/
│   └── LocalModelsProvider.ts  # Tree view for models
└── panels/
    └── ChatPanel.ts      # Webview panel for chat interface
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This extension is part of the Local Multi-Model AI Gateway project.
