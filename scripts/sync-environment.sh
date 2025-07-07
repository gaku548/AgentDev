#!/bin/bash
# AgentDev Environment Synchronization Script
# Keeps both directories in sync for development

set -e

MAIN_DIR="/mnt/c/AgentDev"
WORK_DIR="/mnt/c/Users/kota_/AgentDev"

echo "🔄 Synchronizing AgentDev Environment..."

# Ensure both directories exist
mkdir -p "$MAIN_DIR" "$WORK_DIR"

# Function to sync files bidirectionally
sync_files() {
    local source="$1"
    local target="$2"
    local description="$3"
    
    echo "📂 $description"
    
    # Sync configuration files
    if [ -f "$source/CLAUDE.md" ] && [ ! -f "$target/CLAUDE.md" ]; then
        cp "$source/CLAUDE.md" "$target/"
        echo "  ✅ Copied CLAUDE.md"
    fi
    
    # Sync project files (bidirectional)
    for dir in mcp-servers mcp-tools config scripts tests projects; do
        if [ -d "$source/$dir" ] && [ ! -d "$target/$dir" ]; then
            cp -r "$source/$dir" "$target/"
            echo "  ✅ Copied $dir/"
        fi
    done
}

# Sync from work directory to main directory
sync_files "$WORK_DIR" "$MAIN_DIR" "Work → Main"

# Sync from main directory to work directory  
sync_files "$MAIN_DIR" "$WORK_DIR" "Main → Work"

# Create symbolic links for Python environment access
if [ -d "$MAIN_DIR/claude-env" ] && [ ! -L "$WORK_DIR/claude-env" ]; then
    ln -sf "$MAIN_DIR/claude-env" "$WORK_DIR/claude-env"
    echo "  ✅ Linked Python environment"
fi

# Create environment activation script
cat > "$WORK_DIR/activate-dev.sh" << 'EOF'
#!/bin/bash
# AgentDev Environment Activation Script

export AGENTDEV_ROOT="/mnt/c/AgentDev"
export AGENTDEV_WORK="/mnt/c/Users/kota_/AgentDev" 
export PYTHONPATH="$AGENTDEV_ROOT:$AGENTDEV_WORK:$PYTHONPATH"

# Activate Python virtual environment
if [ -f "$AGENTDEV_ROOT/claude-env/bin/activate" ]; then
    source "$AGENTDEV_ROOT/claude-env/bin/activate"
    echo "🐍 Python virtual environment activated"
else
    echo "⚠️  Python virtual environment not found"
fi

# Add MCP servers to PATH
export PATH="$AGENTDEV_WORK/mcp-servers/local-tools:$PATH"
export PATH="$AGENTDEV_WORK/mcp-servers/gemini-test-agent:$PATH"

# Set up development aliases
alias dev-lint="python $AGENTDEV_WORK/mcp-servers/local-tools/development_server.py run_linter"
alias dev-format="python $AGENTDEV_WORK/mcp-servers/local-tools/development_server.py format_code"  
alias dev-test="python $AGENTDEV_WORK/mcp-servers/local-tools/development_server.py run_tests"
alias dev-validate="python $AGENTDEV_WORK/mcp-servers/gemini-test-agent/server.py validate_test_code"

echo "🚀 AgentDev environment ready!"
echo "📁 Main: $AGENTDEV_ROOT"
echo "💼 Work: $AGENTDEV_WORK"
echo ""
echo "Available commands:"
echo "  dev-lint <file>     - Run linter"
echo "  dev-format <file>   - Format code"
echo "  dev-test <path>     - Run tests"
echo "  dev-validate        - Validate with Gemini"
EOF

chmod +x "$WORK_DIR/activate-dev.sh"

# Update CLAUDE.md with correct paths
cat > "$WORK_DIR/CLAUDE.md" << 'EOF'
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentDev is an AI-optimized development environment featuring multi-model testing, automated code validation, and MCP-based tooling integration.

## Directory Structure

- **Main Environment**: `/mnt/c/AgentDev/` (Python env, core tools)
- **Work Environment**: `/mnt/c/Users/kota_/AgentDev/` (development workspace)
- **Automatic Sync**: Bidirectional synchronization between environments

## Quick Start

```bash
# Activate unified development environment
source activate-dev.sh

# This sets up:
# - Python virtual environment from /mnt/c/AgentDev/claude-env
# - Development tools and MCP servers
# - Unified PATH and PYTHONPATH
# - Development aliases
```

## Development Commands

### Environment Management
```bash
# Sync environments
./scripts/sync-environment.sh

# Activate development environment
source activate-dev.sh
```

### Code Quality (Unified Commands)
```bash
# Using development aliases (after activation)
dev-lint src/myfile.py          # Auto-detect and run linter
dev-format src/myfile.py        # Auto-detect and format
dev-test tests/                 # Run test suite
dev-validate                    # Gemini validation
```

### Manual MCP Tool Access
```bash
# Direct MCP server calls
python mcp-servers/local-tools/development_server.py run_linter <file>
python mcp-servers/gemini-test-agent/server.py validate_test_code <code> <tests>
```

## File Synchronization

The environment automatically synchronizes:
- Source code and projects
- Configuration files  
- MCP servers and tools
- Documentation (including this file)

Python virtual environment remains in main location (`/mnt/c/AgentDev/claude-env`) but is accessible from work directory via symbolic link.

## Multi-Model Development Workflow

### 1. Development Phase (Claude)
- Work in `/mnt/c/Users/kota_/AgentDev/projects/`
- Use `dev-*` commands for quick development
- Files automatically sync to main environment

### 2. Validation Phase (Gemini)  
- `dev-validate` runs external Gemini validation
- Magic number detection and test quality analysis
- Results inform code improvements

### 3. Integration Phase
- Git hooks run from either environment
- Unified tooling ensures consistency
- Python environment shared across both locations

## Environment Variables

```bash
# Set in activate-dev.sh automatically
AGENTDEV_ROOT="/mnt/c/AgentDev"           # Main environment
AGENTDEV_WORK="/mnt/c/Users/kota_/AgentDev"  # Work environment  
PYTHONPATH="$AGENTDEV_ROOT:$AGENTDEV_WORK:$PYTHONPATH"

# Required for Gemini Test Agent
export GEMINI_API_KEY="your_gemini_api_key"
```

## Best Practices

### Development Workflow
1. **Always activate environment**: `source activate-dev.sh`
2. **Use dev-* aliases**: Ensures proper tool usage
3. **Regular sync**: Run `./scripts/sync-environment.sh` when needed
4. **Test in both environments**: Verify functionality across locations

### File Management
- **Source code**: Keep in `projects/` subdirectory
- **Configuration**: Store in `config/` subdirectory  
- **Documentation**: Auto-synced between environments
- **Temporary files**: Use `/tmp` or designated temp directories

This unified approach solves the directory separation issue and provides seamless development experience across both environments.
EOF

# Copy updated CLAUDE.md to main directory
cp "$WORK_DIR/CLAUDE.md" "$MAIN_DIR/"

echo ""
echo "✅ Environment synchronization complete!"
echo ""
echo "Next steps:"
echo "1. Run: source activate-dev.sh"
echo "2. Test unified development environment"
echo "3. Begin development with automatic sync"