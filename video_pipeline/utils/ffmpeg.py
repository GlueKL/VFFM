"""
Utilities for working with FFmpeg
"""
import subprocess
import logging
import sys
import platform

logger = logging.getLogger(__name__)

def check_ffmpeg_installed():
    """
    Checks if FFmpeg is available in the system.
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode == 0:
            version_info = result.stdout.decode('utf-8', errors='ignore').split('\n')[0]
            logger.info(f"FFmpeg found: {version_info}")
            return True
        else:
            logger.error("FFmpeg not found or error checking version.")
            return False
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("FFmpeg is not installed or not available in PATH.")
        _show_installation_guide()
        return False

def _show_installation_guide():
    """
    Shows installation instructions for FFmpeg based on the current operating system.
    """
    os_name = platform.system().lower()
    
    logger.warning("FFmpeg installation instructions:")
    
    if os_name == "windows":
        logger.warning("  - Download FFmpeg from the official website: https://ffmpeg.org/download.html")
        logger.warning("  - Or use Chocolatey package manager: choco install ffmpeg")
        logger.warning("  - Add FFmpeg path to PATH environment variable")
    elif os_name == "darwin":  # MacOS
        logger.warning("  - Install using Homebrew: brew install ffmpeg")
    elif os_name == "linux":
        logger.warning("  - Ubuntu/Debian: sudo apt-get install ffmpeg")
        logger.warning("  - CentOS/RHEL: sudo yum install ffmpeg")
        logger.warning("  - Arch Linux: sudo pacman -S ffmpeg")
    else:
        logger.warning("  - Visit https://ffmpeg.org/download.html for instructions for your OS") 