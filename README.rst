A simple Jupyter kernel for the Magma computer algebra system

This requires IPython 3.

To install::

    pip install magma_kernel
    python -m magma_kernel.install

To use it, run one of:

.. code:: shell

    jupyter notebook
    # In the notebook interface, select Magma from the 'New' menu
    jupyter qtconsole --kernel magma
    jupyter console --kernel magma

This code is based on a Magma kernel for IPython written by Christopher 
Granade, which was in turn based on the Bash example kernel by Thomas 
Kluyver. Improvements made in the current version include Tab 
completion, processing of help requests by returning an appropriate 
help query URL for Magma online documentation, and the reporting of 
partial output.
