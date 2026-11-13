#!/bin/sh
#v1.0

tt=alios
logdir=/private/$tt
echo $logdir
rm -rf $logdir
mkdir -p $logdir

dump_bmlog()
{
	echo "------dump bmlog--------"
    mkdir $logdir/bmlog/
	local number=0
	if [ -d "/private/bmlog/" ]; then
		cd /private/bmlog/
		for num in $(ls | grep ^[0-9] | sort -gr)
		do
		  if [ $number -eq 2 ];then
			break
          fi
		  cp -r /private/bmlog/$num $logdir/bmlog/
		  let number++
		done
	else
		echo "find bmlog error"
	fi
}

dump_yuntool()
{
	echo "------dump yuntool--------"
	mkdir $logdir/yuntool
	local number=0
	if [ -d "/private/yuntool/" ]; then
		cd /private/yuntool/
		for num in $(ls | grep ^[0-9] | sort -gr)
		do
		  if [ $number -eq 2 ];then
			break
          fi
		  cp -r /private/yuntool/$num $logdir/yuntool/
		  let number++
		done
		#echo logdir $logdir
	else
		echo "find yuntool error"
	fi
}

echo 'enable n;' > /proc/alog


dump_bmlog
dump_yuntool
wait
echo "all dump finish"  

cd /private
rm $tt.tar
tar cvf $tt.tar ./$tt
rm -rf ./$tt
date


