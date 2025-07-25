#!/usr/bin/env python3

def fix_all_indentation():
    """Fix all indentation issues in outfit_service.py"""
    
    with open('src/services/outfit_service.py', 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        original_line = line
        
        # Fix all the common patterns of indentation errors
        
        # Pattern 1: if statements that are over-indented
        if (line.strip().startswith('if ') and 
            ('item.occasion:' in line or 'item.style:' in line or 'hasattr(item, \'tags\')' in line) and
            line.startswith('                ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 2: variable assignments that are under-indented
        elif (('has_formal_appropriate_occasion = True' in line or 
               'has_formal_appropriate_style = True' in line or 
               'has_formal_appropriate_tags = True' in line or
               'has_athletic_appropriate_occasion = True' in line or
               'has_athletic_appropriate_style = True' in line or
               'has_athletic_appropriate_tags = True' in line or
               'has_school_appropriate_occasion = True' in line or
               'has_school_appropriate_style = True' in line or
               'has_school_appropriate_tags = True' in line or
               'has_holiday_appropriate_occasion = True' in line or
               'has_holiday_appropriate_style = True' in line or
               'has_holiday_appropriate_tags = True' in line or
               'has_concert_appropriate_occasion = True' in line or
               'has_concert_appropriate_style = True' in line or
               'has_concert_appropriate_tags = True' in line or
               'has_errands_appropriate_occasion = True' in line or
               'has_errands_appropriate_style = True' in line or
               'has_errands_appropriate_tags = True' in line) and
              not line.startswith('                        ')):
            line = '                        ' + line.strip() + '\n'
        
        # Pattern 3: break statements that are under-indented
        elif line.strip() == 'break' and not line.startswith('                        '):
            line = '                        break\n'
        
        # Pattern 4: if statements for checking attributes that are over-indented
        elif (line.strip().startswith('if any(keyword in') and 
              line.startswith('                ')):
            line = '                    ' + line.strip() + '\n'
        
        # Pattern 5: else statements that are under-indented
        elif line.strip() == 'else:' and line.startswith('            '):
            line = '        ' + line.strip() + '\n'
        
        # Pattern 6: print statements that are under-indented
        elif (line.strip().startswith('print(f"⚠️') and 
              line.startswith('            ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 7: return statements that are under-indented
        elif (line.strip() == 'return items' and 
              line.startswith('            ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 8: append statements that are under-indented
        elif (('_appropriate_items.append' in line) and 
              not line.startswith('                ')):
            line = '                ' + line.strip() + '\n'
        
        # Pattern 9: if statements for checking multiple conditions that are under-indented
        elif (line.strip().startswith('if has_') and 
              'or has_' in line and 
              line.startswith('            ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 10: else statements in the main logic that are over-indented
        elif (line.strip() == 'else:' and 
              line.startswith('                ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 11: print statements for debug that are under-indented
        elif (line.strip().startswith('print(f"❌ DEBUG:') and 
              line.startswith('            ')):
            line = '                ' + line.strip() + '\n'
        
        # Pattern 12: return statements in the main logic that are under-indented
        elif (line.strip().startswith('return ') and 
              line.startswith('            ') and
              not line.startswith('                ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 13: if statements for checking if items exist that are under-indented
        elif (line.strip().startswith('if ') and 
              '_appropriate_items:' in line and
              line.startswith('        ')):
            line = '        ' + line.strip() + '\n'
        
        # Pattern 14: print statements for found items that are under-indented
        elif (line.strip().startswith('print(f"✅ DEBUG:') and 
              'Found' in line and
              line.startswith('            ')):
            line = '            ' + line.strip() + '\n'
        
        # Pattern 15: return statements for found items that are under-indented
        elif (line.strip().startswith('return ') and 
              '_appropriate_items' in line and
              line.startswith('            ')):
            line = '            ' + line.strip() + '\n'
        
        fixed_lines.append(line)
    
    # Write the fixed content back
    with open('src/services/outfit_service.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed all indentation issues in outfit_service.py")

if __name__ == "__main__":
    fix_all_indentation() 