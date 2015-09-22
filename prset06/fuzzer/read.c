#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define CHUNKBYTES 1024
#define RATIO .004

#define MAGIC1 0x33ea84f7
#define MAGIC2 0x783bc31f
#define MAGIC3 0x9b5da2fb

static unsigned long seed = 0;

void ReadFile(char *name)
{
	FILE *file;
	char *buffer;
	unsigned long fileLen;
	int32_t random = 0;
	int random_nb = sizeof(random) * 8;
 
	file = fopen(name, "rb");
	if (!file)
	{
		fprintf(stderr, "Unable to open file %s", name);
		return;
	}
	
	fseek(file, 0, SEEK_END);
	fileLen=ftell(file);
	fseek(file, 0, SEEK_SET);

	buffer=(char *)malloc(fileLen+1);
	if (!buffer)
	{
		fprintf(stderr, "Memory error!");
                                fclose(file);
		return;
	}

	fread(buffer,1, fileLen, file );
	fclose(file);

	
        fuzz(buffer,fileLen);


	char filename_buf[] = "/tmp/mutant";
	printf("file is %s \n", filename_buf);

	file = fopen(filename_buf, "w");
	if (!file) {
		fprintf(stderr, "Unable to open file %s", filename_buf);
	}
	else {
		
		write_buffer(buffer, fileLen, file);
		fprintf(stdout, "Dumped to %s \n", filename_buf);
	}

	free(buffer);
}

void write_buffer(void *buffer, int size, FILE *file)
{
  int i;

  for(i = 0;i < size;++i)
     fprintf(file, "%c", ((char *)buffer)[i]);
}



// Copyrights for https://github.com/samhocevar/zzuf
// Code Adapted from zzuf source code,
// I tried to re-write it in python it got really slow
// I keep the randomization functions as it is, which seems the power of its strategy

static unsigned long c = 1;

void my_srand(uint32_t seed)
{
    c = (seed ^ 0x12345678);
}

uint32_t my_rand(uint32_t max)
{
    long hi = c / 12773L;
    long lo = c % 12773L;
    long x = 16807L * lo - 2836L * hi;
    if (x <= 0)
        x += 0x7fffffffL;
    return (c = x) % (unsigned long)max;
}


void fuzz(volatile uint8_t *buf, int64_t len)
{
   
    char data[CHUNKBYTES];
    int fuzz_strategy = 0;
    srand(seed);
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

            my_srand(chunkseed);

            memset(data, 0, CHUNKBYTES);

            
            int todo = (int)((RATIO * (8 * CHUNKBYTES) * 1000000.0
                                + my_rand(1000000)) / 1000000.0);
            while (todo--)
            {
                unsigned int idx = my_rand(CHUNKBYTES);
                uint8_t bit = (1 << my_rand(8));
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
}

main(int argc, char **argv) {
	if (argc > 1) { 
		char * endptr;
		long val = strtol(argv[1], &endptr, 10);
		seed  = val;
		printf("using seed : %u ", seed);
	} 
	/*for (seed = 0; seed < 4294967296; seed++) { 
	                printf("using seed : %u \n", seed);
			ReadFile("gpg_print.pdf");

	/}*/

	if (argc > 2) {
		ReadFile(argv[2]);
	} else { 
		ReadFile("gpg_print.pdf");    
	}
}


