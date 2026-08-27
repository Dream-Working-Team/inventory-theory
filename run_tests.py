"""Script para correr pruebas unitarias y guardar la salida en test_output.txt"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        suite = unittest.defaultTestLoader.discover('tests')
        result = runner.run(suite)
        f.write(f"\nResult: {'SUCCESS' if result.wasSuccessful() else 'FAILED'}\n")
    print("Tests finished execution.")
