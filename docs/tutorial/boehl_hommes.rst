
Boehl-Hommes method
-------------------

The package also contains an alternative "shooting" method much aligned to the one introduced in Boehl & Hommes (2021). In the original paper we use this method to solve for chaotic asset price dynamics. The method can be understood as an extension to Fair & Taylor (1983) and is similar to a  policy function iteration where the initial state is the only fixed grid point and all other grid points are chosen endogenously (as in a "reverse" EGM) to map the expected trajectory.

Assume the model is given by

.. code-block::

    f(x_{t-1}, x_t, x_{t+1}) = 0.

We iterate on the expected trajectory itself instead of the policy function. We hence require

.. code-block::

   d f(x_{t-1}, x_t, x_{t+1} ) < d x_{t-1},
   d f(x_{t-1}, x_t, x_{t+1} ) < d x_{t+1}.

This is also the weakness of the method: not every DSGE model (that is determined in the Blanchard-Kahn sense) is such backward-and-forward contraction. Thus, unless you are interested in chaotic dynamics, the standard "stacking" method is to be prefered.

The following example shows how to use the shooting method to a numerically challenging example: the chaotic rational expectations model of Boehl & Hommes (2021). The YAML for this model can be found `here <https://github.com/gboehl/econpizza/blob/master/econpizza/examples/bh.yml>`_.

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    import econpizza as ep
    from econpizza import example_bh

    # parse the yaml
    mod = ep.load(example_bh, raise_errors=False)
    _ = mod.solve_stst()

    # choose an interesting initial state
    state = np.zeros(len(mod.var_names))
    state[:-1] = [.1, .2, 0.]

    # solve and simulate
    x, _, flag = ep.find_path_shooting(mod, state, T=500, max_horizon=1000, tol=1e-5)

    # plotting
    for i,v in enumerate(mod.var_names):

        plt.figure()
        plt.plot(x[:,i])
        plt.title(v)

This will give you boom-bust cycles in asset pricing dynamics:

.. image:: https://github.com/gboehl/econpizza/blob/master/docs/p_and_n.png?raw=true
  :width: 800
  :alt: Dynamics of prices and fractions

Below, find the documentation for the additional function:

.. autofunction:: econpizza.PizzaModel.find_path_shooting

