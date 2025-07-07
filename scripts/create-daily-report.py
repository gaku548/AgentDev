#!/usr/bin/env python3
"""
Daily Report Generator for AgentDev
Claude用の日報作成支援ツール
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class DailyReportGenerator:
    """日報生成支援クラス"""
    
    def __init__(self):
        self.base_path = Path("/mnt/c/AgentDev")
        self.reports_path = self.base_path / "daily-reports"
        self.work_logs_path = self.base_path / "work-logs"
        self.templates_path = self.base_path / "templates"
        
        # ディレクトリ存在確認
        self.reports_path.mkdir(exist_ok=True)
        self.work_logs_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
    
    def collect_session_info(self) -> Dict[str, Any]:
        """セッション情報を収集"""
        now = datetime.now()
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "end_time": now.strftime("%H:%M"),
            "generation_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "is_weekend": now.weekday() >= 5
        }
    
    def scan_recent_files(self, hours: int = 24) -> List[Dict[str, Any]]:
        """最近変更されたファイルをスキャン"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_files = []
        
        # AgentDevディレクトリをスキャン
        for root, dirs, files in os.walk(self.base_path):
            # 除外ディレクトリ
            dirs[:] = [d for d in dirs if d not in ['claude-env', 'node_modules', '.git', '__pycache__']]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_mtime > cutoff_time.timestamp():
                        recent_files.append({
                            "path": str(file_path.relative_to(self.base_path)),
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%H:%M"),
                            "size": file_path.stat().st_size,
                            "extension": file_path.suffix
                        })
                except (OSError, ValueError):
                    continue
        
        return sorted(recent_files, key=lambda x: x["modified"], reverse=True)
    
    def analyze_work_patterns(self, recent_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """作業パターンを分析"""
        file_types = {}
        total_size = 0
        
        for file_info in recent_files:
            ext = file_info["extension"] or "no-extension"
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file_info["size"]
        
        # 主要なファイルタイプを特定
        primary_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_files": len(recent_files),
            "total_size_kb": total_size // 1024,
            "primary_file_types": primary_types,
            "file_type_distribution": file_types
        }
    
    def generate_work_summary(self, recent_files: List[Dict[str, Any]]) -> Dict[str, str]:
        """作業サマリーを生成"""
        # ファイル拡張子によるカテゴリ分け
        categories = {
            "Python Development": [".py"],
            "JavaScript/TypeScript": [".js", ".ts", ".jsx", ".tsx"],
            "Documentation": [".md", ".rst", ".txt"],
            "Configuration": [".json", ".yaml", ".yml", ".toml", ".ini"],
            "Scripts": [".sh", ".bat", ".ps1"],
            "Data": [".csv", ".json", ".db", ".sqlite"]
        }
        
        categorized_work = {}
        for category, extensions in categories.items():
            files = [f for f in recent_files if f["extension"] in extensions]
            if files:
                categorized_work[category] = files
        
        return categorized_work
    
    def create_report_structure(self, trigger: str) -> Dict[str, Any]:
        """日報の基本構造を作成"""
        session_info = self.collect_session_info()
        recent_files = self.scan_recent_files()
        work_analysis = self.analyze_work_patterns(recent_files)
        work_summary = self.generate_work_summary(recent_files)
        
        return {
            "session": session_info,
            "trigger": trigger,
            "files": recent_files,
            "analysis": work_analysis,
            "work_summary": work_summary,
            "template_vars": {
                "DATE": session_info["date"],
                "END_TIME": session_info["end_time"],
                "GENERATION_TIME": session_info["generation_time"],
                "TRIGGER": trigger,
                "FILES_CREATED": str(work_analysis["total_files"]),
                "LINES_OF_CODE": f"~{work_analysis['total_size_kb']}KB",
            }
        }
    
    def save_work_log(self, structure: Dict[str, Any]) -> str:
        """作業ログを保存"""
        log_file = self.work_logs_path / f"session-{structure['session']['date']}-{structure['session']['end_time'].replace(':', '')}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
        
        return str(log_file)
    
    def get_report_filename(self, date: str) -> str:
        """日報ファイル名を生成"""
        return str(self.reports_path / f"{date}.md")
    
    def load_template(self) -> str:
        """テンプレートを読み込み"""
        template_file = self.templates_path / "daily-report-template.md"
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # デフォルトテンプレート
            return """# Daily Development Report - {DATE}

## Session Overview
- **End Time**: {END_TIME}
- **Trigger**: {TRIGGER}

## Quick Summary
- **Files Modified**: {FILES_CREATED}
- **Approximate Work**: {LINES_OF_CODE}

## Detailed Report
[To be filled by Claude with comprehensive analysis]

---
*Generated on {GENERATION_TIME}*
"""

def main():
    """メイン関数 - Claudeが呼び出し用"""
    generator = DailyReportGenerator()
    
    # 基本構造を生成してファイルに保存
    structure = generator.create_report_structure("Script Execution")
    log_file = generator.save_work_log(structure)
    
    print(f"Work log saved: {log_file}")
    print(f"Recent files analyzed: {structure['analysis']['total_files']}")
    print(f"Report should be saved to: {generator.get_report_filename(structure['session']['date'])}")
    
    return structure

if __name__ == "__main__":
    result = main()