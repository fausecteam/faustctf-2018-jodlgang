# Adversarial Machine Learning Challenge

Jodlgang is an investment syndicate whose fellow patrons irresponsibly gamble with their trusting client's savings on the volatile cryptocurrencies market.
The website provides a platform, where registered patrons exchange brief notes and organize themselves. Patrons can also save private notes only to be seen by each individual himself.
There are 530 active patrons, and registration is closed at the moment.

The Jodlgang platfrom replaced the old password login for a state-of-the-art face authentication system. To sign in, a patron must provide an image of his face alongside her or his email address.
The face snap must be a color image of size 224x224 pixels and must not be larger than 1MB.

The Jodlgang platform is distributed among multiple machines (i.e., there is one platform for each team), each of which runs a standalone version of the platform. There is no synchronization going on between these platforms. One of the registered patrons is assigned as an ambassador to each platform. The patron assignment is chosen based on the team id.

To hide flags, the game server logs in as the ambassador user and stores the flag as a private note.

## Vulnerabilities
All you have to do to steal the private notes including the flags from team 42 is to log in as user 42. Since the platform requires face authentication, you will need to persuade the face recognition system that your uploaded face image shows patron 42. Unfortunately you don't know how this patrons looks like. The face recognition system consists of a state-of-the-art convolutional neural network (CNN) that has been trained to distinguish between the 530 registered patrons.

Luckily, you have access to all parameters of the CNN: the network architecture and the trained weights and biases. This allows you to craft adversarial examples. An adversarial example is an example that has been carefully perturbed to fool the CNN. Our pure Python-CNN implementation `Tensorwow` is actually fully compatible to `TensorFlow`, thus it might help to reimplement the CNN in TensorFlow and restore the trained weights there.
This way you can craft an adversarial example image that fools the CNN into thinking you are user 42.

There is a second vulnerability in the pure Python-CNN implementation itself. The softmax activation function doesn't use the normalization trick, thus it is numerically unstable. By carefully perturbing your input image, you can cause the exp in the softmax activation to overflow, allowing you to sign in using the patron's email address, the patron's password which you can read from the database and which is the same for all platforms, and your perturbed image causing the overflow.

## Authors' notes to themselves

### Pre-trained face recognition models
* VGG-16, available from the [VGG website](http://www.robots.ox.ac.uk/%7Evgg/software/vgg_face/). Unfortunately, they only provide weights for Matlab, Torch, and Caffe but not for TensorFlow or Theano.
* Luckily, someone [converted](https://github.com/rcmalli/keras-vggface/) the Caffe weights to work with Keras.
* [Directly download the trained weights](https://github.com/rcmalli/keras-vggface/releases/download/v2.0/rcmalli_vggface_tf_vgg16.h5)

### Data set

* We do not want the teams to find the admin picture on the internet, thus we should not use too popular data sets.
* Unless the data set consists of images from celebrities, because those could be from any data set.

### FaceScrub

* [Download script](https://github.com/lightalchemist/FaceScrub)
* [Download FaceScrub files](https://github.com/faceteam/facescrub) containing links to the images

[Description](http://www.face-rec.org/databases/):
Large face datasets are important for advancing face recognition research, but they are tedious to build, because a lot of work has to go into cleaning the huge amount of raw data. To facilitate this task, we developed an approach to building face datasets that detects faces in images returned from searches for public figures on the Internet, followed by automatically discarding those not belonging to each queried person. The FaceScrub dataset was created using this approach, followed by manually checking and cleaning the results. It comprises a total of 107,818 face images of 530 celebrities, with about 200 images per person. As such, it is one of the largest public face databases.