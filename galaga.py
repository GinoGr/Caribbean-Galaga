#!/usr/bin/env python3
"""Galaga game entry point."""
import sys
from videogame.game import Galaga

def main():
    """Main function to run the Galaga game."""
    sys.exit(Galaga().run())

if __name__ == '__main__':
    main()
