// I spent most of the time working on the assignment, I only had 15 minutes to write this.
// I am updating README now.. I hope this is fine, I finshed everything on 6pm
## The model 

First, I've learned a lot in how how host-based IDS works, and understand more about system call monitoring. 
First thing I did is that I examined the strace output and in a regex tool, I came with a regular expression tha matches each function, and another one to match system calls with argumuents

The two RegEx I have used:
```
m =  re.findall(r'(\w+)\(.*', strace)
    
m = re.findall(r'(\w+)\(((".*?")|(NULL)|(\w+)|(0[xX][0-9a-fA-F]+)|(\d+))(,.*)?\)\s*=.*', strace)
```

Then I have wrote an algorithm that takes strace output file, and come up with a model that contains pair of system calls. I created around six strace files that produced by several kinds of passing arguments to the program prset03.  such as verify /file XX or cat /file... etc
 
In order to have merged pairs of sytem calls, I had to remove duplicate pairs for doing model coverage, and for the augmneted model, it was very complicated. I had to create a list of arugments for each unique pair of system calls, then from that list, I calculated the shortest common string to come up with a base value that can cover all possible values from the various runs of the program.
I also Included a way to produce a system call model without removing duplicates, which is used for the checker program when it get strace argument.


to run my script that generate the model:

 
```
python2 model/script.py -s
```

I used -s flag, because I used the same script in the checker.


## Mimicry attacks 

For model, without considering the arguments it will be possible to evade detection in this case. for example, if an attacker tried to execute read(), then the IDS has no clue on what the attacker is trying to read, and it could be a dangerous attempt of trying to read /etc/shadow for example.  Also, according to the paper about mimicry attacks, attackers could evade detection if the IDS does not look for passesd arguement. 


For Augmented model, it's more robust in a way it's cannot be evade by passing evil arguments such as trying to read a file that the program is not going to access in any possible legit run. The only exception I came across is that I find some library calls, after I did the prset01 execution, and my assumption here is that it's out of scope of the soundness that we difined. This excpetion made me think if an attacker can rely evade detection if we use model one (without arguments) or not. I assumed that this is off the scope and the attacker should be able to evade model one.

## Running samples

Note that I make checker.py executable...  
usage: ./checker.py /path/to/solution.json /path/to/checking.strace [-s "to show malice node"]
```
spatialisotope@prset03:~/prset03$ ./checker.py solution.json model/strace/exploit.strace -s    (I add -s flag to show extra)
{
    "syscall": "write", 
    "syscall_arg": "1", 
    "malicious": true, 
    "node": {
        "syscall_2_arg": "/bin//sh", 
        "syscall_2": "execve", 
        "syscall_1": "write", 
        "syscall_1_arg": "1"
    }
}
spatialisotope@prset03:~/prset03$ ./checker.py solution.json model/strace/exploit.strace 
{
    "syscall": "write", 
    "syscall_arg": "1", 
    "malicious": true
}

```



## The model generation:

```
spatialisotope@prset03:~/prset03$ python2 model/script.py -s

```


## Extra credit 

I spent a lot of time trying to write the algorithm that produces the FSA model, 

The algorithm, takes, several strace outputs as previos methods, but this time I had to deal with each system call rather than dealing with a pair of them.   Then for each system call, in a recursive storing of calls, I had to check to see if there is a system call that could be a successor so add them in a link.  The object oreientd models had helped me a lot to write the solution to this logical problem, although I never used python before other than some basics. But at the end I found python is very efficient and useful 


Sample:

```
"model_fsa": {
        "module": [
            {
                "syscall": "execve",
                "successors": null,
                "id": 0,
                "arg": "./prset03"
            },
            {
                "syscall": "brk",
                "successors": [
                    55,
                    56,
                    57,
                    58
                ],
                "id": 1,
                "arg": "0"
            },
            {
                "syscall": "access",
                "successors": [
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    27,
                    37
                ],
```


# Code for Objects used for mapping various different of nodes

```
class Node:
        def __init__(self, call_1, call_2):
                self.syscall_1 = call_1
                self.syscall_2 = call_2
        def __str__(self):

                return json.dumps(self.__dict__)

        def __eq__(self, other):
                return self.__dict__ == other.__dict__

class Augmented_node:
        def __init__(self, call_1, call_2,  arg_1, arg_2):
                self.syscall_1 = call_1
                self.syscall_2 = call_2
                self.syscall_1_arg  = arg_1
                self.syscall_2_arg = arg_2
        def __str__(self):
                return json.dumps(self.__dict__, sort_keys=True)

patialisotopedef __eq__(self, other):
                return self.__dict__ == other.__dict__

class FSA_node:
        def __init__(self, call,  arg, id=0):
                self.syscall = call
                self.arg = arg
                self.id = id
                self.successors = []
        def __str__(self):
                return str(self.__dict__)
                #return json.dumps(self.__dict__, sort_keys=True)

        def __eq__(self, other):
                return self.__dict__ == other.__dict__
        def check(self, other):
                return (self.syscall == other.syscall and self.arg == other.arg)

```
