#!/usr/bin/env python3
"""
generate_tests.py - Generate JUnit tests for Java classes using LangChain and GPT-4.

This script scans a Java project, analyzes the source code, and generates
comprehensive JUnit tests for each class.
"""

import os
import sys
import argparse
import re
import glob
import javalang
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

class JavaCodeAnalyzer:
    """Analyzes Java source code to extract class information."""
    
    def __init__(self, file_path: str):
        """Initialize with the path to a Java file."""
        self.file_path = file_path
        self.code = self._read_file()
        
    def _read_file(self) -> str:
        """Read the content of the Java file."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_code(self) -> Dict[str, Any]:
        """Parse Java code to extract class, methods, and imports information."""
        try:
            tree = javalang.parse.parse(self.code)
            
            # Extract package name
            package_name = tree.package.name if tree.package else "unknown"
            
            # Extract imports
            imports = [imp.path for imp in tree.imports]
            
            # Extract class info
            class_info = None
            for _, class_decl in tree.filter(javalang.tree.ClassDeclaration):
                class_info = {
                    'name': class_decl.name,
                    'methods': [],
                    'fields': [],
                    'has_constructor': any(m.name == class_decl.name for m in class_decl.methods)
                }
                
                # Extract fields
                for field_decl in class_decl.fields:
                    for field in field_decl.declarators:
                        modifiers = [str(m) for m in field_decl.modifiers]
                        class_info['fields'].append({
                            'name': field.name,
                            'type': field_decl.type.name,
                            'modifiers': modifiers
                        })
                
                # Extract methods
                for method in class_decl.methods:
                    params = []
                    for param in method.parameters:
                        param_type = param.type.name
                        # Handle array types
                        if hasattr(param.type, 'dimensions') and param.type.dimensions:
                            for _ in range(len(param.type.dimensions)):
                                param_type += "[]"
                        params.append({
                            'name': param.name,
                            'type': param_type
                        })
                    
                    modifiers = [str(m) for m in method.modifiers]
                    return_type = 'void'
                    if method.return_type:
                        return_type = method.return_type.name
                        # Handle array return types
                        if hasattr(method.return_type, 'dimensions') and method.return_type.dimensions:
                            for _ in range(len(method.return_type.dimensions)):
                                return_type += "[]"
                    
                    class_info['methods'].append({
                        'name': method.name,
                        'return_type': return_type,
                        'parameters': params,
                        'modifiers': modifiers,
                        'throws': [ex.name for ex in method.throws] if method.throws else []
                    })
            
            return {
                'package': package_name,
                'imports': imports,
                'class': class_info,
                'file_path': self.file_path,
                'source_code': self.code
            }
            
        except Exception as e:
            print(f"Error parsing {self.file_path}: {str(e)}")
            return {
                'package': 'unknown',
                'imports': [],
                'class': None,
                'file_path': self.file_path,
                'source_code': self.code,
                'error': str(e)
            }

class TestGenerator:
    """Generates JUnit tests for Java classes using GPT."""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.2):
        """Initialize with GPT model parameters."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
    
    def generate_test(self, java_class_info: Dict[str, Any]) -> str:
        """Generate a JUnit test class for the given Java class."""
        if java_class_info.get('error') or not java_class_info.get('class'):
            return f"// Could not generate tests due to parsing error: {java_class_info.get('error', 'Unknown error')}"
        
        # Create test generation prompt
        prompt = self._create_prompt(java_class_info)
        
        # Set up LLMChain
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(prompt)
        )
        
        # Generate test
        try:
            response = llm_chain.invoke({})
            return response['text']
        except Exception as e:
            print(f"Error generating test: {str(e)}")
            return f"// Error generating test: {str(e)}"
    
    def _create_prompt(self, java_class_info: Dict[str, Any]) -> str:
        """Create a prompt for the LLM to generate tests."""
        class_info = java_class_info['class']
        methods_info = "\n".join([
            f"- Method: {method['name']}\n  Return Type: {method['return_type']}\n  Parameters: {', '.join([f'{p['type']} {p['name']}' for p in method['parameters']])}\n  Modifiers: {', '.join(method['modifiers'])}"
            for method in class_info['methods']
        ])
        
        fields_info = "\n".join([
            f"- Field: {field['name']}\n  Type: {field['type']}\n  Modifiers: {', '.join(field['modifiers'])}"
            for field in class_info['fields']
        ])
        
        prompt = f"""
You are a Java expert specialized in writing high-quality JUnit 5 tests.
Your task is to create comprehensive unit tests for the following Java class.

Java Class Information:
- Package: {java_class_info['package']}
- Class Name: {class_info['name']}

Fields:
{fields_info}

Methods:
{methods_info}

Source Code:
```java
{java_class_info['source_code']}
```

Requirements for the JUnit tests:
1. Create a complete, compilable JUnit 5 test class named "{class_info['name']}Test"
2. Include the proper package statement and imports
3. Use @Test, @BeforeEach, and @AfterEach annotations appropriately
4. Test all public methods thoroughly, including edge cases
5. Use appropriate assertions from org.junit.jupiter.api.Assertions
6. For each test method, provide a brief comment explaining what it tests
7. Use Mockito for mocking dependencies when needed
8. Handle exceptions appropriately if methods throw exceptions
9. Aim for high code coverage
10. The tests should be well-structured and follow best practices

Your response should only contain the complete Java test class code, starting with the package statement.
"""
        return prompt

