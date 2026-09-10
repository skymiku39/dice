param(
  [ValidateSet("top", "bottom", "left", "right")]
  [string]$Direction = "top",
  [string]$Values = "",
  [string]$Theme = "",
  [string]$BaseUrl = "http://127.0.0.1:28888"
)

# Values 用字串 "6,6,6"，避免 -File 參數把陣列黏成 666
$parts = New-Object System.Collections.Generic.List[string]
$parts.Add('"type":"dice.roll"')
$parts.Add('"direction":"' + $Direction + '"')
if ($Theme) {
  $parts.Add('"theme":"' + $Theme + '"')
}
if ($Values) {
  $nums = @()
  foreach ($p in ($Values -split "[,\s]+")) {
    if ($p -match '^[1-6]$') { $nums += $p }
  }
  if ($nums.Count -gt 0) {
    $parts.Add('"values":[' + ($nums -join ",") + ']')
  }
}
$json = "{" + ($parts -join ",") + "}"
Write-Host "POST $BaseUrl/api/roll  $json"
Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/roll" -ContentType "application/json; charset=utf-8" -Body $json
