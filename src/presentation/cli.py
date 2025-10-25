"""
CLI Application for PDF Price Search.

This module provides a command-line interface for searching prices
in PDF documents using Click framework.
"""

import sys
import time
from pathlib import Path
from typing import Optional

import click
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import get_container
from src.application.config import AppConfig
from src.presentation.validation import InputValidator


# CLI context class
class CLIContext:
    """Context object for sharing state between commands."""

    def __init__(self):
        self.config = AppConfig()
        self.container = get_container(self.config)
        self.verbose = False


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """
    PDF Price Search CLI - Search for shipping prices in PDF documents.

    This tool allows you to search for shipping prices across multiple
    PDF documents using natural language queries.
    """
    ctx.obj = CLIContext()
    ctx.obj.verbose = verbose


@cli.command()
@click.argument('query')
@click.option('--no-cache', is_flag=True, help='Disable cache for this search')
@click.pass_context
def search(ctx, query, no_cache):
    """
    Search for a price with the given query.

    QUERY: Natural language search query (e.g., "FedEx 2Day, Zone 5, 3 lb")

    Examples:

        pdf-search search "FedEx 2Day, Zone 5, 3 lb"

        pdf-search search "Standard Overnight, z2, 10 lbs"

        pdf-search search "Express Saver Z8 1 lb"
    """
    try:
        # Validate query
        validated_query = InputValidator.validate_query(query)

        # Get search use case
        search_use_case = ctx.obj.container.search_price_use_case()

        # Execute search
        if ctx.obj.verbose:
            click.echo(f"Searching for: {validated_query}")

        start_time = time.time()
        response = search_use_case.execute(validated_query, use_cache=not no_cache)
        elapsed_ms = (time.time() - start_time) * 1000

        # Display result
        if response.success:
            click.echo(f"\n{Fore.GREEN}SUCCESS{Style.RESET_ALL}")
            click.echo(f"  Service:  {Fore.CYAN}{response.service}{Style.RESET_ALL}")
            click.echo(f"  Zone:     {response.zone}")
            click.echo(f"  Weight:   {response.weight} lb")
            click.echo(f"  Price:    {Fore.GREEN}${response.price}{Style.RESET_ALL}")
            click.echo(f"  Source:   {response.source_document}")
            click.echo(f"  Time:     {elapsed_ms:.2f} ms")
        else:
            click.echo(f"\n{Fore.RED}FAILED{Style.RESET_ALL}")
            click.echo(f"  Error:    {response.error_message}")
            click.echo(f"  Time:     {elapsed_ms:.2f} ms")
            sys.exit(1)

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'simple']),
              default='table', help='Output format')
