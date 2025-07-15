# Environment Variables Configuration Guide

This guide explains how to configure each environment variable in your `.env` file.

## Azure AI Foundry Configuration

### `PROJECT_ENDPOINT`
- **Description**: Your Azure AI Foundry project endpoint URL
- **Format**: `https://your-project-name.your-region.services.ai.azure.com/api/projects/your-project-name`
- **How to find**: 
  1. Go to [Azure AI Foundry](https://ai.azure.com)
  2. Select your project
  3. Go to Project settings → Overview
  4. Copy the "Project connection string" or "Endpoint URL"

### `MODEL_DEPLOYMENT_NAME`
- **Description**: Name of your deployed LLM model in Azure AI Foundry
- **Example**: `gpt-4o`, `gpt-35-turbo`
- **How to find**:
  1. In Azure AI Foundry, go to Deployments
  2. Copy the deployment name (not the model name)

## Azure AI Embeddings Configuration

### `AZURE_AI_EMBEDDINGS_ENDPOINT`
- **Description**: Direct endpoint to your embedding model deployment
- **Format**: `https://your-cognitive-service.cognitiveservices.azure.com/openai/deployments/your-embedding-model`
- **How to find**:
  1. In Azure AI Foundry, go to Deployments
  2. Find your embedding model deployment
  3. Copy the endpoint URL

### `AZURE_AI_EMBEDDINGS_KEY`
- **Description**: API key for accessing the embedding service
- **How to find**:
  1. In Azure AI Foundry, go to Project settings
  2. Go to Keys and endpoints
  3. Copy one of the keys

### `AZURE_FOUNDRY_EMBEDDING_MODEL`
- **Description**: Name of your embedding model deployment
- **Example**: `text-embedding-ada-002`, `text-embedding-3-small`
- **How to find**: Same as MODEL_DEPLOYMENT_NAME but for embeddings

## MongoDB Atlas Configuration

### `MONGODB_ATLAS_URI`
- **Description**: Connection string to your MongoDB Atlas cluster
- **Format**: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=app-name`
- **How to find**:
  1. In MongoDB Atlas, go to Database → Connect
  2. Choose "Connect your application"
  3. Copy the connection string
  4. Replace `<password>` with your actual password

### `MONGODB_ATLAS_DATABASE`
- **Description**: Name of the database containing your documents
- **Example**: `contoso`, `products`, `knowledge_base`

### `MONGODB_ATLAS_COLLECTION`
- **Description**: Name of the collection containing your documents
- **Example**: `products`, `documents`, `articles`

## MongoDB Atlas Search Index Configuration

### `MONGODB_ATLAS_VECTOR_INDEXNAME`
- **Description**: Name of your vector search index
- **Default**: `default`
- **How to create**:
  1. In MongoDB Atlas, go to Search → Create Index
  2. Choose "Atlas Vector Search"
  3. Configure with your embedding field

### `MONGODB_ATLAS_FULLTEXT_INDEXNAME`
- **Description**: Name of your full-text search index
- **Default**: `default_fulltext_search`
- **How to create**:
  1. In MongoDB Atlas, go to Search → Create Index
  2. Choose "Atlas Search"
  3. Configure with your text fields

### `MONGODB_ATLAS_VECTORINDEX_PATH`
- **Description**: Field name in your documents that contains the embedding vectors
- **Default**: `embedding`
- **Example**: Your documents should have a field like `{"embedding": [0.1, 0.2, ...]}`

### `MONGODB_ATLAS_FULLTEXTINDEX_PATH`
- **Description**: Field name in your documents that contains the searchable text
- **Default**: `content`
- **Example**: Your documents should have a field like `{"content": "Your text content here"}`

## Optional Configuration

### `AZURE_BING_CONNECTION_ID`
- **Description**: Connection ID for Azure Bing Search integration
- **When needed**: Only if you're using Bing Search functionality

### Service Principal Authentication
Use these instead of DefaultAzureCredential if running in environments without Azure CLI:

- `AZURE_CLIENT_ID`: Application (client) ID
- `AZURE_CLIENT_SECRET`: Client secret value  
- `AZURE_TENANT_ID`: Directory (tenant) ID

## Sample Document Structure

Your MongoDB documents should have this structure for optimal search performance:

```json
{
  "_id": "product_123",
  "title": "Outdoor Camping Tent",
  "description": "High-quality 4-person camping tent...",
  "content": "Complete text content for full-text search...",
  "embedding": [0.1, 0.2, 0.3, ...],  // 1536-dimensional vector for text-embedding-ada-002
  "category": "Camping Gear",
  "price": 299.99
}
```

## Troubleshooting

### Authentication Issues
- Run `az login` to authenticate with Azure CLI
- Verify your Azure AI Foundry project permissions
- Check that keys and endpoints are correct

### MongoDB Connection Issues
- Verify your IP address is whitelisted in MongoDB Atlas
- Check username/password in connection string
- Ensure cluster is running and accessible

### Search Index Issues
- Verify indexes are created and active in MongoDB Atlas
- Check field names match your document structure
- Ensure vector dimensions match your embedding model (1536 for text-embedding-ada-002)
