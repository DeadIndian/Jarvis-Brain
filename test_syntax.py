import ast
import os

def validate_python_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def validate_directory(directory):
    errors = []
    valid_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                is_valid, error = validate_python_file(file_path)
                if is_valid:
                    valid_files.append(file_path)
                else:
                    errors.append(f"{file_path}: {error}")
    
    return valid_files, errors

if __name__ == "__main__":
    valid_files, errors = validate_directory('app')
    
    print(f"Valid Python files: {len(valid_files)}")
    for file in valid_files:
        print(f"  ✓ {file}")
    
    if errors:
        print(f"\nSyntax errors: {len(errors)}")
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print("\nAll files have valid syntax!")
        
    print(f"\nProject structure:")
    for root, dirs, files in os.walk('app'):
        level = root.replace('app', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f"{subindent}{file}")
