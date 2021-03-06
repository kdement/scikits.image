__all__ = ['hough']

from itertools import izip
import numpy as np


def _hough(img, theta=None):
    if img.ndim != 2:
        raise ValueError('The input image must be 2-D')

    if theta is None:
        theta = np.linspace(-np.pi / 2, np.pi / 2, 180)

    # compute the vertical bins (the distances)
    d = np.ceil(np.hypot(*img.shape))
    nr_bins = 2 * d
    bins = np.linspace(-d, d, nr_bins)

    # allocate the output image
    out = np.zeros((nr_bins, len(theta)), dtype=np.uint64)

    # precompute the sin and cos of the angles
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # find the indices of the non-zero values in
    # the input image
    y, x = np.nonzero(img)

    # x and y can be large, so we can't just broadcast to 2D
    # arrays as we may run out of memory. Instead we process
    # one vertical slice at a time.
    for i, (cT, sT) in enumerate(izip(cos_theta, sin_theta)):

        # compute the base distances
        distances = x * cT + y * sT

        # round the distances to the nearest integer
        # and shift them to a nonzero bin
        shifted = np.round(distances) - bins[0]

        # cast the shifted values to ints to use as indices
        indices = shifted.astype(np.int)

        # use bin count to accumulate the coefficients
        bincount = np.bincount(indices)

        # finally assign the proper values to the out array
        out[:len(bincount), i] = bincount

    return out, theta, bins


# try to import and use the faster Cython version if it exists
try:
    from ._hough_transform import _hough
except ImportError:
    pass


def hough(img, theta=None):
    """Perform a straight line Hough transform.

    Parameters
    ----------
    img : (M, N) ndarray
        Input image with nonzero values representing edges.
    theta :1D ndarray, dtype=double
        Angles at which to compute the transform, in radians.
        Defaults to -pi/2 - pi/2

    Returns
    -------
    H : 2-D ndarray, uint64
        Hough transform accumulator.
    distances : ndarray
        Distance values.
    theta : ndarray
        Angles at which the transform was computed.

    Examples
    --------
    Generate a test image:

    >>> img = np.zeros((100, 150), dtype=bool)
    >>> img[30, :] = 1
    >>> img[:, 65] = 1
    >>> img[35:45, 35:50] = 1
    >>> for i in range(90):
    >>>     img[i, i] = 1
    >>> img += np.random.random(img.shape) > 0.95

    Apply the Hough transform:

    >>> out, angles, d = hough(img)

    Plot the results:

    >>> import matplotlib.pyplot as plt
    >>> plt.imshow(out, cmap=plt.cm.bone)
    >>> plt.xlabel('Angle (degree)')
    >>> plt.ylabel('Distance %d (pixel)' % d[0])
    >>> plt.show()

    """
    return _hough(img, theta)
