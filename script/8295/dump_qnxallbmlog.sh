#v1.0 

#tt=$(date +%Y%m%d%H%M%S)
tt=dump_qnxallbmlog
logdir=/var/$tt
echo $logdir
rm -rf $logdir
mkdir -p $logdir

#date +%y%m%d%H%M%S > $logfile
dumpsys() 
{
	touch $logdir/system.txt
	date +%Y%m%d%H%M%S >> $logdir/system.txt
	echo "------dump pid-------"
	echo "------dump pid-------" >> $logdir/system.txt
	pidin ar >> $logdir/system.txt 2>&1
	echo "------dump threads-------" >> $logdir/system.txt
	pidin threads >> $logdir/system.txt 2>&1
	echo "------dump cpu-------"
	echo "------dump cpu-------" >> $logdir/system.txt
	hogs -s 1 -% 1c -i 5 >> $logdir/system.txt 2>&1
	echo "------dump memory-------"
	echo "------dump memory-------" >> $logdir/system.txt
	cd /
	showmem -s >> $logdir/system.txt 2>&1
}

dumpdisk()
{
	touch $logdir/disk.txt
	echo "------dump mount-------"
	echo "------dump mount-------" >> $logdir/disk.txt
	mount >> $logdir/disk.txt 2>&1
	echo "------dump disk-------"
	echo "------dump disk-------" >> $logdir/disk.txt
	df -h >> $logdir/disk.txt 2>&1	
} 

dumpslog()
{
	echo "------dump slog---------"
	slog2info >> $logdir/slog2info.txt 2>&1
}

dump_bmlog()
{
	echo "------dump bmlog--------"
	cd /var
	tar cvf bmlog.tar /var/bmlog
}

dump_core()
{
	echo "------dump coreinfo-------"
	touch $logdir/coreinfo.txt
	
	echo "------dump coreinfo-------" >> $logdir/coreinfo.txt
	cd /var/log/
	ls -l >> $logdir/coreinfo.txt 2>&1
	cat /dev/shmem/lv_gvm.txt $logdir/lv_gvm.txt >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*lv_gvm.txt $logdir/ >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*.core $logdir/  >> $logdir/coreinfo.txt 2>&1
}

execute_cmd()
{
    echo "$1" >> $2
    $1 >> $2 2>&1
}


rm /var/dump_finish

dumpsys
dumpdisk
dumpslog
dump_bmlog
dump_core


cd /var
rm $tt.tar.gz
tar zcvf $tt.tar.gz ./$tt
rm -rf ./$tt
touch /var/dump_finish
