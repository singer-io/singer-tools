import subprocess
import re

def git(*args):
    cmd = ['git'] + list(args)

    print('> {}'.format(' '.join(cmd)))
    lines = str(subprocess.check_output(cmd, universal_newlines=True)).splitlines()
    for line in lines:
        print(line)
    print('')
    return lines


def fail(msg):
    print(msg)
    exit(1)


def git_check_branch():
    branch_lines = git('rev-parse', '--abbrev-ref', 'HEAD')
    if len(branch_lines) == 0:
        fail('Could not determine branch')
    branch = branch_lines[0]
    if branch != 'master':
        fail('Must be on master branch, you are on {}'.format(branch))

def git_check_status():
    status_lines = git('status', '--porcelain')
    if len(status_lines) > 0:
        fail('You have uncommitted changes')

def git_push():
    git('push')

def find_version_number():
    candidates = []
    with open('setup.py') as setup:
        for line in setup:
            m = re.match(r'^\s+version=\'(\d\.\d\.\d)\',', line)
            if m:
                candidates.append(m.group(1))
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        print("I couldn't find the version number in setup.py. Please make sure there's a line that looks like 'version='x.x.x','.")
        exit(1)
    else:
        print("I found multiple candidates for the version number in setup.py. Please make sure there's exactly one line that looks like 'version=x.x.x,'.")
        exit(1)        
    
def main():
    version = find_version_number()
    print(version)
    git_check_branch()
    git_check_status()
    git('push')
    git('tag', '-a', 'v'+version, '-m', 'version '+version)
    git('push', '--tags')
    subprocess.call(['python', 'setup.py', 'sdist', 'upload'])
