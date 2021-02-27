"""Waveguide cavity resonator."""

import numpy as np
from numpy import pi, sqrt
from scipy.constants import c as c0
import scipy.constants as sc
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from .propagation import surface_resistance, wavenumber, intrinsic_impedance


# Free space impedance
eta0 = sc.physical_constants['characteristic impedance of vacuum'][0]


def resonant_frequency(a, b, d, m=1, n=0, l=0, er=1, ur=1):
    """Calculate the resonant frequencies of a waveguide cavity.

    Args:
        a: a waveguide dimension
        b: b waveguide dimension
        d: length of waveguide cavity
        m: mode number m
        n: mode number n
        l: resonance number l
        er: relative permittivity
        ur: relative permeability

    Returns:
        np.ndarray: resonant frequency

    """

    term1 = c0 / 2 / pi / sqrt(er.real * ur.real)
    term2 = sqrt((m * pi / a) ** 2 + (n * pi / b) ** 2 + (l * pi / d) ** 2)

    return term1 * term2


def resonant_frequency2permittivity(l_order, fres, a, b, d, m=1, n=0):
    """Calculate the resonant frequencies of a waveguide cavity.

    Args:
        a: a waveguide dimension
        b: b waveguide dimension
        d: length of waveguide cavity
        m: mode number m
        n: mode number n
        l: resonance number l
        er: relative permittivity
        ur: relative permeability

    Returns:
        np.ndarray: resonant frequency

    """

    term1 = c0 / 2 / pi
    term2 = sqrt((m * pi / a) ** 2 + (n * pi / b) ** 2 + (l_order * pi / d) ** 2)

    return (term1 * term2 / fres) ** 2


# Q-FACTOR ---------------------------------------------------------------- ###

def qfactor_dielectric(tand):
    """Calculate Q-factor due to dielectric filling.

    Args:
        tand: loss tangent

    Returns:
        Q-factor

    """

    return 1 / tand


def qfactor_conduction(a, b, d, cond, m=1, n=0, l=1, er=1, ur=1):
    """Calculate Q-factor due to waveguide conductivity.

    Args:
        a: a waveguide dimension
        b: b waveguide dimension
        d: length of waveguide cavity
        cond: conductivity
        m: mode number m
        n: mode number n
        l: resonance number l
        er: relative permittivity
        ur: relative permeability

    Returns:
        Q-factor

    """

    # Resonant frequency
    fres = resonant_frequency(a, b, d, m, n, l, er=er, ur=ur)

    # Surface resistance
    rs = surface_resistance(fres, cond)

    # Wavenumber (1/m)
    k = wavenumber(fres, er=er, ur=ur)

    # Intrinsic impedance
    eta = intrinsic_impedance(er=er, ur=ur)

    # Eqn 6.46 in Pozar
    t1 = (k * a * d) ** 3 * b * eta / 2 / pi ** 2 / rs
    t2 = 2 * l ** 2 * a ** 3 * b + 2 * b * d ** 3 + l ** 2 * a ** 3 * d + a * d ** 3

    return t1 / t2


def qfactor_parallel(q1, q2):
    """Parallel Q-factors.

    Args:
        q1 (float): Q-factor 1
        q2 (float): Q-factor 2

    Returns:
        float: parallel Q-factor

    """

    return q1 * q2 / (q1 + q2)


def deembed_qfactor(q_net, q_remove):
    """Deembed Q-factor.

    Args:
        q_net (float): overall Q-factor
        q_remove (float): Q-factor to deembed

    Returns:
        float: overall Q-factor with qremove Q-factor removed

    """

    return 1 / (1 / q_net - 1 / q_remove)


# TRANSFORM Q-FACTOR ----------------------------------------------------- ###

def q2surface_resistance(fres, q, a, b, d, l=1, er=1, ur=1):
    """Calculate surface resistance from Q-factor.

    Args:
        fres: resonant frequency
        q: Q-factor
        a: a waveguide dimension
        b: b waveguide dimension
        d: length of waveguide cavity
        m: mode number m
        n: mode number n
        l: resonance number l
        er: relative permittivity
        ur: relative permeability

    Returns:
        surface resistance

    """

    # Wavenumber (1/m)
    k = wavenumber(fres, er=er, ur=ur)

    # Intrinsic impedance
    eta = intrinsic_impedance(er=er, ur=ur)

    # Eqn 6.46 in Pozar
    t1 = (k * a * d) ** 3 * b * eta / 2 / pi ** 2
    t2 = 2 * l ** 2 * a ** 3 * b + 2 * b * d ** 3 + l ** 2 * a ** 3 * d + a * d ** 3

    return t1 / t2 / q


def q2conductivity(fres, q, a, b, d, l=1, er=1, ur=1):
    """Calculate conductivity from Q-factor.

    Args:
        fres: resonant frequency
        q: Q-factor
        a: a waveguide dimension
        b: b waveguide dimension
        d: length of waveguide cavity
        m: mode number m
        n: mode number n
        l: resonance number l
        er: relative permittivity
        ur: relative permeability

    Returns:
        surface resistance

    """

    # Surface resistance
    rs = q2surface_resistance(fres, q, a, b, d, l=l, er=er, ur=ur)

    return 2 * pi * fres * ur * sc.mu_0 / (2 * rs ** 2)


# FIND RESONANCES -------------------------------------------------------- ###

