Installation
============

webb_scraping, as of now, does not include an automated testing suite; however, `this is an issue that will soon be fixed<https://github.com/arjunsavel/webb_scraping/issues/3>`_!

Installing from source
-----------------------

webb_scraping is developed on `GitHub <https://github.com/arjunsavel/webb_scraping>`_. It is recommended to run the below lines in a fresh `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_ environment.

.. code-block:: bash

    python3 -m pip install -U pip
    python3 -m pip install -U setuptools setuptools_scm pep517
    git clone https://github.com/arjunsavel/webb_scraping
    cd webb_scraping
    pip install -r requirements.txt