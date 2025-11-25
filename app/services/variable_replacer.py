"""
Variable replacement service for MCP execution
"""
import re
import json
from typing import Any, Dict
from app.models.models import Variable


class VariableReplacer:
    """変数置換サービス - {{VARIABLE}} を実際の値に置換"""
    
    @staticmethod
    def replace_in_string(text: str) -> str:
        """
        文字列内の {{VARIABLE}} を変数値に置換（常に文字列として展開）
        ヘッダー、URL、Key-Value形式で使用
        
        Args:
            text: 置換対象の文字列
        
        Returns:
            置換後の文字列
        """
        if not text:
            return text
        
        def replacer(match):
            var_name = match.group(1)
            variable = Variable.query.filter_by(name=var_name).first()
            if variable:
                return str(variable.get_value())  # 常に文字列化
            return match.group(0)  # 変数が見つからない場合はそのまま
        
        return re.sub(r'\{\{([A-Z0-9_]+)\}\}', replacer, text)
    
    @staticmethod
    def replace_in_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        辞書内の全ての文字列値に対して変数置換を実行（文字列として展開）
        ヘッダー辞書、Key-Value辞書で使用
        
        Args:
            data: 置換対象の辞書
        
        Returns:
            置換後の辞書
        """
        if not data:
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = VariableReplacer.replace_in_string(value)
            elif isinstance(value, dict):
                result[key] = VariableReplacer.replace_in_dict(value)
            elif isinstance(value, list):
                result[key] = VariableReplacer.replace_in_list(value)
            else:
                result[key] = value
        return result
    
    @staticmethod
    def replace_in_list(data: list) -> list:
        """リスト内の値に対して変数置換を実行"""
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(VariableReplacer.replace_in_string(item))
            elif isinstance(item, dict):
                result.append(VariableReplacer.replace_in_dict(item))
            elif isinstance(item, list):
                result.append(VariableReplacer.replace_in_list(item))
            else:
                result.append(item)
        return result
    
    @staticmethod
    def replace_in_json(json_text: str) -> Any:
        """
        JSON文字列内の {{VARIABLE}} を変数値に置換（型を保持）
        number型変数は数値として展開、string型変数は文字列として展開
        
        Args:
            json_text: JSON文字列
        
        Returns:
            置換後のPythonオブジェクト（dict/list/etc）
        """
        if not json_text:
            return None
        
        # {{VARIABLE}}パターンを全て抽出
        pattern = r'\{\{([A-Z0-9_]+)\}\}'
        variables = {}
        
        for match in re.finditer(pattern, json_text):
            var_name = match.group(1)
            if var_name not in variables:
                variable = Variable.query.filter_by(name=var_name).first()
                if variable:
                    variables[var_name] = variable
        
        # 一時的なプレースホルダーに置換してJSONパース
        temp_json = json_text
        placeholder_map = {}
        
        for i, (var_name, variable) in enumerate(variables.items()):
            placeholder = f'"__VAR_{i}__"'
            placeholder_map[f'__VAR_{i}__'] = variable
            # {{VAR}} を一時プレースホルダーに置換
            temp_json = temp_json.replace(f'{{{{{var_name}}}}}', placeholder)
        
        # JSONパース
        try:
            parsed = json.loads(temp_json)
        except json.JSONDecodeError:
            # パースできない場合は文字列として処理
            return VariableReplacer.replace_in_string(json_text)
        
        # プレースホルダーを実際の値（型付き）に置換
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('__VAR_') and obj.endswith('__'):
                # プレースホルダーを実際の値に置換
                variable = placeholder_map.get(obj)
                if variable:
                    return variable.get_typed_value()  # 型付きで取得
                return obj
            else:
                return obj
        
        return replace_placeholders(parsed)
    
    @staticmethod
    def replace_in_body_params(body_params: Any) -> Any:
        """
        body_paramsの置換
        - 文字列の場合: JSON文字列として型を保持して置換
        - 辞書の場合: 文字列値のみ置換（互換性維持）
        
        Args:
            body_params: body_paramsの値（str or dict）
        
        Returns:
            置換後の値
        """
        if isinstance(body_params, str):
            # JSON文字列の場合は型を保持
            return VariableReplacer.replace_in_json(body_params)
        elif isinstance(body_params, dict):
            # 辞書の場合は文字列値のみ置換
            return VariableReplacer.replace_in_dict(body_params)
        else:
            return body_params
