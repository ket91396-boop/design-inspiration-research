param(
  [Parameter(Mandatory=$true)][string]$InputJson,
  [Parameter(Mandatory=$true)][string]$OutputHtml
)

$ErrorActionPreference = "Stop"

function HtmlEscape($Value) {
  return [System.Net.WebUtility]::HtmlEncode([string]$Value)
}

function AsArray($Value) {
  if ($null -eq $Value) { return @() }
  if ($Value -is [System.Array]) { return @($Value) }
  return @($Value)
}

function TextList($Items) {
  $values = @(AsArray $Items | Where-Object { "$_".Trim() })
  if ($values.Count -eq 0) { return '<span class="muted">未指定</span>' }
  return "<ul>" + (($values | ForEach-Object { "<li>$(HtmlEscape $_)</li>" }) -join "") + "</ul>"
}

function CommaList($Items) {
  $values = @(AsArray $Items | Where-Object { "$_".Trim() })
  if ($values.Count -eq 0) { return '<span class="muted">未指定</span>' }
  return (($values | ForEach-Object { HtmlEscape $_ }) -join "、")
}

function LabelValue($Key, $Value) {
  $text = ([string]$Value).ToLowerInvariant()
  if ($Key -eq "source_quality") {
    if ($text -eq "primary") { return "主要来源" }
    if ($text -eq "secondary") { return "辅助来源" }
    if ($text -eq "supplement") { return "补充参考" }
  }
  if ($Key -eq "quality_tier") {
    if ($text -eq "green") { return "可借鉴" }
    if ($text -eq "yellow") { return "需转化" }
    if ($text -eq "red") { return "避坑参考" }
  }
  if ($Key -eq "copyright_risk") {
    if ($text -eq "low") { return "低风险" }
    if ($text -eq "medium") { return "中风险" }
    if ($text -eq "high") { return "高风险" }
  }
  return [string]$Value
}

function Get-ImageSrc($Image, $JsonDir) {
  $imageText = [string]$Image
  if (-not $imageText.Trim()) { return "" }
  if ($imageText -match '^https?://') { return $imageText }
  $path = if ([System.IO.Path]::IsPathRooted($imageText)) { $imageText } else { Join-Path $JsonDir $imageText }
  if (-not (Test-Path -LiteralPath $path)) { return "" }
  $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $path))
  $ext = [System.IO.Path]::GetExtension($path).ToLowerInvariant()
  $mime = switch ($ext) {
    ".png" { "image/png" }
    ".jpg" { "image/jpeg" }
    ".jpeg" { "image/jpeg" }
    ".webp" { "image/webp" }
    ".gif" { "image/gif" }
    default { "image/png" }
  }
  return "data:$mime;base64,$([Convert]::ToBase64String($bytes))"
}

function Section($Title, $Body) {
  return "<section><h2>$(HtmlEscape $Title)</h2>$Body</section>"
}

$jsonPath = (Resolve-Path -LiteralPath $InputJson).Path
$jsonDir = Split-Path -Parent $jsonPath
$data = Get-Content -LiteralPath $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

$title = if ($data.title) { [string]$data.title } else { "Design Inspiration Research" }
$subtitle = if ($data.subtitle) { [string]$data.subtitle } else { "Sourced references, visual analysis, directions, and prompts." }
$brief = if ($data.brief) { $data.brief } else { @{} }

$facts = @(
  @("产物类型", $brief.artifact_type),
  @("使用场景", $brief.use_context),
  @("受众 / 气质", $brief.audience_tone)
)
$factHtml = ""
foreach ($field in $facts) {
  $factHtml += "<div class=""fact""><span>$(HtmlEscape $field[0])</span><strong>$(HtmlEscape $field[1])</strong></div>"
}
$factHtml += "<div class=""fact wide""><span>核心符号</span>$(TextList $brief.core_symbols)</div>"
$factHtml += "<div class=""fact wide""><span>视觉风险</span>$(TextList $brief.visual_risks)</div>"
$briefHtml = '<div class="facts">' + $factHtml + '</div>'

$keywordHtml = ""
foreach ($item in AsArray $data.keywords) {
  $keywordHtml += "<article><h3>$(HtmlEscape $item.category) <small>$(HtmlEscape $item.priority)</small></h3><p><b>中文：</b>$(CommaList $item.zh)</p><p><b>English：</b>$(CommaList $item.en)</p><p><b>限定站点：</b>$(CommaList $item.site)</p></article>"
}
if (-not $keywordHtml) { $keywordHtml = '<p class="muted">暂无关键词。</p>' } else { $keywordHtml = '<div class="kw">' + $keywordHtml + '</div>' }

