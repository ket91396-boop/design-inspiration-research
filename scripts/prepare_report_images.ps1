param(
  [Parameter(Mandatory=$true)][string]$InputJson,
  [Parameter(Mandatory=$true)][string]$OutputJson,
  [string]$AssetsDir,
  [ValidateSet("extract", "hybrid", "screenshot")][string]$ImageMode = "screenshot",
  [int]$TimeoutSeconds = 18
)

$ErrorActionPreference = "Stop"

function Find-Browser {
  $commands = @("chrome.exe", "msedge.exe")
  foreach ($cmd in $commands) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
  }

  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:LocalAppData\Microsoft\Edge\Application\msedge.exe"
  )
  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
  }
  return $null
}

function Slugify($Value, $Fallback) {
  $slug = ([string]$Value).ToLowerInvariant() -replace "[^a-z0-9]+", "-"
  $slug = $slug.Trim("-")
  if (-not $slug) { $slug = $Fallback }
  if ($slug.Length -gt 60) { $slug = $slug.Substring(0, 60).Trim("-") }
  return $slug
}

function Make-Relative($Path, $BaseDir) {
  $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
  $resolvedBase = (Resolve-Path -LiteralPath $BaseDir).Path
  $baseUri = [Uri]($resolvedBase.TrimEnd("\") + "\")
  $pathUri = [Uri]$resolvedPath
  return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace("/", "\")
}

function Capture-Screenshot($Browser, $Url, $Target, $TimeoutSeconds) {
  $targetDir = Split-Path -Parent $Target
  New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

  $args = @(
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--window-size=1365,1000",
    "--timeout=$($TimeoutSeconds * 1000)",
    "--screenshot=$Target",
    $Url
  )
  $process = Start-Process -FilePath $Browser -ArgumentList $args -Wait -PassThru -WindowStyle Hidden
  if ($process.ExitCode -ne 0) { return "browser exit code $($process.ExitCode)" }
  if (-not (Test-Path -LiteralPath $Target)) { return "screenshot file was not created" }
  if ((Get-Item -LiteralPath $Target).Length -eq 0) { return "screenshot file is empty" }
  return ""
}

function Set-JsonProperty($Object, $Name, $Value) {
  if ($Object.PSObject.Properties[$Name]) {
    $Object.$Name = $Value
  } else {
    $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
  }
}

$inputPath = (Resolve-Path -LiteralPath $InputJson).Path
$outputPath = $OutputJson
$outputDir = Split-Path -Parent $outputPath
if ($outputDir) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }
if (-not $AssetsDir) { $AssetsDir = Join-Path $outputDir "report-assets" }
New-Item -ItemType Directory -Path $AssetsDir -Force | Out-Null

$data = Get-Content -LiteralPath $inputPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not ($data.references -is [System.Array])) {
  throw "Input JSON must contain a references array."
}

$browser = Find-Browser
$index = 0
foreach ($ref in $data.references) {
  $index += 1
  $ref | Add-Member -NotePropertyName "_image_status" -NotePropertyValue "missing" -Force

  if ($ImageMode -ne "screenshot") {
    # PowerShell fallback intentionally keeps extract/hybrid conservative.
    # Use the Python script when exact same-page image extraction is required.
    continue
  }

  $url = [string]$ref.url
  if (-not $url) {
    Set-JsonProperty $ref "_image_error" "no reference page URL for screenshot"
    continue
  }
  if (-not $browser) {
    Set-JsonProperty $ref "_image_error" "Chrome or Edge was not found for screenshot mode"
    continue
  }

  $title = if ($ref.title) { [string]$ref.title } elseif ($ref.title_zh) { [string]$ref.title_zh } else { "reference-$index" }
  $fileName = "{0:D2}-{1}-page.png" -f $index, (Slugify $title "reference-$index")
  $target = Join-Path $AssetsDir $fileName
  $errorMessage = Capture-Screenshot $browser $url $target $TimeoutSeconds
  if ($errorMessage) {
    Set-JsonProperty $ref "_image_error" $errorMessage
    Set-JsonProperty $ref "image" ""
  } else {
    Set-JsonProperty $ref "image" (Make-Relative $target $outputDir)
    $ref._image_status = "screenshot"
    Set-JsonProperty $ref "_image_source" $url
  }
}

$data | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outputPath -Encoding UTF8
$withImages = @($data.references | Where-Object { $_.image }).Count
Write-Host "Prepared $withImages/$($data.references.Count) reference previews -> $outputPath"


