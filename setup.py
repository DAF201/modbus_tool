import setuptools

setuptools.setup(
    name='virtual_simulator',
    version='0.0.1',
    description='the company is running out of real simulator, so I made a virtual one to test UI communication',
    author='DAF201',
    author_email='daf201@blink-in.com',
    url='https://github.com/DAF201/modbus_tool',
    download_url='https://github.com/DAF201/modbus_tool',
    install_requires=['pyserial>=3.5'],
    packages=['modbus'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
    ],
    entry_points={
        'console_scripts': [
            'simu=modbus.modbus:main',
        ],
    },
    python_requires=">=3.9",
)
