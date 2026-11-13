echo proc_name:$1
proc_name=$1
pidin ar | grep $proc_name | grep -v grep | slay `awk '{print $1}'`