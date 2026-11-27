# P5 CFD: build the outer-shape part (cfd/<name>.json from cfd_geom.py) in the open SOLIDWORKS session.
#   powershell -ExecutionPolicy Bypass -File run_cfd_geom.ps1 cfd\wing.json
param([Parameter(Mandatory = $true)][string]$geom)
$api = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist'
$refs = @("$api\SolidWorks.Interop.sldworks.dll", "$api\SolidWorks.Interop.swconst.dll", 'System.Web.Extensions')
Add-Type -Path $refs[0..1]
Add-Type -AssemblyName System.Web.Extensions
Add-Type -TypeDefinition (Get-Content (Join-Path $PSScriptRoot 'SwCfdGeom.cs') -Raw) -ReferencedAssemblies $refs
[SwCfdGeom]::Run((Resolve-Path $geom).Path)
