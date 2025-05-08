A simple Jupyter kernel for the Magma computer algebra , FOR WINDOWS.

This switches `pexpect` to `wexpect`

This kernel requires that Magma is installed and runnable using the
standard path, i.e., that typing the command ``magma`` will run magma.
Furthermore, it requires Jupyter running on Py3.

If ``pip`` and ``python`` point to their Py3 versions, you can install the 
kernel as a user with the commands::

    pip install git+https://github.com/nbruin/magma_kernel --user
    python -m magma_kernel.install

On some systems you may need to use ``pip3`` and ``python3`` instead::

    pip3 install git+https://github.com/nbruin/magma_kernel --user
    python3 -m magma_kernel.install

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
