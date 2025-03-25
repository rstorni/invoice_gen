from setuptools import setup, find_packages

setup(
    name='invoice_system',
    version='0.2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'reportlab',
        'PyQt6',
        'sqlite3'
    ],
    entry_points={
        'console_scripts': [
            'invoice-cli=invoice_system.invoice_generator:main',
            'invoice-desktop=invoice_system.desktop_app:main'
        ]
    },
    author='Your Name',
    description='A comprehensive invoice generation system'
)