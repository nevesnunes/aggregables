# Aggregables

Snippets and scripts to parse and manipulate data patterns. These are categorized by analysis task:

<!-- toc -->

- [Captures](#captures)
  * [Visualize co-ocurrences](#visualize-co-ocurrences)
  * [Histogram](#histogram)
  * [Proximity search for two or more substrings](#proximity-search-for-two-or-more-substrings)
- [Differences](#differences)
  * [Summarize distinct bytes in two files](#summarize-distinct-bytes-in-two-files)
- [Sequences](#sequences)
  * [Filter out repeated k-line patterns in a plaintext stream](#filter-out-repeated-k-line-patterns-in-a-plaintext-stream)
  * [Find longest k-repeating substrings in byte stream](#find-longest-k-repeating-substrings-in-byte-stream)
- [Time Series](#time-series)
  * [Sort logs by timestamps, including lines without one](#sort-logs-by-timestamps-including-lines-without-one)

<!-- tocstop -->

## Captures

### Visualize co-ocurrences

- [heapmap.py](./captures/heatmap.py)

Usage:

```bash
./heatmap.py <(printf '%s\n' \
    'a b 41' \
    'a c 12' \
    'b c 10' \
    'c b 1' \
    'b e 1' \
    'b f 99')
```

Output:

```
|b
|O|f
|o| |a
|.| |.|c
|.| | | |e

99 ('b', 'f')
41 ('a', 'b')
12 ('a', 'c')
11 ('b', 'c')
 1 ('b', 'e')
```

Caption:

|Symbol|Description|
|---|---|
|`O`|counts > max_counts / 2|
|`o`|counts > max_counts / 3|
|`u`|counts > max_counts / 4|
|`.`|counts > 0|

### Histogram

```awk
for (key in out) {
    h = ""
    max_h = 8 * out[key] / total
    for (i=0; i<max_h; i++) {
        h = h "="
    }
    printf "%16s | %8s %.2f | %s\n", out[key], h, (out[key] / total), key
}
```

### Proximity search for two or more substrings

- [magrep.sh](./capture/magrep.sh)
- [magrep.py](./capture/magrep.py)

Usage: `./magrep.py test1 'brown.*quick'`

Output:

```
test1:1-1:quick brown
```

Usage: `./magrep.sh brown quick test1`

Output:

```
test1[1,5]:
the quick brown fox
was quick
and also a fox
bla bla bla
bbbbbbbbbbb
test1[11,12]:
the fox
was quick
```

Alternatives: `grep --color=always -Hin -C 2 quick test1 | grep 'quick\|fox'`

Output:

```
test1:1:the quick brown fox
test1:2:was quick
test1-3-and also a fox
test1:6:it was quick
test1-11-the fox
test1:12:was quick
```

## Differences

### Summarize distinct bytes in two files

- [hexdiff.py](./differences/hexdiff.py)

Alternatives: GNU diffutils contains `cmp`, which outputs offsets and byte values in a byte-by-byte manner:

```
10  24 ^T    25 ^U
11  14 ^L    35 ^]
25  41 !    226 M-^V
26  42 "    252 M-*
27 226 M-^V  41 !
28 252 M-*   42 "
```

`hexdiff.py` adds context by formatting in universal diff format, outputs hex values, and joins differences using [semantic cleanup](https://github.com/google/diff-match-patch/wiki/API#diff_cleanupsemanticdiffs--null):

```bash
./hexdiff.py test-bytes1 test-bytes2-added | vim -c 'set filetype=diff' -
```

```diff
      0x0: 7071a42f707170716d | b'pq\xa4/pqpqm'
-    0x12: 140c | b'\x14\x0c'
+    0x12: 151d | b'\x15\x1d'
     0x12: 6996aa191a1b1c1d771e772122 | b'i\x96\xaa\x19\x1a\x1b\x1c\x1dw\x1ew!"'
-    0x2c: 212296aa9ff3 | b'!"\x96\xaa\x9f\xf3'
+    0x2c: 96aa21229ff31234 | b'\x96\xaa!"\x9f\xf3\x124'
```

- Comparing files recursively:

```bash
diff -aurwq dir1/ dir2/ | grep '^Only'

# Apply pair-wise process substitution recursively
# Alternative: `... | xargs eval "$(printf 'echo %s %s')"`
diff -aurwq dir1/ dir2/ | \
    gawk 'match($0, /Files (.*) and (.*) differ/, matches) {
        print matches[1] "\n" matches[2]
    }' | \
    xargs -n2 bash -c 'echo "$1 $2"; diff -auw \
        <(gawk "/^[[:space:]]*#|\/\/|<!--/{next} {print}" "$1") \
        <(gawk "/^[[:space:]]*#|\/\/|<!--/{next} {print}" "$2")' _

# diff on distinct keys
p='^\('$(diff -Naurw \
        <(grep -o '^[^=]*' ~/f1) \
        <(grep -o '^[^=]*' ~/f2) | \
    awk '
        NR <= 3 || /^[^+-]/ {next}
        {if (a) {a = a "\\|"} a = a substr($0, 2, length($0) + 1)}
        END {print a}
    ')'\)' && \
diff -Naurw <(grep "$p" ~/f1) <(grep "$p" ~/f2)
```

## Sequences

### Filter out repeated k-line patterns in a plaintext stream

- [multi_line-uniq.sh](./captures/multi_line-uniq.sh)

Usage:

```bash
printf '%s\n' 1 2 1 2 3 3 4 | ./multi_line-uniq.sh
```

Output (single occurrences of '1 2' and '3'):

```
1
2
3
4
```

### Find longest k-repeating substrings in byte stream

- [lrs.py](./differences/lrs.py)

Input (hex dump of file):

```
00000000: 7071 a42f 7071 7071 6d14 0c69 96aa 191a  pq./pqpqm..i....
00000010: 1b1c 1d77 1e77 2122 2122 96aa 9ff3       ...w.w!"!"....
```

Output (longest 2-repeating substrings with count):

```
b'pq'
b'\x96\xaa'
b'!"'
3
```

Related work:

- https://pypi.org/project/textdistance/

References:

- https://en.wikipedia.org/wiki/Longest_repeated_substring_problem
- https://en.wikipedia.org/wiki/Gestalt_Pattern_Matching
- https://stackoverflow.com/questions/11090289/find-longest-repetitive-sequence-in-a-string

## Time Series

### Sort logs by timestamps, including lines without one

```bash
awk '
    timestamp {
        if(/^([0-9-]* [0-9,:]* ).*/) { print $0 }
        else { print timestamp $0 }
    }
    match($0, /^([0-9-]* [0-9,:]* ).*/, e) {
        timestamp=e[1]
    }
    NR==1 { print }
' *.log *.log.1 \
    | sort \
    | awk '{
        gsub("^[0-9-]*[[:space:]]*[0-9,:]*", "")
        if(!x[$0]++) { print }
    }' \
    | vim -
```

Alternatives: https://unix.stackexchange.com/questions/195604/matching-and-merging-lines-with-awk-printing-with-solaris
