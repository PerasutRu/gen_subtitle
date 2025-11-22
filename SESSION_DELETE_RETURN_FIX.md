# Session Delete 500 Error Fix

## Problem
When trying to delete a session via the admin dashboard, the API returned a 500 error:
```
❌ Error in admin_delete_session: Traceback...
HTTPException: ไม่สามารถลบ session ได้
```

## Root Cause
The `clear_session` method in `session_manager.py` was not returning the result from `db.delete_session()`:

```python
def clear_session(self, session_id: str):
    """ลบ session (สำหรับ testing หรือ reset)"""
    self.db.delete_session(session_id)  # ❌ No return statement
```

This caused the method to return `None`, which was evaluated as `False` in the endpoint's success check, triggering the error.

## Solution
Added return statement to `clear_session` method:

```python
def clear_session(self, session_id: str) -> bool:
    """ลบ session (สำหรับ testing หรือ reset)"""
    return self.db.delete_session(session_id)  # ✅ Returns True/False
```

Also improved the endpoint error handling to always return success if no exception is raised (since `db.delete_session` is idempotent and returns `True` even if the session doesn't exist).

## Files Changed
- `backend/services/session_manager.py` - Added return statement to `clear_session`
- `backend/main.py` - Improved error handling in `admin_delete_session` endpoint

## Testing
After the fix, deleting a session should work correctly and return:
```json
{
  "success": true,
  "message": "ลบ session user_test3 สำเร็จ",
  "session_id": "user_test3"
}
```
