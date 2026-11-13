#!/bin/sh
#v1.0

tt=alios
logdir=/private
echo $logdir

dump_bmlogall()
{
	echo "------dump all bmlog--------"
	if [ -f $logdir/alios-bmlogall.tar ] 
	then
		rm $logdir/alios-bmlogall.tar
    fi
	tar cvf $logdir/alios-bmlogall.tar /private/bmlog
}

dump_yuntoolall()
{
	echo "------dump yuntool--------"
	if [ -f $logdir/alios-yuntoolall.tar ] 
	then
		rm $logdir/alios-yuntoolall.tar
    fi	
	tar cvf $logdir/alios-yuntoolall.tar /private/yuntool
}

echo 'enable n;' > /proc/alog

dump_bmlogall &
dump_yuntoolall &
wait
echo "all dump finish"  

date


