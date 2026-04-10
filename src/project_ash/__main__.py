import sys

from project_ash.cli import main as cli_main
from project_ash.diagnostics import main as diagnostics_main


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "diagnostics":
        raise SystemExit(diagnostics_main())
    cli_main()
