import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build import save_post, parse_post, read_posts, render_markdown


class PostStorageTests(unittest.TestCase):
    def test_saved_post_survives_a_new_process_and_updates(self):
        with tempfile.TemporaryDirectory() as folder:
            payload = dict(title='새우 크림 파스타', category='메뉴', summary='면 선택 안내',
                           body='펜네·스파게티·링귀니 중 선택할 수 있습니다.', status='published')
            target = save_post(folder, 'cream-pasta', payload, '2026-10-31')
            script = 'from pathlib import Path; import sys;sys.path.insert(0,sys.argv[1]);from build import parse_post;print(parse_post(Path(sys.argv[2]))["body"])'
            process = subprocess.run([sys.executable, '-c', script, str(ROOT), str(target)],
                                     capture_output=True, text=True, encoding='utf-8', check=True,
                                     env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
            self.assertIn('링귀니', process.stdout)
            payload['body'] = '수정된 메뉴 설명입니다.'
            save_post(folder, 'cream-pasta', payload, '2026-11-01')
            stored = parse_post(target)
            self.assertEqual(stored['date'], '2026-10-31')
            self.assertEqual(stored['updated'], '2026-11-01')
            self.assertEqual(stored['body'], payload['body'])

    def test_drafts_stay_saved_but_are_not_published(self):
        with tempfile.TemporaryDirectory() as folder:
            target = save_post(folder, 'draft-post', dict(title='임시 글', category='메뉴',
                summary='아직 작성 중', body='확인할 내용입니다.', status='draft'), '2026-10-31')
            self.assertTrue(target.exists())
            self.assertEqual(read_posts(folder), [])

    def test_unsafe_slug_and_html_cannot_become_active_content(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_post(folder, '../../outside', {}, '2026-10-31')
        rendered = render_markdown('<script>alert(1)</script>\n\n## 메뉴')
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('<h2>메뉴</h2>', rendered)

    def test_article_links_and_photos_keep_unsafe_content_inert(self):
        rendered = render_markdown('[예약](/stories/reservation/)\n\n[위험](javascript:alert)\n\n![한상](/assets/table.webp)\n\n![외부](https://example.com/image.png)')
        self.assertIn('href="/stories/reservation/"', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('src="/assets/table.webp"', rendered)
        self.assertNotIn('src="https://example.com', rendered)


if __name__ == '__main__':
    unittest.main()
