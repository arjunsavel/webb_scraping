Installation
============

webb_scraping, as of now, does not include an automated testing suite; however, `this is an issue that will soon be fixed <https://github.com/arjunsavel/webb_scraping/issues/3>`_!

Installing with pip
-----------------------

The most straightforward way to download the code is too ```pip install``` it. It is recommended to run the below lines in a fresh `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_ environment.

.. code-block:: bash

    python3 -m pip install -U pip
    python3 -m pip install -U setuptools setuptools_scm pep517
    pip install webb_scraping



Installing from source
-----------------------

webb_scraping is developed on `GitHub <https://github.com/arjunsavel/webb_scraping>`_, where you can find the latest developer version of the code. It is recommended to run the below lines in a fresh `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_ environment.

.. code-block:: bash

    python3 -m pip install -U pip
    python3 -m pip install -U setuptools setuptools_scm pep517
    git clone https://github.com/arjunsavel/webb_scraping
    cd webb_scraping
    python3 -m pip install -e .