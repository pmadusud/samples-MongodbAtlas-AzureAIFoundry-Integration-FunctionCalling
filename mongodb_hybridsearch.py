from typing import Optional, List
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from azure.ai.inference import EmbeddingsClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from pymongo.server_api import ServerApi

class MongoDBAtlasHybridSearch:
    """
    Class to perform hybrid search on MongoDB Atlas using Azure AI Foundry embeddings.
    """

    def __init__(self):
        self.mongo_uri = str(os.getenv("MONGODB_ATLAS_URI"))
        self.db_name = str(os.getenv("MONGODB_ATLAS_DATABASE"))
        self.coll_name = str(os.getenv("MONGODB_ATLAS_COLLECTION"))
        self.vector_index_name = str(os.getenv("MONGODB_ATLAS_VECTOR_INDEXNAME", "default"))
        self.fulltext_index_name = str(os.getenv("MONGODB_ATLAS_FULLTEXT_INDEXNAME", "default_fulltext_search"))
        self.vectorindex_path = str(os.getenv("MONGODB_ATLAS_VECTORINDEX_PATH", "embedding"))
        self.fulltextindex_path = str(os.getenv("MONGODB_ATLAS_FULLTEXTINDEX_PATH", "content"))
        self.endpoint = str(os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"])
        self.key = str(os.environ["AZURE_AI_EMBEDDINGS_KEY"])
        
        self.client = MongoClient(self.mongo_uri, server_api=ServerApi('1'))
        self.db = self.client[self.db_name]
        self.collection = self.db[self.coll_name]

    async def close(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()
    
    def _estimate_size_and_truncate(self, results: List[dict], max_size_kb: int = 400) -> List[dict]:
        """
        Estimate the size of results and truncate if needed to stay under the limit.
        
        Args:
            results: List of documents from MongoDB
            max_size_kb: Maximum size in KB (default 400KB, leaving buffer for 512KB limit)
            
        Returns:
            List of truncated documents
        """
        import json
        
        # Estimate current size
        try:
            current_size = len(json.dumps(results, default=str).encode('utf-8'))
            current_size_kb = current_size / 1024
            
            if current_size_kb <= max_size_kb:
                return results
                
            print(f"Results are {current_size_kb:.1f}KB, truncating to fit under {max_size_kb}KB limit...")
            
            # If too large, reduce number of results and truncate fields further
            truncated_results = []
            max_results = min(len(results), 2)  # Further reduce number of results
            
            for i, doc in enumerate(results[:max_results]):
                if i >= max_results:
                    break
                    
                truncated_doc = {}
                for key, value in doc.items():
                    if isinstance(value, str):
                        # More aggressive truncation
                        if len(value) > 200:
                            truncated_doc[key] = value[:200] + "..."
                        else:
                            truncated_doc[key] = value
                    elif isinstance(value, (int, float)):
                        truncated_doc[key] = value
                    elif key in ["_id", "score", "_score"]:
                        truncated_doc[key] = value
                    else:
                        # Skip complex objects to reduce size
                        truncated_doc[key] = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                
                truncated_results.append(truncated_doc)
            
            # Check size again
            new_size = len(json.dumps(truncated_results, default=str).encode('utf-8'))
            new_size_kb = new_size / 1024
            print(f"Truncated to {new_size_kb:.1f}KB with {len(truncated_results)} results")
            
            return truncated_results
            
        except Exception as e:
            print(f"Error estimating size: {e}")
            # Return first 2 results with minimal fields as fallback
            return [{"_id": doc.get("_id", ""), "title": str(doc.get("title", ""))[:100], "error": "Size estimation failed"} 
                   for doc in results[:2]]

    async def get_embedding(self, text):
        """
        Generates an embedding vector for the given input text using Azure AI Embeddings.

        Args:
            text (str): The input text to generate the embedding for.

        Returns:
            list: A single embedding vector (flat list of floats) for the input text.
        """
        embeddings = []
        """ try:
            endpoint = os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"]
            key = os.environ["AZURE_AI_EMBEDDINGS_KEY"]
        except KeyError:
            print("Missing environment variable 'AZURE_AI_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_EMBEDDINGS_KEY'")
            print("Set them before running this sample.")
            raise RuntimeError("Required Azure AI Embeddings environment variables are missing.")
 """
        # [START embeddings]
        
        client = EmbeddingsClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))

        response = client.embed(input=[text])
        # Get the first (and only) embedding vector as a flat list
        if response.data and len(response.data) > 0:
            return response.data[0].embedding
        else:
            raise RuntimeError("No embedding returned from Azure AI service")

    async def async_hybrid_search_mongodb_atlas(self,
            search_content: str,
            limit: int = 3,
            include_fields: Optional[List[str]] = None
        ):
        """
        Connects to MongoDB Atlas and performs a hybrid search (text + vector) on the specified collection.
        Falls back to vector-only search if $rankFusion is not supported.
        
        Assumes the collection has a text index and a vector index (for example, using Atlas Vector Search).

        Args:
            search_content (str): The content to search for (text or embedding).
            limit (int): Maximum number of results to return (default: 3, max: 5)
            include_fields (list): List of fields to include in results (reduces output size)

        Returns:
            list: List of matching documents with limited fields to stay under 512KB limit.
        """
        # Enforce maximum limit to prevent large outputs
        limit = min(limit, 5)
        
        # Default fields to include (excluding large fields like embeddings and full content)
        if include_fields is None:
            include_fields = ["_id", "content"]
        # Get MongoDB Atlas connection string from environment variable
        #mongo_uri = os.getenv("MONGODB_ATLAS_URI")
        #if not mongo_uri:
        #    raise ValueError("MONGODB_ATLAS_URI environment variable not set.")

        try:
            #client = MongoClient(mongo_uri, server_api=ServerApi('1'))
            #db_name = os.getenv("MONGODB_ATLAS_DATABASE")
            #coll_name = os.getenv("MONGODB_ATLAS_COLLECTION")

            #vector_index_name = os.getenv("MONGODB_ATLAS_VECTOR_INDEXNAME", "default")
            #fulltext_index_name = os.getenv("MONGODB_ATLAS_FULLTEXT_INDEXNAME", "default_fulltext_search")
            #vectorindex_path = os.getenv("MONGODB_ATLAS_VECTORINDEX_PATH", "embedding")
            #fulltextindex_path = os.getenv("MONGODB_ATLAS_FULLTEXTINDEX_PATH", "content")

            #if not db_name or not coll_name:
            #    raise ValueError("MONGODB_ATLAS_DATABASE and MONGODB_ATLAS_COLLECTION environment variables must be set.")

            #db = client[db_name]
            #collection = db[coll_name]

            embedding_vector = await self.get_embedding(search_content)
            if not isinstance(embedding_vector, list) or not embedding_vector:
                raise ValueError("Embedding vector is not a valid list. Check the embedding extraction logic.")

            # Ensure the embedding vector is a flat list of numbers
            if isinstance(embedding_vector[0], list):
                # If it's a list of lists, take the first embedding
                embedding_vector = embedding_vector[0]

            # Try hybrid search with $rankFusion first
            try:
                pipeline = [
                    {
                        "$rankFusion": {
                            "input": {
                                "pipelines": {
                                    "vectorPipeline": [
                                        {
                                            "$vectorSearch": {
                                                "index": self.vector_index_name,
                                                "path": self.vectorindex_path,
                                                "queryVector": embedding_vector,
                                                "numCandidates": 50,
                                                "limit": limit
                                            }
                                        }
                                    ],
                                    "fullTextPipeline": [
                                        {
                                            "$search": {
                                                "index": self.fulltext_index_name,
                                                "phrase": {
                                                    "query": search_content,
                                                    "path": self.fulltextindex_path
                                                }
                                            }
                                        },
                                        { "$limit": limit }
                                    ]
                                }
                            },
                            "combination": {
                                "weights": {
                                    "vectorPipeline": 0.7,
                                    "fullTextPipeline": 0.3
                                }
                            },
                            "scoreDetails": False  # Reduce output size
                        }
                    },
                    {
                        "$limit": limit
                    }
                ]

                # Add field projection to reduce document size
                projection = {}
                for field in include_fields:
                    projection[field] = 1
                projection["_score"] = 1  # Include search score
                pipeline.append({"$project": projection})

                results = list(self.collection.aggregate(pipeline))
                
                # Further truncate large fields if they exist
                cleaned_results = []
                for doc in results:
                    clean_doc = {}
                    for key, value in doc.items():
                        if isinstance(value, str) and len(value) > 500:
                            # Truncate large text fields
                            clean_doc[key] = value[:500] + "..."
                        else:
                            clean_doc[key] = value
                    cleaned_results.append(clean_doc)
                
                # Ensure results fit within size limit
                return self._estimate_size_and_truncate(cleaned_results)
                
            except Exception as rank_fusion_error:
                print(f"$rankFusion failed (likely due to MongoDB version or index configuration): {rank_fusion_error}")
                print("Falling back to vector search only...")
                
                # Fallback to vector search only
                fallback_pipeline = [
                    {
                        "$vectorSearch": {
                            "index": self.vector_index_name,
                            "path": self.vectorindex_path,
                            "queryVector": embedding_vector,
                            "numCandidates": 50,
                            "limit": limit
                        }
                    }
                ]
                
                # Add field projection to reduce document size
                projection = {}
                for field in include_fields:
                    projection[field] = 1
                projection["score"] = {"$meta": "vectorSearchScore"}  # Include vector search score
                fallback_pipeline.append({"$project": projection})
                
                results = list(self.collection.aggregate(fallback_pipeline))
                
                # Further truncate large fields if they exist
                cleaned_results = []
                for doc in results:
                    clean_doc = {}
                    for key, value in doc.items():
                        if isinstance(value, str) and len(value) > 500:
                            # Truncate large text fields
                            clean_doc[key] = value[:500] + "..."
                        else:
                            clean_doc[key] = value
                    cleaned_results.append(clean_doc)
                
                # Ensure results fit within size limit
                return self._estimate_size_and_truncate(cleaned_results)
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB Atlas: {e}")
            return []
        except Exception as e:
            print(f"Error in hybrid_search_mongodb_atlas: {e}")
            return []


# Example usage:
import asyncio

if __name__ == "__main__":
    # Set your MongoDB Atlas URI in the environment variable before running
    # os.environ["MONGODB_ATLAS_URI"] = "your-mongodb-atlas-uri"

    async def main():
        searcher = MongoDBAtlasHybridSearch()
        search_results = await searcher.async_hybrid_search_mongodb_atlas("sample search")
        for doc in search_results:
            print(doc)
        await searcher.close()

    asyncio.run(main())