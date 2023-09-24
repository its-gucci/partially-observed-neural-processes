import torch

import functools
import itertools
import operator

_nonempty_prod = functools.partial(functools.reduce, operator.mul)
_nonempty_sum = functools.partial(functools.reduce, operator.add)

def _mirror_index_fixer(index, size):
    s = size - 1 # Half-wavelength of triangular wave
    # Scaled, integer-valued version of the triangular wave |x - round(x)|
    return torch.abs((index + s) % (2 * s) - s)

def _reflect_index_fixer(index, size):
    return torch.div(_mirror_index_fixer(2*index+1, 2*size+1) - 1, 2, rounding_mode='floor')

_INDEX_FIXERS = {
    'constant': lambda index, size: index,
    'nearest': lambda index, size: jnp.clip(index, 0, size - 1),
    'wrap': lambda index, size: index % size,
    'mirror': _mirror_index_fixer,
    'reflect': _reflect_index_fixer,
}

def _round_half_away_from_zero(a):
    return torch.round(a)

def _nearest_indices_and_weights(coordinate):
    index = _round_half_away_from_zero(coordinate).long()
    weight = 1
    return [(index, weight)]

def _linear_indices_and_weights(coordinate):
    lower = torch.floor(coordinate)
    upper_weight = coordinate - lower
    lower_weight = 1 - upper_weight
    index = lower.long()
    return [(index, lower_weight), (index + 1, upper_weight)]

def _map_coordinates(input, coordinates, order, mode='constant', cval=0.0, device='cuda'):
    coordinates = [torch.tensor(c) for c in coordinates]
    cval = torch.tensor(cval)

    if len(coordinates) != len(input.shape):
        raise ValueError('coordinates must be a sequence of length input.ndim, but '
                     '{} != {}'.format(len(coordinates), len(input.shape)))

    index_fixer = _INDEX_FIXERS.get(mode)
    if index_fixer is None:
        raise NotImplementedError(
            'jax.scipy.ndimage.map_coordinates does not yet support mode {}. '
            'Currently supported modes are {}.'.format(mode, set(_INDEX_FIXERS)))

    if mode == 'constant':
        is_valid = lambda index, size: (0 <= index) & (index < size)
    else:
        is_valid = lambda index, size: True

    if order == 0:
        interp_fun = _nearest_indices_and_weights
    elif order == 1:
        interp_fun = _linear_indices_and_weights
    else:
        raise NotImplementedError(
            'jax.scipy.ndimage.map_coordinates currently requires order<=1')

    valid_1d_interpolations = []
    for coordinate, size in zip(coordinates, input.shape):
        interp_nodes = interp_fun(coordinate)
        valid_interp = []
        for index, weight in interp_nodes:
            fixed_index = index_fixer(index, size)
            valid = is_valid(index, size)
            valid_interp.append((fixed_index, valid, weight))
        valid_1d_interpolations.append(valid_interp)

    outputs = []
    for items in itertools.product(*valid_1d_interpolations):
        indices, validities, weights = zip(*items)
        # correct indices to match the out-of-bounds behavior of jnp arrays
        new_indices = []
        for i in range(len(indices)):
            temp = torch.where(indices[i] > 255, 255, indices[i])
            new_indices.append(torch.where(temp < -256, -256, temp))
        if all(valid is True for valid in validities):
            # fast path
            contribution = input[new_indices]
        else:
            all_valid = functools.reduce(operator.and_, validities)
            contribution = torch.where(all_valid.to(device), input[new_indices].to(device), cval.to(device))
        outputs.append(_nonempty_prod(weights) * contribution)
    result = _nonempty_sum(outputs)
#     if jnp.issubdtype(input.dtype, jnp.integer):
#         result = _round_half_away_from_zero(result)
    return result