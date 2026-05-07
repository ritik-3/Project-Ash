$ErrorActionPreference = "Stop"

Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/voice/devices"
