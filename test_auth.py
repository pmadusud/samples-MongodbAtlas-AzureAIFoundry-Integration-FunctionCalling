"""
Azure AI Foundry Authentication Test Script
This script helps diagnose and fix authentication issues when connecting to Azure AI Foundry.
"""

import os
import sys
from azure.identity import DefaultAzureCredential, AzureCliCredential, ManagedIdentityCredential
from azure.ai.inference import EmbeddingsClient

def test_authentication():
    """Test different authentication methods for Azure AI Foundry."""
    
    # Check required environment variables
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    embedding_model = os.getenv("AZURE_FOUNDRY_EMBEDDING_MODEL")
    
    print("=== Azure AI Foundry Authentication Test ===\n")
    
    if not project_endpoint:
        print("❌ PROJECT_ENDPOINT environment variable is not set")
        print("   Please set it to your Azure AI Foundry project endpoint")
        return False
    else:
        print(f"✅ PROJECT_ENDPOINT: {project_endpoint}")
    
    if not embedding_model:
        print("❌ AZURE_FOUNDRY_EMBEDDING_MODEL environment variable is not set")
        print("   Please set it to your embedding model name")
        return False
    else:
        print(f"✅ AZURE_FOUNDRY_EMBEDDING_MODEL: {embedding_model}")
    
    print("\n=== Testing Authentication Methods ===\n")
    
    # Test 1: DefaultAzureCredential
    print("1. Testing DefaultAzureCredential...")
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print("   ✅ DefaultAzureCredential: SUCCESS")
        
        # Test actual API call
        try:
            client = EmbeddingsClient(
                endpoint=project_endpoint,
                credential=credential,
                model=embedding_model
            )
            response = client.embed(input=["test"])
            print("   ✅ API call with DefaultAzureCredential: SUCCESS")
            return True
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            
    except Exception as e:
        print(f"   ❌ DefaultAzureCredential failed: {e}")
    
    # Test 2: Azure CLI Credential
    print("\n2. Testing AzureCliCredential...")
    try:
        credential = AzureCliCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print("   ✅ AzureCliCredential: SUCCESS")
        
        # Test actual API call
        try:
            client = EmbeddingsClient(
                endpoint=project_endpoint,
                credential=credential,
                model=embedding_model
            )
            response = client.embed(input=["test"])
            print("   ✅ API call with AzureCliCredential: SUCCESS")
            return True
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            
    except Exception as e:
        print(f"   ❌ AzureCliCredential failed: {e}")
        print("   💡 Try running: az login")
    
    # Test 3: Managed Identity (if running on Azure)
    print("\n3. Testing ManagedIdentityCredential...")
    try:
        credential = ManagedIdentityCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print("   ✅ ManagedIdentityCredential: SUCCESS")
        
        # Test actual API call
        try:
            client = EmbeddingsClient(
                endpoint=project_endpoint,
                credential=credential,
                model=embedding_model
            )
            response = client.embed(input=["test"])
            print("   ✅ API call with ManagedIdentityCredential: SUCCESS")
            return True
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            
    except Exception as e:
        print(f"   ❌ ManagedIdentityCredential failed: {e}")
        print("   💡 This is expected if not running on Azure")
    
    return False

def print_troubleshooting_guide():
    """Print troubleshooting guide for authentication issues."""
    
    print("\n=== Troubleshooting Guide ===\n")
    
    print("Common Authentication Issues and Solutions:\n")
    
    print("1. 'No subscription found' error:")
    print("   - Run: az login")
    print("   - Run: az account set --subscription <your-subscription-id>")
    print("   - Verify: az account show\n")
    
    print("2. 'Insufficient privileges' error:")
    print("   - Ensure your account has 'Cognitive Services User' role")
    print("   - Check resource-level permissions in Azure portal")
    print("   - Verify the PROJECT_ENDPOINT is correct\n")
    
    print("3. 'Invalid audience' error:")
    print("   - Verify PROJECT_ENDPOINT format: https://<project-name>.<region>.inference.ml.azure.com")
    print("   - Check if the model deployment is active\n")
    
    print("4. Environment variable setup:")
    print("   - PROJECT_ENDPOINT: Your Azure AI Foundry project endpoint")
    print("   - AZURE_FOUNDRY_EMBEDDING_MODEL: Your embedding model deployment name")
    print("   - Optional: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID for service principal\n")
    
    print("5. Alternative authentication methods:")
    print("   - Service Principal: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
    print("   - Managed Identity: Use when running on Azure (VM, App Service, etc.)")
    print("   - Interactive: Let DefaultAzureCredential handle browser-based login\n")

def main():
    """Main function to run authentication tests."""
    
    success = test_authentication()
    
    if not success:
        print_troubleshooting_guide()
        
        print("=== Next Steps ===\n")
        print("1. Follow the troubleshooting guide above")
        print("2. Run this script again to verify authentication")
        print("3. Once authentication works, your main application should work too")
        
        sys.exit(1)
    else:
        print("\n🎉 Authentication is working correctly!")
        print("Your main application should now work without authentication errors.")

if __name__ == "__main__":
    main()
