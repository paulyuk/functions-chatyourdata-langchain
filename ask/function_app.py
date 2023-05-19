import os
import logging
import azure.functions as func
import openai
from langchain.llms.openai import AzureOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA


app = func.FunctionApp()

@app.function_name(name='ask')
@app.route(route='ask')
def main(req):

    logging.info('Running `ask` function')
    question = req.params.get('question') 
    if not question: 
        try: 
            req_body = req.get_json() 
        except ValueError: 
            raise RuntimeError('question data must be set in POST.') 
        else: 
            question = req_body.get('question') 
            if not question:
                raise RuntimeError('question data must be set in POST.')

    logging.info(f'question parameter is: {question}')
    # init OpenAI: Replace these with your own values, either in environment variables or directly here
    AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT") or "chat" #GPT turbo
    if 'AZURE_OPENAI_KEY' not in os.environ:
        raise RuntimeError("No 'AZURE_OPENAI_KEY' env var set.  Please see Readme.")

    # configure azure openai for langchain and/or llm
    openai.api_key = AZURE_OPENAI_KEY
    openai.api_base = AZURE_OPENAI_ENDPOINT # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
    openai.api_type = 'azure'
    openai.api_version = '2022-12-01' # this may change in the future
    logging.info('Using Azure OpenAI endpoint with {AZURE_OPENAI_CHATGPT_DEPLOYMENT} model.')

    index_name = 'functions'
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone.from_existing_index(index_name, embeddings)
    llm = AzureOpenAI(deployment_name=AZURE_OPENAI_CHATGPT_DEPLOYMENT, temperature=0.7, openai_api_key=AZURE_OPENAI_KEY)
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())

    result = qa.run(question)
    logging.info(f'chain result is: {result}')

    return result
