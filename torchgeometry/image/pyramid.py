import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = [
    "PyrDown",
    "PyrUp",
    "pyrdown",
    "pyrup",
]


def _get_pyramid_gaussian_kernel() -> torch.Tensor:
    """Utility function that return a pre-computed gaussian kernel."""
    return torch.tensor([
        [1., 4., 6., 4., 1.],
        [4., 16., 24., 16., 4.],
        [6., 24., 36., 24., 6.],
        [4., 16., 24., 16., 4.],
        [1., 4., 6., 4., 1.]
    ]) / 256.


class PyrDown(nn.Module):
    r"""Blurs a tensor and downsamples it.

    Args:
        x (torch.Tensor): the tensor to be downsampled. The tensor must be in
          the shape of BxCxHxW.

    Return:
        torch.Tensor: the downsampled tensor.
    """

    def __init__(self) -> None:
        super(PyrDown, self).__init__()
        self.kernel: torch.Tensor = _get_pyramid_gaussian_kernel()

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore
        # prepare kernel
        b, c, h, w = x.shape
        tmp_kernel: torch.Tensor = self.kernel.to(x.device).to(x.dtype)
        kernel: torch.Tensor = tmp_kernel.repeat(c, 1, 1, 1)

        # blur image
        x_blur: torch.Tensor = F.conv2d(
            x, kernel, padding=2, stride=1, groups=c)

        # reject even rows and columns.
        out: torch.Tensor = x_blur[..., ::2, ::2]
        return out


class PyrUp(nn.Module):
    r"""Upsamples a tensor and then blurs it.

    Args:
        x (torch.Tensor): the tensor to be upsampled. The tensor must be in
          the shape of BxCxHxW.

    Return:
        torch.Tensor: the upsampled tensor.
    """

    def __init__(self):
        super(PyrUp, self).__init__()
        self.kernel: torch.Tensor = _get_pyramid_gaussian_kernel()

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore
        # prepare kernel
        b, c, height, width = x.shape
        tmp_kernel: torch.Tensor = self.kernel.to(x.device).to(x.dtype)
        kernel: torch.Tensor = tmp_kernel.repeat(c, 1, 1, 1)

        # upsample tensor
        x_up: torch.Tensor = F.interpolate(x, size=(height * 2, width * 2),
                                           mode='bilinear', align_corners=True)

        # blurs upsampled tensor
        x_blur: torch.Tensor = F.conv2d(
            x_up, kernel, padding=2, stride=1, groups=c)
        return x_blur


# functiona api


def pyrdown(x: torch.Tensor) -> torch.Tensor:
    r"""Blurs a tensor and downsamples it.

    See :class:`~torchgeometry.image.PyrDown` for details.
    """
    return PyrDown()(x)


def pyrup(x: torch.Tensor) -> torch.Tensor:
    r"""Upsamples a tensor and then blurs it.

    See :class:`~torchgeometry.image.PyrUp` for details.
    """
    return PyrUp()(x)