#!/bin/sh
#v1.0



# v1.4 添加mcu (tcon) 状态寄存器
# v1.5 添加display apb寄存器
# v1.6 添加bmetrics
# v1.7 修正bug
# v1.8 dump_8295DPReg for ZXDP-1495
# v1.9 add pmic 
#tt=$(date +%Y%m%d%H%M%S)
tt=diag_display
logdir=/var/$tt
echo $logdir
rm -rf $logdir
mkdir -p $logdir


A1_display()
{
	gles2-gears_screen -display=1
}

A2_display()
{	
	touch $logdir/glesA.txt
	gles2-gears_screen -display=2 >> $logdir/glesA.txt 2>&1
}

B_display()
{
    touch $logdir/glesB.txt
	gles2-gears_screen -display=3 >> $logdir/glesB.txt 2>&1
}

C_display()
{
	touch $logdir/glesC.txt
	gles2-gears_screen -display=4 >> $logdir/glesC.txt 2>&1
}

dumpcpu()
{
	touch $logdir/cpu.txt
	echo "------dump cpu-------"
	echo "------dump cpu-------" >> $logdir/cpu.txt
	hogs -s 1 -% 1c -i 5 >> $logdir/cpu.txt 2>&1
}

#date +%y%m%d%H%M%S > $logfile
dumpsys() 
{
	local output_file=$logdir/system.txt
	touch $output_file
	
	date +%Y%m%d%H%M%S >> $output_file
	echo "------dump pid-------"
	echo "------dump pid-------" >> $output_file
	pidin ar >> $output_file 2>&1
	echo "------dump threads-------" >> $output_file
	pidin threads >> $output_file 2>&1
	echo "------dump memory-------"
	echo "------dump memory-------" >> $output_file
	cd /
	showmem -s >> $output_file 2>&1
	echo "------dump start-------"
	echo "------dump start-------" >> $output_file
	cat /dev/bmetrics >> $output_file 2>&1
	echo "------dump pmic-------"
	echo "------dump pmic-------" >> $output_file
	PMICINDEX=8 pmicgpiotool read 10 >> $output_file 2>&1
	msmgpiotool dump >> $output_file 2>&1
	
	echo "------dump zone_config-------"
	echo "------dump zone_config-------" >> $output_file 2>&1
	zone_config -s >> $output_file 2>&1
	ls -l /ifs/lib64 | grep graphics.conf >> $output_file 2>&1
	ls -l /ifs/bin/ | grep qcdisplaycfg >> $output_file 2>&1
	
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
	slog2info >> $logdir/slog2info.txt 2>&1 &
	openwfd0=$(pidin ar | grep "openwfd_server -i 0 -U 70:70,33,21" | grep -v grep | awk '{print $1}')
	slog2info -l /dev/shmem/slogger2/zone_qnxslog.$openwfd0 >> $logdir/$openwfd0.txt 2>&1
	openwfd1=$(pidin ar | grep "openwfd_server -i 1 -U 70:70,33,21" | grep -v grep | awk '{print $1}')
	slog2info -l /dev/shmem/slogger2/zone_qnxslog.$openwfd1 >> $logdir/$openwfd1.txt 2>&1
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
		echo $max-$second
		#cp -r /var/bmlog/$max $logdir/
		tar cvf $logdir/$max.tar /var/bmlog/$max
		#cp -r /var/bmlog/$second $logdir/
		tar cvf $logdir/$second.tar /var/bmlog/$second
	else
		echo "find bmlog error"
	fi
}

