<#
.SYNOPSIS
    Converts DDS image files to PNG format with color channel swapping and vertical flip.

.DESCRIPTION
    This function uses ImageMagick's mogrify command to batch convert all DDS files 
    in the current directory to PNG format. It applies a vertical flip and swaps the 
    red and blue color channels (BGR to RGB conversion), which is commonly needed for 
    DDS textures exported from certain game engines or 3D applications.

.EXAMPLE
    dds2png
    Converts all .dds files in the current directory to .png format.

.NOTES
    Requires ImageMagick to be installed and available in PATH.
    The original DDS files are preserved; new PNG files are created.
#>
function dds2png {
    # Use mogrify to convert DDS to PNG with:
    # -format png: output as PNG files
    # -flip: flip image vertically
    # -color-matrix: swap red and blue channels (BGR → RGB)
    mogrify -format png -flip -color-matrix '0 0 1
                                            0 1 0
                                            1 0 0' *.dds
}

<#
.SYNOPSIS
    Extracts archive files encoded with Japanese (Shift-JIS) character encoding.

.DESCRIPTION
    This function uses 7-Zip to extract archive files that contain Japanese filenames
    encoded in Shift-JIS (code page 932). This prevents garbled filenames when extracting
    Japanese archives on non-Japanese systems.

.PARAMETER args
    Arguments to pass to 7z.exe (such as archive filename and extraction options).

.EXAMPLE
    unzipjis archive.zip
    Extracts archive.zip with Shift-JIS encoding support.

.EXAMPLE
    unzipjis archive.zip -o"C:\output"
    Extracts to a specific output directory.

.NOTES
    Requires 7-Zip to be installed and available in PATH.
#>
function unzipjis {
    # Extract with code page 932 (Shift-JIS) for Japanese character support
    7z.exe x @args -mcp=932
}

<#
.SYNOPSIS
    Converts video files to MKV container format without re-encoding.

.DESCRIPTION
    This function uses FFmpeg to remux video files into the MKV container format.
    It copies both video and audio streams without re-encoding (fast, lossless operation).
    The function accepts input from the pipeline and validates that the file exists.

.PARAMETER file
    Path to the video file to convert. Accepts pipeline input.

.EXAMPLE
    vid2mkv "movie.mp4"
    Converts movie.mp4 to movie.mkv

.EXAMPLE
    Get-ChildItem *.mp4 | ForEach-Object { vid2mkv $_.FullName }
    Converts all MP4 files in the current directory to MKV.

.EXAMPLE
    "video.avi" | vid2mkv
    Uses pipeline input to convert video.avi to video.mkv

.NOTES
    Requires FFmpeg to be installed and available in PATH.
    The original file is preserved; a new MKV file is created.
#>
function vid2mkv([Parameter(ValueFromPipeline = $true)][string]$file) {
    process {
        # Validate that the input file exists
        if (-not (Test-Path -Path $file -PathType Leaf)) {
            Write-Output "Please provide a valid video file"
            return
        }

        # Generate output filename by replacing extension with .mkv
        $output = [System.IO.Path]::ChangeExtension($file, ".mkv")

        # Use FFmpeg to remux without re-encoding:
        # -i: input file
        # -vcodec copy: copy video stream without re-encoding
        # -acodec copy: copy audio stream without re-encoding
        ffmpeg.exe -i $file -vcodec copy -acodec copy $output
    }
}

<#
.SYNOPSIS
    Copies pipeline input to the Windows clipboard.

.DESCRIPTION
    Buffers the entire pipeline before writing, then renders it once through
    Out-String. Rendering the collection as a whole keeps table layout intact for
    formatted objects; rendering item by item would emit a header per row.
    Out-String terminates every line with CRLF. Only the final terminator is
    removed: pipeline items are joined by CRLF and trailing blank items are
    preserved.

.PARAMETER InputObject
    Objects or strings to copy. Accepts pipeline input.

.EXAMPLE
    git log --oneline -10 | pbcopy
    Copies the commit list.

.EXAMPLE
    Get-ChildItem *.md | Select-Object Name, Length | pbcopy
    Copies the rendered table rather than the object type names.

.NOTES
    Named after the macOS utility of the same name.
    An empty pipeline clears the clipboard.
#>
function pbcopy {
    param([Parameter(ValueFromPipeline = $true)][psobject]$InputObject)
    begin { $items = [System.Collections.Generic.List[psobject]]::new() }
    process { $items.Add($InputObject) }
    end {
        $text = $items | Out-String
        if ($text.EndsWith("`r`n")) { $text = $text.Substring(0, $text.Length - 2) }
        Set-Clipboard -Value $text
    }
}

<#
.SYNOPSIS
    Prints the Windows clipboard.

.DESCRIPTION
    Forwards every argument to Get-Clipboard, so clipboard text arrives as one
    string per line and pipes into line-oriented cmdlets unchanged.

.EXAMPLE
    pbpaste | Select-String 'error'
    Filters clipboard text line by line.

.EXAMPLE
    pbpaste -Raw > clip.txt
    Writes the clipboard as a single string, preserving its CRLF line endings.

.NOTES
    Named after the macOS utility of the same name.
#>
function pbpaste {
    Get-Clipboard @args
}
