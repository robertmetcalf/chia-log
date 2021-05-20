# Chia plotting and disk usage

This is an analysis of disk usage for Chia plotting when using one and two
temporary disks.

## Methodology

My goal was to observe temporary file use across phases 1-4 of the plot creation
process.

I cloned the [Chia Proof of Space](https://github.com/Chia-Network/chiapos)
repository and changed the source code to NOT remove temporary files after their
use. Each phase cleans up after itself.

## Caveats

1. Some files are `truncated`, meaning the contents of the file are remove while
   leaving the filename. Those files appear as having zero bytes. I did not
   change any `truncate` commands due to unknown secondary affects. Any file
   with zero bytes is not counted in my summary.

2. I presume a file is written and read once. If a file is read randomly then
   the amount of data would be less than what I observed.

## Analysis

I modified these source code files and commented out the `fs::remove()`
statements. Then I build the `ProofOfSpace` command.

* `src/plotter_disk.hpp`
* `src/sort_manager.hpp`

I created a plot file with this command.

```sh
$ ./ProofOfSpace -b 4096 -k 32 -r 4 -u 128 -t /media/temp001 -2 /media/temp002 -d /media/dest001
```

* -b 4096 - use 4,096 MB (4 GB) of memory
* -k 32 - plot size is 32, yielding a 101 GB final file
* -r 4 - use 4 threads in the first phase
* -u 128 - use 128 buckets, which affects how many files are read/written in
   each phase
* -t - read and write temporary files to an SSD
* -2 - read and write secondary files to an SSD
* -d - write the final file to a hard disk

After the plot was created I captured the files in the temporary (-t option),
secondary (-2 option), and destination (-d option) directories.

This is a summary of each phase and where files are read and written.

| Phase | Temp read | Temp write | Sec read | Sec write | Dest  |
| ----- | --------  | ---------- | -------- | --------- | ----- |
| 1     |           | write      |          |           |       |
| 2     | read      | write      |          |           |       |
| 3     | read      | write      |          |           |       |
| 4     | read      |            |          | write     |       |
| Copy  |           |            | read     |           | write |

Here is the same table, as above, with the amount of data read and written in
each phase to specific disks.

All numbers are in GB (gigabytes), where 1 (one) GB is `1024 * 1024 * 1024`.
Numbers are rounded to the nearest GB.

| Phase | Temp read | Temp write | Sec read | Sec write | Dest  | Total |
| ----- | --------  | ---------- | -------- | --------- | ----- | ----- |
| 1     |           | 476        |          |           |       | 476   |
| 2     | 476       | 164        |          |           |       | 640   |
| 3-1   | 164       | 244        |          |           |       | 408   |
| 3-2   | 244       | 167        |          |           |       | 411   |
| 4     | 167       |            |          | 101       |       | 268   |
| Copy  |           |            | 101      |           | 101   | 202   |
| TOTAL | 1,051     | 1,051      | 101      | 101       | 101   | 2,405 |

The temporary disk (the -t option) bears 91% of all temporary and secondary disk
activity. Which means that using 2 SSD disks as temp drives gains you very
little performance benefits while ensuring that the primary SSD will wear out
long before the secondary SSD (the -2 option) does.

## Alternate solution - 1

If the goal is to spread the read/write load equally over two disks then this
pattern is one alternative.

| Phase | Temp read | Temp write | Sec read | Sec write | Dest  | Total |
| ----- | --------  | ---------- | -------- | --------- | ----- | ----- |
| 1     |           | 476        |          |           |       | 476   |
| 2     | 476       | 164        |          |           |       | 640   |
| 3-1   | 164       |            |          | 244       |       | 408   |
| 3-2   |           |            | 244      | 167       |       | 411   |
| 4     |           |            | 167      | 101       |       | 268   |
| Copy  |           |            | 101      |           | 101   | 202   |
| TOTAL | 640       | 640        | 512      | 512       | 101   | 2,405 |

## Alternate solution - 2

We can optimize the 4th pass, and eliminate the final pass, while reducing the
disk workload by 202 GB.

Phase 4 reads the output from phase 3-2 and writes the final file to the
destination (-d option) disk.

| Phase | Temp read | Temp write | Sec read | Sec write | Dest  | Total |
| ----- | --------  | ---------- | -------- | --------- | ----- | ----- |
| 1     |           | 476        |          |           |       | 476   |
| 2     | 476       | 164        |          |           |       | 640   |
| 3-1   | 164       |            |          | 244       |       | 408   |
| 3-2   |           |            | 244      | 167       |       | 411   |
| 4     |           |            | 167      |           | 101   | 268   |
| Final |           |            |          |           |       |       |
| TOTAL | 640       | 640        | 411      | 411       | 101   | 2,203 |

The temporary disk has 61% of the disk activity and the secondary disk has the
remaining 39%. Flip the disk layout with each plot and you'll equalize the load.

## Bottom line

* There is almost no performance gain when using two temporary disks.
* The cost of a secondary SSD may be better spent on destination disks.
* You would need to replace the temporary SSD 10 times more often then the
  secondary SSD.

A better option would be a second SSD used as a temporary disk and splitting all
of your plot creations across temporary SSDs. For example:

```sh
# first plot uses SSD 1 of 2
$ plot create  -b 4096 -k 32 -r 4 -u 128 -t /media/temp001 -d /media/dest001

# second plot uses SSD 2 of 2
$ plot create  -b 4096 -k 32 -r 4 -u 128 -t /media/temp002 -d /media/dest001
```
