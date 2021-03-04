# Aggregables

Snippets and scripts to parse and manipulate data patterns. These are categorized by analysis task:

<!-- toc -->

- [Time Series](#time-series)
  * [Compare deviations of two time spans in logs, grouped by captured variables](#compare-deviations-of-two-time-spans-in-logs-grouped-by-captured-variables)
  * [Sort logs by timestamps, including non-timestamped lines](#sort-logs-by-timestamps-including-non-timestamped-lines)
- [Captures](#captures)
  * [Visualize co-occurrences](#visualize-co-occurrences)
  * [Histogram](#histogram)
  * [Line chart](#line-chart)
  * [Proximity search for two or more substrings](#proximity-search-for-two-or-more-substrings)
  * [Trace patterns while preserving full output](#trace-patterns-while-preserving-full-output)
- [Differences](#differences)
  * [Summarize distinct bytes in two files](#summarize-distinct-bytes-in-two-files)
  * [Trace changes in variables](#trace-changes-in-variables)
  * [Apply ignore filters to output](#apply-ignore-filters-to-output)
- [Sequences](#sequences)
  * [Summarize matched bytes in file](#summarize-matched-bytes-in-file)
  * [Filter out repeated k-line patterns in a plaintext stream](#filter-out-repeated-k-line-patterns-in-a-plaintext-stream)
  * [Find longest k-repeating substrings in byte stream](#find-longest-k-repeating-substrings-in-byte-stream)
  * [Colorize contiguous longest k-repeating substrings](#colorize-contiguous-longest-k-repeating-substrings)

<!-- tocstop -->

## Time Series

### Compare deviations of two time spans in logs, grouped by captured variables

- [measure_deviating_groups.py](./captures/log-observer/measure_deviating_groups.py)

Use cases:

- Analyzing logs where we are not certain of which variables to observe, but know a point in time to compare against (e.g. before an exception was thrown); Our assumption is that variables with higher deviation of values are more likely to be interesting to observe
    - e.g. to understand why an exception was thrown, if all requests across the full time span (i.e. all logged requests) use the verb `GET`, then the verb doesn't offer any clues; however, if the user making requests only appeares on the second time span and not on the first, maybe we should investigate what is special about that user session

Usage:

```bash
# Split time span at point where timestamps occurred after '1 week ago'
./measure_deviating_groups.py access.log.1 access.log.rules '1 week ago'
```

In this case, assuming the current date is "08/Aug/2020", log lines will be split into two sets for analysis:

```
set 1 | 109.169.248.247 - - [12/Dec/2015:18:25:11 +0100] "GET /administrator/ HTTP/1.1" [...]
      | [...]
      | 109.184.11.34 - - [12/Dec/2015:18:32:56 +0100] "GET /administrator/ HTTP/1.1" [...]
     ---
set 2 | 165.225.8.79 - - [06/Aug/2020:12:47:50 +0200] "GET /foo.com/cpg/displayimage.php?album=1&pos=40 HTTP/1.0" [...]
      | [...]
```

Variables (e.g. `ip`, `date`, `verb`...) are matched against regex patterns containing [named capture groups](https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups). For each variable, we identify values and count their occurrences.

Output (sorted by standard deviation of values and occurrences):

1. Low deviation: identical values or similar distribution of occurrences:

```
virtual_host (std_dev: 0.0)
        [(None, 9)]
        [(None, 5)]
---
request_method (std_dev: 0.0162962962962963)
        [('GET', 5), ('POST', 4)]
        [('GET', 4), ('POST', 1)]
[...]
```

2. High deviation: All values are distinct:

```
path (std_dev: 0.06666666666666667)
        [('/administrator/', 5), ('/administrator/index.php', 4)]
        [('/index.php?option=com_contact&view=contact&id=1', 2), ('/foo.com/cpg/displayimage.php?album=1&pos=40', 1), ('/', 1), ('/index.php?option=com_content&view=article&id=50&Itemid=56', 1)]
```

Caption (for each block):

|Line|Description|
|---:|:---|
|`1`|captured variable|
|`2`|time span 1, observed values and their occurrences|
|`3`|time span 2, observed values and their occurrences|

Related work:

- [The Path from Unstructured Logs to Observability - Honeycomb](https://www.honeycomb.io/wp-content/uploads/2019/08/From-Unstructured-Logs-to-Observability-Honeycomb.pdf)
    - [Explore with BubbleUp](https://docs.honeycomb.io/working-with-your-data/bubbleup/)

### Sort logs by timestamps, including non-timestamped lines

```bash
# Non-timestamped lines will use the last parsed timestamp
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

Alternatives:

- Using `getline` to merge non-timestamped lines - https://unix.stackexchange.com/questions/195604/matching-and-merging-lines-with-awk-printing-with-solaris

## Captures

### Visualize co-occurrences

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
|---:|:---|
|`O`|counts > max_counts / 2|
|`o`|counts > max_counts / 3|
|`u`|counts > max_counts / 4|
|`.`|counts > 0|

Alternatives: 

- 2D data: [matplotlib/heatmap.py](./captures/matplotlib/heatmap.py)
- 1D data shaped as 2D: [matplotlib/heatmap-sequence.py](./captures/matplotlib/heatmap-sequence.py)

Related work:

- [Wow! signal - Signal measurement - Wikipedia](https://en.wikipedia.org/wiki/Wow!_signal#Signal_measurement)
- [PAW: Physics Analysis Workstation - An Introductory Tutorial - CERN Document Server](https://cdsweb.cern.ch/record/2296392/files/paw.pdf)
    - 6.3 HBOOK batch as the first step of the analysis
- [charts \- Command\-line Unix ASCII\-based charting / plotting tool \- Stack Overflow](https://stackoverflow.com/questions/123378/command-line-unix-ascii-based-charting-plotting-tool)
- [GitHub \- Netflix/flamescope: FlameScope is a visualization tool for exploring different time ranges as Flame Graphs\.](https://github.com/Netflix/flamescope)

### Histogram

```awk
#!/usr/bin/awk -f

{
    out[$0]++
    total++
}
END {
    for (key in out) {
        h = ""
        max_h = 8 * out[key] / total
        for (i=0; i<max_h; i++) {
            h = h "="
        }
        printf "%16s | %8s %.2f | %s\n", out[key], h, (out[key] / total), key
    }
}
```

Usage:

```bash
printf '%s\n' 1 1 1 2 3 | histogram.awk
```

Output (occurrences, distribution, value):

```
3 |    ===== 0.60 | 1
1 |       == 0.20 | 2
1 |       == 0.20 | 3
```

Alternatives: 

- Single chart: [matplotlib/bar.py](./captures/matplotlib/bar.py)
    - Usage: `./bar.py 1.csv`
- Small multiple charts: [matplotlib/multiple_bar.py](./captures/matplotlib/multiple_bar.py)
    - Usage: `paste -d ',' 1.csv 3.csv 12.csv | ./multiple_bar.py`
    - Output: [pdf](./captures/matplotlib/output-multiple_bar.pdf)
    - Interpolates bar color to make value differences across multiple scales more explicit
    - Sorts by [Tukey's fences](https://en.wikipedia.org/wiki/Outlier#Tukey's_fences) and standard deviation for faster detection of anomalies
    - Outputs to pdf to handle large numbers of charts

Related work: 

- [GitHub \- bitly/data\_hacks: Command line utilities for data analysis](https://github.com/bitly/data_hacks)
- [GitHub \- wizzat/distribution: Short, simple, direct scripts for creating ASCII graphical histograms in the terminal\.](https://github.com/wizzat/distribution)
- [Edward Tufte forum: Sparkline theory and practice](http://www.edwardtufte.com/bboard/q-and-a-fetch-msg?msg_id=0001OR&topic_id=1)
    - [Wicked Cool Usage · holman/spark Wiki · GitHub](https://github.com/holman/spark/wiki/Wicked-Cool-Usage)

### Line chart

- [line.py](./captures/matplotlib/line.py)

Example (instruction trace of an executable):

- Source code: [loops.c](./sequences/loops.c)
  - This program takes the "else" branch in the first iteration, then the "if" branch in the remaining iterations. We can observe in the line chart that there are two blocks of repeated patterns, with the second block taking significantly more instructions.

```bash
# Generate trace file `instrace.loops.log`
~/opt/dynamorio/build/bin64/drrun \
  -c ~/opt/dynamorio/build/api/bin/libinstrace_x86_text.so \
  -- ./loops

# Filter out addresses from shared library modules
awk '
match($0, /^0x4[0-9a-f]+/) {
  print substr($0, RSTART, RLENGTH)
}
' instrace.loops.log \
  > instrace-filtered.loops.log

# Add csv header, 
# convert hex values to integers, 
# then format label values back to hex
cat \
  <(echo "foo") \
  <(python -c 'import sys; [print(int(x,16)) for x in sys.stdin.read().strip().split("\n")]' \
    < ../../sequences/instrace-filtered.loops.log) \
  | ./line.py --hex
```

Output: [image](./captures/matplotlib/line.png)

### Proximity search for two or more substrings

- [magrep.sh](./captures/magrep.sh)
- [magrep.py](./captures/magrep.py)

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

### Trace patterns while preserving full output

Example (matches `1`, flushing output on each match):

```bash
(echo 1 && sleep 1 && echo 1 && sleep 1 && echo 2) \
    | tee /tmp/a \
    | awk '/1/ {
        cmd = "date +%s%N"
        cmd | getline d
        close(cmd)
        print $0 " " d
        system("")
    }' \
    | tee /tmp/b
```

Alternatives:

- [GitHub \- cirruslabs/echelon: hierarchical progress bars in terminal on steroids](https://github.com/cirruslabs/echelon)

## Differences

### Summarize distinct bytes in two files

- [hexdiff.py](./differences/hexdiff.py)

Benchmarking:

```bash
# Given: 
# - CPU: Intel i5-4200U
# - RAM: 12GiB DDR3 1600 MT/s
# - Input: 2 files with size ~= 481M
seq 1 5 \
  | while read -r i; do \
    sudo sh -c 'free && sync && echo 3 > /proc/sys/vm/drop_caches && free' \
      && time ./hexdiff.py foo bar \
  done
# 21.2406 seconds = (24.555 + 19.692 + 19.115 + 23.204 + 19.637) / 5
```

Alternatives: GNU diffutils contains `cmp`, which outputs offsets and byte values in a byte-by-byte manner:

```
10  24 ^T    25 ^U
11  14 ^L    35 ^]
25  41 !    226 M-^V
26  42 "    252 M-*
27 226 M-^V  41 !
28 252 M-*   42 "
```

`hexdiff.py` adds context by outputting in unified diff format, uses hex values, and joins differences using [semantic cleanup](https://github.com/google/diff-match-patch/wiki/API#diff_cleanupsemanticdiffs--null):

```bash
./hexdiff.py test-bytes1 test-bytes2-added
```

```diff
--- test-bytes1
+++ test-bytes2-added
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

### Trace changes in variables

- [trace.py](./differences/trace.py)

Usage:

```bash
printf '%s\n' 'a 1' 'a 2' 'b 2' 'a 1' 'c 3' \
    | ./trace.py \
    | vim -c 'set ft=diff' -
```

Output (count of variable changes; variable; value):

```diff
-[0]       a: None
+[1]       a: 1
 [0]       b: None
 [0]       c: None
~~~
-[1]       a: 1
+[2]       a: 2
 [0]       b: None
 [0]       c: None
~~~
 [2]       a: 2
-[0]       b: None
+[1]       b: 2
 [0]       c: None
~~~
-[2]       a: 2
+[3]       a: 1
 [1]       b: 2
 [0]       c: None
~~~
 [3]       a: 1
 [1]       b: 2
-[0]       c: None
+[1]       c: 3
~~~
```

### Apply ignore filters to output

- [filterdiff.py](./differences/filterdiff.py)

Usage:

```bash
./filterdiff.py <(printf '%s\n' '([0-9]+)') test1-text1-filterdiff test1-text2-filterdiff
```

Output (Includes filtered value `123` from first file as context, not as difference):

```diff
--- base
+++ derivative
@@ -1,4 +1,4 @@
 apple
 banana 123
 orange
-papaia
+pear
```

Compare with `diff -u test1-text1-filterdiff test1-text2-filterdiff`:

```diff
--- test1-text1-filterdiff
+++ test1-text2-filterdiff
@@ -1,4 +1,4 @@
 apple
-banana 123
+banana 456
 orange
-papaia
+pear
```

Example (`strace` diff):

Consider the following diff between 2 programs:

```diff
--- loops.c
+++ loops.with_access.c
@@ -1,5 +1,6 @@
 #include "stdio.h"
 #include "stdlib.h"
+#include "unistd.h"

 void output(char *msg) { printf("%s\n", msg); }

@@ -16,5 +17,6 @@
             }
         }
     }
+    access("/tmp/1", F_OK);
     printf("%d", k);
 }
```

Usage (filtering out any hex or decimal numbers):

```bash
./filterdiff.py \
  <(printf '%s\n' '((0x[0-9a-f]+)|([0-9]+))') \
  <(strace ./loops 2>&1 | sort -u) \
  <(strace ./loops.with_access 2>&1 | sort -u)
```

Output:

```diff
--- base
+++ derivative
@@ -1,12 +1,13 @@
 28) = 304
 access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
+access("/tmp/1", F_OK)                  = 0
 arch_prctl(0x3001 /* ARCH_??? */, 0x7fff943f5cc0) = -1 EINVAL (Invalid argument)
 arch_prctl(ARCH_SET_FS, 0x7fb1cd9e9540) = 0
 brk(0x118b000)                          = 0x118b000
 brk(NULL)                               = 0x116a000
 brk(NULL)                               = 0x118b000
 close(3)                                = 0
-execve("./loops", ["./loops"], 0x7fff3350eb00 /* 119 vars */) = 0
+execve("./loops.with_access", ["./loops.with_access"], 0x7ffcfe61feb0 /* 119 vars */) = 0
 +++ exited with 0 +++
 exit_group(0)                           = ?
 fstat(1, {st_mode=S_IFIFO|0600, st_size=0, ...}) = 0
```

Compare with `diff -u <(strace ./loops 2>&1 | sort -u) <(strace ./loops.with_access 2>&1 | sort -u)`:

```diff
--- /proc/self/fd/11	2021-03-04 09:00:58.068761187 +0000
+++ /proc/self/fd/13	2021-03-04 09:00:58.069761198 +0000
@@ -1,29 +1,30 @@
 28) = 304
 access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
-arch_prctl(0x3001 /* ARCH_??? */, 0x7ffc5e62e920) = -1 EINVAL (Invalid argument)
-arch_prctl(ARCH_SET_FS, 0x7f76fbd8b540) = 0
-brk(0xdd7000)                           = 0xdd7000
-brk(NULL)                               = 0xdb6000
-brk(NULL)                               = 0xdd7000
+access("/tmp/1", F_OK)                  = 0
+arch_prctl(0x3001 /* ARCH_??? */, 0x7ffe11326df0) = -1 EINVAL (Invalid argument)
+arch_prctl(ARCH_SET_FS, 0x7f0aa1ec1540) = 0
+brk(0x1b4b000)                          = 0x1b4b000
+brk(NULL)                               = 0x1b2a000
+brk(NULL)                               = 0x1b4b000
 close(3)                                = 0
-execve("./loops", ["./loops"], 0x7ffc4a29ea20 /* 119 vars */) = 0
+execve("./loops.with_access", ["./loops.with_access"], 0x7ffe745a6fc0 /* 119 vars */) = 0
 +++ exited with 0 +++
 exit_group(0)                           = ?
 fstat(1, {st_mode=S_IFIFO|0600, st_size=0, ...}) = 0
 fstat(3, {st_mode=S_IFREG|0644, st_size=301428, ...}) = 0
 fstat(3, {st_mode=S_IFREG|0755, st_size=3183216, ...}) = 0
 if
-mmap(0x7f76fbbe5000, 1376256, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x25000) = 0x7f76fbbe5000
-mmap(0x7f76fbd35000, 307200, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x175000) = 0x7f76fbd35000
-mmap(0x7f76fbd80000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1bf000) = 0x7f76fbd80000
-mmap(0x7f76fbd86000, 13160, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f76fbd86000
-mmap(NULL, 1872744, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f76fbbc0000
-mmap(NULL, 301428, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f76fbd8c000
-mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f76fbd8a000
+mmap(0x7f0aa1d1b000, 1376256, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x25000) = 0x7f0aa1d1b000
+mmap(0x7f0aa1e6b000, 307200, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x175000) = 0x7f0aa1e6b000
+mmap(0x7f0aa1eb6000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1bf000) = 0x7f0aa1eb6000
+mmap(0x7f0aa1ebc000, 13160, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f0aa1ebc000
+mmap(NULL, 1872744, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f0aa1cf6000
+mmap(NULL, 301428, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f0aa1ec2000
+mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f0aa1ec0000
 mprotect(0x403000, 4096, PROT_READ)     = 0
-mprotect(0x7f76fbd80000, 12288, PROT_READ) = 0
-mprotect(0x7f76fbe02000, 4096, PROT_READ) = 0
-munmap(0x7f76fbd8c000, 301428)          = 0
+mprotect(0x7f0aa1eb6000, 12288, PROT_READ) = 0
+mprotect(0x7f0aa1f38000, 4096, PROT_READ) = 0
+munmap(0x7f0aa1ec2000, 301428)          = 0
 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
 openat(AT_FDCWD, "/lib64/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
 pread64(3, "\4\0\0\0 \0\0\0\5\0\0\0GNU\0\1\0\0\300\4\0\0\0\330\1\0\0\0\0\0\0"..., 48, 848) = 48
```

## Sequences

### Summarize matched bytes in file

- [hexmatch.py](./sequences/hexmatch.py)

Usage:

```bash
# hex encoded
./hexmatch.py <(printf '%s\n' foo bar) 6f

# literal
./hexmatch.py <(printf '%s\n' foo bar) $(printf '%s' o | xxd -p)

# little-endian
hexmatch.py <(printf '%s\n' DCBA) $(printf '%s' BC | xxd -p) -e le                                 

# up to off-by-2 values
hexmatch.py <(printf '%s\n' AAA BBB ZZZ) $(printf '%s' C | xxd -p) -k 2
```

Output (`0x[...]`: offset in hex, `e`: endianess, `k`: off-by-k, `b'[...]'`: matched bytes):

```
# hex encoded / literal
/proc/self/fd/11:1(0x1):b'o'
/proc/self/fd/11:2(0x2):b'o'

# little-endian
/proc/self/fd/11:1(0x1):e=le,k=0:4342 b'CB'

# up to off-by-2 values
/proc/self/fd/11:0(0x0):e=be,k=-2:41 b'A'
/proc/self/fd/11:1(0x1):e=be,k=-2:41 b'A'
/proc/self/fd/11:2(0x2):e=be,k=-2:41 b'A'
/proc/self/fd/11:4(0x4):e=be,k=-1:42 b'B'
/proc/self/fd/11:5(0x5):e=be,k=-1:42 b'B'
/proc/self/fd/11:6(0x6):e=be,k=-1:42 b'B'
```

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

Output (longest 2-repeating substrings with total count):

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

### Colorize contiguous longest k-repeating substrings

Usage:

```bash
printf '%s\n' 00 111 12 13 111 12 13 14 | ./repeated-sum.py
```

Output (count of contiguous occurrences in `[...]` + single substring):

```
            00
colorized | [2]
          | 111
          | 12
          | 13
            14
```

# TODO

- Sequence Alignment
    - https://campuspress.yale.edu/knightlab/ruddle/plotreads/
