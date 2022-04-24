"""Checking functions for parsing.py.
"""

import jax.numpy as jnp


def check_if_defined(evars, eqns):
    """Check if all variables are defined in period t.
    """

    for v in evars:
        v_in_eqns = [
            v in e.replace(v + "SS", "").replace(v + "Lag",
                                                 "").replace(v + "Prime", "")
            for e in eqns
        ]
        if not any(v_in_eqns):
            raise Exception(f"Variable `{v}` is not defined for time t.")
    return


def check_dublicates_and_determinancy(evars, eqns):
    """Check if there are dublicates and the numbers of eqns/vars match.
    """

    dubs = [x for i, x in enumerate(evars) if x in evars[:i]]
    dubmess = (
        ", variables list contains dublicate(s): %s" % ", ".join(
            dubs) if dubs else ""
    )

    sorted_evars = evars[:] = sorted(list(set(evars)), key=str.lower)

    if len(sorted_evars) != len(eqns):
        raise Exception(
            "Model has %s variables but %s equations%s."
            % (len(sorted_evars), len(eqns), dubmess)
        )
    elif dubs:
        print("(parse:) Warning%s" % dubmess)

    return sorted_evars


def check_func(model, shocks, par):

    init = model['init']
    # collect some information needed later
    model['init_run'] = {}

    if model.get('decisions'):
        # make a test backward and forward run
        init_vf = model['init_vf']
        _, decisions_output_init = model['context']['func_backw'](
            init, init, init, init, init_vf, jnp.zeros(len(shocks)), jnp.array(list(par.values())))
        dists_init = model['context']['func_stst_dist'](decisions_output_init)
    else:
        decisions_output_init = dists_init = []

    model['init_run']['decisions_output'] = decisions_output_init
    model['init_run']['dists'] = dists_init

    # final test of main function
    test = model['context']['func_eqns'](init, init, init, init, jnp.zeros(
        len(shocks)), jnp.array(list(par.values())), dists_init, decisions_output_init)

    if jnp.isnan(test).any():
        raise Exception("Initial values are NaN.")
    if jnp.isinf(test).any():
        raise Exception("Initial values are not finite.")

    return