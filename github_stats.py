#!/usr/bin/python

import sys
import argparse
import requests
 
def printGitRepoReleaseStats(name, args):
    response = requests.get(
        f'https://api.github.com/repos/{name}/releases',
        headers={'Accept': 'application/json'})
    if response.status_code == 200:
        print(f'{name}: ')
        response_json = response.json()
        for release_entry in response_json[:args.max]:
            assets_entries = release_entry['assets']
            tag_name = release_entry['tag_name']
            release_info = '{0:10} :'.format(tag_name)
            if len(assets_entries) == 0:
                release_info += ' none'
            for asset_entry in assets_entries:
                release_info += ' {0:4}'.format(asset_entry['download_count'])
            print(release_info)
    else:
        print(f'{name}: http error - {response.status_code}')
    print('')

def main(args):
    with open(args.repo_file, "r") as f:
        repositories = f.read().splitlines()
    for repository in repositories:
        if len(repository) != 0:
            printGitRepoReleaseStats(repository, args)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display GitHub release download stats', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', '--repo-file', default="github_repositories.txt", help='Filename with list of GitHub repostories in format <owner>/<repo_name>.')
    parser.add_argument('-m', '--max', type=int, default=4, help='Max release entries count to get. Use -1 value to get all.')
    sys.exit(main(parser.parse_args()))
