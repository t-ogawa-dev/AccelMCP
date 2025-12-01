"""
MCP Capability Discovery Service
MCPサーバーに接続してCapabilityを自動検出するサービス
"""
import json
import asyncio
import logging
from typing import Optional
from app.models.models import db, Capability, Service
from app.services.variable_replacer import VariableReplacer


async def _discover_tools_async(mcp_url: str, headers: dict) -> list:
    """
    非同期でMCPサーバーに接続してツールリストを取得
    
    Args:
        mcp_url: MCPサーバーのエンドポイントURL
        headers: 認証ヘッダー等
    
    Returns:
        ツールのリスト
    """
    import httpx
    
    request_headers = headers.copy() if headers else {}
    
    # Step 1: GETリクエストで標準SSEを試す
    try:
        async with httpx.AsyncClient() as http_client:
            get_headers = request_headers.copy()
            get_headers['Accept'] = 'text/event-stream'
            
            response = await http_client.get(
                mcp_url,
                headers=get_headers,
                timeout=10.0,
                follow_redirects=True
            )
            
            content_type = response.headers.get('content-type', '').lower()
            if response.status_code == 200 and 'text/event-stream' in content_type:
                # 標準SSE (GET + endpoint方式)
                logging.info("Detected standard SSE (GET + endpoint)")
                return await _discover_tools_sse_standard(mcp_url, request_headers)
    except Exception as e:
        logging.debug(f"GET request failed: {e}, trying POST...")
    
    # Step 2: POSTリクエストでinitializeを送信してContent-Typeを確認
    async with httpx.AsyncClient() as http_client:
        try:
            # Initialize request to detect server type
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "AccelMCP",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            request_headers['Content-Type'] = 'application/json'
            request_headers['Accept'] = 'application/json, text/event-stream'
            
            response = await http_client.post(
                mcp_url,
                json=init_request,
                headers=request_headers,
                timeout=10.0
            )
            
            content_type = response.headers.get('content-type', '').lower()
            is_sse = 'text/event-stream' in content_type
        except Exception as e:
            # If POST fails, assume HTTP POST JSON-RPC
            logging.debug(f"POST detection failed: {e}")
            is_sse = False
    
    if is_sse:
        # POST + SSE (Microsoft Learn方式)
        logging.info("Detected POST + SSE")
        return await _discover_tools_sse_post(mcp_url, request_headers)
    else:
        # HTTP POST JSON-RPC
        logging.info("Detected HTTP POST JSON-RPC")
        return await _discover_tools_http(mcp_url, headers)


async def _discover_tools_sse_standard(mcp_url: str, headers: dict) -> list:
    """
    標準SSEベースのMCPサーバーからツールリストを取得
    GET + endpoint イベント方式（MCP SDK使用）
    
    Args:
        mcp_url: MCPサーバーのエンドポイントURL
        headers: 認証ヘッダー等
    
    Returns:
        ツールのリスト
    """
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    
    try:
        logging.info(f"Attempting standard SSE connection to {mcp_url}")
        
        # MCP SDKのSSEクライアントを使用
        async with sse_client(mcp_url, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                logging.info("Standard SSE initialized")
                
                # List tools
                tools_result = await session.list_tools()
                
                # Extract tools
                if hasattr(tools_result, 'tools'):
                    tools_data = tools_result.tools
                    logging.info(f"Received {len(tools_data)} tools from standard SSE MCP")
                    
                    return [
                        {
                            'name': tool.name,
                            'description': tool.description if hasattr(tool, 'description') else '',
                            'inputSchema': tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                        }
                        for tool in tools_data
                    ]
                else:
                    logging.warning("Standard SSE: tools_result does not have 'tools' attribute")
                    return []
                    
    except Exception as e:
        logging.error(f"Standard SSE MCP connection failed: {str(e)}")
        raise Exception(f"Standard SSE MCP connection failed: {str(e)}")


async def _discover_tools_sse_post(mcp_url: str, headers: dict) -> list:
    """
    SSEベースのMCPサーバーからツールリストを取得
    Microsoft LearnのようなPOST+SSEサーバー向け
    
    Args:
        mcp_url: MCPサーバーのエンドポイントURL
        headers: 認証ヘッダー等（既にAcceptヘッダーを含む）
    
    Returns:
        ツールのリスト
    """
    import httpx
    import json
    
    try:
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "AccelMCP",
                    "version": "1.0.0"
                }
            }
        }
        
        # SSE用のヘッダーを準備（既にAcceptが含まれている）
        sse_headers = headers.copy() if headers else {}
        if 'Accept' not in sse_headers:
            sse_headers['Accept'] = 'application/json, text/event-stream'
        
        logging.info(f"Attempting SSE connection to {mcp_url} with headers: {list(sse_headers.keys())}")
        
        # POSTでSSE接続を確立（httpxのストリーミングを使用）
        async with httpx.AsyncClient() as client:
            logging.debug("Created httpx client")
            
            # initializeリクエストをストリーミングで送信
            async with client.stream('POST', mcp_url, json=init_request, headers=sse_headers, timeout=30.0) as response:
                logging.info(f"SSE stream opened, status: {response.status_code}")
                response.raise_for_status()
                
                # Session IDを取得
                session_id = response.headers.get('Mcp-Session-Id')
                if session_id:
                    logging.info(f"Received Mcp-Session-Id: {session_id}")
                    sse_headers['Mcp-Session-Id'] = session_id
                
                # SSEストリームを読み取り
                init_response = None
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]  # "data: "を除去
                        try:
                            message = json.loads(data)
                            if message.get('id') == 1:
                                init_response = message
                                logging.info(f"Received initialize response")
                                break
                        except json.JSONDecodeError:
                            continue
                
                if not init_response or 'result' not in init_response:
                    raise Exception("Failed to receive valid initialize response")
        
        # tools/list リクエストを送信
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        logging.info(f"Sending tools/list with headers: {list(sse_headers.keys())}")
        
        async with httpx.AsyncClient() as client:
            async with client.stream('POST', mcp_url, json=tools_request, headers=sse_headers, timeout=30.0) as response:
                response.raise_for_status()
                logging.info("Sent tools/list request via SSE stream")
                
                # SSEストリームを読み取り
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]
                        try:
                            message = json.loads(data)
                            if message.get('id') == 2 and 'result' in message:
                                tools_data = message['result'].get('tools', [])
                                logging.info(f"Received {len(tools_data)} tools from SSE MCP")
                                
                                return [
                                    {
                                        'name': tool.get('name', ''),
                                        'description': tool.get('description', ''),
                                        'inputSchema': tool.get('inputSchema', {})
                                    }
                                    for tool in tools_data
                                ]
                        except json.JSONDecodeError:
                            continue
                
                logging.warning("No tools found in SSE response")
                return []
                    
    except Exception as e:
        logging.error(f"SSE MCP connection failed: {str(e)}")
        raise Exception(f"SSE MCP connection failed: {str(e)}")


