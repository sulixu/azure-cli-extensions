# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.help_files import helps

helps['chat'] = """
    type: group
    short-summary: 
"""

helps['chat ai'] = """
    type: group
    short-summary: Start a chat with the AKS bot
    examples:
        - name: ASK chat bot how to create a microsoft aks cluster with az command line
          text: |-
            az chat ai 
            Prompt: how to create a microsoft aks cluster with az command line

"""

helps['chat welcome'] = """
    type: command
    short-summary: AKS Chatbot Welcome
"""
