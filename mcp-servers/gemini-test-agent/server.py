#!/usr/bin/env python3
"""
Gemini Test Agent MCP Server
テスト検証用の外部AIエージェント
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource
)
import mcp.types as types

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini-test-agent")

class GeminiTestAgent:
    """Gemini 2.5 Proを使用したテスト検証エージェント"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    async def validate_test_code(self, code: str, test_code: str) -> Dict[str, Any]:
        """
        コードとテストコードを検証し、マジックナンバーやズル対策を検出
        """
        prompt = f"""
        以下のコードとテストコードを分析し、テストの品質を評価してください。
        特に以下の点に注意して分析してください：

        1. マジックナンバーの使用
        2. テストケースの網羅性
        3. エッジケースの考慮
        4. テストが実装に依存しすぎていないか
        5. モックやスタブの適切な使用

        【実装コード】
        ```
        {code}
        ```

        【テストコード】
        ```
        {test_code}
        ```

        以下のJSON形式で回答してください：
        {{
            "score": "1-10の評価点",
            "issues": [
                {{
                    "type": "issue種別",
                    "severity": "critical|warning|info",
                    "description": "問題の説明",
                    "suggestion": "改善提案"
                }}
            ],
            "summary": "総合評価コメント"
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # JSONレスポンスを解析
            response_text = response.text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text
                
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "score": 0,
                "issues": [
                    {
                        "type": "api_error",
                        "severity": "critical",
                        "description": f"Gemini API呼び出しエラー: {str(e)}",
                        "suggestion": "API設定とネットワーク接続を確認してください"
                    }
                ],
                "summary": "API呼び出しに失敗しました"
            }
    
    async def suggest_test_cases(self, code: str) -> List[Dict[str, Any]]:
        """コードに対する追加テストケースを提案"""
        prompt = f"""
        以下のコードに対して、追加すべきテストケースを提案してください。
        エッジケース、エラーケース、境界値テストを重視してください。

        【コード】
        ```
        {code}
        ```

        以下のJSON形式で回答してください：
        {{
            "test_cases": [
                {{
                    "name": "テストケース名",
                    "description": "テストの説明",
                    "input": "入力値",
                    "expected_output": "期待される出力",
                    "category": "normal|edge|error|boundary"
                }}
            ]
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            result = json.loads(response.text)
            return result.get("test_cases", [])
        except Exception as e:
            logger.error(f"Test case suggestion error: {e}")
            return []

# MCPサーバー設定
server = Server("gemini-test-agent")
gemini_agent = None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """利用可能なツールのリストを返す"""
    return [
        Tool(
            name="validate_test_code",
            description="コードとテストコードを検証してテスト品質を評価",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "検証対象のコード"
                    },
                    "test_code": {
                        "type": "string", 
                        "description": "テストコード"
                    }
                },
                "required": ["code", "test_code"]
            }
        ),
        Tool(
            name="suggest_test_cases",
            description="コードに対する追加テストケースを提案",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "テストケースを生成するコード"
                    }
                },
                "required": ["code"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """ツール呼び出しの処理"""
    global gemini_agent
    
    if gemini_agent is None:
        return [types.TextContent(
            type="text", 
            text="Error: Gemini API key not configured"
        )]
    
    if name == "validate_test_code":
        code = arguments.get("code", "")
        test_code = arguments.get("test_code", "")
        
        result = await gemini_agent.validate_test_code(code, test_code)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
        
    elif name == "suggest_test_cases":
        code = arguments.get("code", "")
        
        result = await gemini_agent.suggest_test_cases(code)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({"test_cases": result}, ensure_ascii=False, indent=2)
        )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """メイン関数"""
    global gemini_agent
    
    # 環境変数またはコマンドライン引数からAPI keyを取得
    import os
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Some features will be disabled.")
    else:
        gemini_agent = GeminiTestAgent(api_key)
        logger.info("Gemini Test Agent initialized")
    
    # MCPサーバーを起動
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-test-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())