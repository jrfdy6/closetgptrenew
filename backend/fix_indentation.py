#!/usr/bin/env python3

def fix_outfit_service_indentation():
    """Fix indentation issues in outfit_service.py"""
    
    with open('src/services/outfit_service.py', 'r') as f:
        lines = f.readlines()
    
    # Fix specific problematic lines
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix line 4231: if item.occasion: should be properly indented
        if line_num == 4231 and line.strip().startswith('if item.occasion:'):
            line = '            ' + line.strip() + '\n'
        
        # Fix line 4233: has_formal_appropriate_occasion = True should be indented
        elif line_num == 4233 and 'has_formal_appropriate_occasion = True' in line:
            line = '                        ' + line.strip() + '\n'
        
        # Fix line 4234: break should be indented
        elif line_num == 4234 and line.strip() == 'break':
            line = '                        break\n'
        
        # Fix line 4236: if item.style: should be properly indented
        elif line_num == 4236 and line.strip().startswith('if item.style:'):
            line = '            ' + line.strip() + '\n'
        
        # Fix line 4238: has_formal_appropriate_style = True should be indented
        elif line_num == 4238 and 'has_formal_appropriate_style = True' in line:
            line = '                    ' + line.strip() + '\n'
        
        # Fix line 4241: if hasattr(item, 'tags') should be properly indented
        elif line_num == 4241 and line.strip().startswith('if hasattr(item, \'tags\')'):
            line = '            ' + line.strip() + '\n'
        
        # Fix line 4243: has_formal_appropriate_tags = True should be indented
        elif line_num == 4243 and 'has_formal_appropriate_tags = True' in line:
            line = '                    ' + line.strip() + '\n'
        
        # Fix line 4248: has_formal_appropriate_tags = True should be indented
        elif line_num == 4248 and 'has_formal_appropriate_tags = True' in line:
            line = '                        ' + line.strip() + '\n'
        
        # Fix line 4252: if statement should be properly indented
        elif line_num == 4252 and line.strip().startswith('if has_formal_appropriate_occasion'):
            line = '            ' + line.strip() + '\n'
        
        # Fix line 4253: formal_appropriate_items.append should be indented
        elif line_num == 4253 and 'formal_appropriate_items.append' in line:
            line = '                ' + line.strip() + '\n'
        
        # Fix line 4256: else should be properly indented
        elif line_num == 4256 and line.strip() == 'else:':
            line = '        ' + line.strip() + '\n'
        
        # Fix line 4257: print statement should be indented
        elif line_num == 4257 and line.strip().startswith('print(f"⚠️'):
            line = '            ' + line.strip() + '\n'
        
        # Fix line 4258: return items should be indented
        elif line_num == 4258 and line.strip() == 'return items':
            line = '            ' + line.strip() + '\n'
        
        fixed_lines.append(line)
    
    # Write the fixed content back
    with open('src/services/outfit_service.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed indentation issues in outfit_service.py")

if __name__ == "__main__":
    fix_outfit_service_indentation() 