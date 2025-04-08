import glob
import sys
import os.path

from enum import Enum
from tempfile import NamedTemporaryFile
from shutil import copy
from os import unlink

class Codeblock(Enum):
    IN = 1
    IN_WITH_LANG = 2
    OUT = 3

DEFAULT_LANG = "txt"
EDIT_FILES = True

try:
    from magika import Magika
    magika = Magika()
    def guess_language(code):
        codebytes = code.encode(encoding="utf-8")
        lang = magika.identify_bytes(codebytes).prediction.output.label
        if lang == "unknown": return DEFAULT_LANG
        return lang
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

if len(sys.argv) != 2:
    print("Usage: python codeblocks.py dir")
    sys.exit(1)

files = glob.iglob("**/*.md", root_dir=sys.argv[1], recursive=True)
# newline="" is important. See below.
temp = NamedTemporaryFile("w+", encoding="utf-8", newline="", delete=False)

for file in files:
    fullpath = os.path.join(sys.argv[1], file)
    blockstate = Codeblock.OUT
    code = []
    fence = ""
    # The argument newline="" is important here and in the NamedTemporaryFile() call above.
    # We don't want to change line endings in a file which we're editing.
    for linenum, line in enumerate(open(fullpath, encoding="utf-8", newline=""), 1):
        if line.strip().startswith("```"):
            if  blockstate == Codeblock.IN_WITH_LANG:
                blockstate = Codeblock.OUT
                if EDIT_FILES: temp.write(line)
            elif blockstate == Codeblock.IN:
                blockstate = Codeblock.OUT
                indent = len(fence) - len(fence.lstrip())
                code_str = "\n".join(line[indent:].strip() for line in code) + "\n"
                lang = guess_language(code_str) if code_str else ""
                if EDIT_FILES:
                    # When editing files, txt is not very useful edit.
                    if lang == "txt": lang = ""
                    temp.write(fence.replace("```", f"```{lang}"))
                    temp.writelines(code)
                    temp.write(line)
                elif lang:
                    print(f"{fullpath}:{linenum - len(code) - 1}")
                    print(f"```{lang}\n" + code_str + "```")
                    print()
                code = []
            elif line.strip() == "```":
                blockstate = Codeblock.IN
                fence = line
            else:
                blockstate = Codeblock.IN_WITH_LANG
                if EDIT_FILES: temp.write(line)
        elif blockstate == Codeblock.IN:
            code.append(line)
        elif EDIT_FILES:
            temp.write(line)
    if EDIT_FILES:
        if code:
            # non-terminated fence
            temp.write(fence)
            temp.writelines(code)
        temp.flush()
        copy(temp.name, fullpath)
        temp.seek(0)
        temp.truncate(0)

temp.close()
unlink(temp.name)
