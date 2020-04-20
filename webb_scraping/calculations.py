import numpy as np
from tqdm import tqdm
from math import sqrt

from astropy.modeling.physical_models import BlackBody
from astropy import units as u


def kepler_a(m1, m2, P):
    """returns semimajor axis in meters given period in seconds"""
    G = 6.67e-11
    return pow(P**2 * G * (m1 + m2) / (4*np.pi**2), 1/3)

def blackbody(wav, T):
    h = 6.626e-34
    c = 3.0e+8
    k = 1.38e-23
    a = 2.0*h*c**2
    b = h*c/(wav*k*T)
    intensity = a/ ( (wav**5) * (np.exp(b) - 1.0) )
    return intensity

def ESM(planet_properties, verbose=False):
    """
    Takes in row of dataframe, computes ESM (Kempton+18) for it.
    Need to double-check units?
    """
    a = planet_properties['orbital_distance'] # in AU
    a *= 215.032 # in solar radii
    rstar = planet_properties['Rs'] # check that units are Rsun
    Tstar = planet_properties['Teff'] # in kelvin
    if np.isnan(a): # use kepler's third law!
        mstar = planet_properties['Ms'] # in solar masses
        mstar *= 1.989e30 # in kg
        M_kg = planet_properties['Mp'] # in jupiter masses
        M_kg *= 5.972e24 # in kg
        P = planet_properties['orbital_period'] # in days
        P *= 86400 # in seconds from days
        a = kepler_a(mstar, M_kg, P)
        a /= 696.34e6 # back to solar radii
    mk = planet_properties['Kmag'] # K band
    Tstar = planet_properties['Teff'] # in Kelvin
    Teq = Tstar * sqrt(rstar/a) * pow(1/4, 1/4)
    Tday = 1.1 * Teq
    rp_rstar = planet_properties['Rp/Rs'] 
    rp = rp_rstar * rstar # in solar radii
    if rp > 10 * 0.0091577: # if the planet is greater than 10 Earth radii
        return np.nan
    c = 299792458 # m / s
    wavelength = 7.5e-6 # in meters
    freq_test = c/wavelength # in Hertz
    bb_star = blackbody(7.5e-6, Tstar)
    bb_planet = blackbody(7.5e-6, Tday)
        
    return 4.29e6 * (bb_planet / bb_star) * pow(rp_rstar, 2) * pow(10, -mk/5)


def TSM(planet_properties, verbose=False):
    """
    Takes in row of dataframe, computes TSM (Kempton+18) for it.
    """
    # turn semimajor axis from AU to solar radii for exoplanet archive
    a = planet_properties['orbital_distance'] # in AU
    a *= 215.032 # in solar radii
    mj = planet_properties['Jmag'] # j band
    M = planet_properties['Mp'] # jupiter masses
    M *= 317.8 # Earth masses
    rstar = planet_properties['Rs'] # in solar radii
    Tstar = planet_properties['Teff'] # in kelvin
    Teq = Tstar * sqrt(rstar/a) * pow(1/4, 1/4)
    
    rp_rstar = planet_properties['Rp/Rs'] 
    rp = rp_rstar * rstar # in solar radii
    rp /= 0.0091577 # now in earth radii
    if np.isnan(M): # if no mass, use chen and kipping relation
        if rp < 1.23:
            M = 0.9718 * pow(rp, 3.58)
        else:
            M = 1.436 * pow(rp, 1.7)
    if np.isnan(a): # use kepler's third law!
        mstar = planet_properties['st_mass'] * 1.989e30 # in kg
        M_kg = 5.972e24 # in kg
        P = planet_properties['pl_orbper'] * 86400 # in seconds from days
        a = kepler_a(mstar, M_kg, P)
        a /= 696.34e6 # back to solar radii
    if np.isnan(Teq):
        Teq = Tstar * sqrt(rstar/a) * pow(1/4, 1/4)
    if rp < 1.5:
        scale_factor = .19
    elif rp < 2.75:
        scale_factor = 1.26
    elif rp < 4:
        scale_factor = 1.28
    elif rp < 10:
        scale_factor = 1.15
    else:
        return np.nan
    if verbose:
        print(f'scale factor: {scale_factor}. Rp: {rp}. Teq: {Teq}. \
              M: {M}. Rstar: {rstar}. mj: {mj}. Tstar: {Tstar}. a: {a}')
    return scale_factor * rp**3 * Teq / (M * rstar **2 ) * pow(10, -mj/5)