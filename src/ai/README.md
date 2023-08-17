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
To obtain the API keys for OpenAI and Azure, you'll need to sign up for their respective services and create an API key. Here's how to do it:

OpenAI API Key:
a. Go to the OpenAI website (https://www.openai.com/) and sign up for an account if you don't have one already.
b. Once you've signed up and logged in, navigate to the API key section in your account dashboard (https://platform.openai.com/signup).
c. Follow the instructions to create a new API key. After creating the key, you'll be able to see your OpenAI API key. Make sure to keep it secure and not share it with others.

```
export OPENAI_API_KEY=xxx
export OPENAI_API_MODEL=gpt-3.5-turbo
```


Azure OpenAI API Key:
a. Go to the Azure Cognitive Services website (https://azure.microsoft.com/en-us/services/cognitive-services/) and sign up for an account if you don't have one already.
b. Once you've signed up and logged in, navigate to the Azure portal (https://portal.azure.com/).
c. Click on "Create a resource" in the left sidebar, and search for "Cognitive Services" in the search bar.
d. Select "Cognitive Services" from the search results and click "Create" to create a new Cognitive Services resource.
e. Fill in the required information, such as subscription, resource group, region, and name. For the "API type" field, choose the specific API you want to use (e.g., Text Analytics, Computer Vision, etc.).
f. After creating the resource, go to the "Keys and Endpoint" section in the resource's management page. Here, you'll find your Azure OpenAI API key. Make sure to keep it secure and not share it with others.

```
export OPENAI_API_KEY=xxx
export OPENAI_API_BASE=https://xxxinstance.openai.azure.com/
export OPENAI_API_DEPLOYMENT=gpt-4-32k-0314
export OPENAI_API_TYPE=azure
```

### How to get into the interactive shell 

    az aks ai

### Demo Screencast
![](demo.gif)

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

