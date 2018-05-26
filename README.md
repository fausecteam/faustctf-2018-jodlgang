# Adversarial Machine Learning Challenge

Jodlgang is an investment syndicate whose fellow patrons irresponsibly gamble with their trusting client's savings on the crypto market.

## Pre-trained face recognition models
* VGG-16, available from the [VGG website](http://www.robots.ox.ac.uk/%7Evgg/software/vgg_face/). Unfortunately, they only provide weights for Matlab, Torch, and Caffe but not for TensorFlow or Theano.
* Luckily, someone [converted](https://github.com/rcmalli/keras-vggface/) the Caffe weights to work with Keras.
* [Directly download the trained weights](https://github.com/rcmalli/keras-vggface/releases/download/v2.0/rcmalli_vggface_tf_vgg16.h5)

## Data set

* We do not want the teams to find the admin picture on the internet, thus we should not use too popular data sets.
* Unless the data set consists of images from celebrities, because those could be from any data set.

### FaceScrub

* [Download script](https://github.com/lightalchemist/FaceScrub)
* [Download FaceScrub files](https://github.com/faceteam/facescrub) containing links to the images

[Description](http://www.face-rec.org/databases/):
Large face datasets are important for advancing face recognition research, but they are tedious to build, because a lot of work has to go into cleaning the huge amount of raw data. To facilitate this task, we developed an approach to building face datasets that detects faces in images returned from searches for public figures on the Internet, followed by automatically discarding those not belonging to each queried person. The FaceScrub dataset was created using this approach, followed by manually checking and cleaning the results. It comprises a total of 107,818 face images of 530 celebrities, with about 200 images per person. As such, it is one of the largest public face databases.

## Vulnerabilities

1. Log in as admin by providing your face image which the CNN recognizes as the admin user.
2. When face login fails due to an nan value, our Django webserver is configured to use the second authentication backend provided. The fallback authentication backend uses password authentication, and the passwords are known to all teams.

## Installation
**Incomplete** list of packages to install:

```bash
pip install django-widget-tweaks
```