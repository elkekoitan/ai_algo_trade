"""
Strategy Repository

MQL4/5 strateji dosyalarını yöneten repository.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime

from .models import StrategyMetadata, StrategyType
from .parser import MQLParameterParser

logger = logging.getLogger(__name__)

class StrategyRepository:
    """Strateji dosya repository"""
    
    def __init__(self, base_path: str = "mql5_forge_repos/strategies"):
        self.base_path = Path(base_path)
        self.parser = MQLParameterParser()
        
        # Klasör yapısını oluştur
        self._init_directory_structure()
        
        # Metadata cache
        self.metadata_cache: Dict[str, StrategyMetadata] = {}
        
        # Metadata dosyalarını yükle
        self._load_metadata_cache()
    
    def _init_directory_structure(self):
        """Klasör yapısını oluştur"""
        categories = [
            "grid_trading",
            "scalping",
            "trend_following",
            "breakout",
            "arbitrage",
            "hedging",
            "custom"
        ]
        
        for category in categories:
            category_path = self.base_path / category
            category_path.mkdir(parents=True, exist_ok=True)
    
    def _load_metadata_cache(self):
        """Tüm metadata dosyalarını yükle"""
        self.metadata_cache.clear()
        
        # Tüm kategori klasörlerini tara
        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                # Strateji klasörlerini tara
                for strategy_dir in category_dir.iterdir():
                    if strategy_dir.is_dir():
                        metadata_file = strategy_dir / "metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata_dict = json.load(f)
                                    metadata = StrategyMetadata(**metadata_dict)
                                    self.metadata_cache[metadata.strategy_id] = metadata
                            except Exception as e:
                                logger.error(f"Metadata yükleme hatası {metadata_file}: {str(e)}")
    
    def save_strategy(self, 
                     name: str,
                     display_name: str,
                     type: StrategyType,
                     main_file_content: str,
                     platform: str = "MT5",
                     include_files: Optional[Dict[str, str]] = None,
                     description: Optional[str] = None,
                     author: Optional[str] = None,
                     **kwargs) -> Tuple[bool, str, Optional[StrategyMetadata]]:
        """Yeni strateji kaydet"""
        try:
            # Strategy ID oluştur
            strategy_id = f"{name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Kategori klasörü
            category_path = self.base_path / type.value
            strategy_path = category_path / strategy_id
            
            # Strateji klasörünü oluştur
            strategy_path.mkdir(parents=True, exist_ok=True)
            
            # Ana dosyayı kaydet
            file_extension = ".mq5" if platform == "MT5" else ".mq4"
            main_file_name = f"{name}{file_extension}"
            main_file_path = strategy_path / main_file_name
            
            with open(main_file_path, 'w', encoding='utf-8') as f:
                f.write(main_file_content)
            
            # Include dosyalarını kaydet
            include_list = []
            if include_files:
                for filename, content in include_files.items():
                    include_path = strategy_path / filename
                    with open(include_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    include_list.append(filename)
            
            # Parametreleri parse et
            parameters, parse_metadata = self.parser.parse_file(main_file_content)
            
            # Metadata oluştur
            metadata = StrategyMetadata(
                strategy_id=strategy_id,
                name=name,
                display_name=display_name,
                type=type,
                platform=platform,
                description=description,
                author=author,
                main_file=main_file_name,
                include_files=include_list,
                **kwargs
            )
            
            # Metadata'yı kaydet
            metadata_path = strategy_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.dict(), f, indent=2, default=str)
            
            # Parameters'ı kaydet
            params_path = strategy_path / "parameters.json"
            params_data = {
                "parameters": [p.dict() for p in parameters],
                "groups": [g.dict() for g in parse_metadata.get('groups', [])]
            }
            with open(params_path, 'w', encoding='utf-8') as f:
                json.dump(params_data, f, indent=2)
            
            # README oluştur
            self._create_readme(strategy_path, metadata, parameters)
            
            # Cache'e ekle
            self.metadata_cache[strategy_id] = metadata
            
            logger.info(f"Strateji kaydedildi: {strategy_id}")
            return True, strategy_id, metadata
            
        except Exception as e:
            logger.error(f"Strateji kaydetme hatası: {str(e)}")
            return False, str(e), None
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyMetadata]:
        """Strateji metadata'sını getir"""
        return self.metadata_cache.get(strategy_id)
    
    def get_strategy_files(self, strategy_id: str) -> Dict[str, str]:
        """Strateji dosyalarını getir"""
        files = {}
        
        metadata = self.get_strategy(strategy_id)
        if not metadata:
            return files
        
        # Strateji klasörü
        strategy_path = self.base_path / metadata.type.value / strategy_id
        
        if not strategy_path.exists():
            return files
        
        # Ana dosyayı oku
        main_file_path = strategy_path / metadata.main_file
        if main_file_path.exists():
            with open(main_file_path, 'r', encoding='utf-8') as f:
                files[metadata.main_file] = f.read()
        
        # Include dosyalarını oku
        for include_file in metadata.include_files:
            include_path = strategy_path / include_file
            if include_path.exists():
                with open(include_path, 'r', encoding='utf-8') as f:
                    files[include_file] = f.read()
        
        return files
    
    def get_strategy_parameters(self, strategy_id: str) -> Tuple[List[Dict], List[Dict]]:
        """Strateji parametrelerini getir"""
        metadata = self.get_strategy(strategy_id)
        if not metadata:
            return [], []
        
        # Parametre dosyasını oku
        strategy_path = self.base_path / metadata.type.value / strategy_id
        params_path = strategy_path / "parameters.json"
        
        if params_path.exists():
            with open(params_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('parameters', []), data.get('groups', [])
        
        return [], []
    
    def list_strategies(self, 
                       type: Optional[StrategyType] = None,
                       platform: Optional[str] = None,
                       search: Optional[str] = None) -> List[StrategyMetadata]:
        """Strateji listesi"""
        strategies = list(self.metadata_cache.values())
        
        # Filtreleme
        if type:
            strategies = [s for s in strategies if s.type == type]
        
        if platform:
            strategies = [s for s in strategies if s.platform == platform]
        
        if search:
            search_lower = search.lower()
            strategies = [s for s in strategies 
                         if search_lower in s.name.lower() 
                         or search_lower in s.display_name.lower()
                         or (s.description and search_lower in s.description.lower())]
        
        # Sıralama - en yeni önce
        strategies.sort(key=lambda x: x.created_at, reverse=True)
        
        return strategies
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Stratejiyi sil"""
        try:
            metadata = self.get_strategy(strategy_id)
            if not metadata:
                return False
            
            # Strateji klasörünü sil
            strategy_path = self.base_path / metadata.type.value / strategy_id
            if strategy_path.exists():
                shutil.rmtree(strategy_path)
            
            # Cache'den kaldır
            if strategy_id in self.metadata_cache:
                del self.metadata_cache[strategy_id]
            
            logger.info(f"Strateji silindi: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Strateji silme hatası: {str(e)}")
            return False
    
    def update_strategy_metadata(self, strategy_id: str, updates: Dict) -> bool:
        """Strateji metadata'sını güncelle"""
        try:
            metadata = self.get_strategy(strategy_id)
            if not metadata:
                return False
            
            # Metadata'yı güncelle
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            metadata.updated_at = datetime.now()
            
            # Dosyaya kaydet
            strategy_path = self.base_path / metadata.type.value / strategy_id
            metadata_path = strategy_path / "metadata.json"
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.dict(), f, indent=2, default=str)
            
            # Cache'i güncelle
            self.metadata_cache[strategy_id] = metadata
            
            return True
            
        except Exception as e:
            logger.error(f"Metadata güncelleme hatası: {str(e)}")
            return False
    
    def _create_readme(self, strategy_path: Path, metadata: StrategyMetadata, parameters: List):
        """README dosyası oluştur"""
        readme_content = f"""# {metadata.display_name}

## Açıklama
{metadata.description or 'Açıklama eklenmemiş.'}

## Özellikler
- **Tür**: {metadata.type.value}
- **Platform**: {metadata.platform}
- **Versiyon**: {metadata.version}
- **Yazar**: {metadata.author or 'Belirtilmemiş'}
- **Oluşturulma**: {metadata.created_at.strftime('%Y-%m-%d %H:%M')}

## Desteklenen Semboller
{', '.join(metadata.supported_symbols) if metadata.supported_symbols else 'Tüm semboller'}

## Önerilen Timeframe'ler
{', '.join(metadata.recommended_timeframes) if metadata.recommended_timeframes else 'Belirtilmemiş'}

## Risk Parametreleri
- **Minimum Bakiye**: ${metadata.minimum_balance:,.2f}
- **Önerilen Kaldıraç**: 1:{metadata.recommended_leverage}
- **Varsayılan Risk**: %{metadata.default_risk_percent}
- **Maksimum Pozisyon**: {metadata.max_positions}

## Parametreler
Toplam {len(parameters)} parametre bulunmaktadır.

### Parametre Grupları
"""
        
        # Parametreleri gruplara göre yaz
        param_groups = {}
        for param in parameters:
            group = param.group or "Genel Ayarlar"
            if group not in param_groups:
                param_groups[group] = []
            param_groups[group].append(param)
        
        for group_name, group_params in param_groups.items():
            readme_content += f"\n#### {group_name}\n"
            for param in group_params:
                readme_content += f"- **{param.display_name}** ({param.type.value}): {param.description or 'Açıklama yok'}\n"
                if param.default_value is not None:
                    readme_content += f"  - Varsayılan: {param.default_value}\n"
                if param.min_value is not None and param.max_value is not None:
                    readme_content += f"  - Aralık: {param.min_value} - {param.max_value}\n"
        
        readme_content += """
## Kullanım
1. Stratejiyi MT5 Experts klasörüne kopyalayın
2. MT5'te Expert Advisors'ı aktif edin
3. Stratejiyi chart'a sürükleyin
4. Parametreleri ayarlayın
5. AutoTrading'i aktif edin

## Notlar
Bu strateji AI Algo Trade platformu üzerinden yönetilmektedir.
"""
        
        readme_path = strategy_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def get_category_stats(self) -> Dict[str, int]:
        """Kategori istatistikleri"""
        stats = {}
        for strategy in self.metadata_cache.values():
            category = strategy.type.value
            stats[category] = stats.get(category, 0) + 1
        return stats 