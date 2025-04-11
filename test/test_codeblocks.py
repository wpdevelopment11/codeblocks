import contextlib
import os.path
import shutil
import sys
import tempfile
import unittest

import codeblocks

class CodeblocksEditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls._files_dir = files_dir = os.path.join(test_dir, "files")
        cls._temp_dir = temp_dir = tempfile.mkdtemp()
        files = [os.path.join(files_dir, file) for file in os.listdir(files_dir) if not file.endswith("_result.md")]
        files_to_edit = [shutil.copy(file, temp_dir) for file in files]
        codeblocks.add_language(files_to_edit, edit_files=True)

    def check_file(self, filename):
        self.maxDiff = None
        actual = os.path.join(self._temp_dir, filename)
        expected = os.path.join(self._files_dir, filename[:-3] + "_result.md")
        with open(actual, "r", encoding="utf-8") as actual, open(expected, "r", encoding="utf-8") as expected:
            self.assertEqual(actual.read(), expected.read())

    def test_single_block_at_start(self):
        self.check_file("single_block_at_start.md")

    def test_single_block_at_end(self):
        self.check_file("single_block_at_end.md")

    def test_single_block_in_middle(self):
        self.check_file("single_block_in_middle.md")

    def test_multiple_blocks(self):
        self.check_file("multiple_blocks.md")

    def test_multiple_blocks_indent(self):
        self.check_file("multiple_blocks_indent.md")

    def test_inline_code(self):
        self.check_file("inline_code.md")

    def test_more_backticks(self):
        self.check_file("more_backticks.md")

    def test_less_backticks(self):
        self.check_file("less_backticks.md")

    def test_block_termination(self):
        self.check_file("block_termination.md")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temp_dir)

class CodeblocksPrintTest(unittest.TestCase):
    def test_codeblocks_terminal_output(self):
        self.maxDiff = None

        test_dir = os.path.join("test", "files")
        files = [
            os.path.join(test_dir, "multiple_blocks_indent.md"),
            os.path.join(test_dir, "single_block_for_terminal.md")
        ]

        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as actual:
            with contextlib.redirect_stdout(actual):
                codeblocks.add_language(files, edit_files=False)
            actual.flush()
            actual.seek(0)
            result = "terminal_output_win_result.md" if sys.platform == "win32" else "terminal_output_result.md"
            with open(os.path.join(test_dir, result), "r", encoding="utf-8") as expected:
                self.assertEqual(actual.read(), expected.read())
