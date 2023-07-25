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
TEMPERATURE = 0.1
MAX_TOKENS = 800

IS_MS_WINDOWS = os.name == 'nt'

if IS_MS_WINDOWS:
    SCRIPT_TYPE = "Windows PowerShell"
else:
    SCRIPT_TYPE = "Bash Script"

AKS_EXPERT = f'''
You are a microsoft Azure Kubernetes Service expert.

Context: The user will provide you a description of what they want to accomplish

Your task is to help user writing a {SCRIPT_TYPE} to automate AKS that leverage the `az` command

When constructing `az` commands to execute, always fill in a default input value for the command by 
helping the user to make up names, and come up with sensible default like a specific number or region name.

If there are required input value that you need user to provide, prompt the user for the value, 
if possible, provide hints or commands for the user to execute for them to get the required value.

each script block you output enclosed by ``` should be self sufficient to run
if you create variable in a previous script block, repeat it again if it is needed in another script block.

Be aware that as a AI model, your data might be out of date, if user supplied input that you are unaware of, just accept and use it.

Write the {SCRIPT_TYPE} and add explanations as comments within script.
'''.strip()
SYSTEM_PROMPT = {"role": "system", "content": AKS_EXPERT}

# Define a platform-specific function to get a single character
if IS_MS_WINDOWS:
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


def run_system_script(script_content: str):
    # do not set capture_output=True, so user can interact with yes/no answer from script
    if IS_MS_WINDOWS:
        cmd = ["powershell", "-Command", script_content]
    else:
        cmd = ["bash", "-c", script_content]
    result = subprocess.run(cmd, text=True)
    return result.returncode


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
        print(Fore.GREEN)


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
    if n_scripts > 1:
        for i, script in enumerate(scripts):
            print(Style.RESET_ALL)
            print(f"Hit `{i}` key to run the script as below:")
            switch_color_context(STATE_IN_CODE)
            print(script)
    elif n_scripts == 1:
        switch_color_context(STATE_IN_CODE)
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
            script = scripts[i]
            return run_system_script(script)


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
    print("For example: Please create a AKS cluster")

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
