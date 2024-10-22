from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from uuid import uuid4

file_path = "~/Desktop/unix haters handbook.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

print(len(docs))


llm = ChatOpenAI(model="gpt-4o")


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

vectorstore = Chroma(collection_name="uhh", embedding_function=OpenAIEmbeddings())


uuids = [str(uuid4()) for _ in range(len(splits))]
vectorstore.add_documents(documents=splits, ids=uuids)

retriever = vectorstore.as_retriever()


system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the above pieces of retrieved context to answer "
    "the question. If you the context doesn't provide the answer, say that you "
    "don't know. Keep the tone used in the context, use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "--- BEGIN CONTEXT ---"
    "{context}"
    "--- END CONTEXT ---"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

user_input = ""

while True:

    print("\n\nPlease type your question:")
    user_input = input()
    if user_input == "q":
        break
    results = rag_chain.invoke({"input": user_input})

    print(results["answer"])
    print(f"Sources: {results}")