$referenceHtml = ""
foreach ($ref in AsArray $data.references) {
  $displayTitle = if ($ref.title_zh) { [string]$ref.title_zh } elseif ($ref.zh) { [string]$ref.zh } elseif ($ref.title) { [string]$ref.title } else { "未命名参考" }
  $rawTitle = if ($ref.title) { [string]$ref.title } else { "" }
  $url = if ($ref.url) { [string]$ref.url } else { "" }
  $src = Get-ImageSrc $ref.image $jsonDir
  $preview = if ($src) {
    "<a class=""thumb"" href=""$(HtmlEscape $url)"" target=""_blank"" rel=""noreferrer""><img src=""$src"" alt=""$(HtmlEscape $displayTitle)""><span>视觉预览</span></a>"
  } else {
    $message = if ($ref._image_error) { [string]$ref._image_error } else { "保留高质量来源链接，不使用无关缩略图替代。" }
    "<div class=""thumb placeholder""><strong>预览不可用</strong><small>$(HtmlEscape $message)</small><a href=""$(HtmlEscape $url)"" target=""_blank"">打开原始页面</a></div>"
  }
  $chips = ""
  foreach ($pair in @(@("来源", "source_quality"), @("分级", "quality_tier"), @("版权风险", "copyright_risk"))) {
    $value = $ref.($pair[1])
    if ($value) { $chips += "<span class=""chip"">$($pair[0])：$(HtmlEscape (LabelValue $pair[1] $value))</span>" }
  }
  $referenceHtml += "<article class=""ref-card"">$preview<div class=""ref-body""><p class=""source"">$(HtmlEscape $ref.source) · $(HtmlEscape $ref.category)</p><h3><a href=""$(HtmlEscape $url)"" target=""_blank"">$(HtmlEscape $displayTitle)</a></h3><p class=""original"">$(HtmlEscape $rawTitle)</p><div class=""chips"">$chips</div><p><b>可借鉴：</b>$(CommaList $ref.borrowable_parts)</p><p><b>怎么借：</b>$(HtmlEscape $ref.borrow)</p><p><b>别照抄：</b>$(HtmlEscape $ref.avoid)</p></div></article>"
}
if (-not $referenceHtml) { $referenceHtml = '<p class="muted">暂无参考。</p>' } else { $referenceHtml = '<div class="refs">' + $referenceHtml + '</div>' }

$deconstructionHtml = ""
$labels = @{
  composition = "构图"; type = "字体 / 字形"; color = "配色"; motifs = "符号";
  texture = "质感"; mood = "气质"; application = "应用"
}
foreach ($key in @("composition", "type", "color", "motifs", "texture", "mood", "application")) {
  if ($data.deconstruction.$key) {
    $deconstructionHtml += "<div class=""block""><h3>$(HtmlEscape $labels[$key])</h3>$(TextList $data.deconstruction.$key)</div>"
  }
}
if (-not $deconstructionHtml) { $deconstructionHtml = '<p class="muted">暂无审美拆解。</p>' } else { $deconstructionHtml = '<div class="analysis">' + $deconstructionHtml + '</div>' }

$directionHtml = ""
$index = 0
foreach ($direction in AsArray $data.directions) {
  $index += 1
  $directionHtml += "<article class=""direction""><span class=""num"">$($index.ToString("00"))</span><h3>$(HtmlEscape $direction.name)</h3><p><b>适合场景：</b>$(HtmlEscape $direction.best_use_case)</p><p><b>视觉关键词：</b>$(CommaList $direction.visual_keywords)</p><p><b>参考依据：</b>$(HtmlEscape $direction.reference_basis)</p><p><b>构图建议：</b>$(HtmlEscape $direction.composition_advice)</p><p><b>字体建议：</b>$(HtmlEscape $direction.type_advice)</p><p><b>配色建议：</b>$(HtmlEscape $direction.color_advice)</p><p><b>图形 / 质感：</b>$(HtmlEscape $direction.graphic_texture_advice)</p><p><b>今天怎么做：</b></p>$(TextList $direction.execution_steps)</article>"
}
if (-not $directionHtml) { $directionHtml = '<p class="muted">暂无设计方向。</p>' } else { $directionHtml = '<div class="directions">' + $directionHtml + '</div>' }

$promptHtml = ""
foreach ($prompt in AsArray $data.prompts) {
  $promptHtml += "<article class=""prompt""><h3>$(HtmlEscape $prompt.direction)</h3><p class=""source"">$(HtmlEscape $prompt.artifact_type)</p><pre>$(HtmlEscape $prompt.prompt)</pre><p><b>负面提示：</b>$(HtmlEscape $prompt.negative_prompt)</p></article>"
}
if (-not $promptHtml) { $promptHtml = '<p class="muted">暂无提示词。</p>' } else { $promptHtml = '<div class="prompts">' + $promptHtml + '</div>' }

