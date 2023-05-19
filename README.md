# Azure Functions
## functions-chatyourdata-langchain (Functions Python v2)
This repo will have a implementation of the chat your data scenario using Azure Functions 

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=575770869)

## Run on your local environment

### Pre-reqs
1) [Python 3.8+](https://www.python.org/) 
2) [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v4%2Cmacos%2Ccsharp%2Cportal%2Cbash#install-the-azure-functions-core-tools)
3) [Azure OpenAPI API key, endpoint, and deployment](https://portal.azure.com) 
4) [Pinecone]({)https://docs.pinecone.io/docs/quickstart)
5) Add this local.settings.json file to the `ask` function folder to simplify local development and include Key from step 3
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AZURE_OPENAI_KEY": "...",
    "AZURE_OPENAI_ENDPOINT": "https://<service_name>.openai.azure.com/",
    "AZURE_OPENAI_SERVICE": "...",
    "AZURE_OPENAI_CHATGPT_DEPLOYMENT": "..."
  }
}
```
6) Add this local.settings.json file to the `import_page` function folder to simplify local development and include Key from step 3
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "PINECONE_API_KEY": "",
    "PINECONE_ENV": ""
  }
}
```

### Using Functions CLI
#### Import Page Function
1) Open a new terminal and do the following:

```bash
cd import_page
pip3 install -r requirements.text
func start
```
2) Using your favorite REST client, e.g. [RestClient in VS Code](https://marketplace.visualstudio.com/items?itemName=humao.rest-client), PostMan, curl, make a post.  `test.http` has been provided to run this quickly.   

Terminal:
```bash
curl -i -X POST http://localhost:7071/api/importpage/ \
  -H "Content-Type: text/json" \
  --data-binary "@testdata.json"
```

testdata.json
```json
{
    "url": "https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan"
}
```

test.http
```bash

POST http://localhost:7071/api/importpage HTTP/1.1
content-type: application/json

{
    "url": "https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan"
}
```

#### Ask Function
1) Open a new terminal and do the following:

```bash
cd ask
pip3 install -r requirements.text
func start
```
2) Using your favorite REST client, e.g. [RestClient in VS Code](https://marketplace.visualstudio.com/items?itemName=humao.rest-client), PostMan, curl, make a post.  `test.http` has been provided to run this quickly.   

test.http
```bash

POST http://localhost:7071/api/ask HTTP/1.1
content-type: application/json

{
    "question": "does function timeout depend on SKU?"
}
```

## Source Code

The key code that makes this work is as follows in `./ask/function_app.py`.  You can customize this or learn more snippets using the [LangChain Quickstart Guide](https://python.langchain.com/en/latest/getting_started/getting_started.html).

```python
index_name = 'functions'
embeddings = OpenAIEmbeddings()
docsearch = Pinecone.from_existing_index(index_name, embeddings)
llm = AzureOpenAI(deployment_name=AZURE_OPENAI_CHATGPT_DEPLOYMENT, temperature=0.7, openai_api_key=AZURE_OPENAI_KEY)
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())

result = qa.run(question)
logging.info(f'chain result is: {result}')

return result
```

## Deploy to Azure

The easiest way to deploy this app is using the [Azure Dev CLI aka AZD](https://aka.ms/azd).  If you open this repo in GitHub CodeSpaces the AZD tooling is already preinstalled.

To provision and deploy:
```bash
azd up
```
