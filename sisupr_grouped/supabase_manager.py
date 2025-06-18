import supabase
from datetime import datetime, timedelta

SUPABASE_URL = "https://nnixjfqeygpvpeylkbux.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uaXhqZnFleWdwdnBleWxrYnV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxNDAyNzgsImV4cCI6MjA2NTcxNjI3OH0.Es78nkIZlRv9lRB92T8CPygqLiuM6I327iUWr53Q85U"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def format_datetime(dt_str):
    if not dt_str:
        return ""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        return dt_str