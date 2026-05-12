$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -Raw (Join-Path $root "skill.manifest.json") | ConvertFrom-Json
$readme = Get-Content -Raw (Join-Path $root "README.md")
$compat = Get-Content -Raw (Join-Path $root "COMPATIBILITY.md")
$openai = Get-Content -Raw (Join-Path $root "agents/openai.yaml")
$skill = Get-Content -Raw (Join-Path $root "SKILL.md")
$agents = Get-Content -Raw (Join-Path $root "AGENTS.md")
$claude = Get-Content -Raw (Join-Path $root "CLAUDE.md")

$expected = @{
  codex_skill = "SKILL.md"
  codex_workspace = "AGENTS.md"
  claude_code = "CLAUDE.md"
  openai_agent = "agents/openai.yaml"
  compatibility = "COMPATIBILITY.md"
}

foreach ($pair in $expected.GetEnumerator()) {
  if ($manifest.entrypoints.PSObject.Properties[$pair.Key].Value -ne $pair.Value) { throw "Manifest entrypoint mismatch: $($pair.Key)" }
  if (-not (Test-Path (Join-Path $root $pair.Value))) { throw "Missing file: $($pair.Value)" }
}

if (-not $manifest.compatibility.codex_skill -or -not $manifest.compatibility.codex_workspace -or -not $manifest.compatibility.claude_code) { throw "Manifest compatibility flags are incomplete." }
if ($manifest.compatibility.host_native_parity) { throw "host_native_parity must stay false." }
if (-not $manifest.identity.non_workflow) { throw "Manifest must remain non_workflow." }

$markers = @(
  @{ Name = 'README Codex skill'; Text = 'Codex skill-install use, the entry file is `SKILL.md`.' },
  @{ Name = 'README Codex workspace'; Text = 'the host contract file is `AGENTS.md`.' },
  @{ Name = 'README Claude Code'; Text = 'For Claude Code, the host contract file is `CLAUDE.md`.' },
  @{ Name = 'COMPATIBILITY structural claim'; Text = 'structurally compatible with the Codex skill entrypoint `SKILL.md`' },
  @{ Name = 'OpenAI adapter note'; Text = 'optional host adapter, not a second runtime shell' },
  @{ Name = 'SKILL route generator guard'; Text = 'They must not grow into a route generator, solve script, or answer machine.' },
  @{ Name = 'AGENTS host boundary'; Text = 'This file is a host-side boundary, not a router.' },
  @{ Name = 'CLAUDE host boundary'; Text = 'This file is a host-side boundary, not a control surface.' }
)

foreach ($marker in $markers) {
  $haystack = switch ($marker.Name) {
    { $_ -like "README*" } { $readme; break }
    { $_ -like "COMPATIBILITY*" } { $compat; break }
    { $_ -like "OpenAI*" } { $openai; break }
    { $_ -like "SKILL*" } { $skill; break }
    { $_ -like "AGENTS*" } { $agents; break }
    { $_ -like "CLAUDE*" } { $claude; break }
    default { throw "No haystack mapping for marker: $($marker.Name)" }
  }
  if (-not $haystack.Contains($marker.Text)) { throw "Missing marker: $($marker.Name)" }
}

Write-Output "Host-contract consistency check passed."
