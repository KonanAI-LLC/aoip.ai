from setuptools import setup, find_packages

setup(
    name='aoip-eval',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
        'numpy==1.23.5',
        'stempeg',
        'speechmetrics @ git+https://github.com/aliutkus/speechmetrics#egg=speechmetrics',
        'librosa',
        'matplotlib',
        'tqdm'
    ],
    dependency_links=[
        'https://github.com/schmiph2/pysepm/archive/master.zip#egg=pysepm'
    ],
)