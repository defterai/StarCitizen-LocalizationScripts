#!/usr/bin/python

# Export and download translation file from crowdin.
# Please make sure before use script you're created
# configuation file for script. See example below.
#
# Example (crowdin.ini):
# [config_name]
# authKey =
# projectId =
# languageId =

# Requirements:
# pip install crowdin-api-client

import os
import sys
import urllib
import argparse
import configparser
from crowdin_api import CrowdinClient
from crowdin_api.api_resources.enums import ExportProjectTranslationFormat

class crowdinConfig:
    @staticmethod
    def __ReadConfigKey(config, key_name):
        if not key_name in config:
            raise Exception(f"Missing key '{key_name}' in crowdin config")
        key_value = config[key_name].strip()
        if len(key_value) == 0:
            raise Exception(f"Empty key '{key_name}' value in crowdin config")
        return key_value
    
    def __init__(self, config):
        self.authKey = crowdinConfig.__ReadConfigKey(config, 'authKey')
        self.projectId = crowdinConfig.__ReadConfigKey(config, 'projectId')
        self.languageId = crowdinConfig.__ReadConfigKey(config, 'languageId')


def main(args):
    result = -1
    try:
        print('EXPORT crowdin')
        config = configparser.ConfigParser()
        if not config.read('crowdin.ini'):
            print('Error: Missing config file - crowdin.ini')
            return 1
        if len(config.sections()) == 0:
            print('Error: No sections in crowdin config')
            return 1
        print('Available crowdin config - ', ', '.join(str(e) for e in config.sections()))
        config_name = args.config
        if args.interactive or len(config_name) == 0:
            config_name = input('Enter crowdin config name: ').strip()
            while not config.has_section(config_name):
                if len(config_name) > 0:
                    print('Unknown crowdin config name - ', config_name)
                config_name = input('Enter crowdin config name: ').strip()
        if not config.has_section(config_name):
            print('Unknown crowdin config name - ', config_name)
            return 1
        print('Use crowdin config name - ', config_name)
        crowdin_config = crowdinConfig(config[config_name])
        api = CrowdinClient(token=crowdin_config.authKey, timeout=60000)
        print('Get translation link...')
        translation = api.translations.export_project_translation(crowdin_config.projectId, 
                                                                  targetLanguageId=crowdin_config.languageId, 
                                                                  format=ExportProjectTranslationFormat.XLIFF)
        output_filename = os.path.join(args.output_path, 'global.ini.xliff')
        print(f'Download translation {output_filename}...')
        download_result = urllib.request.urlretrieve(translation['data']['url'], output_filename)
        result = 200
    except urllib.error.HTTPError as err:
        result = err.code
        print('Error: Failed download: {0}'.format(err))
    except Exception as err:
        print('Error: Failed export: {0}'.format(err))
    except KeyboardInterrupt as err:
        print('Interrupted')
    if result == 200:
        print('Done')
        return 0
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export crowdin files', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config', nargs='?', metavar='CONFIG_NAME', default='', help='Name of section of config in crowdin.ini')
    parser.add_argument('-o', '--output-path', metavar='DIR', default='./', help='Output directory used to store downloaded files')
    parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Run interactive')
    sys.exit(main(parser.parse_args()))
