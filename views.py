# Superres/views.py

import os
import matplotlib.pyplot as plt
from django.urls import path
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from django.conf import settings
import cv2
import pywt
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from django.shortcuts import render

def index(request):
    return render(request, 'Superres/index.html')

def compare_images(original, super_resolved):
    original = original.astype(np.float64)
    super_resolved = super_resolved.astype(np.float64)
    data_range = original.max() - original.min()
    psnr = peak_signal_noise_ratio(
        original, super_resolved, data_range=data_range)
    ssim = structural_similarity(original, super_resolved, multichannel=True)

    return psnr, ssim

# ... super_resolution function here ...
# Super resolution function here...
def super_resolution(img_path, scale_factor, upscale_superres=False):
    # Read the image
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert image to YCrCb color space
    image_YCrCb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)

    # Separate the Y, Cr, and Cb channels
    y, cr, cb = cv2.split(image_YCrCb)

    # Downscale
    y_down = cv2.pyrDown(y)

    # Calculate the desired output size based on the scale factor
    output_size = (int(y_down.shape[1]*(2*scale_factor)),
                   int(y_down.shape[0]*(2*scale_factor)))

    # Upscale using bicubic interpolation
    y_up = cv2.resize(y_down, output_size, interpolation=cv2.INTER_CUBIC)

    # Perform wavelet transform and get high frequency components
    coeffs = pywt.dwt2(y, 'db1')
    coeffs_up = pywt.dwt2(y_up, 'db1')

    # Modify the coefficients
    coeffs_up_h = list(coeffs_up)

    # Resize coeffs_up_h[0] to the shape of coeffs[0]
    coeffs_up_h[0] = cv2.resize(
        coeffs_up_h[0], (coeffs[0].shape[1], coeffs[0].shape[0]))

    coeffs_up_h[0] *= coeffs[0] / (coeffs_up_h[0] + 1e-8)
    coeffs_up_h[1] = coeffs[1]

    # Compute the inverse wavelet transform
    y_superres = pywt.idwt2(coeffs_up_h, 'db1')

    # Make sure the values are in 8-bit range
    y_superres_8bit = cv2.normalize(
        y_superres, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    # Resizing y_superres_8bit to the shape of cr (or cb as they have same shape)
    y_superres_8bit = cv2.resize(y_superres_8bit, (cr.shape[1], cr.shape[0]))

    # Merge the super-resolved Y channel back with the Cr and Cb channels
    image_superres_YCrCb = cv2.merge([y_superres_8bit, cr, cb])

    # Convert back to RGB color space
    image_superres = cv2.cvtColor(image_superres_YCrCb, cv2.COLOR_YCrCb2RGB)

    # Upscale the super-resolved image if required
    if upscale_superres:
        image_superres = cv2.resize(
            image_superres, output_size, interpolation=cv2.INTER_CUBIC)

    # Save the super-resolved image to disk
    super_resolved_path = os.path.join(
        settings.MEDIA_ROOT, 'super_resolved.png')
    cv2.imwrite(super_resolved_path, cv2.cvtColor(
        image_superres, cv2.COLOR_RGB2BGR))

    # Verify that the image has been saved correctly
    if not os.path.exists(super_resolved_path):
        print(
            f"Failed to save the super-resolved image to {super_resolved_path}")
        return

    # Read the original image again for comparison
    original = cv2.imread(img_path)
    super_resolved = cv2.imread(super_resolved_path)

    # Resize the super_resolved image to match the original's dimensions if necessary
    if original.shape != super_resolved.shape:
        super_resolved = cv2.resize(
            super_resolved, (original.shape[1], original.shape[0]))

    # Convert to YCrCb color space
    original = cv2.cvtColor(original, cv2.COLOR_BGR2YCrCb)
    super_resolved = cv2.cvtColor(super_resolved, cv2.COLOR_BGR2YCrCb)

    # Compute PSNR and SSIM
    psnr, ssim = compare_images(original, super_resolved)
    print(f"PSNR: {psnr}")
    print(f"SSIM: {ssim}")

    return super_resolved_path, psnr, ssim


class ImageProcessingView(View):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        scale_factor = float(request.POST.get('scale_factor'))
        upscale_superres = request.POST.get('upscale') == 'true'

        # save the uploaded file
        file_path = default_storage.save(image_file.name, image_file)

        # Call super resolution function
        super_resolved_path, psnr, ssim = super_resolution(
            file_path, scale_factor, upscale_superres)

        return JsonResponse({
            'message': 'Image processed successfully',
            'super_resolved_image': super_resolved_path,
            'psnr': psnr,
            'ssim': ssim,
        })