@click.pass_context
def list(ctx, format):
    """
    List all available shipping services.

    This command displays all services loaded from PDF documents,
    including their zones and weight ranges.
    """
    try:
        # Get list services use case
        list_use_case = ctx.obj.container.list_services_use_case()

        # Execute list
        services = list_use_case.execute()

        if not services:
            click.echo(f"{Fore.YELLOW}No services loaded.{Style.RESET_ALL}")
            click.echo("Run 'pdf-search load' to load PDFs first.")
            return

        # Display services based on format
        if format == 'json':
            import json
            services_data = [
                {
                    'name': s.name,
                    'zones': s.available_zones,
                    'min_weight': s.min_weight,
                    'max_weight': s.max_weight,
                    'source': s.source_pdf
                }
                for s in services
            ]
            click.echo(json.dumps(services_data, indent=2))

        elif format == 'simple':
            for service in services:
                click.echo(f"{service.name} (Zones: {service.available_zones})")

        else:  # table format
            click.echo(f"\n{Fore.CYAN}Available Services:{Style.RESET_ALL}\n")
            click.echo(f"{'Service Name':<30} {'Zones':<15} {'Weight Range':<20} {'Source'}")
            click.echo("-" * 100)

            for service in services:
                zones_str = f"Z{min(service.available_zones)}-Z{max(service.available_zones)}"
                weight_str = f"{service.min_weight}-{service.max_weight} lb"
                source_str = Path(service.source_pdf).name

                click.echo(
                    f"{service.name:<30} {zones_str:<15} {weight_str:<20} {source_str}"
                )

            # Show summary
            summary = list_use_case.execute_summary()
            click.echo(f"\n{Fore.GREEN}Summary:{Style.RESET_ALL}")
            click.echo(f"  Total Services: {summary['total_services']}")
            click.echo(f"  Available Zones: {summary['available_zones']}")
            click.echo(f"  Weight Range: {summary['weight_range']['min']}-{summary['weight_range']['max']} lb")

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', required=False)
@click.option('--recursive', '-r', is_flag=True, help='Search subdirectories')
@click.pass_context
def load(ctx, directory, recursive):
    """
    Load PDF files from a directory.

    DIRECTORY: Path to directory containing PDF files (optional, uses default if not provided)

    Examples:

        pdf-search load

        pdf-search load /path/to/pdfs

        pdf-search load ./pdfs --recursive
    """
    try:
        # Get load data use case
        load_use_case = ctx.obj.container.load_data_use_case()

        # Determine directory
        if directory:
            dir_path = InputValidator.validate_directory_path(directory)
        else:
            dir_path = None

        # Show loading message
        click.echo(f"\n{Fore.CYAN}Loading PDF files...{Style.RESET_ALL}")

        # Execute load with progress bar
        start_time = time.time()

        if dir_path:
            result = load_use_case.execute(str(dir_path), recursive=recursive)
        else:
            result = load_use_case.execute_default()

        elapsed = time.time() - start_time

        # Display result
        if result['success']:
            click.echo(f"\n{Fore.GREEN}Successfully loaded PDF files{Style.RESET_ALL}")
            click.echo(f"  Total files:   {result['total_files']}")
            click.echo(f"  Loaded:        {result['loaded_count']}")
            click.echo(f"  Failed:        {result['failed_count']}")
            click.echo(f"  Time:          {elapsed:.2f}s")

            if result['failed_count'] > 0:
                click.echo(f"\n{Fore.YELLOW}Failed files:{Style.RESET_ALL}")
                for failed in result['failed_files']:
                    file_name = Path(failed['file']).name
                    click.echo(f"  - {file_name}: {failed['error']}")
        else:
            click.echo(f"{Fore.RED}Failed to load PDF files{Style.RESET_ALL}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--clear', is_flag=True, help='Clear the cache')
@click.option('--stats', is_flag=True, help='Show cache statistics')
@click.pass_context
def cache(ctx, clear, stats):
    """
    Manage the search cache.

    Examples:

        pdf-search cache --stats

        pdf-search cache --clear
    """
    try:
        # Get cache instance
        cache_instance = ctx.obj.container.cache()

        if not cache_instance:
            click.echo(f"{Fore.YELLOW}Cache is disabled{Style.RESET_ALL}")
            return

        if clear:
            cache_instance.clear()
            click.echo(f"{Fore.GREEN}Cache cleared successfully{Style.RESET_ALL}")

        if stats:
            cache_stats = cache_instance.get_stats()
            click.echo(f"\n{Fore.CYAN}Cache Statistics:{Style.RESET_ALL}")
            click.echo(f"  Total Entries:    {cache_stats.get('total_entries', 0)}")
            click.echo(f"  Active Entries:   {cache_stats.get('active_entries', 0)}")
            click.echo(f"  Expired Entries:  {cache_stats.get('expired_entries', 0)}")
            click.echo(f"  Default TTL:      {cache_stats.get('default_ttl', 0)}s")

        if not clear and not stats:
            click.echo("Use --stats to show statistics or --clear to clear cache")

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def demo(ctx):
    """
    Run demonstration queries.

    This command executes a set of predefined queries to demonstrate
    the application's capabilities.
    """
    try:
        # Ensure data is loaded
        click.echo(f"{Fore.CYAN}Loading PDF data...{Style.RESET_ALL}")
        load_use_case = ctx.obj.container.load_data_use_case()
        result = load_use_case.execute_default()

        if not result['success'] or result['loaded_count'] == 0:
            click.echo(f"{Fore.RED}No PDF files loaded. Cannot run demo.{Style.RESET_ALL}")
            sys.exit(1)

        click.echo(f"{Fore.GREEN}Loaded {result['loaded_count']} PDF files{Style.RESET_ALL}\n")

        # Get search use case
        search_use_case = ctx.obj.container.search_price_use_case()

        # Demo queries
        demo_queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
            "Express Saver Z8 1 lb",
            "Ground Z6 12 lb",
            "Priority Overnight, Zone 3, 5 lb",
        ]

        click.echo(f"{Fore.CYAN}Running {len(demo_queries)} demonstration queries:{Style.RESET_ALL}\n")

        successful = 0
        total_time = 0

        for i, query in enumerate(demo_queries, 1):
            click.echo(f"[{i}/{len(demo_queries)}] {Fore.YELLOW}{query}{Style.RESET_ALL}")

            response = search_use_case.execute(query)
            total_time += response.search_time_ms

            if response.success:
                successful += 1
                click.echo(f"  {Fore.GREEN}SUCCESS{Style.RESET_ALL}: "
                          f"{response.service} - ${response.price} "
                          f"({response.search_time_ms:.2f}ms)")
            else:
                click.echo(f"  {Fore.RED}FAILED{Style.RESET_ALL}: "
                          f"{response.error_message} "
                          f"({response.search_time_ms:.2f}ms)")
            click.echo()

        # Summary
        click.echo(f"{Fore.CYAN}Demo Summary:{Style.RESET_ALL}")
        click.echo(f"  Total Queries:  {len(demo_queries)}")
        click.echo(f"  Successful:     {successful}")
        click.echo(f"  Failed:         {len(demo_queries) - successful}")
        click.echo(f"  Success Rate:   {(successful/len(demo_queries)*100):.1f}%")
        click.echo(f"  Average Time:   {total_time/len(demo_queries):.2f}ms")

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """
    Start interactive search mode.

    This command allows you to perform multiple searches in a single session
    without reloading the data each time.
    """
    try:
        # Ensure data is loaded
        click.echo(f"{Fore.CYAN}PDF Price Search - Interactive Mode{Style.RESET_ALL}\n")
        click.echo("Loading PDF data...")

        load_use_case = ctx.obj.container.load_data_use_case()
        result = load_use_case.execute_default()

        if not result['success'] or result['loaded_count'] == 0:
            click.echo(f"{Fore.RED}No PDF files loaded.{Style.RESET_ALL}")
            sys.exit(1)

        click.echo(f"{Fore.GREEN}Loaded {result['loaded_count']} services{Style.RESET_ALL}")
        click.echo("\nEnter your search queries (or 'quit' to exit):")
        click.echo("Example: FedEx 2Day, Zone 5, 3 lb\n")

        # Get search use case
        search_use_case = ctx.obj.container.search_price_use_case()

        query_count = 0

        while True:
            try:
                # Get query from user
                query = click.prompt(f"{Fore.YELLOW}Query{Style.RESET_ALL}", type=str)

                # Check for exit commands
                if query.lower() in ['quit', 'exit', 'q']:
                    break

                # Execute search
                query_count += 1
                response = search_use_case.execute(query)

                # Display result
                if response.success:
                    click.echo(f"  {Fore.GREEN}SUCCESS{Style.RESET_ALL}: "
                              f"{response.service} - ${response.price} "
                              f"(Zone {response.zone}, {response.weight} lb) "
                              f"[{response.search_time_ms:.2f}ms]")
                else:
                    click.echo(f"  {Fore.RED}FAILED{Style.RESET_ALL}: "
                              f"{response.error_message}")

                click.echo()

            except click.Abort:
                break
            except Exception as e:
                click.echo(f"  {Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}\n")

        # Summary
        if query_count > 0:
            click.echo(f"\n{Fore.CYAN}Session Summary:{Style.RESET_ALL}")
            click.echo(f"  Total Queries: {query_count}")

        click.echo(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI application."""
    cli()


if __name__ == '__main__':
    main()
