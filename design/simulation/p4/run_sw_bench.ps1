# P4: compile SwFeaBench.cs against the SolidWorks interop assemblies and run the cantilever benchmark in the open
# SolidWorks session (Windows PowerShell 5.1):  powershell -ExecutionPolicy Bypass -File run_sw_bench.ps1 [h_mm]
param([double]$h = 1.0)
$api = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist'
$refs = @("$api\SolidWorks.Interop.sldworks.dll", "$api\SolidWorks.Interop.swconst.dll", "$api\SolidWorks.Interop.cosworks.dll")
Add-Type -Path $refs
Add-Type -TypeDefinition (Get-Content (Join-Path $PSScriptRoot 'SwFeaBench.cs') -Raw) -ReferencedAssemblies $refs
$part = Join-Path $PSScriptRoot ("bench_cantilever_h{0}.SLDPRT" -f $h)
# L 100, b 10, t 3 mm; E 2.55 GPa (P1 design value, balsa rho 0.12); W 0.5 N on the top face
[SwFeaBench]::Run($part, 100.0, 10.0, 3.0, 2.55e9, 0.5, $h)
