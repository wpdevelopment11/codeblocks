import glob
import sys
import os.path

from enum import Enum

class Codeblock(Enum):
    IN = 1
    IN_WITH_LANG = 2
    OUT = 3

DEFAULT_LANG = "txt"

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

result = open("result.txt", "w", encoding="utf-8")

files = glob.iglob("**/*.md", root_dir=sys.argv[1], recursive=True)

for file in files:
    fullpath = os.path.join(sys.argv[1], file)
    blockstate = Codeblock.OUT
    code = []
    fence = ""
    for linenum, line in enumerate(open(fullpath, encoding="utf-8", newline=''), 1):
        if line.strip().startswith("```"):
            if  blockstate == Codeblock.IN_WITH_LANG:
                blockstate = Codeblock.OUT
            elif blockstate == Codeblock.IN:
                blockstate = Codeblock.OUT
                if code:
                    indent = len(fence) - len(fence.lstrip())
                    code_str = "".join(line[indent:] for line in code)
                    print(f"{fullpath}:{linenum - len(code) - 1}", file=result)
                    print(f"```{guess_language(code_str)}\n" + code_str + "```", file=result)
                    print(file=result)
                    code = []
            elif line.strip() == "```":
                blockstate = Codeblock.IN
                fence = line
            else:
                blockstate = Codeblock.IN_WITH_LANG
        elif blockstate == Codeblock.IN:
            code.append(line)

result.close()
