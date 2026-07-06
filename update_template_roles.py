import os, re
d = 'app/templates'
for root, dirs, files in os.walk(d):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace list-based role checks
            new_content = re.sub(r"{%\s*if\s+current_user\.role\s+in\s+\[[^\]]+\]\s*%}", "{% if current_user.role == 'Hospital Management' %}", content)
            
            # Replace single Admin role check
            new_content = re.sub(r"{%\s*if\s+current_user\.role\s*==\s*'Admin'\s*%}", "{% if current_user.role == 'Hospital Management' %}", new_content)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Updated {path}')
