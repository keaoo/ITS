<#***************************************************************************************
*  Project:        maptools
*  Copyright ?     2015-2022 Banma Technologies Co.,Ltd
*             All rights reserved.
*  Revision History:
*   Author             Date(MM/DD/YYYY)  
*  -------------         -----------------------
*   jiangmf              05/02/2022
#  开启地图各模块日志
****************************************************************************************#>

<# -----用于开启地图log配置项，同时删除所有地图日志（is_clear_logs可配置）----- #>
# 参数0：是否使用云机，本机直连设置为0。
#如果是云机时，通过以下adb_server来设置云机地址
$is_Cloud_car = 0

# 参数1：指定用于获取的云机地址
$adb_server = "30.16.86.171:50789"

#开启地图日志时，同时删除所有地图日志
$is_clear_logs = 1
#指定要开启的各地图进程log
$open_zebramap_log = 1
#开启dr模块的日志
$open_dr_log = 1
#开启ris模块的日志
$open_ris_log = 0
#开启noa模块的日志
$open_noa_log = 0
#开启mrfusion模块的日志
$open_mrfusion_log = 0
#开启yuntool/logctl日志
$open_yuntool_log = 1
#开启模拟导航，在实走车辆时请关闭此选项
$open_simu_navi = 0


<# -----------------参数配置项结束---------------------- #>

#确认车机连接状
if ($is_Cloud_car) { #使用云机
    $conn_status = adb -host connect $adb_server
    if($conn_status.contains("unable to connect to")) {
        write-host -ForegroundColor red "ERROR:unable to connect to device!"
        pause
        return
    }
    $adb_shell = "adb -host -s $adb_server "
}
 else { #adb直连
    $conn_status = adb -host devices
    if($conn_status.Length -eq 2) { #没有连接到设备时，返回的字符串数组只有2行，否则＞2行（最后一行为空）
                     # List of devices attached
                     #30.16.86.160:50906      device
                     #
        write-host -ForegroundColor red "ERROR:unable to connect to device!"
        pause
        return
    }

    $adb_shell = "adb -host "
}

# 设置别名，调用文件表达式
Set-Alias call Invoke-Expression

$cmd = $adb_shell + "remount"
call $cmd

$cmd = $adb_shell + "shell `"echo 'enable 0' > /proc/alog`" "
call $cmd

$cmd = $adb_shell + "shell `"mount -o remount,rw /`" "
call $cmd

# 删除所有地图日志
if ($is_clear_logs) {
    "start clearing map logs ..."
    $cmd = $adb_shell + "shell rm /var/tools/tombstones/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /map/log/drlog/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /map/log/gbllog/loc/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /map/log/gbllog/alc/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /data/rtd/sdk_log/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /private/yuntool/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /private/bmlog/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /map/log/zebralog/* -rf"
    call $cmd

    $cmd = $adb_shell + "shell rm /private/tools/coredump/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /map/log/mrlog/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /map/log/noalog/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /map/log/ris/* -rf"
    call $cmd
	
	$cmd = $adb_shell + "shell rm /map/log/nilog/* -rf"
    call $cmd
    write-host -ForegroundColor green "clear map logs succeeded!"
}

#Split-Path获取当前脚本文件路径的父文件
$cur_directory = Split-Path -Parent $MyInvocation.MyCommand.Definition
#运行各模块的配置文件中，是否发生了错误[ref]
$happen_error = 0

#输出nobom的utf8格式文件（v5 powershell不支持utf8nobom参数）
function OutfileUTF8NoBOM { param( $str, $dest )
    #增加首行，日志配置开始，BOM（EF BB BF）头会导致当前com_readini接口出错

    #判断是否需要增加起始行
    $append_beginning = 0
    if($str.GetType().Name -eq "String") { #String
        if($str.Length -lt 14) {
            $append_beginning = 1       
        }
        else {
            if (-not $str.Substring(0,14).Equals("#the beginning")) {
                $append_beginning = 1
            } 
        }
    }
    else { #数组
        if($str[0].Length -lt 14) {
            $append_beginning = 1       
        }
        else {
            if (-not $str[0].Substring(0,14).Equals("#the beginning")) {
                $append_beginning = 1
            } 
        }
    }

    #需要增加起始行
    if ($append_beginning) {
        "#the beginning of settings`r`n" | out-file -encoding ASCII $dest
    }
    else {#清空文件
        "" | out-file -encoding ASCII -NoNewline $dest
    }
    $str | out-file -encoding UTF8 -Append $dest
}

