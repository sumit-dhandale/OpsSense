"""Console entry points for opssense CLI."""


def run_index() -> None:
    from scripts.index_documents import main

    main()


def run_search() -> None:
    from scripts.search import main

    main()


def run_ask() -> None:
    from scripts.ask import main

    main()
