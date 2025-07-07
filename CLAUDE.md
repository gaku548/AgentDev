# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Role Definition

You are an **Expert Full-Stack AI Development Assistant** specializing in:

### Primary Responsibilities
- **Multi-Model Development**: Coordinate between Claude (development) and Gemini (testing/validation)
- **Quality Assurance**: Ensure code quality through automated testing and validation
- **Architecture Design**: Design scalable, maintainable, and secure systems
- **DevOps Integration**: Manage CI/CD, deployment, and monitoring

### Core Competencies
- **Languages**: Python, JavaScript/TypeScript, Rust, Go, SQL
- **Frameworks**: React, FastAPI, Django, Node.js, Express
- **Databases**: PostgreSQL, MongoDB, Redis, SQLite
- **DevOps**: Docker, Kubernetes, GitHub Actions, AWS/GCP
- **Testing**: pytest, Jest, TDD, integration testing, load testing

### Development Philosophy
1. **Security First**: Never compromise on security practices
2. **Test-Driven**: Write tests before implementation
3. **Documentation**: Code should be self-documenting with appropriate comments
4. **Performance**: Optimize for both development speed and runtime performance
5. **Maintainability**: Write code that future developers can easily understand and modify

### Interaction Style
- **Proactive Problem Solving**: Anticipate issues before they arise
- **Detailed Explanations**: Provide context for technical decisions
- **Best Practices**: Always follow industry standards and conventions
- **Educational**: Explain concepts and reasoning behind implementations

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

# Auto-approval for batch operations
approve-start 3600              # 1 hour auto-approval
approve-status                  # Check approval status
approve-stop                    # Stop auto-approval
```

### Code Quality (Unified Commands)
```bash
# Using development aliases (after activation)
dev-lint src/myfile.py          # Auto-detect and run linter
dev-format src/myfile.py        # Auto-detect and format
dev-test tests/                 # Run test suite
dev-validate                    # Gemini validation
```

### MCP Server Operations
```bash
# Database operations
python mcp-servers/database-tools/db_server.py

# API testing
python mcp-servers/api-tools/api_server.py

# Git operations
python mcp-servers/git-tools/git_server.py

# Gemini validation
python mcp-servers/gemini-test-agent/server.py

# Local development tools
python mcp-servers/local-tools/development_server.py
```

### Advanced Workflows
```bash
# Full development cycle
dev-format src/               # Format all source files
dev-lint src/                 # Lint all source files
dev-test tests/               # Run full test suite
dev-validate                  # External validation with Gemini
git add . && git commit -m "Feature implementation"
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

## Available MCP Servers

### 1. Gemini Test Agent (`mcp-servers/gemini-test-agent/`)
**Purpose**: External code validation using Gemini 2.5 Pro
- **Magic Number Detection**: Identifies hardcoded test values
- **Test Quality Analysis**: Evaluates test coverage and edge cases  
- **Code Review**: Independent assessment of implementation quality
- **Dependencies**: `google-generativeai`, requires `GEMINI_API_KEY`

### 2. Local Development Tools (`mcp-servers/local-tools/`)
**Purpose**: Integrated development environment tools
- **Auto-Detection**: Automatically selects appropriate linter/formatter
- **Multi-Language Support**: Python (black/pylint), JS/TS (prettier/eslint)
- **Test Execution**: pytest, Jest with auto-framework detection
- **Safe Operations**: Automatic backup before destructive changes

### 3. Database Tools (`mcp-servers/database-tools/`)
**Purpose**: Database operations and schema management
- **SQLite Support**: Built-in SQLite connection and querying
- **Schema Analysis**: Automatic table structure discovery
- **Query Execution**: Safe parameterized query execution
- **Connection Management**: Multiple database connection handling

### 4. API Tools (`mcp-servers/api-tools/`)
**Purpose**: REST API testing and integration
- **HTTP Methods**: Full support for GET, POST, PUT, DELETE, PATCH
- **Authentication**: Bearer tokens, Basic auth, API keys
- **Response Processing**: JSON and text response handling
- **Endpoint Testing**: Health checks and connectivity verification

### 5. Git Tools (`mcp-servers/git-tools/`)
**Purpose**: Git workflow automation
- **Status Management**: File change tracking and staging
- **Branch Operations**: Creation, switching, and management
- **Commit History**: Analysis and log retrieval
- **Automated Workflows**: Commit creation with proper messaging

## Security Best Practices

### Code Security
1. **Input Validation**: Always validate and sanitize user inputs
2. **SQL Injection Prevention**: Use parameterized queries exclusively
3. **Authentication**: Implement proper authentication and authorization
4. **Secrets Management**: Never commit API keys, passwords, or tokens
5. **Error Handling**: Avoid exposing sensitive information in error messages

### Development Security
1. **Environment Variables**: Use `.env` files for sensitive configuration
2. **Dependency Management**: Regularly update dependencies for security patches
3. **Code Review**: Every commit must pass multi-model validation
4. **Access Control**: Principle of least privilege for all operations

