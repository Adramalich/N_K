import sys
import json
import re

class ConfigParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.constants = {}
    
    def parse(self):
        result = {}
        self.skip_whitespace()
        while self.pos < len(self.text):
            if self.peek_pattern(r'[A-Z]+\s*:='):
                name, value = self.parse_constant_declaration()
                self.constants[name] = value
            else:
                break
            self.skip_whitespace()
        
        if self.pos < len(self.text):
            result = self.parse_value()
        
        return result
    
    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1
    
    def peek_pattern(self, pattern):
        match = re.match(pattern, self.text[self.pos:])
        return match is not None
    
    def parse_constant_declaration(self):
        name = self.parse_name()
        self.skip_whitespace()
        self.expect(':=')
        self.skip_whitespace()
        value = self.parse_value()
        self.skip_whitespace()
        return name, value
    
    def parse_name(self):
        self.skip_whitespace()
        match = re.match(r'[A-Z]+', self.text[self.pos:])
        if not match:
            self.error(f"Expected name at position {self.pos}")
        name = match.group(0)
        self.pos += len(name)
        return name
    
    def parse_value(self):
        self.skip_whitespace()
        
        if self.text[self.pos:].startswith('@"'):
            return self.parse_string()
        elif self.text[self.pos:].startswith('array('):
            return self.parse_array()
        elif self.text[self.pos] == '{':
            return self.parse_dict()
        elif self.text[self.pos:].startswith('^['):
            return self.parse_constant_ref()
        elif self.text[self.pos].isdigit():
            return self.parse_number()
        else:
            self.error(f"Unexpected character at position {self.pos}: {self.text[self.pos]}")
    
    def parse_number(self):
        self.skip_whitespace()
        match = re.match(r'\d+', self.text[self.pos:])
        if not match:
            self.error(f"Expected number at position {self.pos}")
        num = int(match.group(0))
        self.pos += len(match.group(0))
        return num
    
    def parse_string(self):
        self.skip_whitespace()
        if not self.text[self.pos:].startswith('@"'):
            self.error(f"Expected string at position {self.pos}")
        self.pos += 2
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1
        if self.pos >= len(self.text):
            self.error("Unterminated string")
        string = self.text[start:self.pos]
        self.pos += 1
        return string
    
    def parse_array(self):
        self.skip_whitespace()
        self.expect('array(')
        self.skip_whitespace()
        
        values = []
        if self.text[self.pos] != ')':
            while True:
                values.append(self.parse_value())
                self.skip_whitespace()
                if self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                else:
                    break
        
        self.expect(')')
        return values
    
    def parse_dict(self):
        self.skip_whitespace()
        self.expect('{')
        self.skip_whitespace()
        
        result = {}
        while self.text[self.pos] != '}':
            name = self.parse_name()
            self.skip_whitespace()
            self.expect(':')
            self.skip_whitespace()
            value = self.parse_value()
            self.skip_whitespace()
            self.expect(';')
            self.skip_whitespace()
            result[name] = value
        
        self.expect('}')
        return result
    
    def parse_constant_ref(self):
        self.skip_whitespace()
        self.expect('^[')
        name = self.parse_name()
        self.expect(']')
        if name not in self.constants:
            self.error(f"Undefined constant: {name}")
        return self.constants[name]
    
    def expect(self, text):
        self.skip_whitespace()
        if not self.text[self.pos:].startswith(text):
            self.error(f"Expected '{text}' at position {self.pos}")
        self.pos += len(text)
    
    def error(self, msg):
        print(f"Syntax error: {msg}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python config_parser.py <output_file>", file=sys.stderr)
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_text = sys.stdin.read()
    
    parser = ConfigParser(input_text)
    result = parser.parse()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
