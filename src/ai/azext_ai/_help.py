# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.help_files import helps


helps['ai'] = """
    type: command
    short-summary: Start a chat with the AKS bot
    examples:
        - name: ASK chat bot how to create a microsoft aks cluster with az command line
          text: |-
            az aks ai 
            Prompt: how to create a microsoft aks cluster with az command line

"""

