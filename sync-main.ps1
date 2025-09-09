param([string]$Message = "chore: sync")
& "$PSScriptRoot\tools\git_sync_main.ps1" -Message $Message
