import subprocess
import re
import os

REPOSITORY_URL = 'https://upload.pypi.org/legacy/'

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
    if not branch_lines:
        fail('Could not determine branch')
    branch = branch_lines[0]
    if branch != 'master':
        fail('Must be on master branch, you are on {}'.format(branch))

def git_check_status():
    status_lines = git('status', '--porcelain')
    if status_lines:
        fail('You have uncommitted changes')

def git_push():
    git('push')


class VersionNumberException(Exception):
    pass

def parse_version_number(lines):
    candidates = []
    for line in lines:
        match_sq = re.match(r'^\s+version=\'(\d+\.\d+\.\d+\w*)\',', line)
        match_dq = re.match(r'^\s+version=\"(\d+\.\d+\.\d+\w*)\",', line)
        for match in [match_sq, match_dq]:
            if match:
                candidates.append(match.group(1))
    if len(candidates) == 1:
        return candidates[0]
    elif not candidates:
        raise VersionNumberException(
            "I couldn't find the version number in setup.py. " +
            "Please make sure there's a line that looks like " +
            "'version='...','.")
    else:
        raise VersionNumberException(
            "I found multiple candidates for the version number in " +
            "setup.py. Please make sure there's exactly one line that " +
            "looks like 'version=x.x.x,'.")


def find_version_number():
    try:
        with open('setup.py') as setup:
            return parse_version_number(setup)
    except VersionNumberException as exc:
        print(exc)
        exit(1)

def find_dist(version):
    candidates = os.listdir('dist')
    suffix = version + '.tar.gz'
    for candidate in candidates:
        if candidate.endswith(suffix):
            return 'dist/' + candidate
    raise Exception("I could't find a file ending with " + suffix + " in dist/")
        

def main():
    version = find_version_number()
#    git_check_branch()
    git_check_status()
    git('push')
    git('tag', '-a', 'v'+version, '-m', 'version '+version)
    git('push', '--tags')
    subprocess.call(['python', 'setup.py', 'sdist'])
    dist = find_dist(version)
    print()
    confirmation = input('Upload ' + dist + ' to ' + REPOSITORY_URL + '? [y/n]: ')

    if (confirmation != 'y'):
        print('Aborting')
        return
    
    subprocess.call([
        'twine', 'upload',
        '--repository-url', REPOSITORY_URL,
        dist])
