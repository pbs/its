[![Stability](https://img.shields.io/badge/Stability-Under%20Active%20Development-Red.svg)](https://github.com/pbs/its)

# Warning: under active development

This application is under active development and likely to change further before stabilizing.

# Image Transformation Service

ITS (Image Transform Service) performs transformations and optimizations on images by accepting transform requests in the form of query strings.

---

## Crop

There are three varieties of crop -- default, focal and smart crop.

### _Crop (Default)_

The default crops the input image about the center of the image. The image will be resized down first, depending on the lesser dimension of the image.

To use this crop, use the `crop` keyword with **two** arguments split by x's:

> https://image.pbs.org/path/to/file.jpg?crop=WWxHH

Where:

- crop -- indicates that ITS should perform a crop and use the middle of the image as the focal point for the crop.
- WW -- a numerical pixel value representing the desired width of the output image
- HH -- a numerical pixel value representing the desired height of the output image

#### Example

Original Image:

> https://image.pbs.org/video-assets/5jJewwH-asset-mezzanine-16x9-esGHBDK.png

![A Chocolate Cake](https://image.pbs.org/video-assets/5jJewwH-asset-mezzanine-16x9-esGHBDK.png)

Applying `crop`:

> https://image.pbs.org/video-assets/5jJewwH-asset-mezzanine-16x9-esGHBDK.png?crop=700x200

![A Cropped Chocolate Cake](https://image.pbs.org/video-assets/5jJewwH-asset-mezzanine-16x9-esGHBDK.png?crop=700x200)

### _Focal crop_

Focal crop returns an image focused around a user-specified point in the original image of a user-specified size. To use this crop, utilize the `crop` keyword with **four** arguments split by x's:

> https://image.pbs.org/path/to/file.jpg?crop=WWxHHxXXxYY

Where:

- crop -- indicates that ITS should perform a crop
- WW -- a numerical pixel value representing the desired width of the output image
- HH -- a numerical pixel value representing the desired height of the output image
- XX -- the x axis of the focal point, represented as a percentage value of the **width** of the original picture
- YY -- the y axis of the focal point, represented as a percentage value of the **height** of the original picture

#### Example

Original Image:

> https://image.pbs.org/test/GmtpBa4-asset-mezzanine-16x9-Uu2CpNc.png

![A Key Lime Pie](https://image.pbs.org/test/GmtpBa4-asset-mezzanine-16x9-Uu2CpNc.png)

Applying `crop` with four parameters:

> https://image.pbs.org/test/GmtpBa4-asset-mezzanine-16x9-Uu2CpNc.png?crop=500x400x90x10

![A cropped Key Lime pie](https://image.pbs.org/test/GmtpBa4-asset-mezzanine-16x9-Uu2CpNc.png?crop=500x400x90x10)

### _Smart Crop_

Smart crop returns an image focused around a user-specified point in the original image of a user-specified size. To use this crop, the input image _filename_ must end in `_focus-XXxYY.ext`, and then you can use the `crop` keyword with **two** arguments split by x's:

> https://image.pbs.org/path/to/file_focus-XXxYY.ext?crop=WWxHH

Where:

- XX -- the x axis of the focal point, represented as a percentage value of the height of the original picture
- YY -- the y axis of the focal point, represented as a percentage value of the height of the original picture
- crop -- indicates that ITS should perform a crop
- WW -- a numerical pixel value representing the desired width of the output image
- HH -- a numerical pixel value representing the desired height of the output image

#### Example

Original Image:

> https://image.pbs.org/test/Sjk2Eqs-asset-mezzanine-16x9-0gsKw4z_focus-90x10.png

![A hand holding a knife that is cutting bread](https://image.pbs.org/test/Sjk2Eqs-asset-mezzanine-16x9-0gsKw4z_focus-90x10.png)

Applying `crop`:

> https://image.pbs.org/test/Sjk2Eqs-asset-mezzanine-16x9-0gsKw4z_focus-90x10.png?crop=300x400

![A hand holding a knife that is cutting bread](https://image.pbs.org/test/Sjk2Eqs-asset-mezzanine-16x9-0gsKw4z_focus-90x10.png?crop=300x400)

---

## Overlay

Overlay returns the input image with the specified overlay image placed on top of it. The overlay is placed in the top left corner. To use overlay, use the overlay keyword:

> API_URL/<file_path/filename.ext>?overlay=<overlay_img_path>

Where:

- overlay -- indicates that ITS should put an overlay on the input image
- overlay_img_path -- path to the overlay (optionally, can be a keyword a keyword in the OVERLAYS dictionary in settings)

---

## Resize

Resize returns a resized version of the original image **without distortion of the aspect ratio**. To use it, use the `resize` keyword with **two** arguments split by x's:

> https://image.pbs.org/path/to/file.jpg?resize=WWxHH

Where:

- resize -- indicates that ITS should perform a resize transform
- WW -- a numerical pixel value representing the desired width of the output image
- HH -- a numerical pixel value representing the desired height of the output image

Resize has an option to not scale up, if the provided width and/or height is larger than those of the image. Use the `resize` keyword, but add **a comma and a third** argument `no-scale-up`:

> https://image.pbs.org/path/to/file.jpg?resize=WWxHH,no-scale-up

Or, with missing height:
> https://image.pbs.org/path/to/file.jpg?resize=WWx,no-scale-up

Or, with missing width:
> https://image.pbs.org/path/to/file.jpg?resize=xHH,no-scale-up

Note: Resizing to a larger size isn’t recommended, as it will compromise image quality.

Note: Inputing a single value (either an expected width size or an expected height size followed by an 'x') is also supported.

Example

Original Image:

> https://image.pbs.org/video-assets/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg

![A flowery cake](https://image.pbs.org/test/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg)

With `resize` applied:

> https://image.pbs.org/video-assets/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg?resize=400x200

![A resized flowery cake](https://image.pbs.org/test/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg?resize=400x200)

With `resize` applied and only a width supplied:

> https://image.pbs.org/video-assets/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg?resize=400x

![A resized flowery cake](https://image.pbs.org/video-assets/GTdD9Rq-asset-mezzanine-16x9-d3h7qCm.jpg?resize=400x)

---

## Format

Format returns the input image in the specified type, rather than being left as the original image’s type. It currently supports conversion to JPG, PNG, and WEBP. To use it, use the `format` keyword with the file extension as an argument:

> https://image.pbs.org/path/to/file.jpg?format=ext&quality=<integer>

Where:

- format -- indicates that ITS should perform a format transform
- ext -- the requested output type. Can only be `jpg`, `png`, `webp` or `auto` (`auto` will examine the image and return either a jpg or png depending on the image's complexity)
- quality -- _optional_, allows user to specify the quality that they would like the output image to have. Currently, this parameter only works with the `jpg` format. Accepts a multiple 10 up to 100.

Example

Original Image:

> https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg

![Macaroons](https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg)

Image as a PNG:

> https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?format=png

![Macaroons](https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?format=png)

Image as a JPG with a quality of 20:

> https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?quality=20

![Macaroons](https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?quality=20)

---

## Blur

Blur returns an image subject to a [Gaussian Blur](https://en.wikipedia.org/wiki/Gaussian_blur). To use it, use the `blur` keyword with an integer (for the pixel radius of the blur) as an argument:

> https://image.pbs.org/path/to/file.jpg?blur=radius

Where:

- blur -- indicates that ITS should perform a blur transform
- radius -- an integer pixel value representing the desired radius of the blur effect

Example

Original Image:

> https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg

![Macaroons](https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg)

Blurred Image:

> https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?blur=10

![Macaroons](https://image.pbs.org/test/7Sy3rBL-asset-mezzanine-16x9-xMYNIn3.jpg?blur=10)

---

## Combination

All of the transforms described above can be combined into one query by separating them with `&`.

An image cropped to 600x300px, changed to a PNG:

> https://image.pbs.org/test/nBVLq44-asset-mezzanine-16x9-p0bSjVY.jpg?crop=600x300&format=png

![A fancy cake](https://image.pbs.org/test/nBVLq44-asset-mezzanine-16x9-p0bSjVY.jpg?crop=600x300&format=png)

---

# Development

Here are some commands you can run while developing locally.

Run tests:

```bash
docker-compose build server
docker-compose run server pipenv run pytest its/tests
```

Run development server:

```bash
docker-compose up --build
```

Run autoformatter for python code:

```bash
docker-compose run server ./scripts/docker/server/format.sh
```

Run static type checking:

```bash
docker-compose run server ./scripts/docker/server/type-check.sh
```

Apply autogenerated type annotations:

```bash
docker-compose run server pipenv run pyannotate --write --type-info ./type_info.json its/path_to_file.py
````

Build and publish docker image

> Note: you have to authenticate to [Docker Hub](https://docs.docker.com/engine/reference/commandline/login/) first.

```bash
./scripts/do publish
```