dump_core()
{
	echo "------dump coreinfo-------"
	touch $logdir/coreinfo.txt
	core_info=$(pidin ar | grep generate_guestdump.sh | grep -v grep)
	if [ -z $core_info]; then
		echo $core_info
	else 
		echo "generate_guestdump now please use pull_gcore.bat"
    fi
	
	echo "------dump coreinfo-------" >> $logdir/coreinfo.txt
	cd /var/log/
	ls -l >> $logdir/coreinfo.txt 2>&1
	cp /dev/shmem/lv_gvm.txt $logdir/ >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*lv_gvm.txt $logdir/ >> $logdir/coreinfo.txt 2>&1
	cp /var/log/*.core $logdir/  >> $logdir/coreinfo.txt 2>&1
#	cp /var/log/lv_guestdump.gcore.gz $logdir/ >> $logdir/coreinfo.txt 2>&1
}

dump_picA() 
{
    echo "---dump A pic-----"

	
	echo surfacedump=0xff 1 > /dev/displaylog0
	mkdir -p $logdir/picA
	local output_file=$logdir/picA/dump.txt
	touch $output_file	
	cp /tmp/displog_surface_dump_* $logdir/picA/ >> $output_file 2>&1
	rm /tmp/displog_surface_dump_*
}

dump_picBC() 
{
    echo "---dump BC pic-----"
	echo surfacedump=0xff 1 > /dev/displaylog1
	mkdir $logdir/picBC
	local output_file=$logdir/picBC/dump.txt
	touch $output_file	
	cp /tmp/displog_surface_dump_* $logdir/picBC/ >> $output_file 2>&1
	rm /tmp/displog_surface_dump_*	
}

execute_cmd()
{
    echo "$1" >> $2
    $1 >> $2 2>&1
}

dump_DisplayA() 
{
	echo "------dump displayA info--------"
	local output_file=$logdir/displayA.txt
	touch $output_file
	
	# mcu=0x13 981=0xc 984=0x30 
	i2cdbgr -D /dev/i2c4 -d >> $output_file 2>&1
	
	#a屏的mcu版本
	echo "mcu version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -r  -o 0x40 -i 4 -b 1" "$output_file"
	
	#A屏MCU状态检测
	echo "mcu state=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0x0A -i 1 -r" "$output_file"
	echo "tcon error=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0x0B -i 1 -r" "$output_file"
	echo "tcon detail=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0xF8 -i 1 -r" "$output_file"
	
	#a屏tcon版本
	echo "tcon version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -r  -o 0xfe -i 1 -b 1" "$output_file"
	
	echo "hardware version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0x70 -i 4 -r" "$output_file"
	
	#TI981 硬件pin确认(1.8V、1.15V、PWDB、LOCK) $output_file 2>&1
	echo "pin(1.8V、1.15V、PWDB、LOCK)=====" >> $output_file 2>&1
	execute_cmd "msmgpiotool info 106" "$output_file"
	execute_cmd "msmgpiotool info 105" "$output_file"
	execute_cmd "msmgpiotool info 169" "$output_file"
	execute_cmd "msmgpiotool info 38" "$output_file"

	#backlight
	echo "backlight=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0x05 -i 1 -r"  "$output_file"
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x13 -o 0x02 -i 1 -r"  "$output_file"
	
	cp /tmp/display_a_dtc  $logdir/ >> $output_file 2>&1
	cp /tmp/displayA_monitor.txt $logdir/ >> $output_file 2>&1
}


dump_DisplayBC() 
{
	echo "------dump displayBC info--------"
	local output_file=$logdir/displayBC.txt
	touch $output_file
	
	# 983=0c 988=0x38 Bmcu=0x14 Cmcu=0x15
	i2cdbgr -D /dev/i2c9 -d >> $output_file 2>&1
	
	# b屏mcu版本
	echo "B mcu version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x14 -r  -o 0x40 -i 4 -b 1" "$output_file"

	# c屏mcu版本
	echo "C mcu version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x15 -r  -o 0x40 -i 4 -b 1" "$output_file"

	echo "B hardware version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x14 -o 0x70 -i 4 -r" "$output_file"
	
	echo "C hardware version=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c4 -s 0x15 -o 0x70 -i 4 -r" "$output_file"	

	#B屏MCU状态检测
	echo "B mcu state=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x14 -o 0x0A -i 1 -r" "$output_file"
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x14 -o 0x0B -i 1 -r" "$output_file"

	#C屏MCU状态检测
	echo "C mcu state=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x15 -o 0x0A -i 1 -r" "$output_file"
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x15 -o 0x0B -i 1 -r" "$output_file"	
	
	#TI983 硬件pin确认(1.8V、1.15V、PWDB、LOCK0、LOCK1)
	echo "pin (1.8V、1.15V、PWDB、LOCK)=====" >> $output_file 2>&1
	execute_cmd "msmgpiotool info 107" "$output_file"
	execute_cmd "msmgpiotool info 108" "$output_file"
	execute_cmd "msmgpiotool info 153" "$output_file"
	execute_cmd "msmgpiotool info 68" "$output_file"
	execute_cmd "msmgpiotool info 45" "$output_file"
	
	echo "backlightB=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x14 -o 0x05 -i 1 -r" "$output_file" 
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x14 -o 0x02 -i 1 -r" "$output_file"
	
	echo "backlightC=====" >> $output_file 2>&1
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x15 -o 0x05 -i 1 -r" "$output_file" 
	execute_cmd "i2cdbgr -D /dev/i2c9 -s 0x15 -o 0x02 -i 1 -r" "$output_file"
	
	cp /tmp/display_b_dtc $logdir/ >> $output_file 2>&1
	cp /tmp/display_c_dtc $logdir/ >> $output_file 2>&1
	cp /tmp/displayBC_monitor.txt $logdir/ >> $output_file 2>&1
}

dump_camera()
{	
	echo "------dump camera-------"
	local output_file=$logdir/camera.txt
	touch output_file
	echo "pin=====" >> $output_file 2>&1
	execute_cmd "msmgpiotool info 168" "$output_file"
}

dump_camera_pic()
{
	echo "------dump camera pic-------"
	local output_file=$logdir/camera.txt
	mkdir -p $logdir/pic
	rm -rf /tmp/frame* >> $output_file 2>&1
	echo "------dump camera pic1-------"
	/mnt/bin/camera/qcarcam_test/qcarcam_test -config=/mnt/bin/camera/qcarcam_test/12cam.xml -dumpFrame=100 -seconds=20 >> $output_file 2>&1
	echo "------dump camera pic2-------"
	cp /tmp/frame* $logdir/pic/ >> /var/camera_diag.log 2>&1
	rm -rf /tmp/frame* >> $output_file 2>&1
}

remote_diagnosis() 
{
	local output_file=$logdir/remote_diagnosis.txt
	display_remote_diagnosis -p $logdir/ >> $output_file 2>&1
#	sleep 3
#	mv /tmp/displayA_all_register $logdir/ >> $output_file 2>&1
#	mv /tmp/displayBC_all_register $logdir/ >> $output_file 2>&1
}

rm /var/dump_finish

date
dumpsys
dumpcpu &
#dump_camera_pic &
dump_bmlog &
dumpslog
dump_core
dump_picA
dump_picBC
dump_camera
echo 0 > /tmp/displayA_debug_switch
echo 0 > /tmp/displayBC_debug_switch
sleep 1
dump_DisplayA
dump_DisplayBC
remote_diagnosis
echo 1 > /tmp/displayA_debug_switch
echo 1 > /tmp/displayBC_debug_switch
wait
echo "all dump finish"  
A2_display & 
B_display &
C_display &
dumpdisk &
sleep 3
cd /var
rm $tt.tar.gz
tar zcvf $tt.tar.gz ./$tt
rm -rf ./$tt
touch /var/dump_finish
date