def find_java_files(src_dir: str) -> List[str]:
    """Find all Java files in the given directory recursively."""
    return glob.glob(os.path.join(src_dir, "**", "*.java"), recursive=True)

def generate_test_file_path(java_file_path: str, src_dir: str, test_dir: str) -> str:
    """Generate the path for the test file based on the source file path."""
    rel_path = os.path.relpath(java_file_path, src_dir)
    test_file_path = os.path.join(test_dir, rel_path)
    
    # Replace .java with Test.java
    base, _ = os.path.splitext(test_file_path)
    test_file_path = f"{base}Test.java"
    
    return test_file_path

def save_test_file(content: str, file_path: str) -> None:
    """Save the generated test content to a file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Test file saved: {file_path}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate JUnit tests for Java classes using GPT")
    parser.add_argument("--src", required=True, help="Source directory containing Java files")
    parser.add_argument("--test", required=True, help="Output directory for test files")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--file", help="Process a specific Java file only (relative to src)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip generating tests for files that already have tests")
    
    return parser.parse_args()

def main():
    """Main function to generate tests."""
    args = parse_args()
    
    src_dir = args.src
    test_dir = args.test
    
    # Initialize the test generator
    test_generator = TestGenerator(model=args.model)
    
    # Find all Java files or use the specified file
    if args.file:
        java_files = [os.path.join(src_dir, args.file)]
    else:
        java_files = find_java_files(src_dir)
    
    print(f"Found {len(java_files)} Java files to process")
    
    for java_file in java_files:
        # Skip test files
        if "Test.java" in java_file:
            continue
        
        # Skip files that don't match typical class patterns (e.g., skip package-info.java)
        if not re.search(r'[A-Z][a-zA-Z0-9]*\.java$', os.path.basename(java_file)):
            continue
        
        print(f"\nProcessing: {java_file}")
        
        # Generate the test file path
        test_file_path = generate_test_file_path(java_file, src_dir, test_dir)
        
        # Skip if test file already exists and --skip-existing is set
        if args.skip_existing and os.path.exists(test_file_path):
            print(f"Test already exists, skipping: {test_file_path}")
            continue
        
        # Analyze the Java code
        analyzer = JavaCodeAnalyzer(java_file)
        java_class_info = analyzer.parse_code()
        
        # Skip if there's no class information
        if not java_class_info.get('class'):
            print(f"No class found in {java_file}, skipping")
            continue
        
        # Skip non-public classes or interfaces
        if "interface" in java_class_info.get('source_code', "").lower().split(java_class_info['class']['name'])[0]:
            print(f"Skipping interface: {java_class_info['class']['name']}")
            continue
        
        # Generate the test
        print(f"Generating test for: {java_class_info['class']['name']}")
        test_content = test_generator.generate_test(java_class_info)
        
        # Save the test
        save_test_file(test_content, test_file_path)
    
    print("\nTest generation completed!")

if __name__ == "__main__":
    main()