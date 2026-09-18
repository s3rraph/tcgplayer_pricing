# Stage a self-contained distribution: a copy of the Python runtime with the
# app's dependencies pip-installed into it, plus the app sources. installer.iss
# then wraps dist_pkg/ into a per-user installer, so target machines need
# neither Python nor internet.
param(
    [string]$PythonDir = "C:\Python313",
    [string]$Version = ""
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Per-build stamp (version + date + short git hash), shown in the window title.
$buildStamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$gitHash = (git rev-parse --short HEAD 2>$null)
if ($LASTEXITCODE -eq 0 -and $gitHash) { $buildStamp = "$buildStamp $gitHash" }
$ver = $Version -replace '^v', ''
if (-not $ver) {
    $ver = (git describe --tags --abbrev=0 2>$null) -replace '^v', ''
    if (-not $ver) { $ver = "0.0.0-dev" }
}
Set-Content -Encoding ascii "_build_stamp.py" "STAMP = `"$buildStamp`"`nVERSION = `"$ver`""
Write-Output "build stamp: $buildStamp  version: $ver"

$stage = "dist_pkg"
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

Write-Output "=== copying Python runtime from $PythonDir ==="
if (-not (Test-Path "$PythonDir\python.exe")) { throw "python.exe not found at $PythonDir" }
& "$PythonDir\python.exe" -c "import tkinter" 2>$null
if ($LASTEXITCODE -ne 0) { throw "$PythonDir python lacks tkinter; the bundle would have no GUI" }
Copy-Item -Recurse -Force $PythonDir (Join-Path $stage "python")
$py = Join-Path $stage "python\python.exe"

Write-Output "=== installing requirements into the bundled Python ==="
# PYTHONNOUSERSITE=1 makes pip ignore the build machine's per-user
# site-packages so every wheel lands in the bundle, matching the -s launcher.
$env:PYTHONNOUSERSITE = "1"
& $py -m pip install --no-warn-script-location --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed ($LASTEXITCODE)" }
& $py -s -c "import tkinter, pandas; print('bundle imports ok, pandas', pandas.__version__)"
if ($LASTEXITCODE -ne 0) { throw "bundled Python cannot import the app's dependencies" }

# Trim runtime fat that the app never uses.
foreach ($d in @("python\Lib\test", "python\Lib\idlelib", "python\Tools",
                 "python\Lib\tkinter\test", "python\Lib\lib2to3", "python\Doc")) {
    $p = Join-Path $stage $d
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
Get-ChildItem (Join-Path $stage "python") -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Python ships vcruntime140*.dll but not msvcp140.dll; bundle it app-local so a
# machine without the VC++ Redistributable can still load native wheels.
Write-Output "=== bundling MSVC C++ runtime ==="
$pyRoot = Join-Path $stage "python"
foreach ($dll in @("msvcp140.dll", "vcruntime140_1.dll")) {
    $src = Join-Path $env:windir "System32\$dll"
    if (Test-Path $src) { Copy-Item $src $pyRoot -Force }
    elseif (-not (Test-Path (Join-Path $pyRoot $dll))) {
        Write-Warning "MSVC runtime '$dll' not found; clean-machine installs may fail to load native wheels"
    }
}

Write-Output "=== app sources ==="
$app = @("tcgplayer_pricing.py", "ui_elements.py", "file_handlers.py",
         "price_logic.py", "table_update.py", "_build_stamp.py", "README.MD")
foreach ($f in $app) {
    if (-not (Test-Path $f)) { throw "missing app file: $f" }
    Copy-Item $f $stage
}

$mb = [math]::Round((Get-ChildItem $stage -Recurse | Measure-Object Length -Sum).Sum/1MB, 0)
Write-Output "=== staged '$stage' ($mb MB) ==="
Write-Output "Next: iscc installer.iss"
