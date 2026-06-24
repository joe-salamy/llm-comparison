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
    ".omp/skill-usage.json",
    "compare_models_template.py",
    "index.html",
    "results.csv"
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
    "index.html",
    "results.csv",
    "compare_models.py",
    "compare_models_core.py",
    "compare_models_template.py",
    "README.md",
    ".gitignore"
)

foreach ($path in $publicFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $path))) {
        throw "Required public file is missing on ${sourceBranch}: $path"
    }
}

$branchExists = git show-ref --verify --quiet "refs/heads/$PagesBranch"
if ($LASTEXITCODE -eq 0) {
    Run-Git switch $PagesBranch
} else {
    Run-Git switch --orphan $PagesBranch
}

Get-ChildItem -LiteralPath $repoRoot -Force |
    Where-Object { $_.Name -ne ".git" } |
    Remove-Item -Recurse -Force

foreach ($path in $publicFiles) {
    Run-Git checkout $sourceBranch -- $path
}

Run-Git add -A

$pending = git status --porcelain
if (-not $pending) {
    Write-Host "No GitHub Pages changes to commit."
    exit 0
}

Run-Git commit -m $CommitMessage

Write-Host "Updated $PagesBranch from $sourceBranch."
Write-Host "Review the branch, then run: git push -u origin $PagesBranch"
