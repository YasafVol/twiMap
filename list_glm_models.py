import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

api_key = os.environ.get("GLM_API_KEY")
print(f"API Key present: {bool(api_key)}")

if api_key:
    client = ZhipuAI(api_key=api_key)
    try:
        # ZhipuAI doesn't strictly have a list_models endpoint in the simple SDK usually, 
        # but let's try standard 'glm-4' again with a simple hello world to debug
        # or just try a few known ones.
        
        models_to_test = ["glm-4.6", "glm-4", "glm-4-plus", "glm-4-0520"]
        
        print("Testing models...")
        for model in models_to_test:
            print(f"Testing {model}...")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print(f"  [SUCCESS] {model} works. Response: {response.choices[0].message.content}")
            except Exception as e:
                print(f"  [FAILED] {model}: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API Key found.")
