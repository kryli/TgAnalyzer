import re

def escape_md_v2(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!$])', r'\\\1', text)

def format_report_md(text: str) -> str:
    lines = text.split('\n')
    formatted_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^\d+\.', stripped):  # Numbered heading
            line_esc = escape_md_v2(stripped)
            formatted_lines.append(f'*📝 {line_esc}*')
            # Add a blank line after the heading for better spacing
            formatted_lines.append('')
        elif stripped.startswith('- '):  # Sub-item
            line_esc = escape_md_v2(stripped)
            formatted_lines.append(f'    📌 {line_esc}')
        elif stripped == '':
            formatted_lines.append('')
        else:
            line_esc = escape_md_v2(stripped)
            formatted_lines.append(line_esc)

    return '\n'.join(formatted_lines)
