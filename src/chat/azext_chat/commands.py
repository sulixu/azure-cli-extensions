# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group('chat', is_experimental=True) as g:
        g.custom_command('ai', 'start_chat')
        # Run the program
        g.custom_command('welcome', 'chat_welcome')

    # with self.command_group('chat nextcommand') as g:
    #     g.custom_command('nextnextcommand', 'call_this_function')

