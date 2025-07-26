#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖥️ 系統狀態監控模組
提供詳細的硬體和軟體系統資訊監控
"""

import psutil
import platform
import os
import sys
import datetime
import subprocess
import json
from pathlib import Path

class SystemStatusMonitor:
    """系統狀態監控類"""
    
    def __init__(self):
        self.system_info = {}
        self.update_system_info()
    
    def update_system_info(self):
        """更新系統資訊"""
        try:
            self.system_info = {
                'timestamp': datetime.datetime.now(),
                'platform': self.get_platform_info(),
                'cpu': self.get_cpu_info(),
                'memory': self.get_memory_info(),
                'disk': self.get_disk_info(),
                'gpu': self.get_gpu_info(),
                'network': self.get_network_info(),
                'python': self.get_python_info(),
                'processes': self.get_process_info()
            }
        except Exception as e:
            print(f"❌ 更新系統資訊失敗: {e}")
    
    def get_platform_info(self):
        """獲取平台資訊"""
        try:
            return {
                'system': platform.system(),
                'version': platform.version(),
                'architecture': platform.architecture()[0],
                'machine': platform.machine(),
                'processor': platform.processor(),
                'node': platform.node(),
                'release': platform.release(),
                'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_cpu_info(self):
        """獲取 CPU 資訊"""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A',
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 'N/A',
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else 'N/A',
                'usage_percent': psutil.cpu_percent(interval=1),
                'usage_per_core': psutil.cpu_percent(interval=1, percpu=True),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            }
            
            # 嘗試獲取 CPU 溫度（Linux）
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        cpu_info['temperature'] = temps
                    else:
                        cpu_info['temperature'] = 'N/A'
                else:
                    cpu_info['temperature'] = 'N/A'
            except:
                cpu_info['temperature'] = 'N/A'
            
            return cpu_info
        except Exception as e:
            return {'error': str(e)}
    
    def get_memory_info(self):
        """獲取記憶體資訊"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                'total_gb': round(virtual_mem.total / (1024**3), 2),
                'available_gb': round(virtual_mem.available / (1024**3), 2),
                'used_gb': round(virtual_mem.used / (1024**3), 2),
                'free_gb': round(virtual_mem.free / (1024**3), 2),
                'usage_percent': virtual_mem.percent,
                'swap_total_gb': round(swap_mem.total / (1024**3), 2),
                'swap_used_gb': round(swap_mem.used / (1024**3), 2),
                'swap_free_gb': round(swap_mem.free / (1024**3), 2),
                'swap_percent': swap_mem.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_disk_info(self):
        """獲取磁碟資訊"""
        try:
            disk_info = {}
            
            # 獲取所有磁碟分區
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total_gb': round(partition_usage.total / (1024**3), 2),
                        'used_gb': round(partition_usage.used / (1024**3), 2),
                        'free_gb': round(partition_usage.free / (1024**3), 2),
                        'usage_percent': round((partition_usage.used / partition_usage.total) * 100, 2)
                    }
                except PermissionError:
                    continue
            
            # 獲取磁碟 I/O 統計
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info['io_stats'] = {
                        'read_count': disk_io.read_count,
                        'write_count': disk_io.write_count,
                        'read_bytes': round(disk_io.read_bytes / (1024**3), 2),
                        'write_bytes': round(disk_io.write_bytes / (1024**3), 2)
                    }
            except:
                disk_info['io_stats'] = 'N/A'
            
            return disk_info
        except Exception as e:
            return {'error': str(e)}
    
    def get_gpu_info(self):
        """獲取 GPU 資訊"""
        gpu_info = {}
        
        # 嘗試使用 nvidia-ml-py (NVIDIA GPU)
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            gpu_info['nvidia_gpus'] = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                
                # 記憶體資訊
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # 溫度
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = 'N/A'
                
                # 使用率
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = util.gpu
                    mem_util = util.memory
                except:
                    gpu_util = 'N/A'
                    mem_util = 'N/A'
                
                gpu_info['nvidia_gpus'].append({
                    'id': i,
                    'name': name,
                    'memory_total_mb': round(mem_info.total / (1024**2)),
                    'memory_used_mb': round(mem_info.used / (1024**2)),
                    'memory_free_mb': round(mem_info.free / (1024**2)),
                    'temperature': temp,
                    'gpu_utilization': gpu_util,
                    'memory_utilization': mem_util
                })
        except ImportError:
            gpu_info['nvidia_info'] = 'pynvml 未安裝，無法獲取 NVIDIA GPU 詳細資訊'
        except Exception as e:
            gpu_info['nvidia_error'] = str(e)
        
        # 嘗試使用 Windows 命令獲取 GPU 資訊
        if platform.system() == 'Windows':
            try:
                result = subprocess.run([
                    'wmic', 'path', 'win32_VideoController', 'get', 
                    'name,AdapterRAM,DriverVersion', '/format:csv'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # 跳過標題
                    gpu_info['windows_gpus'] = []
                    
                    for line in lines:
                        if line.strip():
                            parts = line.split(',')
                            if len(parts) >= 4:
                                gpu_info['windows_gpus'].append({
                                    'name': parts[3] if len(parts) > 3 else 'Unknown',
                                    'memory_bytes': parts[1] if len(parts) > 1 else 'Unknown',
                                    'driver_version': parts[2] if len(parts) > 2 else 'Unknown'
                                })
            except Exception as e:
                gpu_info['windows_error'] = str(e)
        
        # 如果沒有找到任何 GPU 資訊
        if not gpu_info:
            gpu_info['status'] = '無法檢測到 GPU 或獲取 GPU 資訊'
        
        return gpu_info
    
    def get_network_info(self):
        """獲取網路資訊"""
        try:
            network_info = {}
            
            # 網路介面資訊
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            network_info['interfaces'] = {}
            for interface_name, interface_addresses in net_if_addrs.items():
                interface_info = {
                    'addresses': [],
                    'is_up': net_if_stats[interface_name].isup if interface_name in net_if_stats else False,
                    'speed': net_if_stats[interface_name].speed if interface_name in net_if_stats else 'Unknown'
                }
                
                for addr in interface_addresses:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                network_info['interfaces'][interface_name] = interface_info
            
            # 網路 I/O 統計
            net_io = psutil.net_io_counters()
            if net_io:
                network_info['io_stats'] = {
                    'bytes_sent': round(net_io.bytes_sent / (1024**2), 2),
                    'bytes_recv': round(net_io.bytes_recv / (1024**2), 2),
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            
            return network_info
        except Exception as e:
            return {'error': str(e)}
    
    def get_python_info(self):
        """獲取 Python 環境資訊"""
        try:
            return {
                'version': sys.version,
                'executable': sys.executable,
                'platform': sys.platform,
                'path': sys.path[:3],  # 只顯示前3個路徑
                'modules_count': len(sys.modules),
                'current_working_directory': os.getcwd()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_process_info(self):
        """獲取進程資訊"""
        try:
            current_process = psutil.Process()
            
            return {
                'current_pid': current_process.pid,
                'current_name': current_process.name(),
                'current_cpu_percent': current_process.cpu_percent(),
                'current_memory_mb': round(current_process.memory_info().rss / (1024**2), 2),
                'current_threads': current_process.num_threads(),
                'total_processes': len(psutil.pids()),
                'running_processes': len([p for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_RUNNING])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_formatted_status(self):
        """獲取格式化的系統狀態文本"""
        status_text = f"🖥️ **系統狀態監控報告**\n"
        status_text += f"📅 **更新時間:** {self.system_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 平台資訊
        platform_info = self.system_info.get('platform', {})
        if 'error' not in platform_info:
            status_text += "💻 **系統平台**\n"
            status_text += f"   • 作業系統: {platform_info.get('system', 'N/A')} {platform_info.get('release', 'N/A')}\n"
            status_text += f"   • 架構: {platform_info.get('architecture', 'N/A')}\n"
            status_text += f"   • 處理器: {platform_info.get('processor', 'N/A')}\n"
            status_text += f"   • 電腦名稱: {platform_info.get('node', 'N/A')}\n"
            boot_time = platform_info.get('boot_time')
            if boot_time:
                uptime = datetime.datetime.now() - boot_time
                status_text += f"   • 開機時間: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                status_text += f"   • 運行時間: {str(uptime).split('.')[0]}\n"
            status_text += "\n"
        
        # CPU 資訊
        cpu_info = self.system_info.get('cpu', {})
        if 'error' not in cpu_info:
            status_text += "🔥 **CPU 資訊**\n"
            status_text += f"   • 物理核心: {cpu_info.get('physical_cores', 'N/A')}\n"
            status_text += f"   • 邏輯核心: {cpu_info.get('logical_cores', 'N/A')}\n"
            
            current_freq = cpu_info.get('current_frequency')
            if current_freq != 'N/A':
                status_text += f"   • 目前頻率: {current_freq:.0f} MHz\n"
            
            max_freq = cpu_info.get('max_frequency')
            if max_freq != 'N/A':
                status_text += f"   • 最大頻率: {max_freq:.0f} MHz\n"
            
            status_text += f"   • CPU 使用率: {cpu_info.get('usage_percent', 'N/A')}%\n"
            
            temp = cpu_info.get('temperature')
            if temp != 'N/A' and temp:
                status_text += f"   • CPU 溫度: {temp}\n"
            
            status_text += "\n"
        
        # 記憶體資訊
        memory_info = self.system_info.get('memory', {})
        if 'error' not in memory_info:
            status_text += "💾 **記憶體資訊**\n"
            status_text += f"   • 總容量: {memory_info.get('total_gb', 'N/A')} GB\n"
            status_text += f"   • 已使用: {memory_info.get('used_gb', 'N/A')} GB ({memory_info.get('usage_percent', 'N/A')}%)\n"
            status_text += f"   • 可用: {memory_info.get('available_gb', 'N/A')} GB\n"
            status_text += f"   • 虛擬記憶體: {memory_info.get('swap_used_gb', 'N/A')} / {memory_info.get('swap_total_gb', 'N/A')} GB\n"
            status_text += "\n"
        
        # GPU 資訊
        gpu_info = self.system_info.get('gpu', {})
        status_text += "🎮 **GPU 資訊**\n"
        
        if 'nvidia_gpus' in gpu_info:
            for i, gpu in enumerate(gpu_info['nvidia_gpus']):
                status_text += f"   • NVIDIA GPU {i}: {gpu['name']}\n"
                status_text += f"     - 記憶體: {gpu['memory_used_mb']} / {gpu['memory_total_mb']} MB\n"
                if gpu['temperature'] != 'N/A':
                    status_text += f"     - 溫度: {gpu['temperature']}°C\n"
                if gpu['gpu_utilization'] != 'N/A':
                    status_text += f"     - GPU 使用率: {gpu['gpu_utilization']}%\n"
        
        if 'windows_gpus' in gpu_info:
            for i, gpu in enumerate(gpu_info['windows_gpus']):
                status_text += f"   • GPU {i}: {gpu['name']}\n"
                if gpu['memory_bytes'] != 'Unknown':
                    try:
                        memory_gb = int(gpu['memory_bytes']) / (1024**3)
                        status_text += f"     - 記憶體: {memory_gb:.1f} GB\n"
                    except:
                        pass
        
        if 'status' in gpu_info:
            status_text += f"   • {gpu_info['status']}\n"
        
        status_text += "\n"
        
        # 磁碟資訊
        disk_info = self.system_info.get('disk', {})
        if 'error' not in disk_info:
            status_text += "💽 **磁碟資訊**\n"
            
            for device, info in disk_info.items():
                if device != 'io_stats' and isinstance(info, dict):
                    status_text += f"   • {device} ({info.get('filesystem', 'N/A')})\n"
                    status_text += f"     - 容量: {info.get('used_gb', 'N/A')} / {info.get('total_gb', 'N/A')} GB ({info.get('usage_percent', 'N/A')}%)\n"
                    status_text += f"     - 可用: {info.get('free_gb', 'N/A')} GB\n"
            
            io_stats = disk_info.get('io_stats')
            if io_stats != 'N/A' and io_stats:
                status_text += f"   • I/O 統計: 讀取 {io_stats.get('read_bytes', 'N/A')} GB, 寫入 {io_stats.get('write_bytes', 'N/A')} GB\n"
            
            status_text += "\n"
        
        # 進程資訊
        process_info = self.system_info.get('processes', {})
        if 'error' not in process_info:
            status_text += "⚙️ **進程資訊**\n"
            status_text += f"   • 目前進程 PID: {process_info.get('current_pid', 'N/A')}\n"
            status_text += f"   • 進程名稱: {process_info.get('current_name', 'N/A')}\n"
            status_text += f"   • CPU 使用率: {process_info.get('current_cpu_percent', 'N/A')}%\n"
            status_text += f"   • 記憶體使用: {process_info.get('current_memory_mb', 'N/A')} MB\n"
            status_text += f"   • 執行緒數: {process_info.get('current_threads', 'N/A')}\n"
            status_text += f"   • 系統總進程數: {process_info.get('total_processes', 'N/A')}\n"
            status_text += "\n"
        
        # Python 環境資訊
        python_info = self.system_info.get('python', {})
        if 'error' not in python_info:
            status_text += "🐍 **Python 環境**\n"
            version_line = python_info.get('version', '').split('\n')[0]
            status_text += f"   • 版本: {version_line}\n"
            status_text += f"   • 執行路徑: {python_info.get('executable', 'N/A')}\n"
            status_text += f"   • 已載入模組: {python_info.get('modules_count', 'N/A')} 個\n"
            status_text += f"   • 工作目錄: {python_info.get('current_working_directory', 'N/A')}\n"
            status_text += "\n"
        
        return status_text

# 全域實例
system_monitor = SystemStatusMonitor()

def get_enhanced_system_status():
    """獲取增強的系統狀態"""
    try:
        system_monitor.update_system_info()
        return system_monitor.get_formatted_status()
    except Exception as e:
        return f"❌ 獲取系統狀態失敗: {str(e)}"

def get_system_summary():
    """獲取系統摘要資訊"""
    try:
        system_monitor.update_system_info()
        cpu = system_monitor.system_info.get('cpu', {})
        memory = system_monitor.system_info.get('memory', {})
        
        summary = f"💻 CPU: {cpu.get('usage_percent', 'N/A')}% | "
        summary += f"💾 記憶體: {memory.get('usage_percent', 'N/A')}% "
        summary += f"({memory.get('used_gb', 'N/A')}/{memory.get('total_gb', 'N/A')} GB)"
        
        return summary
    except Exception as e:
        return f"❌ 系統摘要錯誤: {str(e)}"

if __name__ == "__main__":
    # 測試系統監控
    try:
        print("🖥️ 系統狀態監控測試")
        print("=" * 50)
        print(get_enhanced_system_status())
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