def find_resonances(f, s21db, amp_interp=6, idx_span=20, **kwargs):
    """Find resonances in S21 data.

    Uses scipy.signal.find_peaks.

    """

    # Find peaks
    pidx, _ = find_peaks(s21db, **kwargs)

    # Get better estimate for center frequency
    f_resonances = np.zeros(len(pidx))
    for i, idx in np.ndenumerate(pidx):
        # Truncate
        ftmp = f[idx-idx_span//2:idx+idx_span//2+1]
        s21tmp = s21db[idx-idx_span//2:idx+idx_span//2+1]

        # Peak amplitude
        peak = s21tmp.max()

        # Amplitude for interpolation
        hp = peak - amp_interp

        # Interpolate to estimate center frequency
        peak_idx = s21tmp.argmax()
        flower, s21lower = ftmp[:peak_idx+1],  s21tmp[:peak_idx+1]
        fupper, s21upper = ftmp[peak_idx:],    s21tmp[peak_idx:]
        flow = np.interp(hp, s21lower, flower)
        fhi  = np.interp(hp, s21upper[::-1], fupper[::-1])
        fc = (fhi+flow) / 2
        f_resonances[i] = fc

    return f_resonances


def find_qfactor(f, s21mag, fres_list, fspan=1e8, debug=False):
    """Calculate Q-factor from experimental S21 magnitude.

    Args:
        f (float): frequency, in units [Hz]
        s21mag (float): S21 magnitude (linear units)
        fres_list (np.ndarray): list of resonant frequencies to examine,
            in units [Hz]
        fspan (int): width of frequency span to examine
        debug (bool): plot fitting?

    Returns:
        list: freq, Q-factor, Q-factor error

    """

    # Resonant frequency list
    fres_list = np.array(fres_list, dtype=float)

    # Plot fitting (debug only)
    if debug:
        ncol = 4
        nrow = -(-len(fres_list) // ncol)
        fig, ax = plt.subplots(nrow, ncol, figsize=(15, 25))
        fig.subplots_adjust(wspace=0, hspace=0)
        for r in range(nrow):
            for c in range(ncol):
                ax[r][c].set_xticklabels([])
                ax[r][c].set_yticklabels([])

    # Fit each individual peak
    f_center = np.empty_like(fres_list)
    q_factor = np.empty_like(fres_list)
    q_factor_error = np.empty_like(fres_list)
    for i in range(len(fres_list)):

        # Resonant frequency (initial guess)
        fres = fres_list[i]

        # Truncate data (try to only include one resonance)
        idx1 = np.abs(f - (fres - fspan / 2)).argmin()
        idx2 = np.abs(f - (fres + fspan / 2)).argmin()
        f_t, s21mag_t = f[idx1:idx2+1], s21mag[idx1:idx2+1]

        # Get peak parameters
        peak_mag = s21mag_t.max()
        peak_idx = s21mag_t.argmax()
        peak_3db = peak_mag / np.sqrt(2)

        # Interpolate to estimate Q-factor
        flower, s21lower = f_t[:peak_idx+1], s21mag_t[:peak_idx+1]
        fupper, s21upper = f_t[peak_idx:], s21mag_t[peak_idx:]
        f1 = np.interp(peak_3db, s21lower, flower)
        f2 = np.interp(peak_3db, s21upper[::-1], fupper[::-1])
        fres_mid = (f1 + f2) / 2
        fres_span = f2 - f1
        q_3db = fres_mid / fres_span

        # # Resonance model
        # def _model(x, ymax, xc, q, a1, a2, a3):
        #     w = 2 * np.pi * x
        #     w0 = 2 * np.pi * xc
        #     return a1 + a2 * w + (ymax + a3 * w) / sqrt(1 + 4 * q ** 2 * ((w - w0) / w0) ** 2)

        # Resonance model
        def _model(x, ymax, xc, q, a1, a2):
            w = 2 * np.pi * x
            w0 = 2 * np.pi * xc
            return a1 + a2 * w + ymax / sqrt(1 + 4 * q ** 2 * ((w - w0) / w0) ** 2)

        # Fit resonance model to data
        p0 = [peak_mag, fres_mid, q_3db, s21mag_t.min(), 0]
        # p0 = [peak_mag, fres_mid, q_3db, s21mag_t.min(), 0, 0]
        popt, pcov = curve_fit(_model, f_t, s21mag_t, p0=p0)
        perr = np.sqrt(np.diag(pcov))

        # Add to list
        f_center[i] = popt[1]
        q_factor[i] = popt[2]
        q_factor_error[i] = perr[2]

        # Plot fitting (debug only)
        if debug:
            row, col = i // ncol, i % ncol

            # Plot data
            ax[row][col].plot(f_t, s21mag_t, 'bo')

            # Plot model
            f_model = np.linspace(f_t.min(), f_t.max(), 201)
            s21_model = _model(f_model, *popt)
            ax[row][col].plot(f_model, s21_model, 'r')

            # Print info
            f_str = "f = {:.1f} GHz".format(f_center[i]/1e9)
            q_str = "Q = {:.0f}".format(q_factor[i])
            ax[row][col].text(0.05, 0.9, f_str, transform=ax[row][col].transAxes)
            ax[row][col].text(0.05, 0.8, q_str, transform=ax[row][col].transAxes)

    return f_center, q_factor, q_factor_error
