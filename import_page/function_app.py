import os
import logging
import pinecone
import azure.functions as func
from langchain.vectorstores import Pinecone
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings


app = func.FunctionApp()

index_name = 'functions'

pinecone.init(
    api_key=os.getenv('PINECONE_API_KEY'), 
    environment=os.getenv('PINECONE_ENV')
)

@app.function_name(name='importpage')
@app.route(route='importpage')
def main(req):

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        url = req_body.get('url')

    if url:
        logging.info(f"Retrieving: {url}")
        loader = UnstructuredURLLoader(urls=[url])
        document = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(document)

        logging.info(f"Split into {len(docs)} chunks")
        embeddings = OpenAIEmbeddings()
        docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)
        logging.info(f"Indexed {len(docs)} chunks")
        index_description = pinecone.describe_index(index_name)
        logging.info(index_description)

        return func.HttpResponse(f"Indexed {len(docs)} chunks", status_code=200)
    else:
        return func.HttpResponse(
             "Pass a json object with a url property",
             status_code=400
        )
