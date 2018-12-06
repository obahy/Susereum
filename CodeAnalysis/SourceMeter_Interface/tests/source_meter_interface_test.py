import os
import sys
import unittest
from shutil import rmtree
from StringIO import StringIO
from sourceMeterWrapper import main


class SimpleTest(unittest.TestCase):

    def test_invalid_url_invalid_save_directory(self):
        args = ['sourceMeterWrapper.py', 'vlaksdlkj20', '/dev/foo.bar']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, 'Error: The second passed argument is not a valid directory.\n')
        finally:
            sys.stdout = saved_stdout

    def test_invalid_url_valid_save_directory(self):
        args = ['sourceMeterWrapper.py', 'https://github.com/$/#', '/tmp/']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, 'Error: The first passed argument is not a valid GitHub Repo URL.\n')
        finally:
            sys.stdout = saved_stdout

    def test_valid_url_invalid_save_directory(self):
        args = ['sourceMeterWrapper.py', 'https://github.com/obahy/Susereum', '/dev/foo.bar']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, 'Error: The second passed argument is not a valid directory.\n')
        finally:
            sys.stdout = saved_stdout

    def test_valid_url_valid_save_directory(self):
        args = ['sourceMeterWrapper.py',
                'https://github.com/obahy/Susereum/commit/f73f355109614c4da446fc64f989c1e4b8aa5925',
                '/tmp/Results']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, '/tmp/Results\n')
            self.assertEqual(os.path.isfile('/tmp/Results/Susereum.csv'), True)
        finally:
            rmtree('/tmp/Results')
            sys.stdout = saved_stdout

    def test_more_than_3_args(self):
        args = ['sourceMeterWrapper.py',
                'https://github.com/obahy/Susereum/commit/f73f355109614c4da446fc64f989c1e4b8aa5925',
                '/tmp/Results',
                'https://github.com/obahy/Susereum/commit/f73f355109614c4da446fc64f989c1e4b8aa5925']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, 'Error: Incorrect number of arguments. Usage should be:\n'
                                     '$ python sourceMeterWrapper.py <(GitHub Project Repo) | '
                                     '(Path to Project)> <Directory Where to Store Results>\n')

        finally:
            sys.stdout = saved_stdout

    def test_no_args(self):
        args = ['sourceMeterWrapper.py']
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            main(args)
            output = out.getvalue()
            self.assertEqual(output, 'Error: Incorrect number of arguments. Usage should be:\n'
                                     '$ python sourceMeterWrapper.py <(GitHub Project Repo) | '
                                     '(Path to Project)> <Directory Where to Store Results>\n')
        finally:
            sys.stdout = saved_stdout


if __name__ == '__main__':
    unittest.main()
