
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process
import threading
import json
from time import sleep, time
import os, sys
import gc 

class SampleStrace:
	
	
	def _readerthread(self, fh, buffer):
            buffer.append(fh.read())

	def _communicate(self,p=None, input=None):
	    if p == None:
	    	p = self.process

            stdout = None # Return
            stderr = None # Return
            if p.stdout:
                stdout = []
                stdout_thread = threading.Thread(target=self._readerthread,
                                                 args=(p.stdout, stdout))
                stdout_thread.setDaemon(True)
                stdout_thread.start()
            if p.stderr:
                stderr = []
                stderr_thread = threading.Thread(target=self._readerthread,
                                                 args=(p.stderr, stderr))
                stderr_thread.setDaemon(True)
                stderr_thread.start()

            if p.stdin:
                if input is not None:
                    p.stdin.write(input)
                p.stdin.close()
	    
            
            if p.stdout:
                stdout_thread.join(timeout=2)
            if p.stderr:
                stderr_thread.join(timeout=2)
            
	    if stderr_thread.isAlive() or stdout_thread.isAlive():
		print "[Killed.."
		p.terminate()
		p.kill()
		return ('Process Terminated', 'Process Terminated')
             
            # All data exchanged.  Translate lists into strings.
            if stdout is not None :
                stdout = stdout[0]
            if stderr is not None:
                stderr = stderr[0]

            return (stdout, stderr)



	def __init__(self, id, args=[], path='../samples'):
		self.path = path
		self.id = id
		self.process= None
		self.file = self.path + '/' + self.id
		self.cmd = ['strace', '-o', '../strace/'+ self.id+ '.out_strace'  , self.file ]
		self.cmd.extend(args)
		print self.cmd
		self.process = Popen(self.cmd, stderr=PIPE, stdin=PIPE, stdout=PIPE)
		self._communicate()


samples = json.loads(open('samples.json','r').read())


if len(sys.argv) > 1:
	num = int(sys.argv[1])
	sample = samples['samples'][num]
	if len(sys.argv) > 2:
		print sample
		exit()

	sampleRun =  SampleStrace(sample['path'], sample['args'])
	exit()

def RunProcess(sample):
        sampleRun =  SampleStrace(sample['path'], sample['args'])


for x in range(len(samples['samples'])):
        sample = samples['samples'][x]
	p = Process(target=RunProcess, args=(sample,))
	p.start()
	p.join()
	

