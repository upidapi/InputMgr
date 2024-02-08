import subprocess

print(subprocess.check_output(
            ['dumpkeys', '--full-table', '--keys-only']
        ).decode('utf-8'))