"""
Module contains methods of calculating a pore size distribution starting from a DFT
kernel. Please note that calculation of the DFT/NLDFT/QSDFT kernels are outside the
scope of this program
"""

import numpy
import pandas
import scipy

_KERNELS = {}


def psd_dft_kernel_fit(pressure, loading, kernel_path):
    """
    Fits a DFT kernel on experimental adsorption data

    Parameters
    ----------
    loading : array
        adsorbed amount in mmol/g
    pressure : array
        relative pressure
    kernel_path : str
        the location of the kernel to use

    Returns
    -------
    pore widths : array
        the widths of the pores
    pore_dist : array
        the distributions for each width

    Notes
    -----
    The function will take the data in the form of pressure and loading. It will
    then load the kernel either from disk or from memory and define a minimsation
    function as the sum of squared differences of the sum of all individual kernel
    isotherm loadings multiplied by their contribution as per the following function:

    .. math::

        f(x) = \\sum_{p=p_0}^{p=p_x} (n_{p,exp} - \\sum_{w=w_0}^{w=w_y} n_{p, kernel} X_w )^2

    The function is then minimised using the `scipy.optimise.minimise` module, with the
    constraint that the contribution of each isotherm cannot be negative.

    """

    # get the interpolation kernel
    kernel = _load_kernel(kernel_path)

    # generate the pandas array
    kernel_points = []
    for psize in kernel:
        kernel_points.append(kernel.get(psize)(pressure))

    pore_widths = numpy.array(list(kernel.keys())).astype(float)

    points_arr = pandas.DataFrame(
        kernel_points,
        index=pore_widths,
        columns=pressure)

    # define the minimization function
    def sum_squares(pore_dist):
        return (points_arr.multiply(pore_dist, axis=0)
                # -> multiply each loading with its contribution
                .sum()
                # -> add the contributions together at each pressure
                .subtract(loading)
                # -> difference between calculated and isotherm
                .pow(2)
                # -> square the difference
                .sum()
                # -> sum of squares together
                )

    # define the constraints (x>0)
    cons = [{
        'type': 'ineq',
        'fun': lambda x: x,
    }]

    # run the optimisation algorithm
    guess = [0 for pore in points_arr.index]
    result = scipy.optimize.minimize(
        sum_squares, guess, method='SLSQP', constraints=cons)

    pore_dist = result.x

    return pore_widths, pore_dist


def _load_kernel(path):
    """
    Loads a kernel from disk or from memory

    Parameters
    ----------
    path : str
        path to the kernel to load in .csv form

    Returns
    -------
    array
        kernel
    """

    if path in _KERNELS:
        return _KERNELS[path]

    else:
        raw_kernel = pandas.read_csv(path, index_col=0)

        # add a 0 in the dataframe for interpolation between lowest values
        raw_kernel = raw_kernel.append(pandas.DataFrame(
            [0 for col in raw_kernel.columns], index=raw_kernel.columns, columns=[0]).transpose())

        kernel = dict()
        for pore_size in raw_kernel:
            interpolator = scipy.interpolate.interp1d(
                raw_kernel[pore_size].index,
                raw_kernel[pore_size].values,
                kind='cubic')

            kernel.update({pore_size: interpolator})

        # Save the kernel in memory
        _KERNELS.update({path: kernel})

    return kernel
