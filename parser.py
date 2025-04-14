import re
import xml.etree.ElementTree as ET
from io import StringIO

class TagLangParser:
    def __init__(self):
        self.ast = []
    
    def parse(self, code):
        # Fix self-closing tags to be compatible with ElementTree
        code = re.sub(r'<var\s+name="([^"]+)"\s*\/>', r'<var name="\1" self_closing="true"></var>', code)
        
        # Fix XML by wrapping in a root element
        xml_code = f"<root>{code}</root>"
        
        try:
            root = ET.fromstring(xml_code)
            self.ast = self._process_element(root)
            return self.ast
        except Exception as e:
            print(f"Error parsing TagLang code: {e}")
            return []
    
    def _process_element(self, element):
        result = []
        
        for child in element:
            node = {
                "type": child.tag,
                "attributes": child.attrib,
                "children": self._process_element(child),
                "text": child.text.strip() if child.text else ""
            }
            result.append(node)
        
        return result