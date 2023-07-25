# Azure AKS CLI AI Extension #
This package is for the 'ai' extension, i.e. 'az aks ai'.

## How to build

### Clone azure-cli and azure-cli-extensions repos
    git clone https://github.com/Azure/azure-cli
    git clone https://github.com/Azure/azure-cli-extensions

### Setup virtual env
    python3 -m venv env
    source env/bin/activate

### Install azure dev tool
    pip3 install azdev

### Link the 2 repos for development using below command
    azdev setup --cli azure-cli --repo azure-cli-extensions

### Install other python libraries (Will be vendored in the future)
    pip3 install openai colorama

### Build extension command
    % azdev extension build ai
    Building extension 'azure-cli-extensions/src/ai'...

### Setup environmental variables

    export OPENAI_API_KEY='xxxx'
    export OPENAI_API_TYPE="azure"
    export OPENAI_API_BASE="https://sulidevinstance.openai.azure.com/"
    export OPENAI_API_VERSION="2023-03-15-preview"
    export OPENAI_API_DEPLOYMENT="gpt-4-32k-0314"

### How to get into the interactive shell 

    az aks ai

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

