# -*- coding: utf-8 -*-
"""
System Status Monitor - Simplified Version
"""

import psutil
import platform
import os
import sys
import datetime
import subprocess

def get_basic_system_info():
    """Get basic system information"""
    try:
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_total_gb = round(memory.total / (1024**3), 2)
        memory_used_gb = round(memory.used / (1024**3), 2)
        memory_percent = memory.percent
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total_gb = round(disk.total / (1024**3), 2)
        disk_used_gb = round(disk.used / (1024**3), 2)
        disk_percent = round((disk.used / disk.total) * 100, 2)
        
        # System info
        system = platform.system()
        version = platform.version()
        processor = platform.processor()
        
        # Format output
        status = f"""System Status Report
========================

Platform Info:
- OS: {system}
- Version: {version}
- Processor: {processor}

CPU Info:
- Cores: {cpu_count}
- Usage: {cpu_percent}%

Memory Info:
- Total: {memory_total_gb} GB
- Used: {memory_used_gb} GB ({memory_percent}%)
- Available: {round(memory.available / (1024**3), 2)} GB

Disk Info:
- Total: {disk_total_gb} GB
- Used: {disk_used_gb} GB ({disk_percent}%)
- Free: {round(disk.free / (1024**3), 2)} GB

Python Info:
- Version: {sys.version.split()[0]}
- Executable: {sys.executable}
"""
        
        return status
        
    except Exception as e:
        return f"Error getting system info: {str(e)}"

def get_gpu_info_windows():
    """Get GPU info on Windows"""
    try:
        result = subprocess.run([
            'wmic', 'path', 'win32_VideoController', 'get', 
            'name,AdapterRAM', '/format:csv'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            gpu_info = "GPU Info:\n"
            
            for i, line in enumerate(lines):
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 3:
                        name = parts[2] if len(parts) > 2 else 'Unknown'
                        memory = parts[1] if len(parts) > 1 else 'Unknown'
                        
                        gpu_info += f"- GPU {i}: {name}\n"
                        if memory != 'Unknown' and memory:
                            try:
                                memory_gb = int(memory) / (1024**3)
                                gpu_info += f"  Memory: {memory_gb:.1f} GB\n"
                            except:
                                pass
            
            return gpu_info
    except:
        pass
    
    return "GPU Info: Unable to detect GPU information\n"

def get_enhanced_system_status():
    """Get enhanced system status"""
    try:
        basic_info = get_basic_system_info()
        
        if platform.system() == 'Windows':
            gpu_info = get_gpu_info_windows()
            return basic_info + "\n" + gpu_info
        else:
            return basic_info + "\nGPU Info: GPU detection not supported on this platform\n"
            
    except Exception as e:
        return f"System monitoring error: {str(e)}"

def get_system_summary():
    """Get system summary"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        summary = f"CPU: {cpu_percent}% | Memory: {memory.percent}% ({round(memory.used / (1024**3), 1)}/{round(memory.total / (1024**3), 1)} GB)"
        return summary
    except:
        return "System summary unavailable"

if __name__ == "__main__":
    print("System Monitor Test")
    print("=" * 30)
    print(get_enhanced_system_status())
