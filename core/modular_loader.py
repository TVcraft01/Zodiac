"""
Module 7: Modular Loader
Système de chargement dynamique des modules externes
"""

import importlib
import sys
import os
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
import json

class ModularLoader:
    def __init__(self, modules_dir: str = "modules"):
        """
        Initialise le chargeur de modules
        
        Args:
            modules_dir: Répertoire des modules externes
        """
        self.modules_dir = modules_dir
        self.loaded_modules = {}
        self.module_metadata = {}
        self.metadata_file = "data/modules_metadata.json"
        
        # Créer le dossier modules s'il n'existe pas
        Path(modules_dir).mkdir(exist_ok=True)
        
        # Créer le dossier data
        Path("data").mkdir(exist_ok=True)
        
        # Charger les métadonnées existantes
        self._load_metadata()
    
    def discover_modules(self) -> List[Dict]:
        """
        Découvre les modules disponibles
        
        Returns:
            Liste des modules découverts
        """
        modules = []
        
        try:
            # Rechercher les fichiers .py dans le dossier modules
            modules_path = Path(self.modules_dir)
            
            for py_file in modules_path.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                
                module_name = py_file.stem
                module_info = self._analyze_module_file(py_file)
                
                if module_info:
                    modules.append(module_info)
            
            # Rechercher également dans les sous-dossiers
            for subdir in modules_path.iterdir():
                if subdir.is_dir():
                    init_file = subdir / "__init__.py"
                    if init_file.exists():
                        # C'est un package Python
                        module_info = self._analyze_package(subdir)
                        if module_info:
                            modules.append(module_info)
        
        except Exception as e:
            print(f"✗ Erreur découverte modules: {e}")
        
        return modules
    
    def _analyze_module_file(self, file_path: Path) -> Optional[Dict]:
        """
        Analyse un fichier module
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            Informations du module ou None
        """
        try:
            module_name = file_path.stem
            
            # Lire les premières lignes pour les métadonnées
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # Lire les 2000 premiers caractères
            
            # Extraire les docstrings et commentaires spéciaux
            metadata = {
                'name': module_name,
                'type': 'module',
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            }
            
            # Chercher des métadonnées dans les commentaires
            if '"name":' in content or "'name':" in content:
                # Essayer d'extraire du JSON ou dict Python
                import re
                # Pattern pour dictionnaire Python simple
                dict_pattern = r'\{(?:[^{}]|(?R))*\}'
                matches = re.findall(dict_pattern, content, re.DOTALL)
                
                for match in matches:
                    try:
                        # Convertir en dict (approximation)
                        match = match.replace("'", '"')
                        data = json.loads(match)
                        if 'name' in data:
                            metadata.update(data)
                            break
                    except:
                        pass
            
            # Extraire la docstring
            docstring = self._extract_docstring(content)
            if docstring:
                metadata['description'] = docstring.split('\n')[0]
                metadata['full_doc'] = docstring
            
            # Vérifier les dépendances
            imports = self._extract_imports(content)
            if imports:
                metadata['imports'] = imports
            
            return metadata
            
        except Exception as e:
            print(f"✗ Erreur analyse {file_path}: {e}")
            return None
    
    def _analyze_package(self, package_path: Path) -> Optional[Dict]:
        """
        Analyse un package Python
        
        Args:
            package_path: Chemin du package
        
        Returns:
            Informations du package ou None
        """
        try:
            package_name = package_path.name
            
            # Vérifier le __init__.py
            init_file = package_path / "__init__.py"
            if not init_file.exists():
                return None
            
            metadata = {
                'name': package_name,
                'type': 'package',
                'path': str(package_path),
                'modules': []
            }
            
            # Analyser tous les modules dans le package
            for py_file in package_path.glob("*.py"):
                if py_file.name != "__init__.py":
                    module_info = self._analyze_module_file(py_file)
                    if module_info:
                        metadata['modules'].append(module_info['name'])
            
            return metadata
            
        except Exception as e:
            print(f"✗ Erreur analyse package {package_path}: {e}")
            return None
    
    def _extract_docstring(self, content: str) -> Optional[str]:
        """Extrait la docstring d'un module"""
        try:
            import ast
            tree = ast.parse(content)
            
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Str):
                    return tree.body[0].value.s
            
            # Chercher les triples quotes
            import re
            patterns = [
                r'\"\"\"(.*?)\"\"\"',
                r"\'\'\'(.*?)\'\'\'"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        except:
            pass
        
        return None
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrait les imports d'un module"""
        imports = []
        
        try:
            import ast
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        
        except:
            # Méthode simple avec regex
            import re
            import_patterns = [
                r'^\s*import\s+(\w+)',
                r'^\s*from\s+(\w+)\s+import'
            ]
            
            for line in content.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.append(match.group(1))
        
        return list(set(imports))  # Supprimer les doublons
    
    def load_module(self, module_name: str, reload: bool = False) -> Optional[Any]:
        """
        Charge un module dynamiquement
        
        Args:
            module_name: Nom du module
            reload: Recharger même si déjà chargé
        
        Returns:
            Module chargé ou None
        """
        try:
            # Vérifier si déjà chargé
            if module_name in self.loaded_modules and not reload:
                print(f"✓ Module {module_name} déjà chargé")
                return self.loaded_modules[module_name]
            
            # Construire le chemin d'import
            module_path = f"{self.modules_dir}.{module_name}"
            
            # Ajouter au path Python si nécessaire
            if self.modules_dir not in sys.path:
                sys.path.insert(0, self.modules_dir)
            
            # Charger le module
            module = importlib.import_module(module_name)
            
            # Recharger si demandé
            if reload:
                module = importlib.reload(module)
            
            # Stocker le module
            self.loaded_modules[module_name] = module
            
            # Mettre à jour les métadonnées
            self._update_module_metadata(module_name, module)
            
            print(f"✓ Module {module_name} chargé avec succès")
            return module
            
        except ImportError as e:
            print(f"✗ Erreur import {module_name}: {e}")
            return None
        except Exception as e:
            print(f"✗ Erreur chargement {module_name}: {e}")
            return None
    
    def load_package(self, package_name: str) -> Optional[Dict]:
        """
        Charge un package entier
        
        Args:
            package_name: Nom du package
        
        Returns:
            Modules chargés ou None
        """
        try:
            package_path = Path(self.modules_dir) / package_name
            
            if not package_path.exists() or not package_path.is_dir():
                print(f"✗ Package {package_name} non trouvé")
                return None
            
            # Charger tous les modules du package
            loaded = {}
            
            for py_file in package_path.glob("*.py"):
                if py_file.name != "__init__.py":
                    module_name = py_file.stem
                    module = self.load_module(f"{package_name}.{module_name}")
                    if module:
                        loaded[module_name] = module
            
            print(f"✓ Package {package_name} chargé: {len(loaded)} modules")
            return loaded
            
        except Exception as e:
            print(f"✗ Erreur chargement package {package_name}: {e}")
            return None
    
    def _update_module_metadata(self, module_name: str, module: Any):
        """Met à jour les métadonnées d'un module"""
        try:
            metadata = {
                'name': module_name,
                'loaded_at': importlib.import_module('datetime').datetime.now().isoformat(),
                'functions': [],
                'classes': [],
                'attributes': []
            }
            
            # Inspecter le module
            for name, obj in inspect.getmembers(module):
                if not name.startswith('_'):  # Ignorer les privés
                    if inspect.isfunction(obj):
                        metadata['functions'].append(name)
                    elif inspect.isclass(obj):
                        metadata['classes'].append(name)
                    elif not inspect.ismodule(obj):
                        metadata['attributes'].append(name)
            
            self.module_metadata[module_name] = metadata
            self._save_metadata()
            
        except Exception as e:
            print(f"✗ Erreur métadonnées {module_name}: {e}")
    
    def get_module_functions(self, module_name: str) -> List[str]:
        """
        Récupère les fonctions d'un module
        
        Args:
            module_name: Nom du module
        
        Returns:
            Liste des fonctions
        """
        if module_name in self.module_metadata:
            return self.module_metadata[module_name].get('functions', [])
        return []
    
    def get_module_classes(self, module_name: str) -> List[str]:
        """
        Récupère les classes d'un module
        
        Args:
            module_name: Nom du module
        
        Returns:
            Liste des classes
        """
        if module_name in self.module_metadata:
            return self.module_metadata[module_name].get('classes', [])
        return []
    
    def execute_function(self, module_name: str, function_name: str, *args, **kwargs) -> Any:
        """
        Exécute une fonction d'un module
        
        Args:
            module_name: Nom du module
            function_name: Nom de la fonction
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            Résultat de la fonction
        """
        try:
            # Charger le module si nécessaire
            module = self.load_module(module_name)
            if not module:
                raise ImportError(f"Module {module_name} non chargé")
            
            # Récupérer la fonction
            if not hasattr(module, function_name):
                raise AttributeError(f"Fonction {function_name} non trouvée dans {module_name}")
            
            func = getattr(module, function_name)
            
            if not callable(func):
                raise TypeError(f"{function_name} n'est pas callable")
            
            # Exécuter la fonction
            print(f"⚡ Exécution: {module_name}.{function_name}()")
            result = func(*args, **kwargs)
            
            return result
            
        except Exception as e:
            print(f"✗ Erreur exécution {module_name}.{function_name}: {e}")
            raise
    
    def create_instance(self, module_name: str, class_name: str, *args, **kwargs) -> Any:
        """
        Crée une instance d'une classe
        
        Args:
            module_name: Nom du module
            class_name: Nom de la classe
            *args: Arguments du constructeur
            **kwargs: Arguments nommés du constructeur
        
        Returns:
            Instance de la classe
        """
        try:
            # Charger le module
            module = self.load_module(module_name)
            if not module:
                raise ImportError(f"Module {module_name} non chargé")
            
            # Récupérer la classe
            if not hasattr(module, class_name):
                raise AttributeError(f"Classe {class_name} non trouvée dans {module_name}")
            
            cls = getattr(module, class_name)
            
            if not inspect.isclass(cls):
                raise TypeError(f"{class_name} n'est pas une classe")
            
            # Créer l'instance
            print(f"🏗️  Création: {module_name}.{class_name}()")
            instance = cls(*args, **kwargs)
            
            return instance
            
        except Exception as e:
            print(f"✗ Erreur instanciation {module_name}.{class_name}: {e}")
            raise
    
    def unload_module(self, module_name: str) -> bool:
        """
        Décharge un module de la mémoire
        
        Args:
            module_name: Nom du module
        
        Returns:
            True si succès
        """
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            if module_name in self.loaded_modules:
                del self.loaded_modules[module_name]
            
            print(f"✓ Module {module_name} déchargé")
            return True
            
        except Exception as e:
            print(f"✗ Erreur déchargement {module_name}: {e}")
            return False
    
    def _load_metadata(self):
        """Charge les métadonnées depuis le fichier"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.module_metadata = json.load(f)
        except:
            self.module_metadata = {}
    
    def _save_metadata(self):
        """Sauvegarde les métadonnées dans le fichier"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.module_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"✗ Erreur sauvegarde métadonnées: {e}")
    
    def get_loaded_modules(self) -> List[str]:
        """Retourne la liste des modules chargés"""
        return list(self.loaded_modules.keys())
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Retourne les informations d'un module"""
        return self.module_metadata.get(module_name)

# Test du module
if __name__ == "__main__":
    loader = ModularLoader(modules_dir="test_modules")
    
    # Créer un dossier de test
    test_dir = Path("test_modules")
    test_dir.mkdir(exist_ok=True)
    
    # Créer un module de test
    test_module_code = '''
"""
Module de test pour ModularLoader
"""

def hello(name: str = "World") -> str:
    """Dit bonjour"""
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    """Additionne deux nombres"""
    return a + b

class Calculator:
    """Une calculatrice simple"""
    
    def __init__(self, name: str = "Calc"):
        self.name = name
    
    def multiply(self, a: float, b: float) -> float:
        """Multiplie deux nombres"""
        return a * b
    
    def get_name(self) -> str:
        """Retourne le nom de la calculatrice"""
        return self.name

# Variable de test
VERSION = "1.0.0"
'''
    
    # Écrire le module de test
    with open(test_dir / "test_calc.py", "w", encoding="utf-8") as f:
        f.write(test_module_code)
    
    print("🧪 Test Modular Loader\n")
    
    # Découvrir les modules
    print("1. Découverte des modules:")
    modules = loader.discover_modules()
    for module in modules:
        print(f"   • {module['name']} ({module['type']})")
        if 'description' in module:
            print(f"     {module['description']}")
    
    # Charger un module
    print("\n2. Chargement du module:")
    module = loader.load_module("test_calc")
    
    if module:
        # Afficher les informations
        info = loader.get_module_info("test_calc")
        if info:
            print(f"   Fonctions: {', '.join(info['functions'])}")
            print(f"   Classes: {', '.join(info['classes'])}")
            print(f"   Attributs: {', '.join(info['attributes'])}")
        
        # Exécuter une fonction
        print("\n3. Exécution de fonction:")
        try:
            result = loader.execute_function("test_calc", "hello", "Zodiac")
            print(f"   hello('Zodiac') = {result}")
            
            result = loader.execute_function("test_calc", "add", 5, 3)
            print(f"   add(5, 3) = {result}")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
        
        # Créer une instance
        print("\n4. Instanciation de classe:")
        try:
            calc = loader.create_instance("test_calc", "Calculator", "SuperCalc")
            result = calc.multiply(4, 5)
            print(f"   Calculator('SuperCalc').multiply(4, 5) = {result}")
            print(f"   Nom: {calc.get_name()}")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
        
        # Modules chargés
        print(f"\n5. Modules chargés: {loader.get_loaded_modules()}")
        
        # Nettoyer
        loader.unload_module("test_calc")
    
    # Supprimer le fichier de test
    (test_dir / "test_calc.py").unlink()
    test_dir.rmdir()