
# Intro

The intent of this assignment is to develop a fuzzer tool that takes two arguments:
	- configuration value, i.e. seed used for randomization (unisigned 32 bit number)
	- input file  [gpg_print.pdf]
Then perform mutaitonal fuzzing using that input file and test them on a vulnerable program (pdftotext), and whenever there is a crash we record the used configuration value so we analyze the core file later and cluster the generated core files. 


# The fuzzer

I was first as I mentioned before for you trying to come up with my own implementation but after I wrote the program which pretty much use some functions from zzuf. The source code of zzuf was really complicated and I didnot include pure files of that source code, rather, I only copied three functions:
 - srand,   rand,  and fuzz.  Srand and rand are pretty much the same as the standard library but for somereason this shows better results.
 - fuzz, has all the logic to do the mutational fuzzing on a buffer, however it was pretty advanced that it uses another factor called pos, where zzuf allowed you to do some fuzzing to a certain offset (like videos or something) and I really edit it a lot to match what i need
 - after that I tried to do it on python using the same logic, but the results was so sloooow .. and even i created another simple one using python it was really slow.. so I decided to keep this as I also had crashed the VM before and resulted in some delay in my work (pretty much one night couldnt access it).


# My python attempt

```
!/usr/bin/env python
#coding=utf8

import sys, subprocess, string, time, random
from  math import floor
from random import randrange

log = open('log', 'w')
input_file = 'gpg_print.pdf'
output_filename = 'fuzz_output'
input_seed = int(sys.argv[1])
ratio = 0.04



M1 =0x3eaa84f7
M1 =0x783bc31f
M2 =0x9b5da2fb
CHUNKBYTES = 1024

for test in range (1000):
	random.seed(input_seed) 
	output_file = open(output_filename, 'wb') 

	
	buf = bytearray(open(input_file, 'rb').read())
	

	# trying to implement zzuf, but got so slow
	#loop_range = int((len(buf)+CHUNKBYTES -1) / CHUNKBYTES)
	
	#for i in range(loop_range):
	

		## Creating zzuf bit mask
		#bitmask = [0] * CHUNKBYTES
		#todo = int((ratio * (8 * CHUNKBYTES) * 1000000.0 + randrange(1000000)) / 1000000.0);
	
		#while todo > 0 :
		#	index= randrange(CHUNKBYTES);
                #	bit = (1 << randrange(8))
                #	bitmask[index] ^= bit;
		#	todo -= 1
		


		#start_offset = (i * CHUNKBYTES)
		#stop_offset  = (i + 1) * CHUNKBYTES 
		
		#if (stop_offset > len(buf)) : 
		#	stop_offset = len(buf)
		
		#for j in range(start_offset, stop_offset):
		#	byte = buf[j]
		#	fuzzbyte = bitmask[j % CHUNKBYTES]
		#	byte ^= fuzzbyte
                

	

	nb = int(floor(len(buf)*ratio))
	
	for j in range(nb):
		byte = random.randrange(256)	
		index = random.randrange(len(buf))
		buf[index] ^= byte
	
	output_file.write(buf)
	output_file.close()
	
	p = subprocess.Popen(['pdftotext', output_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	
	print p.returncode
	if p.returncode < 0 :
		if (p.returncode == -6):
			print "Process dumped core ", p.pid
		#print p.returncode
	else :
		print "Process OK"
	
	

log.close()

```

The commented part was trying to do zzuf strategy it was very slow and not efficent
The other part was really trying to to random flipping of bits but did not work .

I am only showing this because I understand what you have told me about plaigraism and its not my intent to just copy available source codes. I also tried to do it on completely from scratch. But The one I did is using C and it is working

```
fuzz_strategy =  (int) rand() % 3;

	printf("using strategy %d \n", fuzz_strategy);

	int64_t i;

	for (i = 0; i < ( len + CHUNKBYTES - 1) / CHUNKBYTES; i++) {

		
		uint32_t chunkseed;
		chunkseed = (uint32_t)i;
		chunkseed ^= MAGIC2;
		chunkseed += (uint32_t)(RATIO * MAGIC1);
		chunkseed ^= seed;
		chunkseed += (uint32_t)(i * MAGIC3);

		zzuf_srand(chunkseed);

		memset(data, 0, CHUNKBYTES);

		int todo = (int)((RATIO * (8 * CHUNKBYTES) * 1000000.0
					+ zzuf_rand(1000000)) / 1000000.0);
		while (todo--)
		{
			unsigned int idx = zzuf_rand(CHUNKBYTES);
			uint8_t bit = (1 << zzuf_rand(8));
			data[idx] ^= bit;
		}

		int64_t start =  i * CHUNKBYTES;
		int64_t stop = ((i + 1) * CHUNKBYTES <  len) ? (i + 1) * CHUNKBYTES : len;

		int64_t j;
		for ( j = start; j < stop; ++j)
		{
			uint8_t byte, fuzzbyte;

			byte = buf[j];
			fuzzbyte = data[j % CHUNKBYTES];

			if (!fuzzbyte)
				continue;

			switch (fuzz_strategy)
			{
				case 1:
					byte ^= fuzzbyte;
					break;
				case 2:
					byte |= fuzzbyte;
					break;
				case 0:
					byte &= ~fuzzbyte;
					break;
			}

			buf[j] = byte;
		}



	}	

```

- So basically we use the configuratration value so the randomized values gets always the same when we pass the configuration value to the program, 
But at the generation loop, i was using random generation of these configuration values, but when it crashes i record the `ppid` and `configuration seed value`



# Clustring 
After that I check on the log file called `coredump_log` then it has like this:

```
core.1725 		 /tmp/mutant/1438178333 
core.1728 		 /tmp/mutant/1438228754 
core.1791 		 /tmp/mutant/1438497666 
core.1868 		 /tmp/mutant/1437808579 
core.1874 		 /tmp/mutant/1437976649 
core.1948 		 /tmp/mutant/1437321176 
core.2120 		 /tmp/mutant/1440228787 
core.2591 		 /tmp/mutant/1434127846 
core.3462 		 /tmp/mutant/1592234131 
core.3510 		 /tmp/mutant/1592503043 
core.3528 		 /tmp/mutant/1595696373 
```

Then using a shell script, parsing each line and calling `gdb` with the `-batch` option, I am able to parse all of these core files, and with extra filtering I am able to cluster them based on the return value 

So an example that I did is a simple grep "#0" 
```
spatialisotope@prset06:~/prset06/fuzzer$ ./script_fuzz.sh | grep "#0"
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
#0  0x00007ffff7acc75b in XRef::getNumEntry(long long) () from /usr/lib/x86_64-linux-gnu/libpoppler.so.44
```

I only found a one generated bug, I am not sure. 

# To run my fuzzer

I could not do it on a script so I made a compile script for you

```
./compile
./fuzz 1595696373 gpg_print.pdf


spatialisotope@prset06:~/prset06/fuzzer$ ./fuzz 11112223 gpg_print.pdf 
using seed : 11112223 using strategy 2 
file is /tmp/mutant 
Dumped to /tmp/mutant 
Syntax Warning: May not be a PDF file (continuing anyway)
Syntax Error (3958283): Bad 'Length' attribute in stream
Segmentation fault
spatialisotope@prset06:~/prset06/fuzzer$ 

```

# Logs

The log folder show results of my fuzzer for longer periods of time, so the submission solution file was only a subset of what I have found.

Thank you


