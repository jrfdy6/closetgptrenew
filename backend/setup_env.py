#!/usr/bin/env python3
"""
Setup script to create .env file for the backend
"""

import os

def create_env_file():
    """Create .env file with required environment variables"""
    
    env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DATABASE_URL=your-database-url-here

# Other Configuration
DEBUG=True
LOG_LEVEL=INFO
"""
    
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file_path):
        print(f"⚠️  .env file already exists at {env_file_path}")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file_path}")
        print("📝 Please edit the .env file and add your actual API keys and configuration values.")
        print("🔑 You'll need to replace 'your-openai-api-key-here' with your actual OpenAI API key.")
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")

if __name__ == "__main__":
    print("🚀 Setting up .env file for backend...")
    create_env_file() 