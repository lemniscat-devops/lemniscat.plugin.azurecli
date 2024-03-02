param(
    [string]$name
)

$result = Get-Location

$variables = Get-Content "$($result.path)/vars.json" | ConvertFrom-Json

Write-Host "Hello, $($variables.rg_name)"

Write-Host "Hello, $name"