$notesHtml = (TextList $data.copyright_notes)
if ($data.next_prompt) { $notesHtml += "<h3>下一步提示词</h3><div class=""prompt""><pre>$(HtmlEscape $data.next_prompt)</pre></div>" }

$body = ""
$body += Section "需求简析" $briefHtml
$body += Section "搜索关键词" $keywordHtml
$body += Section "视觉参考" $referenceHtml
$body += Section "审美拆解" $deconstructionHtml
$body += Section "可执行设计方向" $directionHtml
$body += Section "AI 生图提示词" $promptHtml
$body += Section "版权与下一步" $notesHtml

$html = @"
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$(HtmlEscape $title)</title>
<style>
:root{--ink:#171717;--muted:#6f685f;--paper:#f7efe3;--panel:#fffaf1;--line:#ded1bd;--accent:#c85932;--blue:#223b5f;--green:#2e725f}*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:linear-gradient(90deg,rgba(23,23,23,.04) 1px,transparent 1px),linear-gradient(rgba(23,23,23,.035) 1px,transparent 1px),var(--paper);background-size:28px 28px}main{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:44px 0 72px}header{min-height:48vh;display:grid;align-content:end;padding:56px 0 38px;border-bottom:2px solid var(--ink)}.kicker{margin:0 0 16px;color:var(--accent);font-size:.78rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase}h1{max-width:980px;margin:0;font-family:ui-serif,Georgia,"Times New Roman",serif;font-size:clamp(3rem,8vw,7rem);line-height:.92;letter-spacing:0}.subtitle{max-width:760px;margin:20px 0 0;color:var(--muted);font-size:1.06rem;line-height:1.7}section{padding:34px 0;border-bottom:1px solid var(--line)}h2{margin:0 0 18px;font-size:1.35rem}h3{margin:0 0 8px}p{line-height:1.64}a{color:var(--blue);text-decoration-thickness:1px;text-underline-offset:3px}.facts,.analysis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.fact,.block,.direction,.prompt,.ref-card{border:1px solid var(--line);background:rgba(255,250,241,.9)}.fact{min-height:108px;padding:16px}.fact span,.source{display:block;margin:0 0 8px;color:var(--muted);font-size:.78rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase}.fact strong{font-size:1.04rem;line-height:1.45}.wide{grid-column:1/-1}.kw{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.kw article{padding:15px;border:1px solid var(--line);background:var(--panel)}ul{margin:8px 0 0;padding-left:1.1rem}li{margin:5px 0;line-height:1.45}.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.ref-card{display:grid;grid-template-columns:210px minmax(0,1fr);min-height:210px;overflow:hidden}.thumb{position:relative;display:block;width:100%;height:100%;min-height:210px;background:#eadfce}.thumb img{width:100%;height:100%;object-fit:cover;display:block}.thumb span{position:absolute;left:8px;bottom:8px;padding:4px 8px;background:rgba(23,23,23,.74);color:#fff;font-size:.72rem;font-weight:850}.placeholder{display:grid;align-content:center;justify-items:center;gap:8px;padding:16px;text-align:center;color:var(--muted);font-weight:800}.ref-body,.block,.direction,.prompt{padding:16px}.original{margin:-2px 0 8px;color:var(--muted);font-size:.84rem}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 10px}.chip{display:inline-flex;border:1px solid var(--line);background:#f8f2e8;padding:3px 8px;font-size:.76rem;font-weight:850;color:var(--muted)}.directions,.prompts{display:grid;gap:14px}.direction{position:relative;padding-left:62px}.num{position:absolute;left:16px;top:16px;color:var(--green);font-weight:950}.prompt pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:10px 0 0;padding:14px;border:1px solid var(--line);background:#f9f4ec;font:.92rem/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}@media(max-width:860px){header{min-height:38vh}.facts,.analysis,.kw,.refs{grid-template-columns:1fr}.ref-card{grid-template-columns:1fr}.direction{padding-left:16px}.num{position:static;display:block;margin-bottom:8px}}
</style>
</head>
<body>
<main>
<header><p class="kicker">Design Inspiration Research</p><h1>$(HtmlEscape $title)</h1><p class="subtitle">$(HtmlEscape $subtitle)</p></header>
$body
</main>
</body>
</html>
"@

$outputDir = Split-Path -Parent $OutputHtml
if ($outputDir) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }
[System.IO.File]::WriteAllText($OutputHtml, $html, [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote $OutputHtml"

