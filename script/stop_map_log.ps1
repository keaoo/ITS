<#***************************************************************************************
*  Project:        maptools
*  Copyright ?     2015-2022 Banma Technologies Co.,Ltd
*             All rights reserved.
*  Revision History:
*   Author             Date(MM/DD/YYYY)  
*  -------------         -----------------------
*   jiangmf              05/02/2022
#  关闭地图各模块日志
****************************************************************************************#>

# 是否使用云机，如果本地机器，则设置为0
$is_Cloud_car = 0

# 参数1：指定用于获取的云机地址
$adb_server = "30.16.86.171:50842"
<# -----------------参数配置项结束---------------------- #>

"start replacing map/dr config files to stop logging..."

#指定要关闭的各地图进程log
$close_zebramap_log = 1
$close_dr_log = 1
$close_ris_log = 1
$close_mrfusion_log = 1
$close_noa_log = 1
$close_yuntool_log = 1

#确认车机连接状
if ($is_Cloud_car) {
    #使用云机
    $conn_status = adb -host connect $adb_server
    if ($conn_status.contains("unable to connect to")) {
        write-host -ForegroundColor red "ERROR:unable to connect to device!"
        pause
        return
    }
    $adb_shell = "adb -host -s $adb_server "
}
else {
    #adb直连
    $conn_status = adb -host devices
    if ($conn_status.Length -eq 2) {
        #没有连接到设备时，返回的字符串数组只有2行，否则＞2行（最后一行为空）
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

#Split-Path获取当前脚本文件路径的父文件
$cur_directory = Split-Path -Parent $MyInvocation.MyCommand.Definition
#运行各模块的配置文件中，是否发生了错误
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

function modify_drcfg_ini {
    # pull配置文件DrCfg.ini
    $file_name = "DrCfg.ini"
    $cmd = $adb_shell + "pull /etc/$file_name $cur_directory/$file_name"
    call $cmd

    if (-not (Test-Path $cur_directory/$file_name)) {
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_name"
        $happen_error = 1
        return
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_name
    if ($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_name"
        $happen_error = 1
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*SAVE_LOG.*","SAVE_LOG = 0") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /etc"
    call $cmd
    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_zebramap_ini {
    # pull配置文件ZebraMap.ini
    $file_name = "ZebraMap.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    if (-not (Test-Path $cur_directory/$file_name)) {
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_name"
        $happen_error = 1
        return
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_name
    if ($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_name"
        $happen_error = 1
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*", "MEDIA = 0" `
        -Replace ".*FLUSH_INTERVAL.*", "FLUSH_INTERVAL = 5" `
        -Replace "= R_LEVEL", "= E_LEVEL" `
        -Replace "= M_LEVEL", "= E_LEVEL" `
        -Replace "= D_LEVEL", "= E_LEVEL" `
        -Replace ".*SHOW_DEBUG_INFO.*", "SHOW_DEBUG_INFO = 0" `
        -Replace ".*BL_LOG_LEVEL.*", "BL_LOG_LEVEL = 0" `
		-Replace ".*SAVE_SIGNAL.*","SAVE_SIGNAL = 0" `
		-Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 400" `
        -Replace ".*BL_LOG_MODULE_USE.*", "BL_LOG_MODULE_USE = 0") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd
    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_mrfusion_ini {
    # pull配置文件mr_fusion.ini
    $file_name = "mr_fusion.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    if (-not (Test-Path $cur_directory/$file_name)) {
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_name"
        $happen_error = 1
        return
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_name
    if ($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_name"
        $happen_error = 1
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*", "MEDIA = 0" `
                -Replace "= R_LEVEL", "= E_LEVEL" `
                -Replace "= M_LEVEL", "= E_LEVEL" `
                -Replace "= D_LEVEL", "= E_LEVEL" `
				-Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 400" `
                -Replace ".*SAVE_SIGNAL.*", "SAVE_SIGNAL = 0") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}
function modify_ris_ini {
    # pull配置文件ehorizon.ini
    $file_name = "ehorizon.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    if (-not (Test-Path $cur_directory/$file_name)) {
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_name"
        $happen_error = 1
        return
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_name
    if ($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_name"
        $happen_error = 1
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*LOG_MEDIA.*", "LOG_MEDIA = 0" `
             -Replace ".*LOG_LVL.*", "LOG_LVL=E") $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

function modify_noa_ini {
    # pull配置文件mr_fusion.ini
    $file_name = "ZebraNoa.ini"
    $cmd = $adb_shell + "pull /map/config/$file_name $cur_directory/$file_name"
    call $cmd

    if (-not (Test-Path $cur_directory/$file_name)) {
        write-host -ForegroundColor Yellow "Warnning:file not exist:$file_name"
        $happen_error = 1
        return
    }

    $file_text = Get-Content -Encoding utf8 $cur_directory/$file_name
    if ($file_text.Length -eq 0) {
        write-host -ForegroundColor Red "ERROR:file size is 0:$file_name"
        $happen_error = 1
        return
    }

    OutfileUTF8NoBOM ($file_text -Replace ".*MEDIA.*", "MEDIA = 0" `
                -Replace "= R_LEVEL", "= E_LEVEL" `
                -Replace "= M_LEVEL", "= E_LEVEL" `
                -Replace "= D_LEVEL", "= E_LEVEL" `
				-Replace ".*MAX_FILE_SIZE.*","MAX_FILE_SIZE = 400" `
              ) $cur_directory/$file_name

    #push ini
    $cmd = $adb_shell + "push $cur_directory/$file_name /map/config"
    call $cmd

    #delete local ini file
    Remove-Item "$cur_directory/$file_name"
}

$cmd = $adb_shell + "remount"
call $cmd

$cmd = $adb_shell + "shell `"echo 'enable 0' > /proc/alog`" "
call $cmd

$cmd = $adb_shell + "shell `"mount -o remount,rw /`" "
call $cmd

#修改zebramap.ini
if ($close_zebramap_log) {
    modify_zebramap_ini
}


#drcfg.ini
if ($close_dr_log) {
    modify_drcfg_ini
}

#mr_fusion.ini
if ($close_mrfusion_log) {
    modify_mrfusion_ini
}

#ris.ini
if ($close_ris_log) {
    modify_ris_ini
}

#noa.ini
if ($close_noa_log) {
    modify_noa_ini
}

#开启logcat日志
if ($close_yuntool_log) {
    <#   日志级别说明：
        LOG_V对应等级2 
        LOG_D对应等级3 
        LOG_I对应等级4 
        LOG_W对应等级5 
        LOG_E对应等级6 
        LOG_F对应等级7
    #>
    $log_level = 7

    #本次日志等级设置
    $cmd = $adb_shell + "shell logctl -p $log_level"
    call $cmd

    #修改日志配置文件，以便重启后仍有效
    $cmd = $adb_shell + "shell `"echo '* $log_level' > /etc/log_filters`" "
    call $cmd
}

#关闭模拟导航
if ($is_Cloud_car) {
    adb -host -s $adb_server shell sendlink page://com.yunos.map/map -e showTest -d '{\\\"simulateNavi\\\":\\\"0\\\"}'
}
else {
    adb -host shell sendlink page://com.yunos.map/map -e showTest -d '{\\\"simulateNavi\\\":\\\"0\\\"}'
}

if ($close_dr_log) {
    $cmd = $adb_shell + "shell systemctl restart drservice"
    call $cmd
}

if ($close_mrfusion_log) {
    $cmd = $adb_shell + "shell systemctl restart mrfusion"
    call $cmd
}

if ($close_ris_log) {
    $cmd = $adb_shell + "shell systemctl restart ris"
    call $cmd
}

if ($close_noa_log) {
    $cmd = $adb_shell + "shell systemctl restart noa"
    call $cmd
}

if ($close_zebramap_log) {
    $cmd = $adb_shell + "shell systemctl restart mapd"
    call $cmd
}

if ($happen_error -eq 1) {
    write-host -ForegroundColor Yellow "some errors occured,please check warnning info!"
}
else {
    write-host -ForegroundColor green "stopping map log succeeded!"
}
pause