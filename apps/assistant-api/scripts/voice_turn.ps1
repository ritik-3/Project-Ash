$ErrorActionPreference = "Stop"

param(
  [string]$SessionId = "default",
  [bool]$WaitForWakeWord = $true
)

$body = @{
  session_id = $SessionId
  wait_for_wake_word = $WaitForWakeWord
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/voice/turn" `
  -ContentType "application/json" `
  -Body $body
