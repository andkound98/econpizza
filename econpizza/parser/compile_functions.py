"""Functions that write other functions.
"""
import jax
from .build_functions import func_forw_generic, func_forw_stst_generic


def compile_func_basics_str(evars, par, shocks):

    func_str = f"""
        \n ({"".join(v + "Lag, " for v in evars)}) = XLag
        \n ({"".join(v + ", " for v in evars)}) = X
        \n ({"".join(v + "Prime, " for v in evars)}) = XPrime
        \n ({"".join(v + "SS, " for v in evars)}) = XSS
        \n ({"".join(p + ", " for p in par)}) = pars
        \n ({"".join(s + ", " for s in shocks)}) = shocks"""

    return func_str


def compile_backw_func_str(evars, par, shocks, inputs, outputs, calls):
    """Compile all information to a string that defines the backward function for 'decisions'.
    """

    if isinstance(calls, str):
        calls = calls.splitlines()

    func_str = f"""def func_backw(XLag, X, XPrime, XSS, VFPrime, shocks, pars):
            {compile_func_basics_str(evars, par, shocks)}
            \n ({"".join(v + ", " for v in inputs)}) = VFPrime
            \n %s
            \n return jnp.array(({"".join(v[:-5] + ", " for v in inputs)})), jnp.array(({", ".join(v for v in outputs)}))
            """ % '\n '.join(calls)

    return func_str


def compile_stst_func_str(evars, par, stst, init):
    """Compile all information from 'equations' section to a string that defines the function.
    """

    stst_str = '; '.join([f'{v} = {stst[v]}' for v in stst])

    # compile the final function string
    func_pre_stst_str = f"""def func_pre_stst(INTERNAL_init):
        \n ({"".join(v + ", " for v in init)}) = INTERNAL_init
        \n {stst_str}
        \n INTERNAL_vars = ({"".join(v + ", " for v in evars)})
        \n INTERNAL_par = ({"".join(p + ", " for p in par)})
        \n return jnp.array(INTERNAL_vars), jnp.array(INTERNAL_par)"""

    return func_pre_stst_str


def get_forw_funcs(model):

    distributions = model['distributions']

    if len(distributions) > 1:
        raise NotImplementedError(
            'More than one distribution is not yet implemented.')

    # already prepare for more than one distributions
    for dist_name in distributions:

        dist = distributions[dist_name]

        implemented_endo = ('exogenous_custom', 'exogenous_rouwenhorst')
        implemented_exo = ('endogenous_custom', 'endogenous_log')
        exog = [v for v in dist if dist[v]['type'] in implemented_endo]
        endo = [v for v in dist if dist[v]['type'] in implemented_exo]
        other = [dist[v]['type'] for v in dist if dist[v]
                 ['type'] not in implemented_endo + implemented_exo]

        if len(exog) > 1:
            raise NotImplementedError(
                'Exogenous distributions with more than one dimension are not yet implemented.')
        if len(endo) > 2:
            raise NotImplementedError(
                'Endogenous distributions with more than two dimension are not yet implemented.')
        if other:
            raise NotImplementedError(
                f"Grid(s) of type {str(*other)} not implemented.")

        transition = model['context'][dist[exog[0]]['transition_name']]
        grids = [model['context'][dist[i]['grid_name']] for i in endo]
        indices = [model['decisions']['outputs'].index(i) for i in endo]

        model['context']['func_forw'] = jax.tree_util.Partial(
            func_forw_generic, grids=grids, transition=transition, indices=indices)
        model['context']['func_forw_stst'] = jax.tree_util.Partial(
            func_forw_stst_generic, grids=grids, transition=transition, indices=indices)

    return


def compile_eqn_func_str(evars, eqns, par, eqns_aux, shocks, distributions, decisions_outputs):
    """Compile all information from 'equations' section' to a string that defines the function.
    """

    # start compiling root_container
    for i, eqn in enumerate(eqns):
        if "=" in eqn:
            lhs, rhs = eqn.split("=")
            eqns[i] = f"root_container{i} = {lhs} - ({rhs})"
        else:
            eqns[i] = f"root_container{i} = {eqn}"

    if isinstance(eqns_aux, str):
        eqns_aux = eqns_aux.splitlines()

    eqns_aux_stack = "\n ".join(eqns_aux) if eqns_aux else ""
    eqns_stack = "\n ".join(eqns)

    # compile the final function string
    func_str = f"""def func_eqns(XLag, X, XPrime, XSS, shocks, pars, distributions=[], decisions_outputs=[]):
        {compile_func_basics_str(evars, par, shocks)}
        \n ({"".join(d+', ' for d in distributions)}) = distributions
        \n ({"".join(d+', ' for d in decisions_outputs)}) = decisions_outputs
        \n {eqns_aux_stack}
        \n {eqns_stack}
        \n {"return jnp.array([" + ", ".join("root_container"+str(i) for i in range(len(evars))) + "]).T.ravel()"}"""

    return func_str
