"""Write a post atomically, then regenerate the public pages. JSON is read from stdin."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build import save_post, build

parser = argparse.ArgumentParser()
parser.add_argument('--slug', required=True)
parser.add_argument('--date', required=True, help='Client-local date, YYYY-MM-DD')
args = parser.parse_args()
payload = json.load(sys.stdin)
target = save_post(ROOT / 'content/posts', args.slug, payload, args.date)
build(ROOT)
print('Saved', target.relative_to(ROOT))
