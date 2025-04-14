import re

class Object:
    def __init__(self, class_name, attributes=None, methods=None):
        self.class_name = class_name
        self.attributes = attributes if attributes else {}
        self.methods = methods if methods else {}

class TagLangInterpreter:
    def __init__(self, debug=False):
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.objects = {}
        self.current_object = None
        self.debug = debug
    
    def log(self, message):
        if self.debug:
            print(f"DEBUG: {message}")
    
    def get_variable_value(self, var_name, local_vars=None):
        """Get the value of a variable from the current scope"""
        self.log(f"Looking up variable: {var_name}")
        
        # Check if this is an object property reference
        if var_name.startswith("this.") and self.current_object:
            attr_name = var_name[5:]  # Remove "this."
            if attr_name in self.current_object.attributes:
                return self.current_object.attributes[attr_name]

        # Check local variables first
        if local_vars and var_name in local_vars:
            self.log(f"Found in local vars: {var_name} = {local_vars[var_name]}")
            return local_vars[var_name]
            
        # Check global variables
        if var_name in self.variables:
            self.log(f"Found in global vars: {var_name} = {self.variables[var_name]}")
            return self.variables[var_name]
            
        # Check object attributes
        if self.current_object and var_name in self.current_object.attributes:
            self.log(f"Found in object attributes: {var_name} = {self.current_object.attributes[var_name]}")
            return self.current_object.attributes[var_name]
            
        self.log(f"Variable not found: {var_name}")
        return None
    
    def evaluate_expression(self, expr, local_vars=None):
        """Evaluate an expression with variable substitution"""
        if expr is None:
            return None
            
        self.log(f"Evaluating expression: {expr}")
        
        # If expr is not a string, return it as is
        if not isinstance(expr, str):
            return expr
            
        # If the expression is just a variable name, return its value
        var_value = self.get_variable_value(expr.strip(), local_vars)
        if var_value is not None:
            self.log(f"Expression is a variable reference: {expr} = {var_value}")
            return var_value
        
        try:
            # Replace variable references in the expression
            modified_expr = expr
            
            # Handle object property references
            if self.current_object:
                for attr_name, attr_value in self.current_object.attributes.items():
                    this_ref = f"this.{attr_name}"
                    if this_ref in modified_expr:
                        replacement = repr(attr_value) if isinstance(attr_value, str) else str(attr_value)
                        modified_expr = modified_expr.replace(this_ref, replacement)
            
            # Create a dictionary of variables for substitution
            vars_to_check = {}
            if local_vars:
                vars_to_check.update(local_vars)
            vars_to_check.update(self.variables)
            
            # Sort variables by length (longest first) to avoid partial replacements
            sorted_vars = sorted(vars_to_check.keys(), key=len, reverse=True)
            
            for var_name in sorted_vars:
                if var_name in modified_expr:
                    var_value = vars_to_check[var_name]
                    replacement = repr(var_value) if isinstance(var_value, str) else str(var_value)
                    # Use regex to ensure we're replacing whole words only
                    modified_expr = re.sub(r'\b' + re.escape(var_name) + r'\b', replacement, modified_expr)
            
            self.log(f"Modified expression: {modified_expr}")
            return eval(modified_expr)
        except Exception as e:
            self.log(f"Evaluation error: {e}")
            return expr
    
    def execute_node(self, node, local_vars=None):
        """Execute a node in the AST"""
        if local_vars is None:
            local_vars = {}
            
        node_type = node["type"]
        self.log(f"Executing node type: {node_type}")
        
        if node_type == "var":
            # Check if this is a self-closing var tag for printing
            if "self_closing" in node["attributes"] and node["attributes"]["self_closing"] == "true":
                var_name = node["attributes"]["name"]
                var_value = self.get_variable_value(var_name, local_vars)
                if var_value is not None:
                    print(var_value, end='')
                return
            
            # This is a variable assignment
            var_name = node["attributes"]["name"]
            var_value = self.evaluate_expression(node["text"], local_vars)
            
            self.log(f"Assigning {var_name} = {var_value}")
            
            if self.current_object:
                self.current_object.attributes[var_name] = var_value
            else:
                self.variables[var_name] = var_value
            
        elif node_type == "print":
            # Get the text content
            content = node["text"]
            
            # Process children nodes (like var tags) within the print
            for child in node["children"]:
                self.execute_node(child, local_vars)
            
            # If there were no children or after processing them, print the content
            if not node["children"] and content:
                # Check if it's a variable reference
                if content in self.variables:
                    print(self.variables[content])
                elif content in local_vars:
                    print(local_vars[content])
                else:
                    print(content)
            
            # If we didn't already end with a newline, add one
            if node["children"]:
                print()
                
        elif node_type == "input":
            var_name = node["attributes"]["name"]
            prompt = node["text"] if node["text"] else ""
            value = input(prompt)
            
            # Try to convert to int or float if possible
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
                
            self.variables[var_name] = value
            
        elif node_type == "if":
            condition = self.evaluate_expression(node["attributes"]["condition"], local_vars)
            
            if condition:
                for child in node["children"]:
                    if child["type"] != "else":
                        self.execute_node(child, local_vars)
            else:
                for child in node["children"]:
                    if child["type"] == "else":
                        for else_child in child["children"]:
                            self.execute_node(else_child, local_vars)
                    
        elif node_type == "while":
            while self.evaluate_expression(node["attributes"]["condition"], local_vars):
                for child in node["children"]:
                    self.execute_node(child, local_vars)
                    
        elif node_type == "for":
            var_name = node["attributes"]["var"]
            from_val = int(self.evaluate_expression(node["attributes"]["from"], local_vars))
            to_val = int(self.evaluate_expression(node["attributes"]["to"], local_vars))
            step_val = int(self.evaluate_expression(node["attributes"]["step"], local_vars)) if "step" in node["attributes"] else 1
            
            for i in range(from_val, to_val, step_val):
                loop_vars = local_vars.copy()
                loop_vars[var_name] = i
                
                for child in node["children"]:
                    self.execute_node(child, loop_vars)
                    
        elif node_type == "function":
            func_name = node["attributes"]["name"]
            self.functions[func_name] = {
                "params": [p.strip() for p in node["attributes"].get("params", "").split(",")] if node["attributes"].get("params") else [],
                "body": node["children"]
            }
            
        elif node_type == "call":
            func_name = node["attributes"]["name"]
            if func_name in self.functions:
                # Prepare arguments
                args = []
                if "args" in node["attributes"]:
                    args_str = node["attributes"]["args"]
                    args = [arg.strip() for arg in args_str.split(",")]
                
                # Create local scope for function
                func_vars = {}
                func_params = self.functions[func_name]["params"]
                
                # Assign arguments to parameters
                for i, param in enumerate(func_params):
                    if i < len(args):
                        param = param.strip()
                        if not param:
                            continue
                        arg_value = self.evaluate_expression(args[i], local_vars)
                        func_vars[param] = arg_value
                
                # Execute function body
                for child in self.functions[func_name]["body"]:
                    self.execute_node(child, func_vars)
                    
        elif node_type == "class":
            class_name = node["attributes"]["name"]
            
            # Separate methods and attributes
            methods = {}
            attributes = {}
            
            for child in node["children"]:
                if child["type"] == "method":
                    method_name = child["attributes"]["name"]
                    methods[method_name] = child["children"]
                elif child["type"] == "var":
                    var_name = child["attributes"]["name"]
                    var_value = self.evaluate_expression(child["text"])
                    attributes[var_name] = var_value
            
            self.classes[class_name] = {
                "methods": methods,
                "attributes": attributes
            }
            
        elif node_type == "new":
            class_name = node["attributes"]["class"]
            object_name = node["attributes"]["name"]
            
            if class_name in self.classes:
                # Create a new instance of the class
                obj = Object(class_name, 
                             attributes=self.classes[class_name]["attributes"].copy(),
                             methods=self.classes[class_name]["methods"])
                
                # Set the current object for initialization
                prev_obj = self.current_object
                self.current_object = obj
                
                # Initialize with constructor parameters if any
                for child in node["children"]:
                    self.execute_node(child)
                    
                # Reset current object
                self.current_object = prev_obj
                
                # Store the new object
                self.objects[object_name] = obj
                
        elif node_type == "callmethod":
            object_name = node["attributes"]["object"]
            method_name = node["attributes"]["method"]
            
            if object_name in self.objects:
                obj = self.objects[object_name]
                
                if method_name in obj.methods:
                    prev_obj = self.current_object
                    self.current_object = obj
                    
                    for child in obj.methods[method_name]:
                        self.execute_node(child)
                        
                    self.current_object = prev_obj
    
    def run(self, ast):
        """Run the TagLang program"""
        for node in ast:
            self.execute_node(node)