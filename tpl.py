from parser import TagLangParser
from interpreter import TagLangInterpreter
import sys
import re

def preprocess_code(code):
    """
    Preprocess the TagLang code to handle XML syntax
    """
    # Handle self-closing tags
    code = re.sub(r'<var\s+name="([^"]+)"\s*\/>', r'<var name="\1" self_closing="true"></var>', code)
    
    # Fix problematic XML characters in text content
    code = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', r'&amp;', code)
    
    return code

def run_taglang_file(filename, debug=False):
    """
    Load and run a TagLang program from a file
    """
    try:
        with open(filename, 'r') as file:
            code = file.read()
        
        # Preprocess the code
        code = preprocess_code(code)
        
        parser = TagLangParser()
        interpreter = TagLangInterpreter(debug=debug)
        
        ast = parser.parse(code)
        interpreter.run(ast)
        
    except Exception as e:
        print(f"Error running TagLang program: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        debug = "--debug" in sys.argv
        
        if not filename.endswith('.tpl'):
            print("Error: File must have .tpl extension")
        else:
            run_taglang_file(filename, debug)
    else:
        print("Usage: python tpl.py <filename.tpl> [--debug]")