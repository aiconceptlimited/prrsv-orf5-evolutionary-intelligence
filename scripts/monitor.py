#!/usr/bin/env python3
"""
System Monitor - Check if everything is running properly
"""
import os
import sys
import time
import subprocess
import smtplib
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

DB_URI = "${DATABASE_URL}"

def check_pipeline_health():
    """Check if pipeline has run recently"""
    try:
        engine = create_engine(DB_URI)
        df = pd.read_sql("SELECT MAX(created_at) as latest FROM eii_index", engine)
        latest = df['latest'].iloc[0]
        
        if latest:
            minutes_ago = (datetime.now() - latest).total_seconds() / 60
            if minutes_ago > 150:  # More than 2.5 hours
                return False, f"Pipeline hasn't run for {int(minutes_ago)} minutes"
        return True, "Pipeline healthy"
    except Exception as e:
        return False, f"Database error: {e}"

def check_dashboard_health():
    """Check if dashboard is responding"""
    try:
        import requests
        response = requests.get("http://localhost:8056", timeout=5)
        if response.status_code == 200:
            return True, "Dashboard responding"
        return False, f"Dashboard status: {response.status_code}"
    except Exception as e:
        return False, f"Dashboard error: {e}"

def send_alert(message):
    """Send alert (for future email notifications)"""
    print(f"🔴 ALERT: {message}")
    # Future: email, slack, telegram notifications

def main():
    print(f"\n🔍 System Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*50)
    
    issues = []
    
    # Check pipeline
    pipeline_ok, pipeline_msg = check_pipeline_health()
    if pipeline_ok:
        print(f"✅ Pipeline: {pipeline_msg}")
    else:
        print(f"❌ Pipeline: {pipeline_msg}")
        issues.append(pipeline_msg)
    
    # Check dashboard
    dashboard_ok, dashboard_msg = check_dashboard_health()
    if dashboard_ok:
        print(f"✅ Dashboard: {dashboard_msg}")
    else:
        print(f"❌ Dashboard: {dashboard_msg}")
        issues.append(dashboard_msg)
    
    # Summary
    if issues:
        print("\n" + "="*50)
        print("⚠️  Issues Found:")
        for issue in issues:
            print(f"  • {issue}")
        print("="*50)
    else:
        print("\n✅ All systems healthy!")
    
    return len(issues) == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
