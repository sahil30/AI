import javalang
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JavaProcessor:
    def __init__(self):
        pass

    def analyze_java_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Java file and return structured information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.analyze_java_code(content, file_path)
        except Exception as e:
            raise Exception(f"Failed to analyze Java file {file_path}: {str(e)}")

    def analyze_java_code(self, code: str, file_name: str = "unknown") -> Dict[str, Any]:
        """Analyze Java code and extract structural information."""
        try:
            tree = javalang.parse.parse(code)
            
            analysis = {
                'file_name': file_name,
                'package_name': self._extract_package_name(tree),
                'imports': self._extract_imports(tree),
                'classes': self._extract_classes(tree),
                'interfaces': self._extract_interfaces(tree),
                'methods': self._extract_methods(tree),
                'fields': self._extract_fields(tree),
                'annotations': self._extract_annotations(tree),
                'complexity': self._calculate_complexity(tree),
                'lines_of_code': len(code.split('\n')),
                'ast': str(tree)  # Convert AST to string for JSON serialization
            }
            
            return analysis
        except Exception as e:
            raise Exception(f"Failed to parse Java code: {str(e)}")

    def _extract_package_name(self, tree: javalang.tree.CompilationUnit) -> Optional[str]:
        """Extract package name from AST."""
        return tree.package.name if tree.package else None

    def _extract_imports(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract imports from AST."""
        imports = []
        for imp in tree.imports:
            imports.append({
                'name': imp.path,
                'static': imp.static,
                'wildcard': imp.wildcard
            })
        return imports

    def _extract_classes(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract classes from AST."""
        classes = []
        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                class_info = {
                    'name': type_decl.name,
                    'modifiers': type_decl.modifiers if type_decl.modifiers else [],
                    'extends': type_decl.extends.name if type_decl.extends else None,
                    'implements': [impl.name for impl in type_decl.implements] if type_decl.implements else [],
                    'methods': self._extract_methods_from_class(type_decl),
                    'fields': self._extract_fields_from_class(type_decl),
                    'annotations': [ann.name for ann in type_decl.annotations] if type_decl.annotations else [],
                    'is_abstract': 'abstract' in (type_decl.modifiers or []),
                    'is_final': 'final' in (type_decl.modifiers or []),
                    'visibility': self._get_visibility(type_decl.modifiers)
                }
                classes.append(class_info)
        return classes

    def _extract_interfaces(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract interfaces from AST."""
        interfaces = []
        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.InterfaceDeclaration):
                interface_info = {
                    'name': type_decl.name,
                    'modifiers': type_decl.modifiers if type_decl.modifiers else [],
                    'extends': [ext.name for ext in type_decl.extends] if type_decl.extends else [],
                    'methods': self._extract_methods_from_interface(type_decl),
                    'constants': self._extract_fields_from_class(type_decl),
                    'annotations': [ann.name for ann in type_decl.annotations] if type_decl.annotations else [],
                    'visibility': self._get_visibility(type_decl.modifiers)
                }
                interfaces.append(interface_info)
        return interfaces

    def _extract_methods(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract all methods from AST."""
        methods = []
        for type_decl in tree.types:
            if hasattr(type_decl, 'body'):
                for member in type_decl.body:
                    if isinstance(member, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
                        methods.append(self._parse_method(member))
        return methods

    def _extract_methods_from_class(self, class_node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Extract methods from a class node."""
        methods = []
        for member in class_node.body:
            if isinstance(member, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
                methods.append(self._parse_method(member))
        return methods

    def _extract_methods_from_interface(self, interface_node: javalang.tree.InterfaceDeclaration) -> List[Dict[str, Any]]:
        """Extract methods from an interface node."""
        methods = []
        for member in interface_node.body:
            if isinstance(member, javalang.tree.MethodDeclaration):
                methods.append(self._parse_method(member))
        return methods

    def _parse_method(self, method_node) -> Dict[str, Any]:
        """Parse a method node and extract information."""
        is_constructor = isinstance(method_node, javalang.tree.ConstructorDeclaration)
        
        method_info = {
            'name': method_node.name,
            'return_type': method_node.return_type.name if hasattr(method_node, 'return_type') and method_node.return_type else 'void',
            'parameters': self._extract_parameters(method_node.parameters) if method_node.parameters else [],
            'modifiers': method_node.modifiers if method_node.modifiers else [],
            'annotations': [ann.name for ann in method_node.annotations] if method_node.annotations else [],
            'is_constructor': is_constructor,
            'is_abstract': 'abstract' in (method_node.modifiers or []),
            'is_static': 'static' in (method_node.modifiers or []),
            'is_final': 'final' in (method_node.modifiers or []),
            'visibility': self._get_visibility(method_node.modifiers),
            'complexity': self._calculate_method_complexity(method_node)
        }
        
        return method_info

    def _extract_parameters(self, parameters) -> List[Dict[str, Any]]:
        """Extract method parameters."""
        params = []
        for param in parameters:
            params.append({
                'name': param.name,
                'type': param.type.name if hasattr(param.type, 'name') else str(param.type)
            })
        return params

    def _extract_fields(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract all fields from AST."""
        fields = []
        for type_decl in tree.types:
            if hasattr(type_decl, 'body'):
                fields.extend(self._extract_fields_from_class(type_decl))
        return fields

    def _extract_fields_from_class(self, class_node) -> List[Dict[str, Any]]:
        """Extract fields from a class or interface node."""
        fields = []
        for member in class_node.body:
            if isinstance(member, javalang.tree.FieldDeclaration):
                for declarator in member.declarators:
                    field_info = {
                        'name': declarator.name,
                        'type': member.type.name if hasattr(member.type, 'name') else str(member.type),
                        'modifiers': member.modifiers if member.modifiers else [],
                        'annotations': [ann.name for ann in member.annotations] if member.annotations else [],
                        'is_static': 'static' in (member.modifiers or []),
                        'is_final': 'final' in (member.modifiers or []),
                        'visibility': self._get_visibility(member.modifiers),
                        'initializer': 'present' if declarator.initializer else None
                    }
                    fields.append(field_info)
        return fields

    def _extract_annotations(self, tree: javalang.tree.CompilationUnit) -> List[Dict[str, Any]]:
        """Extract all annotations from AST."""
        annotations = []
        for type_decl in tree.types:
            if type_decl.annotations:
                for ann in type_decl.annotations:
                    annotations.append({
                        'name': ann.name,
                        'values': []  # Simplified - could extract annotation values
                    })
        return annotations

    def _get_visibility(self, modifiers: Optional[List[str]]) -> str:
        """Determine visibility from modifiers."""
        if not modifiers:
            return 'package-private'
        if 'public' in modifiers:
            return 'public'
        if 'protected' in modifiers:
            return 'protected'
        if 'private' in modifiers:
            return 'private'
        return 'package-private'

    def _calculate_complexity(self, tree: javalang.tree.CompilationUnit) -> int:
        """Calculate cyclomatic complexity of the entire compilation unit."""
        complexity = 1  # Base complexity
        
        def count_complexity(node):
            nonlocal complexity
            if isinstance(node, (
                javalang.tree.IfStatement,
                javalang.tree.WhileStatement,
                javalang.tree.ForStatement,
                javalang.tree.DoStatement,
                javalang.tree.SwitchStatement,
                javalang.tree.ConditionalExpression
            )):
                complexity += 1
            elif isinstance(node, javalang.tree.CatchClause):
                complexity += 1
            
            # Recursively check child nodes
            for child in node.children:
                if hasattr(child, 'children'):
                    count_complexity(child)
                elif isinstance(child, list):
                    for item in child:
                        if hasattr(item, 'children'):
                            count_complexity(item)
        
        count_complexity(tree)
        return complexity

    def _calculate_method_complexity(self, method_node) -> int:
        """Calculate cyclomatic complexity for a specific method."""
        complexity = 1  # Base complexity
        
        def count_complexity(node):
            nonlocal complexity
            if isinstance(node, (
                javalang.tree.IfStatement,
                javalang.tree.WhileStatement,
                javalang.tree.ForStatement,
                javalang.tree.DoStatement,
                javalang.tree.SwitchStatement,
                javalang.tree.ConditionalExpression
            )):
                complexity += 1
            elif isinstance(node, javalang.tree.CatchClause):
                complexity += 1
            
            # Recursively check child nodes
            for child in node.children:
                if hasattr(child, 'children'):
                    count_complexity(child)
                elif isinstance(child, list):
                    for item in child:
                        if hasattr(item, 'children'):
                            count_complexity(item)
        
        if method_node.body:
            count_complexity(method_node)
        return complexity

    def generate_java_class(self, class_name: str, options: Dict[str, Any] = None) -> str:
        """Generate Java class code."""
        if options is None:
            options = {}
        
        package_name = options.get('package_name')
        imports = options.get('imports', [])
        super_class = options.get('super_class')
        interfaces = options.get('interfaces', [])
        fields = options.get('fields', [])
        methods = options.get('methods', [])
        annotations = options.get('annotations', [])
        modifiers = options.get('modifiers', ['public'])
        
        code = []
        
        # Package declaration
        if package_name:
            code.append(f"package {package_name};")
            code.append("")
        
        # Imports
        if imports:
            for imp in imports:
                code.append(f"import {imp};")
            code.append("")
        
        # Class annotations
        for annotation in annotations:
            code.append(f"@{annotation}")
        
        # Class declaration
        class_decl = f"{' '.join(modifiers)} class {class_name}"
        if super_class:
            class_decl += f" extends {super_class}"
        if interfaces:
            class_decl += f" implements {', '.join(interfaces)}"
        class_decl += " {"
        code.append(class_decl)
        code.append("")
        
        # Fields
        for field in fields:
            field_modifiers = field.get('modifiers', ['private'])
            field_type = field.get('type', 'String')
            field_name = field.get('name', 'field')
            initializer = field.get('initializer', '')
            
            field_line = f"    {' '.join(field_modifiers)} {field_type} {field_name}"
            if initializer:
                field_line += f" = {initializer}"
            field_line += ";"
            code.append(field_line)
        
        if fields:
            code.append("")
        
        # Methods
        for method in methods:
            method_annotations = method.get('annotations', [])
            for ann in method_annotations:
                code.append(f"    @{ann}")
            
            method_modifiers = method.get('modifiers', ['public'])
            return_type = method.get('return_type', 'void')
            method_name = method.get('name', 'method')
            parameters = method.get('parameters', [])
            body = method.get('body', '        // TODO: Implement method')
            
            param_str = ', '.join([f"{p.get('type', 'String')} {p.get('name', 'param')}" for p in parameters])
            method_line = f"    {' '.join(method_modifiers)} {return_type} {method_name}({param_str}) {{"
            code.append(method_line)
            code.append(body)
            code.append("    }")
            code.append("")
        
        code.append("}")
        
        return '\n'.join(code)

    def write_java_file(self, file_path: str, content: str) -> bool:
        """Write Java code to a file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Failed to write Java file {file_path}: {str(e)}")

    def find_java_files(self, directory: str) -> List[str]:
        """Find all Java files in a directory recursively."""
        try:
            java_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.java'):
                        java_files.append(os.path.join(root, file))
            return java_files
        except Exception as e:
            raise Exception(f"Failed to find Java files in {directory}: {str(e)}")