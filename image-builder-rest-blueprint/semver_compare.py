from packaging import version
import argparse


parser = argparse.ArgumentParser(description='Returns true if second SemVer is greater or equal then the first')
parser.add_argument('semver_1', type=str, help='First SemVer expression')
parser.add_argument('semver_2', type=str, help='Second SemVer expression')

args = parser.parse_args()
greater_or_equal = version.parse(args.semver_1) <= version.parse(args.semver_2)
if not greater_or_equal:
    exit(1)
