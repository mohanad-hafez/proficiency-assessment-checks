"""Render native assessment values and convention-based changed-file inventory."""
import json
from pathlib import Path

def is_context(path):
    name = path.split('/')[-1]
    return name in {'CLAUDE.md','AGENTS.md','.cursorrules','ARCHITECTURE.md','CONVENTIONS.md','PATTERNS.md'} or path == '.github/copilot-instructions.md' or path.startswith(('.claude/skills/','.claude/commands/','.claude/hooks/')) or (path.startswith(('docs/','.github/workflows/')) and path.endswith('.md'))

def cell(value):
    return str(value).replace('|','&#124;').replace('\n',' ').replace('\r',' ').replace('<','&lt;').replace('>','&gt;')

def render(report, changes):
    level = report['overall_level']
    if level not in range(1,9):
        raise ValueError('Invalid native level')
    scores = report['level_scores']
    total = sum(x['file_count'] for x in scores.values())
    recs = [r for r in report['recommendations'] if not r.startswith('🔍 Detected AI tools:')][:3]
    context = [x for x in changes if is_context(x['filename'])]
    lines = ['## AI Proficiency Assessment','', '| Metric | Value |','| --- | --- |',f'| **Overall Level** | Level {level}: {cell(scores[str(level)]["name"])} |',f'| **Overall Score** | {report["overall_score"]:.1f}/100 |',f'| **Files Detected** | {total} context files |','','### Level Breakdown','','| Level | Files |','| --- | ---: |']
    for key, value in sorted(scores.items(),key=lambda x:int(x[0])):
        lines.append(f'| Level {key}: {cell(value["name"])} | {value["file_count"]} |')
    lines += ['',"### This PR's Impact",'']
    if any(x['status']=='added' for x in context):
        lines.append('This PR adds context artifacts. Thank you for strengthening the repository context.')
    if context:
        lines += [f'- `{cell(x["filename"])}`: {cell(x["status"])}' for x in context]
    else:
        lines.append('No listed context-artifact paths changed in this PR.')
    if level >= 4:
        lines += ['',f'The native tool reports an advanced Level {level} baseline. The recommendations below describe next steps.']
    elif level == 1:
        lines += ['','This is a starting point. The native recommendations identify concrete context files to add.']
    lines += ['','### Top Recommendations',''] + [f'{i}. {cell(r)}' for i,r in enumerate(recs,1)]
    lines += ['','---','*Powered by [measure-ai-proficiency](https://github.com/pskoett/measuring-ai-proficiency)*']
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    Path('assessment-comment.md').write_text(render(json.loads(Path('proficiency-report.json').read_text()),json.loads(Path('pr-changes.json').read_text())))
