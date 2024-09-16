from src import ambiguity_resolver_rag

def main_loop():
    rag = ambiguity_resolver_rag.ambiguity_resolver_rag
    
    print('Hello, I am Vague Resolver RAG.')
    print('Type "exit" or "quit" to end the program.')
    
    while True:
        vague_question = input('Input your vague statement: ').strip()
        
        if vague_question.lower() in ['exit', 'quit']:
            print('Thank you for using Vague Resolver RAG. Goodbye!')
            break
        
        if not vague_question:
            print('Please enter a valid statement.')
            continue
        
        result = rag.rag_results(vague_question)
        print(f'Your boss meant: {result}')
        
if __name__ == '__main__':
    main_loop()