async def _discover_tools_http(mcp_url: str, headers: dict) -> list:
    """
    HTTP POSTベースのMCPサーバーからツールリストを取得
    
    Args:
        mcp_url: MCPサーバーのエンドポイントURL
        headers: 認証ヘッダー等
    
    Returns:
        ツールのリスト
    """
    import httpx
    
    async with httpx.AsyncClient() as http_client:
        # Initialize connection
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "AccelMCP",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        # Add headers
        request_headers = headers.copy()
        request_headers['Content-Type'] = 'application/json'
        
        # Initialize
        response = await http_client.post(
            mcp_url,
            json=init_request,
            headers=request_headers,
            timeout=10.0
        )
        
        if response.status_code != 200:
            raise Exception(f"MCP initialize failed with status {response.status_code}")
        
        init_result = response.json()
        
        if 'error' in init_result:
            error_msg = init_result['error'].get('message', 'Unknown error')
            raise Exception(f"MCP initialize error: {error_msg}")
        
        # Extract session ID from response headers
        session_id = response.headers.get('mcp-session-id') or response.headers.get('Mcp-Session-Id')
        
        # GitHub Copilot MCPは通常のJSON-RPC over HTTPではなく、
        # SSEベースのストリーミング接続が必要な場合があります
        # ここではinitializeのレスポンスからcapabilitiesを取得します
        server_capabilities = init_result.get('result', {}).get('capabilities', {})
        
        # toolsがサポートされているか確認
        if 'tools' not in server_capabilities:
            raise Exception("MCP server does not support tools capability")
        
        # tools/list リクエストを送信（セッションIDを含める）
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        # セッションIDをヘッダーに追加
        tools_headers = request_headers.copy()
        if session_id:
            tools_headers['Mcp-Session-Id'] = session_id
        
        tools_response = await http_client.post(
            mcp_url,
            json=tools_request,
            headers=tools_headers,
            timeout=10.0
        )
        
        if tools_response.status_code != 200:
            error_body = tools_response.text
            # セッションベースのエラーの場合
            if "session" in error_body.lower():
                raise Exception(
                    f"This MCP server requires persistent session management. "
                    f"HTTP-based discovery is not supported. Please register capabilities manually."
                )
            raise Exception(f"MCP tools/list failed with status {tools_response.status_code}: {error_body}")
        
        tools_result = tools_response.json()
        
        if 'error' in tools_result:
            error_msg = tools_result['error'].get('message', 'Unknown error')
            raise Exception(f"MCP tools/list error: {error_msg}")
        
        # ツールリストを取得
        tools = tools_result.get('result', {}).get('tools', [])
        return tools


def discover_mcp_capabilities(service_id, mcp_url):
    """
    MCPサーバーに接続してtoolsリストを取得し、Capabilityとして登録
    
    Args:
        service_id: サービスID
        mcp_url: MCPサーバーのエンドポイントURL
    """
    try:
        # サービス情報を取得
        service = Service.query.get(service_id)
        if not service:
            raise Exception(f"Service with id {service_id} not found")
        
        # 共通ヘッダーを取得して変数置換
        common_headers = json.loads(service.common_headers) if service.common_headers else {}
        replacer = VariableReplacer()
        resolved_headers = {}
        for key, value in common_headers.items():
            resolved_key = replacer.replace_in_string(key)
            resolved_value = replacer.replace_in_string(value)
            resolved_headers[resolved_key] = resolved_value
        
        # 非同期関数を実行
        tools = asyncio.run(_discover_tools_async(mcp_url, resolved_headers))
        
        # 既存のMCP Capabilityを削除
        Capability.query.filter_by(
            app_id=service_id,
            capability_type='mcp_tool'
        ).delete()
        
        # 各toolをCapabilityとして登録
        for tool in tools:
            capability = Capability(
                app_id=service_id,
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
