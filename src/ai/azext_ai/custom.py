# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
import openai
import os
import sys
import subprocess

openai.api_type = os.getenv("OPENAI_API_TYPE") or "azure"
openai.api_base = os.getenv("OPENAI_API_BASE") or "https://api.openai.com"
openai.api_version = os.getenv("OPENAI_API_VERSION") or "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_DEPLOYMENT = os.getenv("OPENAI_API_DEPLOYMENT")
TEMPERATURE = 0.2
MAX_TOKENS = 800

PROGRAMMER = "you are an expert programmer that can help develop programs and solve problems"
AZ_CLI_EXPERT = "You are a microsoft azure cloud expert trying to with how to use azure `az` CLI. "  # Do not provide any explanations, only generate az commands.
K8S_EXPERT = "You are a Kubernetes YAML generator, only generate valid Kubernetes YAML manifests. Do not provide any explanations, only generate YAML."

if os.name == 'nt':
    SCRIPT_TYPE = "Windows PowerShell"
else:
    SCRIPT_TYPE = "Bash Script"

AKS_EXPERT = \
    f'''You are a microsoft Azure Kubernetes Service expert that helps user on 
    writing a {SCRIPT_TYPE} to automate AKS that leverage the `az` command.
    When constructing `az` commands to execute, 
    always fill in a default input value for the command by 
    helping the user to make up names, and come up with sensible default like a specific number or region name.
    Write the {SCRIPT_TYPE} and add explanations as comments within script.
    '''
SYSTEM_PROMPT = {"role": "system", "content": AKS_EXPERT}

# Define a platform-specific function to get a single character
if os.name == 'nt':
    # Windows system
    import msvcrt


    def getch():
        return msvcrt.getch().decode('utf-8')

