import os
import json
import time
from typing import List, Dict, Any, Callable, Optional
import argparse

class PromptWorkflow:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the prompt workflow with an optional configuration file.
        
        Args:
            config_path: Path to a JSON configuration file (optional)
        """
        self.prompts = []
        self.results = {}
        self.config = {}
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Load predefined prompts from config if available
            if 'prompts' in self.config:
                self.prompts = self.config['prompts']
    
    def add_prompt(self, prompt_template: str, name: str, 
                   processor: Optional[Callable] = None) -> None:
        """
        Add a prompt to the workflow.
        
        Args:
            prompt_template: Template string with {placeholders} for variable substitution
            name: Unique name for this prompt step
            processor: Optional function to process the result
        """
        self.prompts.append({
            'name': name,
            'template': prompt_template,
            'processor': processor
        })
    
    def run(self, initial_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the prompt workflow from start to finish.
        
        Args:
            initial_input: Initial variables to populate first prompt
            
        Returns:
            Dictionary containing results from all steps
        """
        context = initial_input or {}
        self.results = {}
        
        for i, prompt_config in enumerate(self.prompts):
            name = prompt_config['name']
            template = prompt_config['template']
            processor = prompt_config['processor']
            
            # Fill in the template with available context
            try:
                filled_prompt = template.format(**context)
            except KeyError as e:
                print(f"Error: Missing variable {e} for prompt '{name}'")
                return self.results
            
            # Display the prompt to the user and get input
            print(f"\n--- STEP {i+1}: {name} ---")
            print(f"Prompt: {filled_prompt}")
            
            # Get result from user
            result = input("\nEnter result (or type 'AUTO' to simulate automatic response): ")
            
            # Simple simulation of automatic response for testing
            if result == "AUTO":
                result = f"Simulated response for: {filled_prompt}"
                print(f"Simulated: {result}")
            
            # Process the result if a processor exists
            if processor and callable(processor):
                processed_result = processor(result)
                print(f"Processed: {processed_result}")
                self.results[name] = processed_result
                # Add to context for next prompt
                context[name] = processed_result
            else:
                self.results[name] = result
                # Add to context for next prompt
                context[name] = result
                
            # Add raw result as well
            context[f"{name}_raw"] = result
            
            # Pause briefly for readability
            time.sleep(0.5)
            
        return self.results
    
    def save_results(self, output_path: str) -> None:
        """
        Save the workflow results to a JSON file.
        
        Args:
            output_path: File path for the output JSON
        """
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {output_path}")

# Example processors you can use
def extract_keywords(text: str) -> List[str]:
    """Example processor that extracts keywords from text"""
    # This is a simple implementation - you can replace with more sophisticated logic
    words = text.lower().split()
    keywords = [word for word in words if len(word) > 4]
    return keywords[:5]  # Return top 5 keywords

def summarize(text: str) -> str:
    """Example processor that summarizes text"""
    # Simple summarization - replace with better algorithm
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text
    return '. '.join(sentences[:2]) + '.'

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a prompt workflow")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", default="results.json", help="Output file path")
    args = parser.parse_args()
    
    # Create a workflow
    workflow = PromptWorkflow(args.config)
    
    # If no config file, set up a default workflow
    if not args.config:
        # Initial creative prompt
        workflow.add_prompt(
            prompt_template="Generate a short story about {theme} in {setting}.",
            name="story_generation"
        )
        
        # Follow-up prompt using the result
        workflow.add_prompt(
            prompt_template="Based on this story: '{story_generation}'\n\nIdentify the main character and describe their motivation.",
            name="character_analysis"
        )
        
        # Final prompt building on previous results
        workflow.add_prompt(
            prompt_template="Create a sequel idea based on this character motivation: {character_analysis}",
            name="sequel_idea",
            processor=summarize
        )
    
    # Run the workflow with initial context
    results = workflow.run({
        "theme": input("Enter a theme: "),
        "setting": input("Enter a setting: ")
    })
    
    # Save results
    workflow.save_results(args.output)