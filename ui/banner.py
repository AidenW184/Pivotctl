"""ASCII banner for Pivotctl."""

try:
    from ui.colours import Colour, colour_text

except ModuleNotFoundError:
    from colours import Colour, colour_text


BANNER = r"""
██████╗ ██╗██╗   ██╗ ██████╗ ████████╗██╗
██╔══██╗██║██║   ██║██╔═══██╗╚══██╔══╝██║
██████╔╝██║██║   ██║██║   ██║   ██║   ██║
██╔═══╝ ██║╚██╗ ██╔╝██║   ██║   ██║   ╚═╝
██║     ██║ ╚████╔╝ ╚██████╔╝   ██║   ██╗
╚═╝     ╚═╝  ╚═══╝   ╚═════╝    ╚═╝   ╚═╝

SHUT UP!, SHUT UP!, SHUT UPPPPPPP!!!
"""
SUBTITLE = """
Network Pivot Configuration Manager
 By AJ Whitfield A.K.A "Hypercube"
            v1.0"""


def show_banner():
    """Print the Pivotctl banner."""

    print(
        colour_text(
            BANNER,
            Colour.BRIGHT_GREEN,
        )
    )

    print()

    print(
        colour_text(
            SUBTITLE,
            Colour.BRIGHT_CYAN,
        )
    )

    print()


if __name__ == "__main__":
    show_banner()