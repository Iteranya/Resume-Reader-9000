import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class AIProviderClient:
    def __init__(self, provider="openrouter", model="gpt-3.5-turbo"):
        """
        Initialize the client with a provider and model.
        Expects OPENAI_API_KEY in your .env file.
        """
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file.")
        openai.api_key = self.api_key
        self.set_provider(provider)

    def set_provider(self, provider):
        """
        Set the API provider. By default, OpenRouter is used.
        For a custom provider, you can also set the base URL in your .env file
        under OPENAI_API_BASE.
        """
        self.provider = provider.lower()
        if self.provider == "openrouter":
            openai.api_base = "https://openrouter.ai/api/v1"
        elif self.provider == "openai":
            openai.api_base = "https://api.openai.com/v1"
        else:
            # For custom providers, ensure you have set OPENAI_API_BASE in your .env
            custom_api_base = os.getenv("OPENAI_API_BASE")
            if not custom_api_base:
                raise ValueError("For custom providers, set OPENAI_API_BASE in your .env file.")
            openai.api_base = custom_api_base

    def send_prompt(self, prompt, system_prompt="You are a helpful assistant.", temperature=0.7, max_tokens=150):
        """
        Send a prompt to the AI provider and return the generated response.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message["content"]
        except Exception as e:
            print(f"Error sending prompt: {e}")
            return None

    def send_prompt_stream(self, prompt, system_prompt="You are a helpful assistant.", temperature=0.7, max_tokens=150):
        """
        Send a prompt with streaming enabled and yield incremental response chunks.
        Useful for handling long responses.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in response:
                if 'choices' in chunk:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
        except Exception as e:
            print(f"Error in streaming prompt: {e}")

    def list_models(self):
        """
        List available models from the provider.
        """
        try:
            models = openai.Model.list()
            return models.get("data", [])
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def set_model(self, model):
        """
        Update the model used for generating responses.
        """
        self.model = model

    def update_api_key(self, new_api_key):
        """
        Update the API key both in the instance and in the OpenAI library.
        """
        self.api_key = new_api_key
        openai.api_key = new_api_key

# Example usage:
if __name__ == "__main__":
    client = AIProviderClient()  # Uses default provider (OpenRouter) and model (gpt-3.5-turbo)
    answer = client.send_prompt("Tell me a joke about programmers.")
    print("AI Response:", answer)

    # Streaming example:
    print("Streaming response:")
    for part in client.send_prompt_stream("Explain quantum computing in simple terms."):
        print(part, end="", flush=True)
