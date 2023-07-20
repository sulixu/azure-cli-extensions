# Azure CLI chat Extension #
This package is for the 'chat' extension, i.e. 'az chat'.

### How to build ###
python3 -m venv env
source env/bin/activate
pip3 install azdev
azdev setup --cli azure-cli --repo azure-cli-extensions
# install openai python library
pip3 install openai



sulixu@Sulis-MacBook-Pro azure-cli-extensions % . ../env/bin/activate
(env) sulixu@Sulis-MacBook-Pro azure-cli-extensions % azdev extension build chat

Building extension '/Users/sulixu/ms/azure-cli-extensions/src/chat'...
(env) sulixu@Sulis-MacBook-Pro azure-cli-extensions % . src/chat/azext_chat/secrets_do_not_check_in.sh
(env) sulixu@Sulis-MacBook-Pro azure-cli-extensions % 


### How to use ###
Install this extension using the below CLI command
```
az extension add --name chat
```

### Included Features
*Examples:*

```
az chat
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

