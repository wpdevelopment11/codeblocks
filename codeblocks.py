from enum import Enum
from itertools import chain
from tempfile import NamedTemporaryFile

import argparse
import glob
import os
import os.path
import re
import shutil
import sys

class Codeblock(Enum):
    IN = 1
    IN_WITH_LANG = 2
    OUT = 3

INTLINE_PATTERN = re.compile("```+[^`]+`")
DEFAULT_LANG = "txt"

try:
    from magika import Magika
    magika = Magika()
    def guess_language(code):
        codebytes = code.encode(encoding="utf-8")
        lang = magika.identify_bytes(codebytes).prediction.output.label
        return lang if lang != "unknown" else DEFAULT_LANG
except ImportError:
    try:
        from guesslang import Guess
        guesslang = Guess()
        def guess_language(code):
            lang = guesslang.language_name(code)
            return lang.lower() if lang else DEFAULT_LANG
    except ImportError:
        print("Magika or Guesslang is required to run this script. Install one of them to proceed!")
        sys.exit(1)

def add_language(files, edit_files):
    def is_made_of_char(str, char):
        return len(str) == str.count(char)
    # newline="" is important. See below.
    temp = NamedTemporaryFile("w+", encoding="utf-8", newline="", delete=False)
    for file in files:
        blockstate = Codeblock.OUT
        code = []
        # The argument newline="" is important here and in the NamedTemporaryFile() call above.
        # We don't want to change line endings in a file which we're editing.
        with open(file, encoding="utf-8", newline="") as f:
            for linenum, line in enumerate(f, 1):
                stripped = line.strip()
                if (stripped.startswith("```") and not INTLINE_PATTERN.match(stripped)
                        and (blockstate == Codeblock.OUT or is_made_of_char(stripped, "`")
                            and len(stripped) >= backticks_num)):
                    if  blockstate == Codeblock.IN_WITH_LANG:
                        blockstate = Codeblock.OUT
                        if edit_files: temp.write(line)
                    elif blockstate == Codeblock.IN:
                        blockstate = Codeblock.OUT
                        code_str = "\n".join(line.removeprefix(indent).rstrip() for line in code) + "\n"
                        lang = guess_language(code_str) if code_str else ""
                        if edit_files:
                            # When editing files, txt is not very useful edit.
                            if lang == "txt": lang = ""
                            fence_start = "`" * backticks_num
                            temp.write(fence.replace(fence_start, fence_start + lang))
                            temp.writelines(code)
                            temp.write(line)
                        elif lang:
                            print(f"{file}:{linenum - len(code) - 1}")
                            print(("`" * backticks_num) + lang + "\n" + code_str + stripped)
                            print()
                        code = []
                    elif is_made_of_char(stripped, "`"):
                        backticks_num = len(stripped)
                        blockstate = Codeblock.IN
                        count = len(line) - len(line.lstrip())
                        indent = line[:count]
                        fence = line
                    else:
                        backticks_num = stripped.count("`")
                        blockstate = Codeblock.IN_WITH_LANG
                        if edit_files: temp.write(line)
                elif blockstate == Codeblock.IN:
                    code.append(line)
                elif edit_files:
                    temp.write(line)
            if edit_files:
                if code:
                    # non-terminated fence
                    temp.write(fence)
                    temp.writelines(code)
                temp.flush()
                shutil.copy(temp.name, file)
                temp.seek(0)
                temp.truncate(0)
    temp.close()
    os.unlink(temp.name)

def main():
    parser = argparse.ArgumentParser(description="Detect and insert the language in the Markdown code blocks.")
    parser.add_argument("--edit", action="store_true", help="Edit files by inserting the language")
    parser.add_argument("path", nargs="+", help="Paths to process")
    args = parser.parse_args()

    files = []
    iters = []

    for path in args.path:
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            iters.append(glob.iglob(os.path.join(path, "**", "*.md"), recursive=True))
        else:
            print(f"Path doesn't exist: \"{path}\"")
            sys.exit(1)

    iters.append(iter(files))
    add_language(chain.from_iterable(iters), args.edit)

if __name__ == "__main__":
    main()
