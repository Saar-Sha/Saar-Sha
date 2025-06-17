import os
import re
from github import Github

TAG_PATTERN = re.compile(r'#(\w+)', re.IGNORECASE)
username = os.environ['GITHUB_USERNAME']
token = os.environ['GITHUB_TOKEN']
g = Github(token)
user = g.get_user()

counters = {}

repo_name = os.getenv('GITHUB_REPOSITORY')  # e.g. 'Saar-Sha/Saar-Sha'
repo = g.get_repo(repo_name)
repos = [repo]

for repo in repos:
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

start_marker = '<!-- TAG_DASHBOARD_START -->'
end_marker = '<!-- TAG_DASHBOARD_END -->'

new_block = start_marker + '\n'
new_block += '| Tag | Count |\n|------|-------|\n'
for tag, count in sorted(counters.items(), key=lambda x: -x[1]):
    new_block += f'| #{tag} | {count} |\n'
new_block += end_marker + '\n'

with open('README.md', 'w', encoding='utf-8') as f:
    in_block = False
    for line in lines:
        if line.strip() == start_marker:
            in_block = True
            f.write(new_block)
        elif line.strip() == end_marker:
            in_block = False
        elif not in_block:
            f.write(line)
