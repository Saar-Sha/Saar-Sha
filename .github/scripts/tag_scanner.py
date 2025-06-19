import os
import re
from github import Github

TAG_PATTERN = re.compile(r'#(\w+)', re.IGNORECASE)
username = os.environ['GITHUB_USERNAME']
token = os.environ['GITHUB_TOKEN']
g = Github(token)
user = g.get_user()

counters = {}
all_repos_scanned = set()

# Get all public repos
for repo in user.get_repos(visibility='public'):
    if repo.private:
        continue
    try:
        readme = repo.get_readme()
        contents = readme.decoded_content.decode()
        tags_in_repo = set()
        for tag in TAG_PATTERN.findall(contents):
            tag = tag.lower()
            tags_in_repo.add(tag)
        for tag in tags_in_repo:
            if tag not in counters:
                counters[tag] = set()
            counters[tag].add(repo.full_name)
        all_repos_scanned.add(repo.full_name)
    except:
        continue

# Convert sets to counts
final_counts = {tag: len(repos) for tag, repos in counters.items()}

with open('README.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_marker = '<!-- TAG_DASHBOARD_START -->'
end_marker = '<!-- TAG_DASHBOARD_END -->'

new_block = start_marker + '\n'
new_block += f'Total Repos Scanned: {len(all_repos_scanned)}\n\n'
new_block += '| Tag | Count |\n|------|-------|\n'
for tag, count in sorted(final_counts.items(), key=lambda x: -x[1]):
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
