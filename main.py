import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv
from pymongo import MongoClient

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from schemas.schema import AuditReport, AuditResult, Transaction

load_dotenv()

class Main:

    def __init__(self):
        
        self.tools = [self.search_transactions_db, self.document_to_vector_db, self.search_vector_db]

        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.agent = ChatGoogleGenerativeAI(model = "gemini-2.5-flash",  temperature = 0).bind_tools(self.tools).with_structured_output(AuditReport)
        
        # self.agent = self.agent

        self.mode = 'RETRIEVING'
        self.vector_db_host = os.getenv('QDRANT_DB_LOCAL')
        self.vector_db_collection = "automated-audit-compliance"

        self.mongo_client = MongoClient(os.getenv("MONGO_DB_ATLAS_CONNECTION_URL"))
        self.mongo_db = self.mongo_client['audit_db']
        self.mongo_collection = self.mongo_db['transactions']


    def document_to_vector_db(
            self, 
            file_path: str, 
            chunk_size: int, 
            chunk_overlap: int
    ):
        
        pdf_loader = PyPDFLoader(file_path=file_path)
        docs = pdf_loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        chunks = text_splitter.split_documents(documents=docs)
        to_vector_store = QdrantVectorStore.from_documents(
            documents= chunks,
            embedding= self.embedding_model,
            url= self.vector_db_host,
            collection_name= self.vector_db_collection
        )

    def search_vector_db(self, user_query: str):
        self.from_vector_store = QdrantVectorStore.from_existing_collection(
            embedding= self.embedding_model,
            url= self.vector_db_host,
            collection_name= self.vector_db_collection
        )
                
        return self.from_vector_store.similarity_search(query=user_query)
    
    def search_transactions_db(self, json_query: str):
        json_query = json.loads(json_query)
        results = list(self.mongo_collection.find(json_query))

        if not results:
            return "No records found that match the query"
        
        transactions =[]
        for i in results:
            txn = Transaction(**i)
            transactions.append(txn.model_dump())
        
        return json.dumps(results, indent=2)


    def main(self):
        if self.mode == 'CHUNKING':
            self.document_to_vector_db("policy.pdf", 1000, 400)

        user_prompt = input("> ")

        # search_results = self.search_vector_db(user_query)
        # search_results = "\n\n".join([doc.page_content for doc in search_results])

        system_prompt = SystemMessagePromptTemplate.from_template(
            """
            You are an expert Ernst & Young internal auditor. 
            You have access to a transaction database and a policy vector database.
            1. First, query the transaction database for the records requested by the user.
            2. Second, search the corporate policy for the rules regarding those specific transaction types.
            3. Finally, evaluate the transactions against the policy and output your findings.
            """
        )

        user_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, ("user", "{user_prompt}")])

        chat_prompt = chat_prompt.invoke({"user_prompt": user_prompt})

        response = self.agent.invoke(chat_prompt)  

        print(response)      


if __name__ == "__main__":
    app = Main()
    app.main()