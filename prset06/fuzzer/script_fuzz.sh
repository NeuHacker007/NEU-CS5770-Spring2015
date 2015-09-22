  #!/bin/bash

for line in $(cat coredump_log) ;  do

if [[ $line =~ ^core.*$ ]]; then

echo $line; 

  binary="pdftotext"
  core="$line"
 
  gdb $binary -batch \
      -ex "set pagination off" \
      -ex "printf \"**\n** Process info for $binimg - $core \n** Generated `date`\n\"" \
      -ex "core-file $core " \
      -ex "bt" \
      -ex "printf \"*\n* Done \n*\n\"" \
      -ex "quit" 

fi
done
