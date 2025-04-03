#!/usr/bin/env python3
"""
hf_code_generation.py - Generate code using Hugging Face's code models.

This script demonstrates how to use Hugging Face models to generate code,
specifically focusing on creating Java test methods.
"""

import os
import argparse
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

class HuggingFaceCodeGenerator:
    """Generate code using Hugging Face models."""
    
    def __init__(self, model_name: str = "bigcode/starcoder"):
        """Initialize with the model name."""
        api_key = os.environ.get("HF_API_KEY")
        if not api_key:
            raise ValueError("Hugging Face API key not found. Please set the HF_API_KEY environment variable.")
        
        self.client = InferenceClient(model=model_name, token=api_key)
        self.model_name = model_name
    
    def generate_test_method(self, method_signature: str, class_name: str) -> str:
        """Generate a test method for the given method signature."""
        prompt = f"""
// Given the following Java method from class {class_name}, 
// write a JUnit 5 test method that tests this method thoroughly.

{method_signature}

// Test method:
@Test
void test{method_signature.split(' ')[1].split('(')[0]}() {{
"""
        
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=300,
                temperature=0.2,
                top_p=0.95,
                repetition_penalty=1.03
            )
            
            # Clean up the response
            test_method = f"@Test\nvoid test{method_signature.split(' ')[1].split('(')[0]}() {{\n{response.split('{', 1)[1]}"
            if not test_method.strip().endswith("}"):
                test_method += "\n}"
                
            return test_method
        
        except Exception as e:
            print(f"Error generating test method: {str(e)}")
            return f"// Error generating test: {str(e)}\n@Test\nvoid test{method_signature.split(' ')[1].split('(')[0]}() {{\n    // TODO: Implement test\n}}"
    
    def generate_complete_test_class(self, class_info: Dict[str, Any]) -> str:
        """Generate a complete test class for the given class information."""
        class_name = class_info['name']
        package_name = class_info.get('package', '')
        
        prompt = f"""
// Generate a complete JUnit 5 test class for the following Java class:
// Class name: {class_name}
// Package: {package_name}

package {package_name};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

class {class_name}Test {{
"""
        
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=500,
                temperature=0.2,
                top_p=0.95,
                repetition_penalty=1.03
            )
            
            # Clean up the response and extract the class content
            test_class = f"package {package_name};\n\nimport org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.BeforeEach;\nimport org.junit.jupiter.api.AfterEach;\nimport static org.junit.jupiter.api.Assertions.*;\n\nclass {class_name}Test {{\n{response.split('{', 1)[1]}"
            
            # Ensure the class is properly closed
            if not test_class.strip().endswith("}"):
                test_class += "\n}"
                
            return test_class
        
        except Exception as e:
            print(f"Error generating test class: {str(e)}")
            return f"""package {package_name};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Error occurred during generation: {str(e)}
 */
class {class_name}Test {{
    
    @BeforeEach
    void setUp() {{
        // TODO: Set up test environment
    }}
    
    @AfterEach
    void tearDown() {{
        // TODO: Clean up test environment
    }}
    
    @Test
    void testExample() {{
        // TODO: Implement tests
        fail("Tests not implemented yet");
    }}
}}"""

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Java code using Hugging Face models")
    parser.add_argument("--model", default="bigcode/starcoder", help="Hugging Face model to use")
    parser.add_argument("--method", help="Java method signature to generate test for")
    parser.add_argument("--class-name", help="Class name for the method")
    parser.add_argument("--output", help="Output file path")
    
    return parser.parse_args()

def main():
    """Main function to generate code."""
    args = parse_args()
    
    # Initialize the code generator
    generator = HuggingFaceCodeGenerator(model_name=args.model)
    
    if args.method and args.class_name:
        # Generate test method
        test_method = generator.generate_test_method(args.method, args.class_name)
        
        # Print or save output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(test_method)
            print(f"Test method saved to {args.output}")
        else:
            print(test_method)
    else:
        # Example usage if no arguments provided
        print("No method signature provided. Here's an example:")
        example_method = "public int add(int a, int b) { return a + b; }"
        example_class = "Calculator"
        test_method = generator.generate_test_method(example_method, example_class)
        print(test_method)

if __name__ == "__main__":
    main()