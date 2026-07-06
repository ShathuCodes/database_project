import os, re
d = 'app/routes'
for f in os.listdir(d):
    if f.endswith('.py'):
        path = os.path.join(d, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace roles_required decorators
        new_content = re.sub(r"@roles_required\([^)]+\)", "@roles_required('Hospital Management')", content)
        
        # Replace UROLES and ROLES
        new_content = re.sub(r"UROLES\s*=\s*\[[^\]]+\]", "UROLES = ['Hospital Management', 'Police Management']", new_content)
        new_content = re.sub(r"ROLES\s*=\s*\[[^\]]+\]", "ROLES = ['Hospital Management', 'Police Management']", new_content)
        
        if content != new_content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'Updated {f}')
