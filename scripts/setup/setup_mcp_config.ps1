# MACHO-GPT MCP Server Configuration Script
# Version: 3.4-mini
# Date: 2025-10-24

Write-Host "`n=== MACHO-GPT MCP Server Setup ===" -ForegroundColor Cyan
Write-Host "Configuring Claude Desktop MCP servers...`n" -ForegroundColor Gray

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$logiOntolPath = "C:\logi_ontol"

# Step 1: Verify logi_ontol exists
Write-Host "[1/5] Verifying directories..." -ForegroundColor Yellow
if (-not (Test-Path $logiOntolPath)) {
    Write-Host "ERROR: C:\logi_ontol does not exist!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ C:\logi_ontol found" -ForegroundColor Green

# Step 2: Backup existing config
Write-Host "`n[2/5] Backing up existing configuration..." -ForegroundColor Yellow
if (Test-Path $configPath) {
    $backupPath = "$configPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $configPath $backupPath -Force
    Write-Host "  ✓ Backup created: $backupPath" -ForegroundColor Green
} else {
    Write-Host "  ! No existing config found" -ForegroundColor Gray
}

# Step 3: Create config directory
Write-Host "`n[3/5] Preparing configuration directory..." -ForegroundColor Yellow
$configDir = Split-Path $configPath -Parent
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "  ✓ Created directory: $configDir" -ForegroundColor Green
} else {
    Write-Host "  ✓ Directory exists: $configDir" -ForegroundColor Green
}

# Step 4: Create MCP configuration
Write-Host "`n[4/5] Creating MCP server configuration..." -ForegroundColor Yellow

$mcpConfig = @{
    mcpServers = @{
        filesystem = @{
            command = "npx"
            args = @(
                "-y"
                "@modelcontextprotocol/server-filesystem"
                "C:\Users\minky\Downloads"
                "C:\cursor-mcp"
                "C:\logi_ontol"
            )
        }
        "windows-mcp" = @{
            command = "uvx"
            args = @("windows-mcp")
        }
        "pdf-tools" = @{
            command = "uvx"
            args = @("mcp-server-pdftools")
        }
    }
}

$jsonConfig = $mcpConfig | ConvertTo-Json -Depth 10
$jsonConfig | Set-Content -Path $configPath -Encoding UTF8

Write-Host "  ✓ Configuration saved to: $configPath" -ForegroundColor Green

# Step 5: Display configuration
Write-Host "`n[5/5] Configuration summary:" -ForegroundColor Yellow
Write-Host $jsonConfig -ForegroundColor Gray

# Final instructions
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host @"

✓ MCP servers configured:
  - filesystem: Access to C:\logi_ontol
  - windows-mcp: System control capabilities
  - pdf-tools: PDF processing

📋 Next steps:
  1. CLOSE Claude Desktop completely (Task Manager if needed)
  2. RESTART Claude Desktop
  3. Start a NEW conversation
  4. Test with: /logi-meta

⚠️  Important:
  - You MUST restart Claude Desktop for changes to take effect
  - Existing conversations won't have the new configuration
  - Check logs if issues occur: $env:APPDATA\Claude\logs

🔧 Recommended test commands:
  /logi-master invoice-audit    # Test file access
  /visualize_data              # Test data processing
  /check_KPI                   # Test KPI dashboard

"@ -ForegroundColor White

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
