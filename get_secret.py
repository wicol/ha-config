#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    print('Print a secret with:')
    print('{} <secret_name>'.format(__file__))
    sys.exit(1)

target_secret_name = sys.argv[1]
secrets_str = open('secrets.yaml').read()

# PyYAML is for suckers
secrets_dict = {}
for s in secrets_str.splitlines():
    secret_name, secret = s.split(': ', 1)
    if secret_name == target_secret_name:
        print(secret.strip("'").strip('"'))
        break
else:
    sys.exit(2)
