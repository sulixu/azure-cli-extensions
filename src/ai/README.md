# Azure AKS CLI AI Extension #
This package is for the 'ai' extension, i.e. 'az aks ai'.

### How to build ###
```
python3 -m venv env
source env/bin/activate
pip3 install azdev
azdev setup --cli azure-cli --repo azure-cli-extensions
# install other python library
pip3 install openai colorama
```
```
% azdev extension build ai
Building extension 'azure-cli-extensions/src/ai'...
```

### How to set required ENV ###

```
export OPENAI_API_KEY='xxxx'
export OPENAI_API_TYPE="azure"
export OPENAI_API_BASE="https://sulidevinstance.openai.azure.com/"
export OPENAI_API_VERSION="2023-03-15-preview"
export OPENAI_API_DEPLOYMENT="gpt-4-32k-0314"
```

### How to get into the interactive shell ###
```
az aks ai
```


### How to use ###
Install this extension using the below CLI command
```
az extension add --name ai
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

