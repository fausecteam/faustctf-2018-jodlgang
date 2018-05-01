# Adversarial Machine Learning Challenge

## Pre-trained face recognition models
* VGG-16, available from the [VGG website](http://www.robots.ox.ac.uk/%7Evgg/software/vgg_face/). Unfortunately, they only provide weights for Matlab, Torch, and Caffe but not for TensorFlow or Theano.
* Luckily, someone [converted](https://github.com/rcmalli/keras-vggface/) the Caffe weights to work with Keras.
* [Directly download the trained weights](https://github.com/rcmalli/keras-vggface/releases/download/v2.0/rcmalli_vggface_tf_vgg16.h5)


## Unordered stuff

* We do not want the teams to find the admin picture on the internet, thus we should not use too popular data sets.

### Data sets
Dataset | Identities | Images
CelebFaces | 10177 | 202599
Parkhi15 (Oxford) | 2622 | 2.6M

http://cswww.essex.ac.uk/mv/allfaces/index.html
http://www1.uwe.ac.uk/et/mvl/projects.aspx
https://www.openu.ac.il/home/hassner/Adience/data.html
http://www.ivl.disco.unimib.it/activities/large-age-gap-face-verification/
https://cyberextruder.com/face-matching-data-set-download/ (License does not allow to redistribute)

### Vulnerabilities

When face login fails due to an nan value, the fallback authentication backend is uses. The fallback authentication backend uses password authentication, and the passwords are known to all teams.

### Installation
```bash
pip install django-widget-tweaks
```