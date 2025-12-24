# PSAbbreviations.ps1 - PowerShell abbreviation manager

# Initialize abbreviations storage
if (-not $global:PSAbbreviations) {
    $global:PSAbbreviations = @{}
}

function abbr {
    <#
    .SYNOPSIS
    Manage command abbreviations similar to zsh-abbr
    
    .EXAMPLE
    abbr "gst=git status"
    abbr 'gcm=git commit -m "%"'
    abbr -add "gco=git checkout"
    abbr -erase gst
    abbr -rename gst newname
    abbr -list
    abbr -show
    abbr -version
    #>
    param(
        [Parameter(Position = 0)]
        [string]$Definition,
        
        [Parameter()]
        [switch]$add,
        
        [Parameter()]
        [switch]$erase,
        
        [Parameter()]
        [switch]$rename,
        
        [Parameter()]
        [switch]$list,
        
        [Parameter()]
        [switch]$show,
        
        [Parameter()]
        [switch]$version,
        
        [Parameter(Position = 1)]
        [string]$NewName
    )
    
    # abbr -version: Show version
    if ($version) {
        Write-Host "0.0.1"
        return
    }
    
    # abbr -list or abbr -show: List all abbreviations
    if ($list -or $show) {
        if ($global:PSAbbreviations.Count -eq 0) {
            Write-Host "No abbreviations defined" -ForegroundColor Yellow
            return
        }
        foreach ($key in $global:PSAbbreviations.Keys | Sort-Object) {
            Write-Host "abbr $key=" -NoNewline -ForegroundColor Cyan
            Write-Host """$($global:PSAbbreviations[$key])"""
        }
        return
    }
    
    # abbr -erase gst: Erase abbreviation
    if ($erase) {
        if (-not $Definition) {
            Write-Error "Usage: abbr -erase <abbreviation>"
            return
        }
        if ($global:PSAbbreviations.ContainsKey($Definition)) {
            $global:PSAbbreviations.Remove($Definition)
            Write-Host "Removed abbreviation: $Definition" -ForegroundColor Green
        } else {
            Write-Error "Abbreviation '$Definition' not found"
        }
        return
    }
    
    # abbr -rename gst newname: Rename abbreviation
    if ($rename) {
        if (-not $Definition -or -not $NewName) {
            Write-Error "Usage: abbr -rename <old-name> <new-name>"
            return
        }
        if ($global:PSAbbreviations.ContainsKey($Definition)) {
            $value = $global:PSAbbreviations[$Definition]
            $global:PSAbbreviations.Remove($Definition)
            $global:PSAbbreviations[$NewName] = $value
            Write-Host "Renamed '$Definition' to '$NewName'" -ForegroundColor Green
        } else {
            Write-Error "Abbreviation '$Definition' not found"
        }
        return
    }
    
    # abbr gst="git status" or abbr -add gst="git status": Add abbreviation
    if ($Definition) {
        if ($Definition -match '^([^=]+)=(.+)$') {
            $abbr = $matches[1].Trim()
            $expansion = $matches[2]
            
            # Only strip outer quotes if they exist and match
            if (($expansion.StartsWith('"') -and $expansion.EndsWith('"')) -or 
                ($expansion.StartsWith("'") -and $expansion.EndsWith("'"))) {
                $expansion = $expansion.Substring(1, $expansion.Length - 2)
            }
            
            $global:PSAbbreviations[$abbr] = $expansion
            # Silently add when sourcing from profile
            if ($MyInvocation.CommandOrigin -eq 'Runspace') {
                Write-Host "Added abbreviation: $abbr -> $expansion" -ForegroundColor Green
            }
        } else {
            Write-Error "Invalid format. Use: abbr <name>=<expansion> or abbr <name>='<expansion>'"
        }
        return
    }
    
    # No arguments: show usage
    Write-Host @"
Usage:
  abbr <name>=<expansion>    Add an abbreviation
  abbr -add <name>=<expansion> Add an abbreviation (explicit)
  abbr -erase <name>         Erase an abbreviation
  abbr -rename <old> <new>   Rename an abbreviation
  abbr -list                 List all abbreviations
  abbr -show                 Show all abbreviations (same as -list)
  abbr -version              Show version

Cursor Placement:
  Use % in the expansion to set cursor position after expansion
  Example: abbr 'gcm=git commit -m "%"'
"@ -ForegroundColor Cyan
}

# Helper function to expand abbreviation and handle cursor placement
function Expand-Abbreviation {
    param(
        [string]$Word
    )
    
    if (-not $global:PSAbbreviations.ContainsKey($Word)) {
        return $null
    }
    
    $expansion = $global:PSAbbreviations[$Word]
    
    # Check if expansion contains cursor placeholder %
    if ($expansion -match '%') {
        $cursorIndex = $expansion.IndexOf('%')
        $expandedText = $expansion -replace '%', ''
        return @{
            Text = $expandedText
            CursorOffset = $cursorIndex
            HasCursorPlaceholder = $true
        }
    }
    
    return @{
        Text = $expansion
        CursorOffset = $expansion.Length
        HasCursorPlaceholder = $false
    }
}

# Spacebar expands abbreviations
Set-PSReadLineKeyHandler -Chord Spacebar -ScriptBlock {
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    
    $tokens = $line -split '\s+'
    $currentWord = $tokens[-1]
    
    $result = Expand-Abbreviation -Word $currentWord
    
    if ($result) {
        $startPos = $line.LastIndexOf($currentWord)
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace($startPos, $currentWord.Length, $result.Text)
        
        # Set cursor position
        $newCursorPos = $startPos + $result.CursorOffset
        [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($newCursorPos)
        
        # Only insert space if there's no cursor placeholder
        if (-not $result.HasCursorPlaceholder) {
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert(' ')
        }
    } else {
        # No abbreviation found, insert space normally
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert(' ')
    }
}

# Enter expands and accepts
Set-PSReadLineKeyHandler -Chord Enter -ScriptBlock {
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    
    $tokens = $line -split '\s+'
    $currentWord = $tokens[-1]
    
    $result = Expand-Abbreviation -Word $currentWord
    
    if ($result) {
        $startPos = $line.LastIndexOf($currentWord)
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace($startPos, $currentWord.Length, $result.Text)
        
        # If there's a cursor placeholder, position cursor and don't accept line
        if ($result.HasCursorPlaceholder) {
            $newCursorPos = $startPos + $result.CursorOffset
            [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($newCursorPos)
            return  # Don't accept line, let user fill in the placeholder
        }
    }
    
    [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
}
