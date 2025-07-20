#!/usr/bin/env python3
"""
Setup Daily Price Update Cron Job
Configures the system to run price updates daily at 1 AM
"""

import os
import sys
import subprocess
from pathlib import Path

def get_script_paths():
    """Get the full paths to the price update scripts"""
    script_dir = Path(__file__).parent.absolute()
    python_path = sys.executable
    price_updater_path = script_dir / "daily_price_updater.py"
    
    return python_path, price_updater_path

def create_cron_entry():
    """Create the cron entry for daily price updates"""
    python_path, script_path = get_script_paths()
    
    # Cron entry: Run daily at 1:00 AM
    cron_entry = f"0 1 * * * {python_path} {script_path} >> {script_path.parent}/price_update.log 2>&1"
    
    return cron_entry

def add_to_crontab():
    """Add the price update job to the user's crontab"""
    try:
        cron_entry = create_cron_entry()
        
        print("🕐 Setting up Daily Price Update Cron Job")
        print("=" * 50)
        print(f"Schedule: Daily at 1:00 AM")
        print(f"Command: {cron_entry}")
        print()
        
        # Get current crontab
        try:
            current_cron = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            current_cron = ""
        
        # Check if our job already exists
        if "daily_price_updater.py" in current_cron:
            print("⚠️ Price update cron job already exists!")
            print("Current crontab entries with price updater:")
            for line in current_cron.split('\n'):
                if "daily_price_updater.py" in line:
                    print(f"   {line}")
            
            response = input("\nReplace existing entry? (y/N): ").strip().lower()
            if response != 'y':
                print("Setup cancelled.")
                return False
            
            # Remove existing entries
            lines = current_cron.split('\n')
            filtered_lines = [line for line in lines if "daily_price_updater.py" not in line and line.strip()]
            current_cron = '\n'.join(filtered_lines)
        
        # Add our new entry
        new_cron = current_cron.rstrip() + '\n' + cron_entry + '\n'
        
        # Write to crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
        process.communicate(new_cron.encode())
        
        if process.returncode == 0:
            print("✅ Cron job added successfully!")
            print()
            print("📅 Schedule Summary:")
            print("   • Daily execution at 1:00 AM")
            print("   • Logs saved to price_update.log")
            print("   • Updates all items not checked in 24+ hours")
            print("   • Handles out-of-stock detection")
            print("   • Rate limited to avoid blocking")
            print()
            print("🔧 To manage the cron job:")
            print("   • View: crontab -l")
            print("   • Edit: crontab -e")
            print("   • Remove: crontab -r")
            
            return True
        else:
            print("❌ Failed to add cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up cron job: {e}")
        return False

def verify_dependencies():
    """Verify that required dependencies are available"""
    print("🔍 Verifying dependencies...")
    
    # Check Python modules
    required_modules = ['supabase', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module}")
    
    if missing_modules:
        print()
        print("⚠️ Missing required modules. Install with:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    # Check if price updater script exists
    _, script_path = get_script_paths()
    if not script_path.exists():
        print(f"❌ Price updater script not found: {script_path}")
        return False
    else:
        print(f"   ✅ daily_price_updater.py")
    
    return True

def show_manual_setup():
    """Show manual cron setup instructions"""
    cron_entry = create_cron_entry()
    
    print()
    print("📋 MANUAL SETUP INSTRUCTIONS")
    print("=" * 40)
    print("If automatic setup failed, add this manually:")
    print()
    print("1. Open crontab editor:")
    print("   crontab -e")
    print()
    print("2. Add this line:")
    print(f"   {cron_entry}")
    print()
    print("3. Save and exit")
    print()

def main():
    """Main setup function"""
    print("🚀 DAILY PRICE UPDATE CRON SETUP")
    print("=" * 50)
    
    # Verify dependencies first
    if not verify_dependencies():
        print()
        print("❌ Setup cannot continue due to missing dependencies")
        return
    
    print()
    print("This will set up automatic daily price updates at 1:00 AM")
    print()
    
    # Ask for confirmation
    response = input("Proceed with cron setup? (y/N): ").strip().lower()
    if response != 'y':
        print("Setup cancelled.")
        show_manual_setup()
        return
    
    # Set up cron job
    success = add_to_crontab()
    
    if not success:
        show_manual_setup()
    else:
        print()
        print("🎉 Setup complete! Price updates will run daily at 1:00 AM")
        print()
        print("💡 Next steps:")
        print("   • Test with: python test_price_updater.py")
        print("   • Monitor logs: tail -f price_update.log")
        print("   • Check reports: ls price_update_report_*.json")

if __name__ == "__main__":
    main() 