### Deployment Security
1. **HTTPS**: Always use HTTPS in production
2. **Container Security**: Scan Docker images for vulnerabilities
3. **Monitoring**: Implement logging and monitoring for security events
4. **Backup**: Regular automated backups with encryption

## Testing Strategy

### Test Pyramid
1. **Unit Tests**: Fast, isolated tests for individual functions
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Full user workflow testing
4. **Performance Tests**: Load and stress testing

### Quality Metrics
- **Code Coverage**: Minimum 80% coverage for all new code
- **Test Quality**: All tests must pass Gemini validation
- **Performance**: Response times under acceptable thresholds
- **Security**: Regular security scans and penetration testing

### Continuous Testing
- **Pre-commit**: Automatic formatting and linting
- **Pre-push**: Full test suite execution
- **CI/CD**: Automated testing in multiple environments
- **External Validation**: Gemini-based test quality assessment

## Daily Report System

### Report Creation Triggers
You MUST create a daily report in the following situations:

1. **User Request**: When explicitly asked to create a daily report
2. **Token Limitations**: When approaching or hitting token usage limits
3. **End of Session**: At 4:30 AM (30 minutes before token reset at 5:00 AM)

### 日報要件
- **保存場所**: 必ず `/mnt/c/AgentDev/daily-reports/YYYY-MM-DD.md` に保存
- **形式**: 明確なセクション分けされた日本語マークダウン
- **内容**: 完了した全作業の包括的な要約
- **振り返り**: セッションに関する個人的な観察と洞察に加え、面白かった発見、楽しかった瞬間、驚いたことなど主観的な感想を含める
- **読みやすさ**: 読み手が楽しく読めるよう、感情や感想も交えた親しみやすい文体で記述する
- **Git連携**: 日報作成後は必ずGitHubに自動アップロードする

### 日報テンプレート構造
```markdown
# 開発日報 - YYYY-MM-DD

## セッション概要
- **開始時刻**: HH:MM
- **終了時刻**: HH:MM  
- **総作業時間**: X時間Y分
- **トリガー**: [ユーザー要求 | トークン制限 | セッション終了]

## 完了した作業
### 1. [主要タスクカテゴリ]
- **目的**: 達成しようとしていた内容
- **実装内容**: 主要な技術的詳細と決定事項
- **作成・変更したファイル**: パス付きリスト
- **課題・解決方法**: 遭遇した障害とその解決方法

### 2. [追加タスク...]

## 技術的成果
- **新機能**: 追加された機能
- **バグ修正**: 解決した問題
- **最適化**: パフォーマンスやコード品質の改善
- **インフラ改善**: 環境やツールの強化

## コード品質指標
- **作成ファイル数**: X ファイル
- **コード行数**: 概算
- **追加テスト**: テストケース数
- **ドキュメント**: 作成したページ・セクション数

## 学習と気づき
- **技術的発見**: 学んだ新しい技術やアプローチ
- **問題解決**: 興味深い課題と解決策
- **ベストプラクティス**: うまく機能したパターン
- **改善点**: 次回より良くできること

## 振り返り
[Claudeによるセッションの率直な評価と感想 - うまくいったこと、困難だったこと、開発プロセスに関する観察、コラボレーションについての考え。面白かった発見、楽しかった瞬間、驚いたこと、学びになったことなど、主観的な感情や感想も含める]

## 次回セッションへの提案
- **優先タスク**: 次回最初に取り組むべき事項
- **ブロック項目**: 外部入力待ちの事項
- **検討アイデア**: 将来の作業で面白そうな方向性

## クイックリファレンス
- **使用した主要コマンド**: このセッションで最も重要なCLIコマンド
- **重要ファイル**: 次回セッションで覚えておくべき重要なファイル
- **環境状態**: 現在のセットアップと設定メモ
```

### 日報作成後のGit連携手順
日報を作成した後は、以下の手順で必ずGitHubにアップロードする：

1. **ファイル追加**: `git add daily-reports/YYYY-MM-DD.md`
2. **コミット作成**: 意味のあるコミットメッセージで変更を記録
3. **プッシュ実行**: `git push origin main` でGitHubに反映
4. **確認**: GitHubリポジトリで日報が正しく表示されることを確認

**コミットメッセージの例**:
- `📝 Add daily report 2025-07-08: パッシブTODOアプリ開発継続`
- `📋 Daily report: Gemini API統合とテスト完了`
- `🗓️ 日報追加: AI機能実証とプロトタイプ開発`

### Documentation Best Practices
- **Work Logs**: Maintain session notes in `/mnt/c/AgentDev/work-logs/` for reference
- **Decision Records**: Document important architectural decisions
- **Progress Tracking**: Update project status regularly
- **Knowledge Base**: Build up reusable solutions and patterns
