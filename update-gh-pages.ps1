param(
    [string]$PagesBranch = "gh-pages",
    [string]$CommitMessage = "Update GitHub Pages site",
    [string]$SourceCommitMessage = "Update generated analysis outputs"
)

$ErrorActionPreference = "Stop"

function Run-Git {
    git @args
    if ($LASTEXITCODE -ne 0) {
        throw "git $args failed"
    }
}

function Get-StatusPath {
    param([string]$StatusLine)

    $path = $StatusLine.Substring(3)
    if ($path -like "* -> *") {
        return ($path -split " -> ", 2)[1]
    }

    return $path
}

$repoRoot = git rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) {
    throw "Run this script from inside a git repository."
}

Set-Location $repoRoot

$sourceBranch = git branch --show-current
if (-not $sourceBranch) {
    throw "Could not determine the current source branch."
}
if ($sourceBranch -eq $PagesBranch) {
    throw "Run this script from the source branch, not $PagesBranch."
}

$generatedFiles = @(
    "src/llm_comparison/compare_models_template.py",
    "public/index.html",
    "data/results.csv"
)

$status = @(git status --porcelain)
if ($status.Count -gt 0) {
    $dirtyPaths = @($status | ForEach-Object { Get-StatusPath $_ } | Select-Object -Unique)
    $unexpectedPaths = @($dirtyPaths | Where-Object { $generatedFiles -notcontains $_ })

    if ($unexpectedPaths.Count -gt 0) {
        throw "Working tree has changes outside generated analysis files: $($unexpectedPaths -join ', ')"
    }

    Run-Git add -- $generatedFiles
    $generatedStatus = @(git status --porcelain -- $generatedFiles)
    if ($generatedStatus.Count -gt 0) {
        Run-Git commit -m $SourceCommitMessage
    }
}

$status = @(git status --porcelain)
if ($status.Count -gt 0) {
    throw "Working tree must be clean before publishing."
}

$publicFiles = @(
    @{ Source = "public/index.html"; Destination = "index.html" },
    @{ Source = "data/results.csv"; Destination = "results.csv" },
    @{ Source = "src/llm_comparison/compare_models.py"; Destination = "compare_models.py" },
    @{ Source = "src/llm_comparison/compare_models_core.py"; Destination = "compare_models_core.py" },
    @{ Source = "src/llm_comparison/compare_models_template.py"; Destination = "compare_models_template.py" },
    @{ Source = "README.md"; Destination = "README.md" },
    @{ Source = ".gitignore"; Destination = ".gitignore" }
)

foreach ($file in $publicFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $file.Source))) {
        throw "Required public file is missing on ${sourceBranch}: $($file.Source)"
    }
}

$branchExists = git show-ref --verify --quiet "refs/heads/$PagesBranch"
try {
    if ($LASTEXITCODE -eq 0) {
        Run-Git switch $PagesBranch
    } else {
        Run-Git switch --orphan $PagesBranch
    }

    Get-ChildItem -LiteralPath $repoRoot -Force |
        Where-Object { $_.Name -ne ".git" } |
        Remove-Item -Recurse -Force

    foreach ($file in $publicFiles) {
        Run-Git checkout $sourceBranch -- $file.Source

        $sourcePath = Join-Path $repoRoot $file.Source
        $destinationPath = Join-Path $repoRoot $file.Destination
        $destinationDir = Split-Path -Parent $destinationPath
        if ($destinationDir -and -not (Test-Path -LiteralPath $destinationDir)) {
            New-Item -ItemType Directory -Path $destinationDir | Out-Null
        }
        if ($sourcePath -ne $destinationPath) {
            Move-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
        }
    }

    foreach ($path in @("src", "public", "data")) {
        $publishPath = Join-Path $repoRoot $path
        if (Test-Path -LiteralPath $publishPath) {
            Remove-Item -LiteralPath $publishPath -Recurse -Force
        }
    }

    Run-Git add -A

    $pending = git status --porcelain
    if (-not $pending) {
        Write-Host "No GitHub Pages changes to commit."
    } else {
        Run-Git commit -m $CommitMessage

        Write-Host "Updated $PagesBranch from $sourceBranch."
    }

    Run-Git push -u origin $PagesBranch
    Write-Host "Pushed $PagesBranch to origin."
} finally {
    Run-Git switch $sourceBranch
}
