# pdiff

Python implement of a file diff tool, similar to GNU [diff](https://www.gnu.org/software/diffutils/manual/html_node/diff-Options.html).

```console
$ ./pdiff.py help				# get usage
$ ./pdiff.py diff file1.txt file2.txt > file.patch
$ ./pdiff.py patch file1.txt fie.patch
$ diff -u file1.txt file2.txt                   # verify file1 equals file2
```k

### TODO:

- File version control