"""
Module de surveillance système
"""

import psutil
import platform
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.update_interval = 2.0  # secondes
    
    def get_system_info(self):
        """Récupère les informations système"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu,
                'memory_percent': memory.percent,
                'memory_used': memory.used // 1024 // 1024,  # MB
                'memory_total': memory.total // 1024 // 1024,  # MB
                'disk_percent': disk.percent,
                'disk_used': disk.used // 1024 // 1024 // 1024,  # GB
                'disk_total': disk.total // 1024 // 1024 // 1024,  # GB
                'os': f"{platform.system()} {platform.release()}",
                'python_version': platform.python_version(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_processes(self, limit=10):
        """Liste les processus"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'] or 'Unknown',
                        'cpu': info['cpu_percent'],
                        'memory': info['memory_percent']
                    })
                except:
                    continue
                
                if len(processes) >= limit:
                    break
            
            # Trier par CPU
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            
        except:
            pass
        
        return processes
    
    def format_system_report(self):
        """Formate un rapport système"""
        info = self.get_system_info()
        
        if 'error' in info:
            return f"❌ Erreur: {info['error']}"
        
        report = f"""💻 **Rapport système** ({info['timestamp']})

🔸 **CPU**: {info['cpu_percent']:.1f}%
🔸 **Mémoire**: {info['memory_percent']:.1f}% ({info['memory_used']}MB/{info['memory_total']}MB)
🔸 **Disque**: {info['disk_percent']:.1f}% ({info['disk_used']}GB/{info['disk_total']}GB)
🔸 **OS**: {info['os']}
🔸 **Python**: {info['python_version']}

"""
        
        # Ajouter les processus
        processes = self.get_processes(5)
        if processes:
            report += "🔥 **Top processus:**\n"
            for proc in processes:
                report += f"  • {proc['name'][:20]:20} CPU:{proc['cpu']:5.1f}% MEM:{proc['memory']:5.1f}%\n"
        
        return report

# Test
if __name__ == "__main__":
    monitor = SystemMonitor()
    print(monitor.format_system_report())