on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 06:00 UTC
  workflow_dispatch:

jobs:
  scan-repos:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Profile Repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install PyGithub
        run: pip install PyGithub

      - name: Run Tag Scanner
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_USERNAME: Saar-Sha
        run: |
          mkdir -p .github/scripts
          echo "import os
import re
from github import Github

TAG_PATTERN = re.compile(r'#(\\w+)', re.IGNORECASE)
username = os.environ['GITHUB_USERNAME']
token = os.environ['GITHUB_TOKEN']
g = Github(token)
user = g.get_user()

counters = {}

for repo in user.get_repos():
    if repo.private:
        continue
    contents = ''
    try:
        readme = repo.get_readme()
        contents = readme.decoded_content.decode()
    except:
        pass

    try:
        for file in repo.get_contents(''):
            if file.path.endswith('.py') or file.path.endswith('.md'):
                contents += file.decoded_content.decode()
    except:
        pass

    for tag in TAG_PATTERN.findall(contents):
        tag = tag.lower()
        counters[tag] = counters.get(tag, 0) + 1

with open('README.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_marker = '<!-- TAG_DASHBOARD_START -->\\n'
end_marker = '<!-- TAG_DASHBOARD_END -->\\n'

new_block = start_marker
new_block += '| Tag | Count |\\n|------|-------|\\n'
for tag, count in sorted(counters.items(), key=lambda x: -x[1]):
    new_block += f'| #{tag} | {count} |\\n'
new_block += end_marker

with open('README.md', 'w', encoding='utf-8') as f:
    in_block = False
    for line in lines:
        if line == start_marker:
            in_block = True
            f.write(new_block)
        elif line == end_marker:
            in_block = False
        elif not in_block:
            f.write(line)
" > .github/scripts/tag_scanner.py

      - name: Commit Changes
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add README.md
          git commit -m "📊 Update project tag summary"
          git push || echo "No changes to commit."
