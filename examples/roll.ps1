param(
  [ValidateSet("top", "bottom", "left", "right")]
  [string]$Direction = "top",
  [int[]]$Values = @(),
  [string]$Theme = "",
  [string]$BaseUrl = "http://127.0.0.1:28888"
)

# 手動組 JSON，避免 Windows PowerShell 5 把 int[] 序列化成字串
$parts = New-Object System.Collections.Generic.List[string]
$parts.Add('"type":"dice.roll"')
$parts.Add('"direction":"' + $Direction + '"')
if ($Theme) {
  $parts.Add('"theme":"' + $Theme + '"')
}
if ($Values.Count -gt 0) {
  $arr = ($Values | ForEach-Object { [string]$_ }) -join ","
  $parts.Add('"values":[' + $arr + ']')
}
$json = "{" + ($parts -join ",") + "}"
Write-Host "POST $BaseUrl/api/roll  $json"
Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/roll" -ContentType "application/json; charset=utf-8" -Body $json
