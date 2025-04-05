#!/usr/bin/env python3
"""
hf_code_generation.py - Generate Java test methods using Hugging Face's code models.

This script demonstrates how to use Hugging Face code models
to generate JUnit 5 test methods or full test classes.
"""

import os
import argparse
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient

# Load Hugging Face API key from .env
load_dotenv()

class HuggingFaceCodeGenerator:
    """Generates Java code using Hugging Face code models."""
    
    def __init__(self, model_name: str = "bigcode/starcoder"):
        api_key = os.environ.get("HF_API_KEY")
        if not api_key:
            raise ValueError("Hugging Face API key not found. Set HF_API_KEY in .env")
        
        self.client = InferenceClient(model=model_name, token=api_key)
        self.model_name = model_name

    def generate_test_method(self, method_signature: str, class_name: str) -> str:
        """Generate a JUnit 5 test method from a Java method signature."""
        try:
            method_name = method_signature.strip().split(' ')[1].split('(')[0]
        except IndexError:
            method_name = "UnknownMethod"

        prompt = f"""
// Given the following Java method from class {class_name},
// write a JUnit 5 test method that tests this method thoroughly.

{method_signature}

// Test method:
@Test
void test{method_name.capitalize()}() {{
"""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=300,
                temperature=0.2,
                top_p=0.95,
                repetition_penalty=1.03
            )

            body = response.split("{", 1)[1].rsplit("}", 1)[0].strip()
            return f"""@Test
void test{method_name.capitalize()}() {{
{body}
}}"""

        except Exception as e:
            print(f"Error generating test method: {str(e)}")
            return f"""// Error generating test: {str(e)}
@Test
void test{method_name.capitalize()}() {{
    // TODO: Implement test
}}"""

    def generate_complete_test_class(self, class_info: Dict[str, Any]) -> str:
        """Generate a full JUnit 5 test class."""
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

            body = response.split("{", 1)[1].strip()
            if not body.endswith("}"):
                body += "\n}"

            return f"""package {package_name};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

class {class_name}Test {{
{body}"""

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
