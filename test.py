import xarray
filename = 'https://data.gdex.ucar.edu/d559000/catalogs/wy1980.2d.json'
ds = xarray.open_dataset(filename, engine='kerchunk')
ds['FORCTLSM']