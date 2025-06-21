from typing import List, Optional
import subprocess

# Windows API imports
try:
    import win32api
    import win32security
    import win32con
    import win32net
    import win32netcon
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False


def get_current_user_sid() -> Optional[str]:
    """Get the current user's SID using Windows API."""
    if not WINDOWS_API_AVAILABLE:
        return _get_current_user_sid_fallback()
    
    try:
        # Get current user token
        token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(), 
            win32con.TOKEN_QUERY
        )
        
        # Get user SID from token
        user_sid = win32security.GetTokenInformation(token, win32security.TokenUser)
        sid_string = win32security.ConvertSidToStringSid(user_sid['User'].Sid)
        
        return sid_string
        
    except Exception as e:
        print(f"Warning: Could not get current user SID via API: {e}")
        return _get_current_user_sid_fallback()

def _get_current_user_sid_fallback() -> Optional[str]:
    """Fallback method using subprocess if Windows API is not available."""
    try:
        result = subprocess.run(['whoami', '/all'], 
                              capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'S-1-5-21-' in line and 'S-1-5-21-' in line.split():
                    # Extract SID from the line
                    parts = line.split()
                    for part in parts:
                        if part.startswith('S-1-5-21-'):
                            return part
    except Exception as e:
        print(f"Warning: Could not get current user SID: {e}")
    return None

def get_all_user_sids() -> List[str]:
    """Get all local user SIDs using Windows API."""
    if not WINDOWS_API_AVAILABLE:
        return _get_all_user_sids_fallback()
    
    sids = []
    try:
        # Get all local users
        users = win32net.NetUserEnum("", 0, win32netcon.FILTER_NORMAL_ACCOUNT, 0)[0]
        
        for user in users:
            try:
                # Get user info including SID
                user_info = win32net.NetUserGetInfo("", user['name'], 4)
                if user_info and 'user_sid' in user_info:
                    sid_string = win32security.ConvertSidToStringSid(user_info['user_sid'])
                    if sid_string.startswith('S-1-5-21-'):
                        sids.append(sid_string)
            except Exception:
                # Skip users that can't be queried
                continue
                
    except Exception as e:
        print(f"Warning: Could not get user SIDs via API: {e}")
        return _get_all_user_sids_fallback()
    
    return sids

def _get_all_user_sids_fallback() -> List[str]:
    """Fallback method using subprocess if Windows API is not available."""
    sids = []
    try:
        result = subprocess.run(['wmic', 'useraccount', 'get', 'name,sid'], 
                              capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and 'S-1-5-21-' in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('S-1-5-21-'):
                            sids.append(part)
                            break
    except Exception as e:
        print(f"Warning: Could not get user SIDs: {e}")
    return sids 