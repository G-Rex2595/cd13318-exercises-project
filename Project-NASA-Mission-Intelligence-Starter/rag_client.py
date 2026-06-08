import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional
from pathlib import Path
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

def discover_chroma_backends() -> Dict[str, Dict[str, str]]:
    """Discover available ChromaDB backends in the project directory"""
    backends = {}
    current_dir = Path(".")
    
    # Look for ChromaDB directories
    # TODO: Create list of directories that match specific criteria (directory type and name pattern)
    chroma_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name.startswith("chroma_")]

    # TODO: Loop through each discovered directory
    for chroma_dir in chroma_dirs:
        # TODO: Wrap connection attempt in try-except block for error handling
        try:
            # TODO: Initialize database client with directory path and configuration settings
            client = chromadb.PersistentClient(
                path=str(chroma_dir)
            )
            
            # TODO: Retrieve list of available collections from the database
            collections = client.list_collections()
            
            # TODO: Loop through each collection found
            for collection in collections:
                # TODO: Create unique identifier key combining directory and collection names
                collection_id = f"{chroma_dir.name}_{collection.name}"
                # TODO: Build information dictionary containing:
                    # TODO: Store directory path as string
                    # TODO: Store collection name
                    # TODO: Create user-friendly display name
                    # TODO: Get document count with fallback for unsupported operations
                metadata = {
                    "directory": str(chroma_dir),
                    "collection_name": collection.name,
                    "display_name": f"{chroma_dir.name} - {collection.name}",
                    "document_count": collection.count() if hasattr(collection, 'count') else "N/A"
                }
                # TODO: Add collection information to backends dictionary
                backends[collection_id] = metadata
        
        # TODO: Handle connection or access errors gracefully
        except Exception as e:
            # TODO: Create fallback entry for inaccessible directories
            # TODO: Include error information in display name with truncation
            # TODO: Set appropriate fallback values for missing information
            error_message = str(e)[:50]  # Truncate error message for display
            metadata = {
                "directory": str(chroma_dir),
                "collection_name": "N/A",
                "display_name": f"{chroma_dir.name} - {error_message}",
                "document_count": "N/A"
            }

    # TODO: Return complete backends dictionary with all discovered collections
    return backends

def initialize_rag_system(chroma_dir: str, collection_name: str):
    """Initialize the RAG system with specified backend (cached for performance)"""

    # TODO: Create a chomadb persistentclient
    client = chromadb.PersistentClient(
        path=chroma_dir
    )
    # TODO: Return the collection with the collection_name
    return client.get_collection(
        collection_name, 
        embedding_function=OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small",
            api_base="https://openai.vocareum.com/v1"
        )
    ), True, None

def retrieve_documents(collection, query: str, n_results: int = 3, 
                      mission_filter: Optional[str] = None) -> Optional[Dict]:
    """Retrieve relevant documents from ChromaDB with optional filtering"""

    # TODO: Initialize filter variable to None (represents no filtering)
    filter = None

    # TODO: Check if filter parameter exists and is not set to "all" or equivalent
    if mission_filter and mission_filter.lower() != "all":
        # TODO: If filter conditions are met, create filter dictionary with appropriate field-value pairs
        filter = {"mission": mission_filter}

    # TODO: Execute database query with the following parameters:
        # TODO: Pass search query in the required format
        # TODO: Set maximum number of results to return
        # TODO: Apply conditional filter (None for no filtering, dictionary for specific filtering)
    try:
        result = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter
        )
    except Exception as e:
        raise Exception(f"Error during document retrieval: {e}")

    # TODO: Return query results to caller
    return result

def format_context(documents: List[str], metadatas: List[Dict]) -> str:
    """Format retrieved documents into context"""
    if not documents:
        return ""
    
    # TODO: Initialize list with header text for context section
    context_parts = ["Context:"]

    # TODO: Loop through paired documents and their metadata using enumeration
    for index, (doc, metadata) in enumerate(zip(documents, metadatas)):
        # TODO: Extract mission information from metadata with fallback value
        mission_info = metadata.get('mission', 'Unknown Mission')
        # TODO: Clean up mission name formatting (replace underscores, capitalize)
        mission_info = mission_info.replace('_', ' ').title()
        # TODO: Extract source information from metadata with fallback value  
        source_info = metadata.get('source', 'Unknown Source')
        # TODO: Extract category information from metadata with fallback value
        category_info = metadata.get('document_category', 'Unknown Category')
        # TODO: Clean up category name formatting (replace underscores, capitalize)
        category_info = category_info.replace('_', ' ').title()
        # TODO: Create formatted source header with index number and extracted information
        source_header = f"Document {index + 1}: {mission_info} - {category_info} (Source: {source_info})"
        # TODO: Add source header to context parts list
        context_parts.append(source_header)

        # TODO: Check document length and truncate if necessary
        if len(doc) > 500:
            truncated_doc = doc[:500]
            last_period = truncated_doc.rfind('.')
            if last_period != -1:
                truncated_doc = truncated_doc[:last_period + 1]
            doc = truncated_doc + " [Content truncated for brevity]"
        # TODO: Add truncated or full document content to context parts list
        context_parts.append(doc)

    # TODO: Join all context parts with newlines and return formatted string
    return "\n".join(context_parts)