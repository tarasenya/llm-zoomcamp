import os

import click
from dotenv import load_dotenv

import ambiguity_resolver_rag


@click.command()
@click.option('--elastic_url', default='http://localhost:9200', 
              help='Elasticsearch URL')
def main(elastic_url):
    """RAG CLI for resolving ambiguous statements."""
    # Load environment variables from .env file
    load_dotenv()

    # Create a new RAG instance with the provided ELASTIC_URL
    rag = ambiguity_resolver_rag.create_rag(elastic_url)
    
    # Print the ELASTIC_URL being used
    click.echo(f"Using ELASTIC_URL: {os.getenv('ELASTIC_URL', 'Not set')}")

    click.echo('Welcome to the Vague Resolver RAG CLI.')
    click.echo('Type "exit" or "quit" to end the program.')

    while True:
        vague_question = click.prompt('Input your vague statement', type=str).strip()

        if vague_question.lower() in ['exit', 'quit']:
            click.echo('Thank you for using Vague Resolver RAG. Goodbye!')
            break

        if not vague_question:
            click.echo('Please enter a valid statement.')
            continue

        try:
            result = rag.rag_results(vague_question)
            click.echo(f'Clear statement: {result}')
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()