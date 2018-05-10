from ..interfaces.decorators import reversible_operation

__all__ = ['smooth_data']


@reversible_operation("Apply Smooth")
def smooth_data(data, kernel, context):
    from astropy.convolution import convolve

    conv_data = convolve(data, kernel)
    context['old_data'] = data

    return conv_data


@smooth_data.register_undo
def unsmooth_data(context):
    print("Unsmoothing data")

    return context['old_data']
