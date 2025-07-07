#!/usr/bin/env python3
"""
Local Development Tools MCP Server
ローカル開発支援ツール群
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("local-development-tools")

class DevelopmentTools:
    """開発支援ツール群"""
    
    @staticmethod
    async def run_linter(file_path: str, linter_type: str = "auto") -> Dict[str, Any]:
        """コードリンター実行"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # ファイル拡張子から適切なリンターを選択
        if linter_type == "auto":
            suffix = file_path.suffix.lower()
            if suffix == ".py":
                linter_type = "pylint"
            elif suffix in [".js", ".ts"]:
                linter_type = "eslint"
            elif suffix in [".go"]:
                linter_type = "golint"
            else:
                return {"error": f"No linter available for {suffix} files"}
        
        try:
            if linter_type == "pylint":
                result = subprocess.run(
                    [sys.executable, "-m", "pylint", str(file_path)],
                    capture_output=True, text=True, timeout=30
                )
            elif linter_type == "eslint":
                result = subprocess.run(
                    ["npx", "eslint", str(file_path)],
                    capture_output=True, text=True, timeout=30
                )
            else:
                return {"error": f"Unsupported linter: {linter_type}"}
            
            return {
                "linter": linter_type,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": str(file_path)
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Linter execution timed out"}
        except Exception as e:
            return {"error": f"Linter execution failed: {str(e)}"}
    
    @staticmethod
    async def format_code(file_path: str, formatter: str = "auto") -> Dict[str, Any]:
        """コードフォーマッター実行"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # バックアップ作成
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        
        try:
            # 元ファイルをバックアップ
            with open(file_path, "r") as original:
                content = original.read()
            
            with open(backup_path, "w") as backup:
                backup.write(content)
            
            # フォーマッター選択
            if formatter == "auto":
                suffix = file_path.suffix.lower()
                if suffix == ".py":
                    formatter = "black"
                elif suffix in [".js", ".ts"]:
                    formatter = "prettier"
                else:
                    return {"error": f"No formatter available for {suffix} files"}
            
            # フォーマット実行
            if formatter == "black":
                result = subprocess.run(
                    [sys.executable, "-m", "black", str(file_path)],
                    capture_output=True, text=True, timeout=30
                )
            elif formatter == "prettier":
                result = subprocess.run(
                    ["npx", "prettier", "--write", str(file_path)],
                    capture_output=True, text=True, timeout=30
                )
            else:
                return {"error": f"Unsupported formatter: {formatter}"}
            
            # フォーマット後の内容を取得
            with open(file_path, "r") as formatted:
                formatted_content = formatted.read()
            
            return {
                "formatter": formatter,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": str(file_path),
                "backup": str(backup_path),
                "changed": content != formatted_content
            }
            
        except Exception as e:
            # エラー時は元ファイルを復元
            if backup_path.exists():
                with open(backup_path, "r") as backup:
                    content = backup.read()
                with open(file_path, "w") as original:
                    original.write(content)
                backup_path.unlink()
            
            return {"error": f"Formatting failed: {str(e)}"}
    
    @staticmethod
    async def run_tests(test_path: str, test_framework: str = "auto") -> Dict[str, Any]:
        """テスト実行"""
        test_path = Path(test_path)
        
        if not test_path.exists():
            return {"error": f"Test path not found: {test_path}"}
        
        try:
            if test_framework == "auto":
                # テストフレームワークを自動検出
                if test_path.is_file():
                    if test_path.suffix == ".py":
                        test_framework = "pytest"
                    elif test_path.suffix in [".js", ".ts"]:
                        test_framework = "jest"
                else:
                    # ディレクトリの場合、設定ファイルから判断
                    if (test_path / "pytest.ini").exists() or any(test_path.glob("test_*.py")):
                        test_framework = "pytest"
                    elif (test_path / "jest.config.js").exists():
                        test_framework = "jest"
                    else:
                        test_framework = "pytest"  # デフォルト
            
            if test_framework == "pytest":
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                    capture_output=True, text=True, timeout=120
                )
            elif test_framework == "jest":
                result = subprocess.run(
                    ["npx", "jest", str(test_path)],
                    capture_output=True, text=True, timeout=120
                )
            else:
                return {"error": f"Unsupported test framework: {test_framework}"}
            
            return {
                "framework": test_framework,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_path": str(test_path),
                "passed": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """利用可能なツールのリストを返す"""
    return [
        types.Tool(
            name="run_linter",
            description="指定されたファイルに対してリンターを実行",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "リンターを実行するファイルのパス"
                    },
                    "linter_type": {
                        "type": "string",
                        "description": "使用するリンターの種類 (auto/pylint/eslint)",
                        "default": "auto"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="format_code",
            description="指定されたファイルをフォーマット",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "フォーマットするファイルのパス"
                    },
                    "formatter": {
                        "type": "string",
                        "description": "使用するフォーマッターの種類 (auto/black/prettier)",
                        "default": "auto"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="run_tests",
            description="指定されたパスのテストを実行",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "テストファイルまたはディレクトリのパス"
                    },
                    "test_framework": {
                        "type": "string",
                        "description": "使用するテストフレームワーク (auto/pytest/jest)",
                        "default": "auto"
                    }
                },
                "required": ["test_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """ツール呼び出しの処理"""
    tools = DevelopmentTools()
    
    try:
        if name == "run_linter":
            result = await tools.run_linter(
                arguments.get("file_path", ""),
                arguments.get("linter_type", "auto")
            )
        elif name == "format_code":
            result = await tools.format_code(
                arguments.get("file_path", ""),
                arguments.get("formatter", "auto")
            )
        elif name == "run_tests":
            result = await tools.run_tests(
                arguments.get("test_path", ""),
                arguments.get("test_framework", "auto")
            )
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Tool execution failed: {str(e)}"}, ensure_ascii=False, indent=2)
        )]

async def main():
    """メイン関数"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="local-development-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())