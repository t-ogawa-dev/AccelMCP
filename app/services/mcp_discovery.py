"""
MCP Capability Discovery Service
MCPサーバーに接続してCapabilityを自動検出するサービス
"""
import json
import requests
from app.models.models import db, Capability


def discover_mcp_capabilities(service_id, mcp_url):
    """
    MCPサーバーに接続してtoolsリストを取得し、Capabilityとして登録
    
    Args:
        service_id: サービスID
        mcp_url: MCPサーバーのSSEエンドポイントURL
    """
    try:
        # MCPサーバーに接続してtools/listを実行
        # Note: 実際のMCP接続はSSEストリームを使用する必要があります
        # ここでは簡易版として、HTTP POSTでtools/listを実行する想定です
        
        response = requests.post(
            mcp_url,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"MCP server returned status {response.status_code}")
        
        result = response.json()
        
        # MCPからのtools配列を取得
        tools = result.get('result', {}).get('tools', [])
        
        # 既存のMCP Capabilityを削除
        Capability.query.filter_by(
            service_id=service_id,
            capability_type='mcp_tool'
        ).delete()
        
        # 各toolをCapabilityとして登録
        for tool in tools:
            capability = Capability(
                service_id=service_id,
                name=tool.get('name', 'Unknown Tool'),
                capability_type='mcp_tool',
                description=tool.get('description', ''),
                # MCPツールはURLやヘッダーを持たない（MCP経由で実行）
                url=None,
                headers=None,
                body_params=json.dumps(tool.get('inputSchema', {}))  # パラメータスキーマを保存
            )
            db.session.add(capability)
        
        db.session.commit()
        return len(tools)
        
    except Exception as e:
        db.session.rollback()
        raise Exception(f"MCP capability discovery failed: {str(e)}")
