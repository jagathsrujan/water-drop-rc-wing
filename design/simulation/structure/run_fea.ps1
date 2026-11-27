# P6: run one SOLIDWORKS Simulation case (a JSON case file written by fea_cases.py) in the open SOLIDWORKS session.
#   powershell -ExecutionPolicy Bypass -File run_fea.ps1 <case.json>
param([Parameter(Mandatory = $true)][string]$case)
$api = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist'
$refs = @("$api\SolidWorks.Interop.sldworks.dll", "$api\SolidWorks.Interop.swconst.dll", "$api\SolidWorks.Interop.cosworks.dll",
          'System.Web.Extensions')
Add-Type -Path $refs[0..2]
Add-Type -AssemblyName System.Web.Extensions
Add-Type -TypeDefinition (Get-Content (Join-Path $PSScriptRoot 'SwFea.cs') -Raw) -ReferencedAssemblies $refs
[SwFea]::Run((Resolve-Path $case).Path)
