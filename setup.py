import setuptools


with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

    name='mixbaba',

    version='0.1',

    scripts=['bin/mixbaba'] ,

    author="Vincenzo Lavorini",

    author_email="vincenzo.lavorini@naturalcycles.com",

    description="A tool to analyze AB tests data from Mixpanel funnels",

    long_description=long_description,

    long_description_content_type="text/markdown",

    packages=['mixbaba'],

    python_requires='>=3.6',

    install_requires=[
        "numpy",
        "pandas",
        "numba",
        "matplotlib",
        "scipy",
        "tqdm",
        "tabulate"
    ],

    tests_require=['nose'],

    test_suite="tests",

    classifiers=[

         "Development Status :: 3 - Alpha",

         "Environment :: Console",

         "Intended Audience :: Developers",

         "Natural Language :: English",

         "Programming Language :: Python :: 3",

         "Operating System :: OS Independent",

         "Topic :: Utilities"

    ],

 )
