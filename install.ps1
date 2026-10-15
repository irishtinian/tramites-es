#Requires -Version 5.1
<#
.SYNOPSIS
  Instala el skill tramites-es para tus agentes de IA (Windows).

.DESCRIPTION
  Copia la carpeta skills\tramites-es de este repositorio, sin enlaces simbolicos, en:
    %USERPROFILE%\.agents\skills\tramites-es     (Codex, Gemini CLI, OpenClaw, Cursor, Copilot... leen .agents\skills)
    %USERPROFILE%\.claude\skills\tramites-es     (Claude Code)
    %USERPROFILE%\.openclaw\skills\tramites-es   (solo si ya existe .openclaw\skills)
    %USERPROFILE%\.hermes\skills\tramites-es     (solo si ya existe .hermes\skills)

  Es para personas: muestra lo que va a copiar y pide confirmacion antes de tocar nada.
  No usa la red, no pide permisos de administrador y no escribe fuera de esas carpetas.
  Si ya habia una copia de tramites-es en un destino, la sustituye entera.

  Este fichero esta escrito solo en ASCII a proposito: Windows PowerShell 5.1 lee los .ps1
  sin BOM con la pagina de codigos del sistema y estropearia las tildes.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Skill = 'tramites-es'

function Fallo([string]$Mensaje) {
  Write-Host ('Error: {0}' -f $Mensaje) -ForegroundColor Red
  exit 1
}

$Origen = Join-Path (Join-Path $PSScriptRoot 'skills') $Skill
if (-not (Test-Path -LiteralPath (Join-Path $Origen 'SKILL.md') -PathType Leaf)) {
  Fallo ('no encuentro {0}. Ejecuta install.ps1 desde la carpeta del repositorio.' -f (Join-Path $Origen 'SKILL.md'))
}
$Origen = (Resolve-Path -LiteralPath $Origen).ProviderPath

$Casa = $env:USERPROFILE
if (-not $Casa) { $Casa = $HOME }
if (-not $Casa -or -not (Test-Path -LiteralPath $Casa -PathType Container)) {
  Fallo 'no encuentro tu carpeta personal (USERPROFILE).'
}

$EnWindows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
if ($EnWindows) {
  $Identidad = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  if ($Identidad.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Fallo 'no lo ejecutes como administrador: abre PowerShell normal (sin elevar) e instala el skill con tu usuario.'
  }
}

$Todo = @(Get-ChildItem -LiteralPath $Origen -Recurse -Force)
$Enlaces = @($Todo | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
if ($Enlaces.Count -gt 0) {
  Fallo ('la carpeta del skill contiene enlaces simbolicos o puntos de union y no se copian por seguridad: {0}' -f (($Enlaces | ForEach-Object { $_.FullName }) -join ', '))
}
$Ficheros = @($Todo | Where-Object { -not $_.PSIsContainer -and $_.FullName -notmatch '[\\/]__pycache__[\\/]' })

$Version = '?'
$Linea = Select-String -LiteralPath (Join-Path $Origen 'SKILL.md') -Pattern '^\s*version:\s*"?([^"\s]+)"?' | Select-Object -First 1
if ($Linea) { $Version = $Linea.Matches[0].Groups[1].Value }

$Destinos = New-Object System.Collections.Generic.List[string]
$Destinos.Add((Join-Path (Join-Path $Casa '.agents') 'skills'))
$Destinos.Add((Join-Path (Join-Path $Casa '.claude') 'skills'))
$Avisos = New-Object System.Collections.Generic.List[string]
foreach ($Agente in @('.openclaw', '.hermes')) {
  $CarpetaAgente = Join-Path $Casa $Agente
  $CarpetaSkills = Join-Path $CarpetaAgente 'skills'
  if (Test-Path -LiteralPath $CarpetaSkills -PathType Container) {
    $Destinos.Add($CarpetaSkills)
  } elseif (Test-Path -LiteralPath $CarpetaAgente -PathType Container) {
    $Avisos.Add(('existe {0} pero no {1}. Si quieres instalarlo alli, crea esa carpeta y vuelve a ejecutar install.ps1.' -f $CarpetaAgente, $CarpetaSkills))
  }
}

Write-Host ''
Write-Host ('tramites-es {0}: se copiaran {1} ficheros de' -f $Version, $Ficheros.Count)
Write-Host ('  {0}' -f $Origen)
Write-Host 'a estas carpetas:'
foreach ($Destino in $Destinos) {
  $Final = Join-Path $Destino $Skill
  if (Get-Item -LiteralPath $Final -Force -ErrorAction SilentlyContinue) {
    Write-Host ('  {0}   (ya existe: se sustituira)' -f $Final)
  } else {
    Write-Host ('  {0}' -f $Final)
  }
}
Write-Host ''
Write-Host 'Ficheros:'
$Ficheros | ForEach-Object { $_.FullName.Substring($Origen.Length).TrimStart('\', '/') } | Sort-Object | ForEach-Object { Write-Host ('  {0}' -f $_) }
foreach ($Aviso in $Avisos) { Write-Host ('Aviso: {0}' -f $Aviso) -ForegroundColor Yellow }
Write-Host ''

if ([Console]::IsInputRedirected -or -not [Environment]::UserInteractive) {
  Fallo 'hace falta una consola interactiva para confirmar. Ejecuta install.ps1 desde PowerShell.'
}
$Respuesta = Read-Host 'Continuar? [s/N]'
if ($Respuesta -notmatch '^\s*(s|si|y|yes)\s*$') {
  Write-Host 'Cancelado. No se ha copiado nada.'
  exit 0
}

foreach ($Destino in $Destinos) {
  $Final = Join-Path $Destino $Skill
  $Temporal = Join-Path $Destino ('.{0}.nuevo.{1}' -f $Skill, $PID)
  try {
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null
    if (Test-Path -LiteralPath $Temporal) { Remove-Item -LiteralPath $Temporal -Recurse -Force }
    Copy-Item -LiteralPath $Origen -Destination $Temporal -Recurse -Force
    @(Get-ChildItem -LiteralPath $Temporal -Recurse -Force -Directory -Filter '__pycache__') | Remove-Item -Recurse -Force
    $Existente = Get-Item -LiteralPath $Final -Force -ErrorAction SilentlyContinue
    if ($Existente) {
      if ($Existente.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        $Existente.Delete()   # si era un enlace, se borra el enlace, no su destino
      } else {
        Remove-Item -LiteralPath $Final -Recurse -Force
      }
    }
    Rename-Item -LiteralPath $Temporal -NewName $Skill
  } catch {
    if (Test-Path -LiteralPath $Temporal) { Remove-Item -LiteralPath $Temporal -Recurse -Force -ErrorAction SilentlyContinue }
    Fallo ('no se pudo instalar en {0}: {1}' -f $Final, $_.Exception.Message)
  }
  Write-Host ('OK  {0}' -f $Final) -ForegroundColor Green
}

Write-Host ''
Write-Host 'Hecho. Reinicia tu agente para que cargue el skill.'
Write-Host 'Despues, pidele: "comprueba el entorno de tramites-es" (ejecutara scripts\entorno.py).'
Write-Host ('El certificado lo configuras tu en tu terminal: lee skills\{0}\references\setup-windows.md.' -f $Skill)
