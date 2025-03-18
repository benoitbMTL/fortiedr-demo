import os
import subprocess
import curses

# Define MITRE ATT&CK tests
tests = [
    {
        "id": "T1027.007",
        "title": "Obfuscated Files or Information: Dynamic API Resolution",
        "test": "Dynamic API Resolution - Ninja-syscall",
        "description": "This test calls NtCreateFile via API hashing and dynamic syscall resolution. I have dubbed this particular combination of techniques 'Ninja-syscall'. When successful, a new file named 'hello.log' will be created in the default user's temporary folder, which is a common location for a dropper.",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1027.007 -TestNumbers 1"
    },
    {
        "id": "T1036.003",
        "title": "Masquerading: Rename System Utilities",
        "test": "Masquerading - Windows EXE running as different Windows EXE",
        "description": "Copies a Windows EXE, renames it as another EXE, and runs it to masquerade as a system utility.",
        "rules": [
            "Exfiltration Prevention",
            "- Fake Critical Program - Attempted to Hide as a Service"
        ],
        "command": "Invoke-AtomicTest T1036.003 -TestNumbers 7"
    },
    {
        "id": "T1055",
        "title": "Process Injection",
        "test": "Dirty Vanity process Injection",
        "description": "This test uses the Windows undocumented remote-fork API RtlCreateProcessReflection to create a cloned process of the parent process with shellcode written in its memory. The shellcode is executed after being forked to the child process. The technique was first presented at BlackHat Europe 2022. Shellcode will open a message box and a notepad.",
        "rules": [
            "Exfiltration Prevention",
            "- Injected Process - Process Created from an Injected Thread",
            "- Injected Thread - Connection from an Injected Thread",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program",
            "- Process Injection - Entry Point Modification Detected",
            "Ransomware Prevention",
            "- Injected Process - Process Created from an Injected Thread",
            "- Injected Thread - Connection from an Injected Thread",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program",
            "- Process Injection - Entry Point Modification Detected"
        ],
        "command": "Invoke-AtomicTest T1055 -TestNumbers 4"
    },
    {
        "id": "T1059.001",
        "title": "Command and Scripting Interpreter: PowerShell",
        "test": "Download Mimikatz and dump credentials",
        "description": "Download Mimikatz and dump credentials. Upon execution, Mimikatz dump details and password hashes will be displayed.",
        "rules": [
            "Exfiltration Prevention",
            "- Suspicious Application - Connection Attempt from a Suspicious Application",
            "- Unmapped Executable - Executable File Without a Corresponding File System Reference"
        ],
        "command": "Invoke-AtomicTest T1059.001 -TestNumbers 1"
    },
    {
        "id": "T1105",
        "title": "Ingress Tool Transfer",
        "test": "Download a file using wscript",
        "description": "Use wscript to run a local VisualBasic file to download a remote file.",
        "rules": [
            "Exfiltration Prevention",
            "- Suspicious Application - Connection Attempt from a Suspicious Application"
        ],
        "command": "Invoke-AtomicTest T1105 -TestNumbers 26"
    },
    {
        "id": "T1106",
        "title": "Native API",
        "test": "Run Shellcode via Syscall in Go",
        "description": "Runs shellcode in the current running process via a syscall. Steps taken with this technique:\n- Allocate memory for the shellcode with VirtualAlloc setting the page permissions to Read/Write\n- Use the RtlCopyMemory macro to copy the shellcode to the allocated memory space\n- Change the memory page permissions to Execute/Read with VirtualProtect\n- Use syscall to execute the entrypoint of the shellcode",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1106 -TestNumbers 5"
    },
    {
        "id": "T1134.001",
        "title": "Access Token Manipulation: Token Impersonation/Theft",
        "test": "utilizes Juicy Potato to obtain privilege escalation",
        "description": "This Atomic utilizes Juicy Potato to obtain privilege escalation. Upon successful execution of this test, a vulnerable CLSID will be used to execute a process with system permissions. This tactic has been previously observed in SnapMC Ransomware, amongst numerous other campaigns.",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program"
        ],
        "command": "Invoke-AtomicTest T1134.001 -TestNumbers 5"
    },
    {
        "id": "T1555.003",
        "title": "Credentials from Password Stores: Credentials from Web Browsers",
        "test": "WebBrowserPassView - Credentials from Browser",
        "description": "The following Atomic test utilizes WebBrowserPassView to extract passwords from browsers on a Windows system. WebBrowserPassView is an open-source application used to retrieve passwords stored on a local computer. Recently noticed as a tool used in the BlackCat Ransomware.",
        "rules": [
            "Exfiltration Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1555.003 -TestNumbers 15"
    },
    {
        "id": "T1562.002",
        "title": "Impair Defenses: Disable Windows Event Logging",
        "test": "Makes Eventlog blind with Phant0m",
        "description": "Use Phant0m to disable Eventlog.",
        "rules": [
            "Exfiltration Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1562.002 -TestNumbers 7"
    }
]

def display_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal text
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Highlighted selection
    
    selected_index = 0
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "MITRE ATT&CK Test Menu", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 2, "Use UP/DOWN to navigate, ENTER to select, BACKSPACE to exit.", curses.color_pair(1))
        
        for idx, test in enumerate(TESTS):
            if idx == selected_index:
                stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
            stdscr.addstr(4 + idx, 2, f"{test['id']}\t{test['title']}")
            if idx == selected_index:
                stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(TESTS)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(TESTS)
        elif key == 10:  # ENTER
            display_test_details(stdscr, TESTS[selected_index])
        elif key == 8 or key == 127:  # BACKSPACE
            break

def display_test_details(stdscr, test):
    stdscr.clear()
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White text
    
    stdscr.addstr(2, 2, f"{test['id']}\t{test['title']}", curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(4, 2, test['test'], curses.color_pair(4))
    stdscr.addstr(6, 2, "Press ENTER to execute or BACKSPACE to return.", curses.color_pair(1))
    
    while True:
        key = stdscr.getch()
        if key == 10:  # ENTER
            run_test(stdscr, test['command'])
            break
        elif key == 8 or key == 127:  # BACKSPACE
            return

def run_test(stdscr, command):
    stdscr.clear()
    stdscr.addstr(2, 2, "Executing test...", curses.color_pair(1))
    stdscr.refresh()
    os.system(f'powershell -ExecutionPolicy Bypass -NoProfile -Command "{command}"')
    display_menu(stdscr)  # Return to menu after execution

def main():
    curses.wrapper(display_menu)

if __name__ == "__main__":
    main()
