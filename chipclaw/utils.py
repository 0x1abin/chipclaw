"""
ChipClaw Utility Functions
"""
import os
import time


def ensure_dir(path):
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path)
    except OSError:
        pass


def today_date():
    """Return YYYY-MM-DD string"""
    t = time.localtime()
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"


def timestamp():
    """Return Unix timestamp"""
    return time.time()


def safe_filename(name):
    """Sanitize filename (replace : / \\ with _)"""
    return name.replace(":", "_").replace("/", "_").replace("\\", "_")


def truncate_string(s, max_len=1000):
    """Truncate string with ellipsis"""
    if len(s) > max_len:
        return s[:max_len] + "...(truncated)"
    return s


def get_runtime_info():
    """Get ESP32-S3 runtime information"""
    info = {}
    
    try:
        import gc
        info['mem_free'] = gc.mem_free()
        info['mem_alloc'] = gc.mem_alloc()
    except:
        pass
    
    try:
        # Flash filesystem stats
        stats = os.statvfs('/')
        block_size = stats[0]
        total_blocks = stats[2]
        free_blocks = stats[3]
        info['flash_total'] = (total_blocks * block_size) // 1024  # KB
        info['flash_free'] = (free_blocks * block_size) // 1024   # KB
    except:
        pass
    
    try:
        import sys
        info['platform'] = sys.platform
        info['version'] = sys.version
    except:
        pass
    
    return info


def format_runtime_info():
    """Format runtime info as human-readable string"""
    info = get_runtime_info()
    lines = []
    
    if 'platform' in info:
        lines.append(f"Platform: {info['platform']}")
    if 'version' in info:
        lines.append(f"Version: {info['version']}")
    if 'mem_free' in info:
        lines.append(f"RAM Free: {info['mem_free'] // 1024} KB")
    if 'mem_alloc' in info:
        lines.append(f"RAM Allocated: {info['mem_alloc'] // 1024} KB")
    if 'flash_free' in info:
        lines.append(f"Flash Free: {info['flash_free']} KB / {info.get('flash_total', 0)} KB")
    
    return "\n".join(lines) if lines else "Runtime info unavailable"
