"""
MQL Parameter Parser

MQL4/5 kodlarından parametreleri otomatik olarak parse eder.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from .models import StrategyParameter, ParameterType, ParameterGroup

logger = logging.getLogger(__name__)

class MQLParameterParser:
    """MQL4/5 parametre parser"""
    
    def __init__(self):
        # MQL extern/input parameter pattern
        self.param_pattern = re.compile(
            r'(?:extern|input)\s+(\w+)\s+(\w+)\s*=\s*([^;]+);(?:\s*//(.*))?',
            re.MULTILINE
        )
        
        # Enum pattern
        self.enum_pattern = re.compile(
            r'enum\s+(\w+)\s*{([^}]+)}',
            re.MULTILINE | re.DOTALL
        )
        
        # Property pattern
        self.property_pattern = re.compile(
            r'#property\s+(\w+)\s+"?([^"\n]+)"?',
            re.MULTILINE
        )
        
        # Type mappings
        self.type_map = {
            'bool': ParameterType.BOOL,
            'int': ParameterType.INT,
            'uint': ParameterType.INT,
            'long': ParameterType.INT,
            'ulong': ParameterType.INT,
            'double': ParameterType.DOUBLE,
            'float': ParameterType.DOUBLE,
            'string': ParameterType.STRING,
            'datetime': ParameterType.DATETIME,
            'color': ParameterType.COLOR
        }
        
        # Default value type inference
        self.value_inference = {
            'true': ParameterType.BOOL,
            'false': ParameterType.BOOL,
            'clr': ParameterType.COLOR,
            '"': ParameterType.STRING,
            "'": ParameterType.STRING,
            '.': ParameterType.DOUBLE
        }
    
    def parse_file(self, content: str) -> Tuple[List[StrategyParameter], Dict[str, Any]]:
        """MQL dosyasını parse et"""
        try:
            # Properties çıkar
            properties = self._extract_properties(content)
            
            # Enum'ları çıkar
            enums = self._extract_enums(content)
            
            # Parametreleri çıkar
            parameters = self._extract_parameters(content, enums)
            
            # Grupları oluştur
            groups = self._create_parameter_groups(parameters)
            
            # Metadata oluştur
            metadata = {
                'properties': properties,
                'enums': enums,
                'groups': groups,
                'total_parameters': len(parameters)
            }
            
            return parameters, metadata
            
        except Exception as e:
            logger.error(f"MQL parse error: {str(e)}")
            return [], {}
    
    def _extract_properties(self, content: str) -> Dict[str, str]:
        """#property direktiflerini çıkar"""
        properties = {}
        
        for match in self.property_pattern.finditer(content):
            prop_name = match.group(1)
            prop_value = match.group(2)
            properties[prop_name] = prop_value
        
        return properties
    
    def _extract_enums(self, content: str) -> Dict[str, List[str]]:
        """Enum tanımlarını çıkar"""
        enums = {}
        
        for match in self.enum_pattern.finditer(content):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Enum değerlerini parse et
            values = []
            for line in enum_body.split(','):
                line = line.strip()
                if '=' in line:
                    value_name = line.split('=')[0].strip()
                else:
                    value_name = line.strip()
                
                if value_name and not value_name.startswith('//'):
                    values.append(value_name)
            
            enums[enum_name] = values
        
        return enums
    
    def _extract_parameters(self, content: str, enums: Dict[str, List[str]]) -> List[StrategyParameter]:
        """Parametreleri çıkar"""
        parameters = []
        
        for match in self.param_pattern.finditer(content):
            param_type = match.group(1)
            param_name = match.group(2)
            default_value = match.group(3).strip()
            comment = match.group(4).strip() if match.group(4) else ""
            
            # Parametre tipini belirle
            if param_type in self.type_map:
                type_enum = self.type_map[param_type]
            elif param_type in enums:
                type_enum = ParameterType.ENUM
            else:
                # Tip inference yap
                type_enum = self._infer_type(default_value)
            
            # Default değeri parse et
            parsed_value = self._parse_default_value(default_value, type_enum)
            
            # Display name oluştur
            display_name = self._create_display_name(param_name, comment)
            
            # Min/max değerleri belirle
            min_val, max_val, step = self._infer_constraints(param_name, type_enum, comment)
            
            # Grup belirle
            group = self._infer_group(param_name, comment)
            
            # Parametre oluştur
            parameter = StrategyParameter(
                name=param_name,
                display_name=display_name,
                type=type_enum,
                default_value=parsed_value,
                description=comment if comment else None,
                min_value=min_val,
                max_value=max_val,
                step=step,
                options=enums.get(param_type, None) if type_enum == ParameterType.ENUM else None,
                group=group,
                is_required=True,
                is_visible=True
            )
            
            parameters.append(parameter)
        
        return parameters
    
    def _infer_type(self, value: str) -> ParameterType:
        """Değerden tip çıkarımı yap"""
        value_lower = value.lower()
        
        # Bool kontrolü
        if value_lower in ['true', 'false']:
            return ParameterType.BOOL
        
        # Color kontrolü
        if 'clr' in value_lower or 'color' in value_lower:
            return ParameterType.COLOR
        
        # String kontrolü
        if value.startswith('"') or value.startswith("'"):
            return ParameterType.STRING
        
        # Double/Float kontrolü
        if '.' in value:
            return ParameterType.DOUBLE
        
        # Default: INT
        return ParameterType.INT
    
    def _parse_default_value(self, value_str: str, param_type: ParameterType) -> Any:
        """Default değeri parse et"""
        try:
            value_str = value_str.strip()
            
            if param_type == ParameterType.BOOL:
                return value_str.lower() == 'true'
            
            elif param_type == ParameterType.INT:
                # Hex değer kontrolü
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            
            elif param_type == ParameterType.DOUBLE:
                return float(value_str)
            
            elif param_type == ParameterType.STRING:
                # Tırnakları kaldır
                return value_str.strip('"').strip("'")
            
            elif param_type == ParameterType.COLOR:
                # Color değerini string olarak sakla
                return value_str
            
            else:
                return value_str
                
        except:
            return value_str
    
    def _create_display_name(self, param_name: str, comment: str) -> str:
        """Parametre için görüntü adı oluştur"""
        if comment:
            # Comment'ten display name al
            parts = comment.split('-')
            if len(parts) > 0:
                return parts[0].strip()
        
        # CamelCase'i space'li hale getir
        display = re.sub(r'(?<!^)(?=[A-Z])', ' ', param_name)
        
        # Bazı kısaltmaları düzelt
        replacements = {
            'Tp': 'Take Profit',
            'Sl': 'Stop Loss',
            'Lot': 'Lot Size',
            'Ma': 'Moving Average',
            'Rsi': 'RSI',
            'Ema': 'EMA',
            'Sma': 'SMA'
        }
        
        for old, new in replacements.items():
            display = display.replace(old, new)
        
        return display.strip()
    
    def _infer_constraints(self, name: str, param_type: ParameterType, comment: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Parametre kısıtlamalarını çıkar"""
        name_lower = name.lower()
        
        # Lot size constraints
        if 'lot' in name_lower:
            return 0.01, 100.0, 0.01
        
        # Period constraints
        elif 'period' in name_lower:
            return 1, 500, 1
        
        # Level/Percent constraints
        elif 'level' in name_lower or 'percent' in name_lower:
            return 0, 100, 1
        
        # TP/SL constraints (pips)
        elif 'tp' in name_lower or 'sl' in name_lower:
            return 0, 10000, 10
        
        # Hour constraints
        elif 'hour' in name_lower:
            return 0, 23, 1
        
        # Minute constraints
        elif 'minute' in name_lower:
            return 0, 59, 1
        
        # Comment'ten constraint ara
        constraint_match = re.search(r'\[(\d+)-(\d+)\]', comment)
        if constraint_match:
            min_val = float(constraint_match.group(1))
            max_val = float(constraint_match.group(2))
            step = 1.0 if param_type == ParameterType.INT else 0.01
            return min_val, max_val, step
        
        return None, None, None
    
    def _infer_group(self, name: str, comment: str) -> str:
        """Parametre grubunu belirle"""
        name_lower = name.lower()
        
        # Comment'ten grup ara
        group_match = re.search(r'\[([A-Za-z\s]+)\]', comment)
        if group_match:
            return group_match.group(1).strip()
        
        # İsimden grup çıkar
        if 'time' in name_lower or 'hour' in name_lower or 'minute' in name_lower:
            return "Time Settings"
        
        elif 'lot' in name_lower or 'risk' in name_lower:
            return "Risk Management"
        
        elif 'tp' in name_lower or 'sl' in name_lower or 'profit' in name_lower or 'loss' in name_lower:
            return "Take Profit / Stop Loss"
        
        elif 'ma' in name_lower or 'ema' in name_lower or 'sma' in name_lower:
            return "Moving Averages"
        
        elif 'rsi' in name_lower or 'macd' in name_lower or 'stoch' in name_lower:
            return "Indicators"
        
        elif 'buy' in name_lower or 'sell' in name_lower:
            return "Trade Settings"
        
        elif 'alert' in name_lower or 'notification' in name_lower:
            return "Alerts & Notifications"
        
        elif 'position' in name_lower or 'order' in name_lower:
            return "Position Management"
        
        else:
            return "General Settings"
    
    def _create_parameter_groups(self, parameters: List[StrategyParameter]) -> List[ParameterGroup]:
        """Parametreleri gruplara ayır"""
        groups_dict = {}
        
        # Parametreleri gruplara ayır
        for param in parameters:
            group_name = param.group or "General Settings"
            
            if group_name not in groups_dict:
                groups_dict[group_name] = []
            
            groups_dict[group_name].append(param.name)
        
        # ParameterGroup objelerine dönüştür
        groups = []
        order = 0
        
        # Öncelik sırası
        priority_order = [
            "General Settings",
            "Trade Settings",
            "Risk Management",
            "Take Profit / Stop Loss",
            "Position Management",
            "Moving Averages",
            "Indicators",
            "Time Settings",
            "Alerts & Notifications"
        ]
        
        # Öncelikli grupları ekle
        for group_name in priority_order:
            if group_name in groups_dict:
                group = ParameterGroup(
                    name=group_name.lower().replace(' ', '_'),
                    display_name=group_name,
                    parameters=groups_dict[group_name],
                    order=order,
                    is_expanded=order < 3  # İlk 3 grup açık
                )
                groups.append(group)
                order += 1
                del groups_dict[group_name]
        
        # Kalan grupları ekle
        for group_name, param_names in groups_dict.items():
            group = ParameterGroup(
                name=group_name.lower().replace(' ', '_'),
                display_name=group_name,
                parameters=param_names,
                order=order,
                is_expanded=False
            )
            groups.append(group)
            order += 1
        
        return groups 