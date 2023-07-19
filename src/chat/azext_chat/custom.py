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

PROGRAMMER="you are an expert programmer that can help develop programs and solve problems"
AZ_CLI_EXPERT="You are a microsoft azure cloud expert trying to with how to use azure `az` CLI. " # Do not provide any explanations, only generate az commands.
K8S_EXPERT="You are a Kubernetes YAML generator, only generate valid Kubernetes YAML manifests. Do not provide any explanations, only generate YAML."
AKS_EXPERT=\
'''You are a microsoft Azure Kubernetes Service expert.
When answer questions with code or command line to be executed, 
always fill in a default input value for the command line by 
helping the user to make up names, and come up with other sensible default like a specific number or region.
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


def run_command(cmd):
    # cmd = "ls -al"
    # cmd = "dir /w "
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return process.returncode, stderr.decode()
    else:
        return process.returncode, stdout.decode()


def chat_welcome(**kwargs):
    print('Welcome to use chat extension!')


def extract_backticks_commands(text):
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    strip_pattern = r'^(bash\s*|shell\s*)'
    return [re.sub(strip_pattern, '', match.strip()) for match in matches]
     
def filter_az_commands(input):
    merge_cli_to_single_lines = re.sub(r'\\\n', '', input)
    matches = [m.strip() for m in merge_cli_to_single_lines.split('\n')]
    return [m for m in matches if m.startswith('az')]

def flatten_list(nested_list):
    return [item for sublist in nested_list for item in sublist]

def extract_az_commands(text):
    matches = extract_backticks_commands(text)
    return flatten_list([filter_az_commands(match) for match in matches])

# engine="gpt-4-32k-0314"
engine = "gpt3516k"

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

def chatgpt(messages):
    response = openai.ChatCompletion.create(
        engine=engine,
        messages=messages,
        temperature=0.1,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=True)
    # if not using stream=True, then response is a dict
    # response['choices'][0]['finish_reason']=='stop'
    # response['choices'][0]['message']['role'] #'assistant'
    # msg = response['choices'][0]['message']['content']

    collected_messages = []
    for chunk in response:
        content = get_prop(chunk, 'choices.0.delta.content', '')  # extract the message
        if content:
            collected_messages.append(content)  # save the message
            print(content, end="")
    print("\n", flush=True)

    msg = ''.join(collected_messages)

    messages.append({"role": 'assistant',  # response['choices'][0]['message']['role'],
                     "content": msg})
    prefix = ''
    azcommands = extract_az_commands(msg)
    # msg = msg.replace('```'+prefix,'')
    # msg = msg.replace('```','')
    return (msg, azcommands, messages)


# Define the callback function
def run_az_command(azcommands):
    for i, cmd in enumerate(azcommands):
        print(f"{i}: {cmd}")
    print(f"Hit `c` to cancel, otherwise please select the command to run: ", end="", flush=True)
    while True:
        user_input = getch()
        if user_input == 'c':
            return
        ordcode = ord(user_input)
        if ordcode >= ord('0') and ordcode < ord('0') + len(azcommands):
            option = ordcode - ord('0')
            cmd = azcommands[option]
            print('\n' + cmd)
            cmd = cmd.replace('<', '').replace('>', '').replace('`', '').replace('|', '').replace('&', '').replace(';', '')
            #cmd = "echo " + cmd
            returncode, output = run_command(cmd)
            print(output)
            return


def start_chat(**kwargs):
    messages = [SYSTEM_PROMPT]

    lines = [
        "Please enter your request below:",
        "For example: how to create a microsoft aks cluster",
    ]
    for line in (lines):
        print(line)

    text_input = input("Prompt: ")
    messages.append({"role": "user", "content": text_input})
    _, azcommands, messages = chatgpt(messages)

    while True:
        print("\nMenu: [p: re-Prompt, ", end="")
        if len(azcommands) > 0:
            print("r: Run command, ", end="")
        print("q: Quit]", flush=True)

        user_input = getch()

        # Handle user input
        if user_input == 'p':
            text_input = input("Prompt: ")
            messages.append({"role": "user", "content": text_input})
            _, azcommands, messages = chatgpt(messages)
        elif user_input == 'r' and len(azcommands) > 0:
            run_az_command(azcommands)
        elif user_input == 'q':
            # Exiting the program...
            break
