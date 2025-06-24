from typing import List, Optional
import subprocess

# Windows API imports
try:
    import win32api
    import win32security
    import win32con
    import win32net
    import win32netcon
    import win32process
    import win32ts
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False


def get_current_user_sid() -> Optional[str]:
    """Get the current user's SID using Windows API."""
    if not WINDOWS_API_AVAILABLE:
        return _get_current_user_sid_fallback()
    
    try:
        # Method 1: Get from current process token
        token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(), 
            win32con.TOKEN_QUERY
        )
        
        # Get user SID from token
        user_sid = win32security.GetTokenInformation(token, win32security.TokenUser)
        sid_string = win32security.ConvertSidToStringSid(user_sid['User'].Sid)
        
        return sid_string
        
    except Exception as e:
        print(f"Warning: Could not get current user SID via process token: {e}")
        try:
            # Method 2: Get from current session
            session_id = win32ts.WTSGetActiveConsoleSessionId()
            if session_id != 0xFFFFFFFF:
                session_info = win32ts.WTSQuerySessionInformation(
                    win32ts.WTS_CURRENT_SERVER_HANDLE, 
                    session_id, 
                    win32ts.WTSUserName
                )
                if session_info:
                    # Handle both bytes and string return types
                    if isinstance(session_info, bytes):
                        username = session_info.decode('utf-8')
                    else:
                        username = str(session_info)
                    # Get SID for this username
                    return _get_sid_for_username(username)
        except Exception as e2:
            print(f"Warning: Could not get current user SID via session: {e2}")
        
        return _get_current_user_sid_fallback()

def _get_sid_for_username(username: str) -> Optional[str]:
    """Get SID for a given username using Windows API."""
    try:
        # Get user info including SID
        user_info = win32net.NetUserGetInfo("", username, 4)
        if user_info and 'user_sid' in user_info:
            return win32security.ConvertSidToStringSid(user_info['user_sid'])
    except Exception:
        pass
    return None

def _get_current_user_sid_fallback() -> Optional[str]:
    """Fallback method using whoami if Windows API is not available."""
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
    """Fallback method using whoami if Windows API is not available."""
    sids = []
    try:
        # Use whoami to get current user SID as fallback
        current_sid = _get_current_user_sid_fallback()
        if current_sid:
            sids.append(current_sid)
    except Exception as e:
        print(f"Warning: Could not get user SIDs: {e}")
    return sids

def resolve_sid_to_username(sid: str) -> Optional[str]:
    """Resolve a SID to a username using Windows API."""
    if not WINDOWS_API_AVAILABLE:
        return _resolve_sid_to_username_fallback(sid)
    
    try:
        # Convert string SID to SID object
        sid_object = win32security.ConvertStringSidToSid(sid)
        
        # Get account name and domain
        name, domain, account_type = win32security.LookupAccountSid("", sid_object)
        
        # Return username (with domain if available)
        if domain and domain != ".":
            return f"{domain}\\{name}"
        else:
            return name
            
    except Exception as e:
        print(f"Warning: Could not resolve SID {sid} to username via API: {e}")
        # Try fallback method
        return _resolve_sid_to_username_fallback(sid)

def _resolve_sid_to_username_fallback(sid: str) -> Optional[str]:
    """Fallback method using whoami to resolve SID to username."""
    try:
        # For fallback, we can only get current user info
        # This is a limitation when pywin32 is not available
        result = subprocess.run(['whoami'], 
                              capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode == 0:
            current_user = result.stdout.strip()
            # We can't reliably map SID to username without API, so return SID
            return f"Unknown User ({sid})"
    except Exception as e:
        print(f"Warning: Could not resolve SID {sid} to username: {e}")
    return f"Unknown User ({sid})"

def get_sid_info(sid: str) -> dict:
    """Get comprehensive information about a SID including username and account type."""
    info = {
        'sid': sid,
        'username': None,
        'account_type': None,
        'description': None
    }
    
    if not WINDOWS_API_AVAILABLE:
        info['username'] = _resolve_sid_to_username_fallback(sid)
        return info
    
    try:
        # Convert string SID to SID object
        sid_object = win32security.ConvertStringSidToSid(sid)
        
        # Get account name, domain, and account type
        name, domain, account_type = win32security.LookupAccountSid("", sid_object)
        
        # Set username
        if domain and domain != ".":
            info['username'] = f"{domain}\\{name}"
        else:
            info['username'] = name
        
        # Set account type description
        account_types = {
            win32security.SidTypeUser: "User",
            win32security.SidTypeGroup: "Group", 
            win32security.SidTypeDomain: "Domain",
            win32security.SidTypeAlias: "Alias",
            win32security.SidTypeWellKnownGroup: "Well Known Group",
            win32security.SidTypeDeletedAccount: "Deleted Account",
            win32security.SidTypeInvalid: "Invalid",
            win32security.SidTypeUnknown: "Unknown",
            win32security.SidTypeComputer: "Computer"
        }
        info['account_type'] = account_types.get(account_type, "Unknown")
        
        # Add description for common SIDs
        common_sids = {
            'S-1-5-18': 'Local System',
            'S-1-5-19': 'NT Authority (Local Service)',
            'S-1-5-20': 'NT Authority (Network Service)',
            'S-1-5-32-544': 'Administrators',
            'S-1-5-32-545': 'Users',
            'S-1-5-32-546': 'Guests',
            'S-1-5-32-547': 'Power Users',
            'S-1-5-32-548': 'Account Operators',
            'S-1-5-32-549': 'Server Operators',
            'S-1-5-32-550': 'Print Operators',
            'S-1-5-32-551': 'Backup Operators',
            'S-1-5-32-552': 'Replicators'
        }
        info['description'] = common_sids.get(sid, None)
        
    except Exception as e:
        # Fallback to basic method
        info['username'] = _resolve_sid_to_username_fallback(sid)
        print(f"Warning: Could not get full SID info for {sid}: {e}")
    
    return info 