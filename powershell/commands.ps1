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
