# Read current file
with open('app/models/subject_property.py', 'r') as f:
    content = f.read()

# Find and replace user_notes line
old_line = '    user_notes: str'
new_line = '    user_notes: str = ""'

if old_line in content:
    content = content.replace(old_line, new_line)
    
    # Write back
    with open('app/models/subject_property.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed: user_notes is now optional with default empty string")
else:
    print("⚠️ Could not find line to update")
    print("Manual update needed")
