#!/usr/bin/python

import os
import sys
import argparse
import configparser

def main(args):
    try:
        if len(args.documents) % 2 != 0:
            print(f'Error: Invalid documents parameter pairs: {args.documents}')
            return 1
        config = configparser.ConfigParser()
        config.optionxform = str
        config.add_section(args.section_name)
        config.set(args.section_name, 'accountId', args.account_id)
        config.set(args.section_name, 'authKey', args.auth_key)
        i = 0
        docId = 1
        while i < len(args.documents):
            config.set(args.section_name, f'documentId_{docId}', f'{args.documents[i + 1]}, {args.documents[i]}')
            docId = docId + 1
            i = i + 2
        config.set(args.section_name, 'languageId', str(args.lang))
        fileName = os.path.join(args.output_path, 'smartcat.ini')
        with open(fileName, 'w') as configfile:
            config.write(configfile)
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error:', err)
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate smartCAT configuration file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('documents', nargs='+', metavar='NAME ID', help='Pair with name of document and smartCAT document id')
    parser.add_argument('-o', '--output-path', metavar='DIR', default='./', help='Output directory used to store config file')
    parser.add_argument('--section-name', metavar='NAME', default='default', help='config section name')
    parser.add_argument('--account-id', metavar='ID', required=True, help='smartCAT account identifier')
    parser.add_argument('--auth-key', metavar='KEY', required=True, help='smartCAT account authentication key')
    parser.add_argument('-l', '--lang', metavar='NAME', type=int, required=True, help='Language locale code')
    sys.exit(main(parser.parse_args()))