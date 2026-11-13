#v1.0 

#tt=$(date +%Y%m%d%H%M%S)
tt=dump_camera
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

dumpslog()
{
	echo "------dump slog---------"
	slog2info >> $logdir/slog2info.txt 2>&1
}

dump_bmlog()
{
	echo "------dump bmlog--------"
	local max=0
	local second=0
	if [ -d "/var/bmlog/" ]; then
		cd /var/bmlog/
		for num in $(ls)
		do
		  if ((${num} > ${max})); then
		    second=${max}
			max=${num}
		  fi
		done
		#echo logdir $logdir
		cp -r /var/bmlog/$max $logdir/
		cp -r /var/bmlog/$second $logdir/
	else
		echo "find bmlog error"
	fi
}

dump_core()
{
	echo "------dump coreinfo-------"
	touch $logdir/coreinfo.txt
	
	echo "------dump coreinfo-------" >> $logdir/coreinfo.txt
	cd /var/log/
	ls -l >> $logdir/coreinfo.txt 2>&1
	cp /dev/shmem/lv_gvm.txt $logdir/ >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*_lv_gvm.txt $logdir/ >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*.core $logdir/  >> $logdir/coreinfo.txt 2>&1
}

execute_cmd()
{
    echo "$1" >> $2
    $1 >> $2 2>&1
}

dump_camera()
{	
	echo "------dump camera-------"
	local output_file=$logdir/camera.txt
	touch output_file
	echo "pin=====" >> $output_file 2>&1
	execute_cmd "msmgpiotool info 168" "$output_file"
	
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x0 8 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0xd 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x26 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x38 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x8 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0xc " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x10 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x18 14 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x28 10 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x50 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x112 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1fc" "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x21c" "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x115 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x118 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x11a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x11c " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x124 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x127 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x12a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x12c " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x12e " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x160 3 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x302 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x308 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x30b 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x312 23 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x330 7 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x339 13 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x312 23 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x40a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x4Ca " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x441 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x450 40 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x44a 6 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x481 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x490 40 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x48a 6 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x510 16 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x520 16 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x55c 4 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x568 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x570 3 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x575 5 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1403 5 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x140a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1418  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1421  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1423  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1431  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1445 3 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1464  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1470 6 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x148c  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1495  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1498  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x14a4 5 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x14ac 2" "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1503 5 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x150a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1518  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1521  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1523  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1531  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1545 3 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1564  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1570 6 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x158c  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1595  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1598  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x15a4 5 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x15ac 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1c00  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1c03  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1c07 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1c0a  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1d00  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1d03  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1d07 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1d0a  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1e00  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1e03  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1e07 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1e0a  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1f00  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1f03  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1f07 2 " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x1f0a " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x2000 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x2008 20  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x2100 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x2108 20  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5009 5  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5018  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5024 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x501a 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5020 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5028 5  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5030 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5060 2  " "$output_file"
	execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 0x5063 2  " "$output_file"
}

dump_pic()
{
	echo "------dump camera pic-------"
	local output_file=$logdir/camera.txt
	mkdir -p $logdir/pic
	rm -rf /tmp/frame* >> $output_file 2>&1
	echo "------dump camera pic1-------"
	/mnt/bin/camera/qcarcam_test/qcarcam_test -config=/mnt/bin/camera/qcarcam_test/12cam.xml -dumpFrame=100 -seconds=20 >> $output_file 2>&1
	cp /tmp/frame* $logdir/pic/ >> /var/camera_diag.log 2>&1
	rm -rf /tmp/frame* >> $output_file 2>&1
}

dump_all()
{
	echo "------dump camera all-------"
	local output_file=$logdir/camera_all.txt
	touch output_file
	echo "ALL Regsisters : " >> $output_file 2>&1
	sum=0
	while [ $sum -le 65535 ]
	do
		execute_cmd "/mnt/bin/camera/ccidbgr /dev/cci2 0x28 read21 $sum" "$output_file"
		let sum=$sum+1
	done
}

rm /var/dump_finish

dump_pic
dump_camera
dumpsys
dumpslog
dump_bmlog
dump_core



if [[ $1 == "-enable_allregs" ]]; then
dump_all
fi



cd /var
rm $tt.tar.gz
tar zcvf $tt.tar.gz ./$tt
rm -rf ./$tt
touch /var/dump_finish
