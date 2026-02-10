class PixelExceptionError(Exception):
    pass


class PixelIterationError(PixelExceptionError):
    pass


class PixelMergeError(PixelExceptionError):
    pass


class PixelValidationError(PixelExceptionError):
    pass
