import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from schemas.schema import AuditResult, Transaction

load_dotenv()

class Main:

    def __init__(
            self,
    ):
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.mode = 'CHUNKING'
        self.connection_url = os.getenv('QDRANT_DB_LOCAL')
        self.collection_name = "automated-audit-compliance"

    def document_to_vector(
            self, 
            file_path, 
            chunk_size, 
            chunk_overlap
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
            url= self.connection_url,
            collection_name= self.collection_name
        )

    def search_vector_db(self, user_query):
        self.from_vector_store = QdrantVectorStore.from_existing_collection(
            embedding= self.embedding_model,
            url= self.connection_url,
            collection_name= self.collection_name
        )
                
        search_results = self.from_vector_store.similarity_search(query=user_query)
        
        return search_results


    def main(self):
        if self.mode == 'CHUNKING':
            self.document_to_vector("policy.pdf", 1000, 400)

        
        with open('transaction.json', 'r') as transaction_json:
            transactions = json.load(transaction_json)

        user_query = f"Company policy rules regarding {transactions[0].get('category')} expenses, specifically {transactions[0].get('subcategory')} for amount {transactions[0].get('amount')} {transactions[0].get('currency')}."

        search_results = self.search_vector_db(user_query)
        
        agent = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature = 0)
        auditor = agent.with_structured_output(AuditResult)

        system_message = SystemMessagePromptTemplate.from_template(
            """
            You are an expert Ernst & Young internal auditor. 
            Your job is to review employee transactions against the company policy.
            Be strict, objective, and always cite the specific policy rule you are using.
            
            COMPANY POLICY CONTEXT:
            {search_results}
            """
        )

        human_message = HumanMessagePromptTemplate.from_template(user_query)
        chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        chain = chat_prompt | auditor
        result = chain.invoke({
            "search_results": search_results,
            "user_query": user_query
            })
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app = Main()
    app.main()