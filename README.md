## Description

Find the fenced code blocks in the Markdown file that don't have the language specified.
Detect the language from the block contents and insert the language name after the starting fence.
Print the resulting code blocks or edit the files in-place.

Under the hood it uses [Magika](https://github.com/google/magika) (recommended) or [Guesslang](https://github.com/yoeo/guesslang) deep learning models to detect the language.

Tested on Windows and Linux.

## Install

```bash
git clone https://github.com/wpdevelopment11/codeblocks
cd codeblocks
python3 -m venv .venv
source .venv/bin/activate

# Install one of them:
pip install magika==0.6.1 # Recommended
# Or
pip install guesslang # May not work,
                      # depending on your Python version
                      # and OS combination.
```

> **Note:** <a id="guesslang"></a>
> [Guesslang](https://github.com/yoeo/guesslang) is not maintained. I got it working on Windows with Python 3.10.
>
> First `pip install tensorflow==2.13`.
>
> Next, copy [guesslang directory](https://github.com/yoeo/guesslang/tree/master/guesslang) to the top-level directory of your project.
> Start the Python shell with `python` and run `import guesslang` to check if it's installed properly.

## Usage

```bash
python3 codeblocks.py [--edit] path ...
```

* `--edit`

  Edit files by inserting the language.
  By default, files are not modified,
  instead code blocks for which the language can be detected are printed to the terminal.

* `path`

  Paths to process.
  Can be Markdown files or directories, or any combination of them.
  Directories are processed recursively.

### Insert the language names in all Markdown files in directory

This command will edit your files, make a backup.

```bash
python3 codeblocks.py --edit /path/to/dir
```

### Insert the language names in specified file(s) only

```bash
python3 codeblocks.py --edit /path/to/file.md
```

### Print code blocks with the detected language, without modifying files

```bash
python3 codeblocks.py /path/to/file.md
```

## Docker

Build the image:

```bash
cd codeblocks
docker build -t codeblocks .
```

Insert the languages in all Markdown files in `/path/on/host`:

* Replace `/path/on/host` with your Markdown files directory.

```bash
docker run --rm -v /path/on/host:/app/mdfiles codeblocks --edit mdfiles
```

## Run tests

```bash
python3 -m unittest discover test
```

## Limitations

* Line that consists of three or more backticks is always detected as a fenced code block.
Normal Markdown parsers consider them as such only if up to three spaces of indentation are used outside of a list item,
and up to seven spaces otherwise.

## Motivation

The language names in the fenced code blocks are commonly used for syntax highlighting.

Some people forget to or don't know how to specify the language.
This leads to a code that is not highlighted and hard to read.
This script is intended to solve that issue.

Example:

* Before:

  ````
  ```
  def print_table():
      for num in range(10):
          sqr = num * num
          print(f"{num}^2\t= {sqr}")

  print_table()
  ```
  ````

* After:

  ````python
  ```python
  def print_table():
      for num in range(10):
          sqr = num * num
          print(f"{num}^2\t= {sqr}")

  print_table()
  ```
  ````
