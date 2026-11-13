import json, time
from pathlib import Path

# Load profile
with open('profiles/shardex_profile.json', encoding='utf-8') as f:
    profile = json.load(f)

# Build application data
app_data = {
    'program': 'NLnet Foundation',
    'program_key': 'nlnet',
    'url': 'https://nlnet.nl/propose/',
    'method': 'web_form',
    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    'profile': profile['project_name'],
    'fields': {}
}

# Fill fields from profile and overrides
overrides = profile['overrides'].get('nlnet', {})
for key, value in profile.items():
    if key not in ['overrides', 'funding_targets'] and value:
        app_data['fields'][key] = value

for key, value in overrides.items():
    if value:
        app_data['fields'][key] = value

# Save
output_dir = Path('evidence') / f'nlnet_application_{int(time.time())}'
output_dir.mkdir(parents=True, exist_ok=True)

json_path = output_dir / 'application_nlnet.json'
json_path.write_text(json.dumps(app_data, indent=2))

md_path = output_dir / 'application_nlnet.md'
md_lines = [
    '# NLnet Foundation Application',
    '',
    f'**Program:** NLnet Foundation',
    f'**URL:** https://nlnet.nl/propose/',
    f'**Method:** web_form',
    f'**Generated:** {app_data["generated_at"]}',
    f'**Profile:** {app_data["profile"]}',
    '',
    '## Filled Fields',
    '',
]
for field_key, value in app_data['fields'].items():
    md_lines.append(f'### {field_key}')
    md_lines.append('')
    md_lines.append('```')
    md_lines.append(str(value))
    md_lines.append('```')
    md_lines.append('')

md_path.write_text('\n'.join(md_lines))

print(f'Application document generated:')
print(f'  JSON: {json_path}')
print(f'  Markdown: {md_path}')
print(f'  Directory: {output_dir}')