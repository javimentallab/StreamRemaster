# Runs the frame generation bench in a throwaway Zen profile, on the display named by -Display.
# The clip comes from ffmpeg (no audio):
#   ffmpeg -f lavfi -i "testsrc2=size=1280x720:rate=60" -t 40 -an -vf "format=yuv420p,geq=lum='if(lt(X,64)*lt(Y,64),mod(N,26)*8+24,lum(X,Y))':cb='if(lt(X,32)*lt(Y,32),128,cb(X,Y))':cr='if(lt(X,32)*lt(Y,32),128,cr(X,Y))'" -c:v libx264 -crf 16 -preset veryfast -pix_fmt yuv420p clip60.mp4
param(
  [Parameter(Mandatory)][string]$WorkDir,
  [string]$Display = '\\.\DISPLAY4',
  [string]$Browser = 'C:\Program Files\Zen Browser\zen.exe',
  [int]$TimeoutS = 130
)
$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class Win {
  [DllImport("user32.dll")] public static extern IntPtr SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int ht, bool r);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int w, int ht, uint flags);
}
"@
[void][Win]::SetProcessDpiAwarenessContext([IntPtr](-4))
Add-Type -AssemblyName System.Windows.Forms

$bench = $PSScriptRoot
$clip = Join-Path $WorkDir 'clip60.mp4'
$results = Join-Path $WorkDir 'results.jsonl'
$profileDir = Join-Path $WorkDir 'zen-profile'
if (Test-Path $results) { Remove-Item $results -Confirm:$false }
New-Item -ItemType Directory -Force $profileDir | Out-Null
@'
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("zen.welcome-screen.seen", true);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("app.update.auto", false);
user_pref("media.autoplay.default", 0);
user_pref("widget.windows.window_occlusion_tracking.enabled", false);
'@ | Set-Content -Encoding utf8NoBOM (Join-Path $profileDir 'user.js')

$server = Start-Process python -ArgumentList '-I', '-X', 'utf8', (Join-Path $bench 'server.py'), $clip, $results -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 1
$browserProc = Start-Process $Browser -ArgumentList '-no-remote', '-profile', $profileDir, 'http://127.0.0.1:8792/tools/fg-bench/index.html' -PassThru

try {
  $target = [System.Windows.Forms.Screen]::AllScreens | Where-Object DeviceName -eq $Display
  if (-not $target) { throw "Display $Display not found" }
  $window = $null
  for ($i = 0; $i -lt 40 -and -not $window; $i++) {
    Start-Sleep -Milliseconds 500
    $window = Get-Process zen -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*fg-bench*' } | Select-Object -First 1
  }
  if (-not $window) { throw 'The bench window did not appear' }
  $b = $target.Bounds
  [void][Win]::MoveWindow($window.MainWindowHandle, $b.X + 80, $b.Y + 80, 2100, 1400, $true)
  # Topmost without taking the focus: a covered window gets almost no animation frames.
  [void][Win]::SetWindowPos($window.MainWindowHandle, [IntPtr](-1), 0, 0, 0, 0, 0x0013)
  "Window on $Display at ($($b.X + 80),$($b.Y + 80)), process $($window.Id)"

  $deadline = (Get-Date).AddSeconds($TimeoutS)
  while ((Get-Date) -lt $deadline -and -not $server.HasExited) { Start-Sleep -Milliseconds 500 }
  if (-not $server.HasExited) { 'TIMEOUT: the page did not finish' }
} finally {
  if ($window -and -not $window.HasExited) { [void]$window.CloseMainWindow(); Start-Sleep -Seconds 2 }
  if ($window -and -not $window.HasExited) { Stop-Process -Id $window.Id -Confirm:$false }
  if (-not $window -and -not $browserProc.HasExited) { Stop-Process -Id $browserProc.Id -Confirm:$false }
  if (-not $server.HasExited) { Stop-Process -Id $server.Id -Confirm:$false }
}
if (Test-Path $results) { Get-Content $results } else { 'no results' }
