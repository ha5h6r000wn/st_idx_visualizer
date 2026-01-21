# ================== 配置区 ==================
# $ProjectDir = "E:\hk\st_idx_visualizer"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Resolve-Path (Join-Path $ScriptDir "..")
$AppPath    = Join-Path $ProjectDir "app.py"
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"

$Port = 8501
$Args = @(
  "-u",                 # 关键：无缓冲输出（实时写日志）
  "-m","streamlit","run",$AppPath,
  "--server.headless","true",
  # "--server.address","0.0.0.0",
  "--server.port",$Port.ToString()
)

# ================== 日志 ==================
$OpsDir  = Join-Path $ProjectDir "ops"
$LogDir  = Join-Path $OpsDir "logs"
$DateTag = Get-Date -Format "yyyyMMdd"

$AppLog     = Join-Path $LogDir "streamlit_$DateTag.log"   # 实时滚动（合并 stdout/stderr）
$ServiceLog = Join-Path $LogDir "service_$DateTag.log"     # 脚本运维日志
$LockFile   = Join-Path $OpsDir "streamlit.lock"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log([string]$Msg, [string]$Level="INFO") {
  $Line = "{0} [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Msg
  Add-Content -Path $ServiceLog -Value $Line -Encoding UTF8
}

# ================== 日志保留策略 ==================
$KeepDays = 3   # ← 改成你想保留的天数（比如 2 或 3 或 7）

Get-ChildItem -Path $LogDir -File -Filter "*.log" -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays) } |
  Remove-Item -Force -ErrorAction SilentlyContinue

# ================== 主流程 ==================
try {
  Write-Log "==== Streamlit service starting ===="

  if (-not (Test-Path $VenvPython)) { throw "Python not found: $VenvPython" }
  if (-not (Test-Path $AppPath))    { throw "App not found: $AppPath" }

  # 防重复（端口级）
  if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Log "Port $Port already listening, service already running. Exit." "WARN"
    exit 0
  }

  # 写 lock
  Set-Content -Path $LockFile -Value $PID -Encoding ASCII

  Set-Location $ProjectDir
  Write-Log "WorkingDir=$ProjectDir"
  Write-Log "Command=$VenvPython $($Args -join ' ')"
  Write-Log "AppLog=$AppLog"

  # 关键：确保 Python 不缓冲（双保险）
  $env:PYTHONUNBUFFERED = "1"

  # 关键：用 Tee-Object 让输出实时落盘（合并 stdout+stderr）
  & $VenvPython @Args 2>&1 | Tee-Object -FilePath $AppLog -Append

  # 如果 Streamlit 正常情况下不会退出；一旦退出，执行到这里
  Write-Log "Streamlit exited." "WARN"
  exit 0
}
catch {
  Write-Log ("ERROR: " + $_.Exception.Message) "ERROR"
  exit 1
}
finally {
  if (Test-Path $LockFile) {
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
  }
  Write-Log "==== Streamlit service stopped ===="
}