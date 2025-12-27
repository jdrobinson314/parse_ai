param(
    [Parameter(ValueFromRemainingArguments = $true)]
    $ScriptArgs
)

$ErrorActionPreference = "Stop"

# Resolve directories
$ScriptDir = $PSScriptRoot
$ProjectRoot = Resolve-Path "$ScriptDir\.."
$AppsDir = Join-Path $ScriptDir "apps"

# Check if help is requested
if ($ScriptArgs -contains "--help" -or $ScriptArgs -contains "-h") {
    Write-Host "========================================================"
    Write-Host " ParseAI - JSON Parser & Code Extractor"
    Write-Host "========================================================"
    Write-Host "Usage: .\run_parser.bat [OPTIONS]"
    Write-Host ""
    Write-Host "Description:"
    Write-Host "  Parses JSON conversation logs from the 'ingest' directory,"
    Write-Host "  converts them to human-readable text, and extracts any"
    Write-Host "  marked code files into separate directories."
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --help, -h          Show this help message and exit."
    Write-Host "  --add-numbering, -n Prepend sequential numbers to filenames."
    Write-Host "  --strip, -s         Regex pattern to strip from filenames."
    Write-Host "  -r, --reconstruct    Enable Path-Aware Extraction (create directories from fence paths)"
    Write-Host "  -m, --merge-to DIR   Merges reconstructed files into a single unified directory (e.g. ./my_app)"
    Write-Host "  -cp, --clean-project Automatically merge into a 'merged_project' subfolder."
    Write-Host ""
    Write-Host "Structure:"
    Write-Host "  Input:  $ProjectRoot\ingest\*.json"
    Write-Host "  Output: $ProjectRoot\output\"
    Write-Host ""
    exit 0
}

# Set PYTHONPATH to include the project root
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"
}
else {
    $env:PYTHONPATH = "$ProjectRoot"
}



# Default Output Directory
$DefaultOutputDir = Join-Path $ProjectRoot "output"
$OutputDir = $DefaultOutputDir

# Pre-scan arguments to find --output or -o
for ($i = 0; $i -lt $ScriptArgs.Count; $i++) {
    if ($ScriptArgs[$i] -eq "--output" -or $ScriptArgs[$i] -eq "-o") {
        if (($i + 1) -lt $ScriptArgs.Count) {
            $PotentialPath = $ScriptArgs[$i + 1]
            if (Test-Path $PotentialPath -PathType Container) {
                $OutputDir = Resolve-Path $PotentialPath
            }
            else {
                # If path doesn't exist yet or is relative, resolve it
                if ([System.IO.Path]::IsPathRooted($PotentialPath)) {
                    $OutputDir = $PotentialPath
                }
                else {
                    $OutputDir = Join-Path (Get-Location) $PotentialPath
                }
            }
        }
    }
}

Write-Host "Starting ParseAI..."
Write-Host "Project Root: $ProjectRoot"
Write-Host "Output Directory: $OutputDir"

# 1. Run the JSON Parser
Write-Host "Running JSON Parser..."
$JsonParserPath = Join-Path $AppsDir "json_parser.py"

# Call python with arguments. We use & operator or direct call.
# Using splatting for args.
python $JsonParserPath @ScriptArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "ParseAI: JSON Parser failed (Exit Code: $LASTEXITCODE)."
    exit $LASTEXITCODE
}

# 2. Run the Markdown Extractor
Write-Host "Running Code Extraction..."

if (Test-Path $OutputDir) {
    $MdFiles = Get-ChildItem -Path $OutputDir -Filter "*.md" -Recurse
    $MarkdownExtractorPath = Join-Path $AppsDir "markdown_extractor.py"
    
    foreach ($File in $MdFiles) {
        Write-Host "Extracting code from: $($File.FullName)"
        
        # Pass the file path first, then the rest of the original arguments
        python $MarkdownExtractorPath $File.FullName @ScriptArgs
               
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ParseAI: Markdown extractor failed for $($File.FullName)."
            # Continue processing other files
        }
    }
}
else {
    Write-Host "ParseAI: Output directory not found: $OutputDir. Skipping markdown extraction."
}

Write-Host "ParseAI completed successfully."
