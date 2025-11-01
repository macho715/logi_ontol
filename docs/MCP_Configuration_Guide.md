# Claude Desktop MCP Configuration Guide

## Overview

This guide explains how to configure Claude Desktop with Model Context Protocol (MCP) servers for the logi_ontol project. The configuration enables Claude to access project files, system tools, and external services.

## Configuration Files

- **Active Config**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Project Backup**: `C:\logi_ontol\claude_desktop_config.json`

## MCP Servers Configured

### 1. AWS MCP Server
- **Purpose**: AWS services integration
- **Command**: Python script execution
- **Environment**: AWS credentials and logging configuration

### 2. Filesystem Server
- **Purpose**: File system access for project directories
- **Command**: `npx @modelcontextprotocol/server-filesystem`
- **Accessible Paths**:
  - `C:\Users\minky\Downloads`
  - `C:\cursor-mcp`
  - `C:\logi_ontol` (project root)

### 3. Windows MCP Server
- **Purpose**: Windows system operations
- **Command**: `uvx windows-mcp`

### 4. PDF Tools Server
- **Purpose**: PDF processing and analysis
- **Command**: `uvx mcp-server-pdftools`

## Manual Configuration Steps

### Method 1: File Explorer (Recommended)

1. **Open Claude Config Directory**
   ```
   Windows Key + R
   Type: %APPDATA%\Claude
   Press Enter
   ```

2. **Edit Configuration**
   - Open `claude_desktop_config.json` in a text editor
   - Replace content with the configuration from `C:\logi_ontol\claude_desktop_config.json`

3. **Restart Claude Desktop**
   - Close Claude Desktop completely
   - Reopen Claude Desktop

### Method 2: PowerShell (Advanced)

```powershell
# Copy project config to active location
Copy-Item "C:\logi_ontol\claude_desktop_config.json" "$env:APPDATA\Claude\claude_desktop_config.json" -Force

# Restart Claude Desktop (if running)
Get-Process "Claude Desktop" | Stop-Process -Force
Start-Process "Claude Desktop"
```

## Verification

### 1. JSON Validation
```powershell
# Validate active config
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" | ConvertFrom-Json

# Validate project backup
Get-Content "C:\logi_ontol\claude_desktop_config.json" | ConvertFrom-Json
```

### 2. Path Verification
```powershell
# Check all referenced paths exist
Test-Path "C:\Users\minky\Downloads"
Test-Path "C:\cursor-mcp"
Test-Path "C:\logi_ontol"
```

### 3. MCP Server Status
- Open Claude Desktop
- Check if MCP servers are listed in the interface
- Verify file system access to project directories

## Troubleshooting

### Common Issues

1. **JSON Syntax Errors**
   - Use a JSON validator to check syntax
   - Ensure proper escaping of backslashes in Windows paths

2. **Path Not Found**
   - Verify all referenced directories exist
   - Check for typos in path names

3. **MCP Servers Not Loading**
   - Restart Claude Desktop completely
   - Check if required tools (npx, uvx) are installed
   - Verify network connectivity for package downloads

4. **Permission Issues**
   - Run Claude Desktop as administrator if needed
   - Check file permissions on configuration directory

### Fallback Configuration

If the automated configuration fails, use this minimal configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\logi_ontol"
      ]
    }
  }
}
```

## Maintenance

### Synchronizing Configurations

To keep both configuration files in sync:

```powershell
# Copy active config to project backup
Copy-Item "$env:APPDATA\Claude\claude_desktop_config.json" "C:\logi_ontol\claude_desktop_config.json" -Force

# Or copy project config to active location
Copy-Item "C:\logi_ontol\claude_desktop_config.json" "$env:APPDATA\Claude\claude_desktop_config.json" -Force
```

### Backup Recommendations

- Keep the project backup config in version control
- Document any manual changes to the active config
- Test configuration changes in a development environment first

## Security Notes

- AWS credentials are stored in the configuration file
- Keep the configuration file secure and do not share publicly
- Consider using environment variables for sensitive credentials
- Regularly rotate AWS access keys

## Support

For issues with MCP configuration:
1. Check Claude Desktop logs
2. Verify all dependencies are installed
3. Test with minimal configuration first
4. Consult Claude Desktop documentation for MCP server requirements