#测试文件路径是否存在
function read_ini_file($file_basename) {
    if(-not (Test-Path $cur_directory/$file_basename)){
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_basename"
        $happen_error = 1
        return ""
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_basename
    if($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_basename"
        $happen_error = 1
        return ""
    }
    return $file_text
}

function modify_drcfg_ini
{
    # pull配置文件DrCfg.ini
    $file_name = "DrCfg.ini"
    $cmd = $adb_shell + "pull /etc/$file_name $cur_directory/$file_name"
    call $cmd

    $file_text = read_ini_file $file_name
    if ($file_text.Length -eq 0) {
       return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*SAVE_LOG.*","SAVE_LOG = 1" `
								 -Replace ".*COMPRESS_LOG.*", "COMPRESS_LOG = 1") $cur_directory/$file_name

    #push ini file
    $cmd = $adb_shell + "push $cur_directory/$file_name /etc"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_zebramap_ini
{
    # pull配置文件ZebraMap.ini
    $file_name = "ZebraMap.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    $file_text = read_ini_file $file_name
    if ($file_text.Length -eq 0) {
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*", "MEDIA = 2" `
	-Replace ".*COMPRESS_LOG.*", "COMPRESS_LOG = 1" `
    -Replace ".*FLUSH_INTERVAL.*", "FLUSH_INTERVAL = 1" `
    -Replace "= R_LEVEL", "= M_LEVEL" `
    -Replace "= E_LEVEL", "= M_LEVEL" `
    -Replace "= D_LEVEL", "= M_LEVEL" `
    -Replace ".*SHOW_DEBUG_INFO.*","SHOW_DEBUG_INFO = 1" `
    -Replace ".*BL_LOG_LEVEL.*","BL_LOG_LEVEL = 4" `
    -Replace ".*SAVE_SIGNAL.*","SAVE_SIGNAL = 1" `
    -Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 1000" `
    -Replace ".*BL_LOG_MODULE_USE.*","BL_LOG_MODULE_USE = 3") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_mrfusion_ini
{
    # pull配置文件ZebraMap.ini
    $file_name = "mr_fusion.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    $file_text = read_ini_file $file_name
    if ($file_text.Length -eq 0) {
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*","MEDIA = 2" `
			-Replace ".*COMPRESS_LOG.*", "COMPRESS_LOG = 0" `
            -Replace "= R_LEVEL", "= M_LEVEL" `
            -Replace "= E_LEVEL", "= M_LEVEL" `
            -Replace "= D_LEVEL", "= M_LEVEL" `
			-Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 1000" `
            -Replace ".*SAVE_SIGNAL.*","SAVE_SIGNAL = 1") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_ris_ini
{
    # pull配置文件ehorizon.ini
    $file_name = "ehorizon.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd
    
    $file_text = read_ini_file $file_name
    if ($file_text.Length -eq 0) {
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*LOG_MEDIA.*","LOG_MEDIA = 2" `
			 -Replace ".*COMPRESS_LOG.*", "COMPRESS_LOG = 0" `
             -Replace ".*LOG_LVL.*","LOG_LVL=M") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_noa_ini
{
    # pull配置文件ZebraNoa.ini
    $file_name = "ZebraNoa.ini"
	$cmd = $adb_shell + "shell cp /usr/share/noa/config/$file_name /map/config/$file_name"
    call $cmd
	
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd
    
    $file_text = read_ini_file $file_name
    if ($file_text.Length -eq 0) {
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*","MEDIA = 2" `
			-Replace ".*COMPRESS_LOG.*", "COMPRESS_LOG = 0" `
            -Replace "= R_LEVEL", "= M_LEVEL" `
            -Replace "= E_LEVEL", "= M_LEVEL" `
            -Replace "= D_LEVEL", "= M_LEVEL" `
			-Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 1000" `
             ) $cur_directory/$file_name
    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

"start modifying configuration files to start logging..."

#修改zebramap.ini
if ($open_zebramap_log) {
    modify_zebramap_ini
}

#drcfg.ini
if ($open_dr_log) {
    modify_drcfg_ini
}

#mr_fusion.ini
if ($open_mrfusion_log) {
    modify_mrfusion_ini
}

#ris.ini
if ($open_ris_log) {
    modify_ris_ini
}

if ($open_noa_log) {
    modify_noa_ini
}

#开启logcat日志
if ($open_yuntool_log) {
    <#   日志级别说明：
        LOG_V对应等级2 
        LOG_D对应等级3 
        LOG_I对应等级4 
        LOG_W对应等级5 
        LOG_E对应等级6 
        LOG_F对应等级7
    #>
    $log_level = 3 

    #本次日志等级设置
    $cmd = $adb_shell + "shell logctl -p $log_level"
    call $cmd

    #修改日志配置文件，以便重启后仍有效
    $cmd = $adb_shell + "shell `"echo '* $log_level' > /etc/log_filters`" "
    call $cmd
}

#开启模拟导航
if ($open_simu_navi) {
    if ($is_Cloud_car) {
        adb -host -s $adb_server shell sendlink page://com.yunos.map/map -e showTest -d '{\\\"simulateNavi\\\":\\\"1\\\"}'
    }
    else {
        adb -host shell sendlink page://com.yunos.map/map -e showTest -d '{\\\"simulateNavi\\\":\\\"1\\\"}'
    }
}

"start restarting service to make it take effect..."

if ($open_dr_log) {
    $cmd = $adb_shell + "shell systemctl restart drservice"
    call $cmd
}

if ($open_mrfusion_log) {
    $cmd = $adb_shell + "shell systemctl restart mrfusion"
    call $cmd
}

if ($open_ris_log) {
    $cmd = $adb_shell + "shell systemctl restart ris"
    call $cmd
}

if ($open_noa_log) {
    $cmd = $adb_shell + "shell systemctl restart noa"
    call $cmd
}

if ($open_zebramap_log) {
    $cmd = $adb_shell + "shell systemctl restart mapd"
    call $cmd
}

if ($happen_error -eq 1) {
    write-host -ForegroundColor Yellow "some errors occured,please check the warnning info!"
}
else {
    write-host -ForegroundColor green "starting map log succeeded!"
}
pause

