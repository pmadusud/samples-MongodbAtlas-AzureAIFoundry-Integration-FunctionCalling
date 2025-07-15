# MongoDB Atlas + Azure AI Foundry Integration with Function Calling

This sample demonstrates how to build an intelligent agent that combines **MongoDB Atlas Vector Search** with **Azure AI Foundry** using function calling capabilities. The agent can perform hybrid search (vector + full-text) on MongoDB Atlas data and provide intelligent responses using Azure AI models.

## 🚀 Features

- **Hybrid Search**: Combines vector similarity search with full-text search using MongoDB's `$rankFusion` operator
- **Azure AI Integration**: Uses Azure AI Foundry for LLM responses and embeddings generation
- **Function Calling**: Implements Azure AI Agents with custom function tools
- **Intelligent Fallback**: Automatically falls back to vector-only search if `$rankFusion` isn't available
- **Size Optimization**: Handles Azure AI Agents' 512KB tool output limit with smart truncation
- **Streaming Responses**: Real-time streaming of AI responses with proper event handling
- **Authentication Testing**: Built-in utilities to test and troubleshoot Azure authentication

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Azure AI Agent  │───▶│ MongoDB Atlas   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Azure Embeddings │    │ Hybrid Search   │
                       │    Service       │    │ (Vector + Text) │
                       └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Azure Resources
- **Azure AI Foundry Project** with deployed models:
  - LLM model (e.g., `gpt-4o`)
  - Embedding model (e.g., `text-embedding-ada-002`)

### MongoDB Atlas
- **MongoDB Atlas cluster** with Vector Search enabled
- **Database and collection** with your documents
- **Search indexes** configured:
  - Vector search index for embeddings
  - Full-text search index for text content

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pmadusud/samples-MongodbAtlas-AzureAIFoundry-Integration-FunctionCalling.git
   cd samples-MongodbAtlas-AzureAIFoundry-Integration-FunctionCalling
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration values
   ```

4. **Configure authentication**:
   ```bash
   az login  # For Azure CLI authentication
   ```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

#### Azure AI Foundry
```env
PROJECT_ENDPOINT=https://your-project.your-region.services.ai.azure.com/api/projects/your-project
MODEL_DEPLOYMENT_NAME=gpt-4o
AZURE_AI_EMBEDDINGS_ENDPOINT=https://your-service.cognitiveservices.azure.com/openai/deployments/your-embedding-model
AZURE_AI_EMBEDDINGS_KEY=your-embeddings-api-key
AZURE_FOUNDRY_EMBEDDING_MODEL=text-embedding-ada-002
```

#### MongoDB Atlas
```env
MONGODB_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_ATLAS_DATABASE=your-database-name
MONGODB_ATLAS_COLLECTION=your-collection-name
MONGODB_ATLAS_VECTOR_INDEXNAME=default
MONGODB_ATLAS_FULLTEXT_INDEXNAME=default_fulltext_search
MONGODB_ATLAS_VECTORINDEX_PATH=embedding
MONGODB_ATLAS_FULLTEXTINDEX_PATH=content
```

📖 **For detailed configuration instructions, see [ENVIRONMENT_SETUP_GUIDE.md](ENVIRONMENT_SETUP_GUIDE.md)**

## 📊 Document Structure

Your MongoDB documents should follow this structure:

```json
{
  "_id": "product_123",
  "content": "Complete description and features of the camping tent...",
  "embedding": [0.1, 0.2, 0.3, ...],  // 1536-dimensional vector
}
```

## 🚀 Usage

### Basic Usage

1. **Test authentication** (recommended first step):
   ```bash
   python test_auth.py
   ```

2. **Run the agent**:
   ```bash
   python main.py
   ```

3. **Interact with the agent**:
   ```
   Enter your query: What camping tents do you have under $300?
   ```

### Example Queries

- "Show me outdoor camping gear"
- "What products are available in the sporting goods category?"
- "Find lightweight camping equipment"
- "What's the most expensive item in your inventory?"

## 🔧 Key Components

### `main.py`
- Main application entry point
- Sets up Azure AI Agents with function calling
- Handles user interaction and streaming responses

### `mongodb_hybridsearch.py`
- MongoDB Atlas hybrid search implementation
- Handles vector and full-text search combination
- Includes size optimization for 512KB tool output limits
- Automatic fallback mechanisms

### `stream_event_handler.py`
- Manages streaming responses from Azure AI
- Handles different event types (messages, errors, completion)
- Provides real-time user feedback

### `test_auth.py`
- Authentication testing utility
- Tests different Azure credential methods
- Provides troubleshooting guidance

## 🎯 Advanced Features

### Hybrid Search with $rankFusion

The implementation uses MongoDB's `$rankFusion` operator to combine:
- **Vector search**: Semantic similarity using embeddings
- **Full-text search**: Keyword matching on text content
- **Weighted combination**: 70% vector, 30% full-text (configurable)

### Size Optimization

Handles Azure AI Agents' 512KB tool output limit through:
- Field projection (only return necessary fields)
- Text truncation for large content
- Dynamic result count adjustment
- Progressive size reduction strategies

### Error Handling

- Comprehensive error handling for both Azure and MongoDB
- Automatic fallback strategies
- Detailed logging and user feedback
- Connection retry mechanisms

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Run `python test_auth.py` to diagnose
   - Ensure `az login` is completed
   - Verify project endpoints and keys

2. **MongoDB Connection Issues**:
   - Check IP whitelist in MongoDB Atlas
   - Verify connection string format
   - Ensure cluster is running

3. **Search Index Issues**:
   - Verify indexes are created and active
   - Check field name mappings
   - Ensure vector dimensions match model (1536 for text-embedding-ada-002)

4. **Tool Output Size Errors**:
   - The system automatically handles size limits
   - Check [TOOL_OUTPUT_SIZE_FIX.md](TOOL_OUTPUT_SIZE_FIX.md) for details

## 📚 Documentation

- [Environment Setup Guide](ENVIRONMENT_SETUP_GUIDE.md) - Detailed configuration instructions
- [Tool Output Size Fix](TOOL_OUTPUT_SIZE_FIX.md) - Technical details on size optimization
- [Function Calling Instructions](instructions/function_calling.txt) - Agent behavior configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the documentation files
3. Run `python test_auth.py` for authentication issues
4. Open an issue in this repository