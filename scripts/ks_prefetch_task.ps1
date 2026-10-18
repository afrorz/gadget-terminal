# Kickstarter 先読み(scripts/ks_prefetch.py)を、毎日 02:00 に自宅PCで走らせるタスクを(再)作成する。
#
#   powershell -ExecutionPolicy Bypass -File scripts\ks_prefetch_task.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\ks_prefetch_task.ps1 -Time 03:00   # 時刻を変える
#   powershell -ExecutionPolicy Bypass -File scripts\ks_prefetch_task.ps1 -Remove       # 消す
#
# 「ユーザーがログオンしている時だけ実行」で作る。パスワードは保存しない。
# PC は電源オフではなくスリープにしておくこと(WakeToRun でスリープから起こす)。
# 電源オプションの「スリープ解除タイマーを許可」が有効である必要がある。
param(
    [string]$Time = '02:00',
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
$TaskName = 'GadgetTerminal Kickstarter先読み'

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "削除しました: $TaskName"
    return
}

$repo = Split-Path -Parent $PSScriptRoot
$py = (Get-Command python -ErrorAction Stop).Source
if ($py -like '*WindowsApps*') {
    throw "python が Microsoft Store のエイリアス($py)を指しています。実体の python.exe を PATH の先頭に置いてください。"
}
$script = Join-Path $repo 'scripts\ks_prefetch.py'
if (-not (Test-Path $script)) { throw "見つかりません: $script" }

$action = New-ScheduledTaskAction -Execute $py -Argument "`"$script`"" -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Force `
    -Description 'Gadget Terminal: Kickstarter の案件を自宅PCで読んで data/kscache に貯め、git push する(GitHub Actions からは Kickstarter が 403 のため)' | Out-Null

$t = Get-ScheduledTask -TaskName $TaskName
Write-Host "作成しました: $TaskName"
Write-Host "  実行: $py `"$script`" (作業フォルダ $repo)"
Write-Host "  毎日 $Time / 次回: $((Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime)"
Write-Host "  WakeToRun=$($t.Settings.WakeToRun) StartWhenAvailable=$($t.Settings.StartWhenAvailable) 上限=$($t.Settings.ExecutionTimeLimit)"
