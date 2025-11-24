import subprocess
import json
import os

def run_test(input_file, output_file):
    print(f"\nTesting: {input_file}")
    print("=" * 60)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    print("Input:")
    print(input_text)
    
    process = subprocess.Popen(
        ['python', 'config_parser.py', output_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    stdout, stderr = process.communicate(input=input_text)
    
    if stderr:
        print(f"Errors: {stderr}")
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        print("\nOutput JSON:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("=" * 60)

def main():
    tests = [
        ('test1_server_config.txt', 'output1.json'),
        ('test2_student_data.txt', 'output2.json'),
    ]
    
    for input_file, output_file in tests:
        run_test(input_file, output_file)

if __name__ == '__main__':
    main()