else:
    # Unix-based system
    import termios
    import tty


    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def run_command_as_shell(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return process.returncode, stderr.decode()
    else:
        return process.returncode, stdout.decode()


def run_bash_script(shell_script: str):
    # Run the shell script using 'bash -c' and capture the output
    result = subprocess.run(["bash", "-c", shell_script], capture_output=True, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    return result.returncode, output


def run_powershell_script(powershell_script: str):
    # Run the PowerShell script using 'powershell -Command' and capture the output
    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    return result.returncode, output


def extract_backticks_commands(text):
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    strip_pattern = r'^(powershell\s*|bash\s*|shell\s*)'
    return [re.sub(strip_pattern, '', match.strip()) for match in matches]


def process_result(text):
    matches = extract_backticks_commands(text)
    return matches


def get_prop(multilayers_dict, key, default=None):
    keys = key.split('.')
    val = multilayers_dict
    try:
        for k in keys:
            if k.isdigit():
                k = int(k)
            val = val[k]
    except Exception:
        return default
    return val


from colorama import Fore, Style

STATE_IN_CHAT = 1
STATE_IN_CODE = 0


# Fore.RED
# Fore.GREEN
# Fore.YELLOW
# Fore.BLUE
# Fore.MAGENTA
# Fore.CYAN
# Fore.WHITE
def switch_color_context(state):
    if state == STATE_IN_CHAT:
        print(Fore.CYAN)
    else:
        print(Fore.BLUE)


def process_message_prefix(content, previous_context=None):
    if not previous_context:
        return content, False
    elif len(previous_context) == 1 and len(content) > 1 and content[0:2] == '``':
        print('```', end='')
        return content[2:], True
    elif len(previous_context) == 2 and len(content) >= 1 and content[0] == '`':
        print('```', end='')
        return content[1:], True
    else:
        print(previous_context)
        return content, False


def process_message_suffix(content):
    if content == '`' or content == '``':
        return content
    if re.match(r"""[^`]+`$""", content):
        print(content[0:-1], end='')
        return '`'
    if re.match(r"""[^`]+``$""", content):
        print(content[0:-2], end='')
        return '``'
    return ''


def chatgpt(messages):
    response = openai.ChatCompletion.create(
        engine=OPENAI_API_DEPLOYMENT,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=True)
    # if not using stream=True, then response is a dict
    # response['choices'][0]['finish_reason']=='stop'
    # response['choices'][0]['message']['role'] #'assistant'
    # msg = response['choices'][0]['message']['content']

    state = STATE_IN_CHAT
    switch_color_context(state)
    collected_messages = []
    previous_context = ''
    for chuck_idx, chunk in enumerate(response):
        content = get_prop(chunk, 'choices.0.delta.content', '')  # extract the message

        if content:
            collected_messages.append(content)  # save the message

            if previous_context:
                content = previous_context + content
                previous_context = ''
            if content == '``' or content == '`':
                previous_context = content
                continue
            if re.search(r"""[^`]+``$""", content):
                previous_context = '``'
                content = content[0:-2]
            elif re.search(r"""[^`]+`$""", content):
                previous_context = '`'
                content = content[0:-1]

            parts = content.split('```')
            if len(parts) > 1:
                for i, part in enumerate(parts):
                    if i > 0:
                        if state == STATE_IN_CHAT:
                            state = state ^ 1
                            switch_color_context(state)
                            print('```', end='')
                        else:
                            print('```', end='')
                            state = state ^ 1
                            switch_color_context(state)
                    print(part, end='')
            else:
                print(content, end="")
    if previous_context:
        print(previous_context, end='')
    print("\n", flush=True)
    print(Style.RESET_ALL)

    msg = ''.join(collected_messages)
    # if not using stream=True, then role is in response['choices'][0]['message']['role']
    messages.append({"role": 'assistant',
                     "content": msg})
    scripts = process_result(msg)
    return msg, scripts, messages


def prompt_user_to_run_script(scripts):
    n_scripts = len(scripts)
    switch_color_context(STATE_IN_CODE)
    if n_scripts > 1:
        for i, script in enumerate(scripts):
            print(f"Hit `{i}` key to run:")
            print(script)
    elif n_scripts == 1:
        print(scripts[0])
    else:
        return
    print(Style.RESET_ALL)
    print(f"Hit `c` to cancel", end="")
    if n_scripts == 1:
        print(", `r` to run the script", end="")
    print(": ", end="", flush=True)
    while True:
        user_input = getch()
        if user_input == 'c' or user_input == 'C':
            return
        if user_input == 'r' or user_input == 'R':
            user_input = '0'
        ord_0 = ord('0')
        ord_code = ord(user_input)
        if ord_0 <= ord_code < ord_0 + n_scripts:
            i = ord_code - ord_0
            # scripts = scripts.replace('<', '').replace('>', '').replace('`', '').replace('|', '').replace('&', '')
            script = scripts[i]
            # test script, remove below for production
            # script = """
            # echo "Hello, World!"
            # ls -ltr
            # """
            returncode, output = run_bash_script(script)
            print(output)
            return


USER_INPUT_PROMPT = "Prompt: "


def prompt_chat_gpt(messages, insist=True, scripts=''):
    while True:
        text_input = str(input(USER_INPUT_PROMPT)).strip()
        if re.search(r'[a-zA-Z]', text_input):
            messages.append({"role": "user", "content": text_input})
            _, scripts, messages = chatgpt(messages)
            return scripts, messages
        if not insist:
            return scripts, messages


def start_chat(**kwargs):
    print("Please enter your request below.")
    print("For example: How to create a AKS cluster")

    scripts, messages = prompt_chat_gpt([SYSTEM_PROMPT])
    while True:
        print("\nMenu: [p: re-Prompt, ", end="")
        if len(scripts) > 0:
            print("r: Run, ", end="")
        print("q: Quit]", flush=True)

        # Handle user input
        user_input = getch()
        if user_input == 'p' or user_input == 'P':
            scripts, messages = prompt_chat_gpt(messages, insist=False, scripts=scripts)
        elif (user_input == 'r' or user_input == 'R') and len(scripts) > 0:
            prompt_user_to_run_script(scripts)
        elif user_input == 'q' or user_input == 'Q':
            # Exiting the program...
            break
