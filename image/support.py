from abc import ABC, abstractmethod
from typing import Type

import PIL.Image

from image.profile import IStaticImageProfile, IAnimatedImageProfile


ImageProfile = Type[IStaticImageProfile] | Type[IAnimatedImageProfile] | None
SupportedImages = dict[str, dict[str, ImageProfile]]


class IImageSupport(ABC):
    def __init__(self, image: PIL.Image.Image, supported_images: SupportedImages):
        self._image: PIL.Image.Image = image
        self._supported_images: SupportedImages = supported_images

    @abstractmethod
    def get_image_profile(self) -> ImageProfile: pass


class StaticImageSupport(IImageSupport):
    def get_image_profile(self) -> ImageProfile:
        format_mode = '_'.join([self._image.format or '', self._image.mode])
        return self._supported_images['STATIC'].get(format_mode)


class AnimatedImageSupport(IImageSupport):
    def get_image_profile(self) -> ImageProfile:
        format_mode = '_'.join([self._image.format or '', self._image.mode])
        return self._supported_images['ANIMATED'].get(format_mode)


class ImageSupportProxy(IImageSupport):
    _image_support: IImageSupport
    _image_profile: ImageProfile

    def get_image_support(self) -> IImageSupport:
        if not hasattr(self, '_image_support'):
            # Determine between static or animated
            if (getattr(self._image, 'is_animated', False) is False
                and self._image.format != 'GIF'):
                self._image_support = StaticImageSupport(
                    self._image, self._supported_images)
            else:
                self._image_support = AnimatedImageSupport(
                    self._image, self._supported_images)

        return self._image_support

    def get_image_profile(self) -> ImageProfile:
        self.get_image_support()

        if not hasattr(self, '_image_profile'):
            self._image_profile = self._image_support.get_image_profile()
        return self._image_profile

    def is_supported(self) -> bool:
        self.get_image_profile()

        return self._image_profile is not None
