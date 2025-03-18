import os
import subprocess
import curses
import textwrap

# Define Atomic Red Team tests in JSON format
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

def clear_screen():
    """Clears the console screen"""
    os.system("cls" if os.name == "nt" else "clear")

def display_menu(stdscr):
    """Displays the interactive menu"""
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Titles / Success messages
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Descriptions / Warnings
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Commands / Execution text
    selected_index = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "FortiEDR Demo - MITRE ATT&CK", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 2, "Use UP/DOWN to navigate, ENTER to select, Q to quit.", curses.color_pair(3))

        for idx, test in enumerate(tests):
            if idx == selected_index:
                stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
                stdscr.addstr(4 + idx, 2, f"{test['id']}\t{test['title']}")
                stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.addstr(4 + idx, 2, f"{test['id']}\t{test['title']}", curses.color_pair(2))

        stdscr.addstr(6 + len(tests), 2, "[Q] Quit", curses.color_pair(3))

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(tests)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(tests)
        elif key == 10:  # ENTER
            display_test_details(stdscr, tests[selected_index])
        elif key in (ord('q'), ord('Q')):
            break

def display_test_details(stdscr, test):
    """Displays details of the selected test using curses"""
    stdscr.clear()
    stdscr.addstr(1, 2, f"{test['id']}\t{test['title']}", curses.color_pair(3))  # Green for title
    stdscr.addstr(3, 2, test['test'], curses.color_pair(1))  # White for test name
    stdscr.addstr(5, 2, "Triggered Rules:", curses.color_pair(3))  # Green for rules
    for rule in test["rules"]:
        stdscr.addstr(6 + test["rules"].index(rule), 4, rule)  # Indented for readability
    stdscr.addstr(8 + len(test["rules"]), 2, "Command:", curses.color_pair(3))  # Green for command
    stdscr.addstr(9 + len(test["rules"]), 4, test['command'])
    stdscr.addstr(11 + len(test["rules"]), 2, "Press ENTER to execute or BACKSPACE to return.", curses.color_pair(3))  # Green for instructions

    while True:
        key = stdscr.getch()
        if key == 10:  # ENTER
            curses.endwin()  # Exit curses mode
            run_test(test["command"])  # Run test
            curses.wrapper(display_menu)  # Restart curses after returning
            break
        elif key in (curses.KEY_BACKSPACE, 127):  # Handle BACKSPACE properly
            display_menu(stdscr)
            break

def run_test(command):
    """Executes the selected Atomic Red Team test and returns to menu automatically"""
    clear_screen()
    os.system(f'powershell -ExecutionPolicy Bypass -NoProfile -Command "{command}"')

def main():
    """Runs the interactive menu inside curses wrapper"""
    curses.wrapper(display_menu)

if __name__ == "__main__":
    main()
