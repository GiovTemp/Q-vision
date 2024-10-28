# Q-Vision/qvision/neuron.py

import collections
import numpy as np
from typing import Callable, Tuple
import matplotlib.pyplot as plt

from .utils import sig, sigPrime, loss, accuracy
from .phase_modulation import neuron as neuron_phase_modulation

def neuron(weights, bias, Img, num_shots):
    """ Compute the output of the quantum optical neuron, with parameters
        weights and bias, and input Img. The predicted probability is sampled
        for a given number of shots (deactived by choosing shots = -1). """
    norm = np.sqrt(np.sum(np.square(weights)))
    prob = np.abs(np.sum(np.multiply(Img, weights/norm)))**2
    # Sampling (1: Coincidence)
    if num_shots == -1:
        f = prob
    else:
        samples = np.random.choice([0, 1], num_shots, p=[1 - prob, prob])
        counter = collections.Counter(samples)
        f = counter[1]/num_shots
    return sig(f + bias)

def spatial_loss_derivative(output, target, weights, bias, Img):
    """ Compute the derivative of the binary cross-entropy with respect to the
        neuron parameters, with spatial-encoded input. """
    # Check
    if output == 1:
        raise ValueError('Output is 1!')
    elif output <= 0:
        raise ValueError('Output is negative!')
    elif 1 - output <= 0:
        raise ValueError('Output is greater than 1!')

    # Declarations
    F = output
    y = target
    norm = np.sqrt(np.sum(np.square(weights)))

    # Compute the derivative with respect to the weights
    g = np.sum(np.multiply(Img, weights/norm)) # <I, U>
    gPrime = (Img - g*weights/norm)/norm # <I, dlambdaU>

    fPrime = 2*np.real(g*np.conjugate(gPrime)) # 2Re[<I, U><I, dU>*]

    crossPrime = (F - y)/(F*(1-F))

    gAbs = np.abs(g) # sqrt(f)
    weights_derivative = crossPrime*sigPrime(gAbs**2 + bias)*fPrime

    # Compute the derivative with respect to the bias
    bias_derivative = crossPrime*sigPrime(gAbs**2 + bias)

    return weights_derivative, bias_derivative

def Fourier_loss_derivative(output, target, weights, bias, Img):
    """ Compute the derivative of the binary cross-entropy with respect to the
        neuron parameters, with Fourier-encoded input. """
    # Check
    if output == 1:
        raise ValueError('Output is 1!')
    elif output <= 0:
        raise ValueError('Output is negative!')
    elif 1 - output <= 0:
        raise ValueError('Output is greater than 1!')

    # Declarations
    F = output
    y = target
    norm = np.sqrt(np.sum(np.square(weights)))

    # Compute the derivative with respect to the weights
    g = np.sum(np.multiply(Img, weights/norm)) # <I, U>
    gAbs = np.abs(g) # sqrt(f)

    gPrime = (Img - gAbs*weights/norm)/norm # Approximation
    fPrime = 2*np.real(gAbs*np.conjugate(gPrime)) # Approximation

    crossPrime = (F - y)/(F*(1-F))

    weights_derivative = crossPrime*sigPrime(gAbs**2 + bias)*fPrime

    # Compute the derivative with respect to the bias
    bias_derivative = crossPrime*sigPrime(gAbs**2 + bias)

    return weights_derivative, bias_derivative

# def update_rule(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias):
#     """ Parameters update rule of the gradient descent algorithm. """
#     new_weights = weights - lrWeights*np.mean(lossWeightsDerivatives, axis=0)
#     new_bias = bias - lrBias*np.mean(lossBiasDerivatives, axis=0)
#     return new_weights, new_bias
#
# def optimization(loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, num_epochs, lrWeights, lrBias, num_shots):
#     """ Gradient descent optimization. """
#     # Training set
#     outputs = np.array([neuron(weights, bias, trainImgs[idx,:,:], num_shots) for idx in range(images_length)])
#
#     losses = np.array([loss(outputs[idx], targets[idx]) for idx in range(outputs.shape[0])])
#
#     # History initialization
#     loss_history = [np.mean(losses)]
#     accuracy_history = [accuracy(outputs, targets)]
#
#     # Weights initialization
#     lossWeightsDerivatives = np.zeros(trainImgs.shape)
#     lossBiasDerivatives = np.zeros(images_length)
#
#     # Compute derivates of the loss function
#     for idx in range(images_length):
#         lossWeightsDerivatives[idx,:,:], lossBiasDerivatives[idx] = loss_derivative(outputs[idx], targets[idx], weights, bias, trainImgs[idx,:,:])
#
#     # Validation set
#     test_outputs = np.array([neuron(weights, bias, testImgs[idx,:,:], num_shots) for idx in range(test_images_length)])
#     test_losses = np.array([loss(test_outputs[idx], test_targets[idx]) for idx in range(test_outputs.shape[0])])
#
#     test_loss_history = [np.mean(test_losses)]
#     test_accuracy_history = [accuracy(test_outputs, test_targets)]
#
#     # Verbose
#     print('EPOCH', 0)
#     print('Loss', loss_history[0], 'Val_Loss', test_loss_history[0])
#     print('Accuracy', accuracy_history[0], 'Val_Acc', test_accuracy_history[0])
#     print('---')
#
#     for epoch in range(num_epochs):
#         # Update weights
#         weights, bias = update_rule(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias)
#
#         # Training set
#         outputs = np.array([neuron(weights, bias, trainImgs[idx,:,:], num_shots) for idx in range(images_length)])
#         losses = np.array([loss(outputs[idx], targets[idx]) for idx in range(outputs.shape[0])])
#         loss_history.append(np.mean(losses))
#
#         # Update accuracy
#         accuracy_history.append(accuracy(outputs, targets))
#
#         # Validation set
#         test_outputs = np.array([neuron(weights, bias, testImgs[idx,:,:], num_shots) for idx in range(test_images_length)])
#         test_losses = np.array([loss(test_outputs[idx], test_targets[idx]) for idx in range(test_outputs.shape[0])])
#         test_loss_history.append(np.mean(test_losses))
#         test_accuracy_history.append(accuracy(test_outputs, test_targets))
#
#         # Update loss derivative
#         for idx in range(images_length):
#             lossWeightsDerivatives[idx,:,:], lossBiasDerivatives[idx] = loss_derivative(outputs[idx], targets[idx], weights, bias, trainImgs[idx,:,:])
#
#         # Verbose
#         print('EPOCH', epoch + 1)
#         print('Loss', loss_history[epoch + 1], 'Val_Loss', test_loss_history[epoch + 1])
#         print('Accuracy', accuracy_history[epoch + 1], 'Val_Acc', test_accuracy_history[epoch + 1])
#         print('---')
#
#     return weights, bias, loss_history, test_loss_history, accuracy_history, test_accuracy_history


def optimizer(optimizer_function, loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, momentum, batch_size, phase_modulation, **kwargs):
    if optimizer_function == 'gd':
        return optimization_standard_gd(loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, phase_modulation, **kwargs)
    elif optimizer_function == 'sgd':
        return optimization_sgd(loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, phase_modulation, **kwargs)
    elif optimizer_function == 'sgd_momentum':
        return optimization_sgd_momentum(loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, phase_modulation, momentum, **kwargs)
    elif optimizer_function == 'mini_batch_gd':
        return optimization_minibatch_gd(loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, phase_modulation, batch_size, **kwargs)


def common_optimization(
    loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
    test_source_images, test_modulated_images, test_labels, num_epochs, lrWeights, lrBias, num_shots, phase_modulation, update_fn: Callable, **kwargs
):
    """Common optimization loop with handling for complex numbers due to phase modulation and multiple optimizers."""

    # History initialization
    loss_history = []
    accuracy_history = []

    test_loss_history = []
    test_accuracy_history = []

    # Cache initialization for momentum or other optimizers that need cache
    cache = kwargs.get('cache', {})
    momentum = kwargs.get('momentum', 0.9)

    if phase_modulation:
        # Retrieve batch size from kwargs, default to full-batch if not specified
        training_images_length = train_modulated_images.shape[0]
        test_images_length = test_modulated_images.shape[0]
        batch_size = kwargs.get('batch_size', training_images_length)
    else:
        # Retrieve batch size from kwargs, default to full-batch if not specified
        training_images_length = trainImgs.shape[0]
        test_images_length = testImgs.shape[0]
        batch_size = kwargs.get('batch_size', training_images_length)

    for epoch in range(num_epochs):
        # Shuffle if using mini-batch or SGD, keep order for standard GD
        indices = np.arange(training_images_length)
        if batch_size < training_images_length:  # Only shuffle for mini-batch or SGD
            np.random.shuffle(indices)

        # Divide into batches
        for start_idx in range(0, training_images_length, batch_size):
            end_idx = start_idx + batch_size
            batch_indices = indices[start_idx:end_idx]

            batch_lossWeightDerivatives = []
            batch_lossBiasDerivatives = []

            # Calculate gradients for each sample in batch
            for idx in batch_indices:
                if phase_modulation:
                    output = neuron_phase_modulation(weights, bias, None, train_modulated_images[idx, :, :], num_shots)
                else:
                    output = neuron(weights, bias, trainImgs[idx, :, :], num_shots)

                # Compute loss derivatives with respect to weights and bias
                lossWeightDerivative, lossBiasDerivative = loss_derivative(
                    np.abs(output), train_labels[idx], train_source_images[idx, :, :], train_modulated_images[idx, :, :], weights, bias, None
                )

                # print('lossWeightDerivative:', lossWeightDerivative)
                # print('lossBiasDerivative:', lossBiasDerivative)

                if update_fn == sgd_update:
                    weights, bias, cache = update_fn(
                        weights, bias, lossWeightDerivative, lossBiasDerivative, lrWeights, lrBias, cache
                    )
                elif update_fn == sgd_momentum_update:
                    weights, bias, cache = update_fn(
                        weights, bias, lossWeightDerivative, lossBiasDerivative, lrWeights, lrBias, cache, momentum
                    )

                batch_lossWeightDerivatives.append(lossWeightDerivative)
                batch_lossBiasDerivatives.append(lossBiasDerivative)

            # Update weights and biases
            if update_fn == standard_gd_update or update_fn == mini_batch_gd:
                weights, bias, cache = update_fn(
                    weights, bias, batch_lossWeightDerivatives, batch_lossBiasDerivatives, lrWeights, lrBias, cache
                )

        # Calculate losses and accuracy after each epoch
        if phase_modulation:
            outputs = np.array([
                neuron_phase_modulation(weights, bias, None, train_modulated_images[idx, :, :], num_shots)
                for idx in range(training_images_length)
            ], dtype=np.complex128)
        else:
            outputs = np.array([
                neuron(weights, bias, trainImgs[idx, :, :], num_shots)
                for idx in range(training_images_length)
            ])

        # Calculate training loss and accuracy
        losses = np.array([loss(np.abs(outputs[idx]), train_labels[idx]) for idx in range(outputs.shape[0])])
        loss_history.append(np.mean(losses))
        accuracy_history.append(accuracy(outputs, train_labels))

        # Calculate test losses and accuracy
        if phase_modulation:
            test_outputs = np.array([
                neuron_phase_modulation(weights, bias, None, test_modulated_images[idx, :, :], num_shots)
                for idx in range(test_images_length)
            ], dtype=np.complex128)
        else:
            test_outputs = np.array([
                neuron(weights, bias, testImgs[idx, :, :], num_shots)
                for idx in range(test_images_length)
            ])

        test_losses = np.array([loss(np.abs(test_outputs[idx]), test_labels[idx]) for idx in range(test_outputs.shape[0])])
        test_loss_history.append(np.mean(test_losses))
        test_accuracy_history.append(accuracy(test_outputs, test_labels))

        print('EPOCH', epoch + 1)
        print('Loss', loss_history[-1], 'Val_Loss', test_loss_history[-1])
        print('Accuracy', accuracy_history[-1], 'Val_Acc', test_accuracy_history[-1])
        print('---')

    return weights, bias, loss_history, test_loss_history, accuracy_history, test_accuracy_history

# Define the standard gradient descent update function
def standard_gd_update(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias, cache):
    """ Parameters update rule of the gradient descent algorithm. """
    new_weights = weights - lrWeights * np.mean(lossWeightsDerivatives, axis=0)
    new_bias = bias - lrBias * np.mean(lossBiasDerivatives, axis=0)
    return new_weights, new_bias, cache


# Define the SGD update function
def sgd_update(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias, cache):
    clipped_gradients_weights = clip_gradients(lossWeightsDerivatives)
    clipped_gradients_bias = clip_gradients(lossBiasDerivatives)
    weights -= lrWeights * clipped_gradients_weights
    bias -= lrBias * clipped_gradients_bias
    # weights -= lrWeights * lossWeightsDerivatives
    # bias -= lrBias * lossBiasDerivatives
    return weights, bias, cache

def mini_batch_gd(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias, cache):
    return None

# def minibatch_gd_update(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias, cache, batch_size):
#     """ Update rule for Mini-Batch Gradient Descent (MBGD) """
#     # Qui calcoliamo la media su ciascun mini-batch
#     new_weights = weights - lrWeights * np.mean(lossWeightsDerivatives, axis=0)
#     new_bias = bias - lrBias * np.mean(lossBiasDerivatives, axis=0)
#     return new_weights, new_bias, cache

def sgd_momentum_update(weights, bias, lossWeightsDerivatives, lossBiasDerivatives, lrWeights, lrBias, cache, momentum=0.9):
    """Update rule for Stochastic Gradient Descent (SGD) with Momentum."""

    # Ensure derivatives are treated as at least 1D arrays
    lossWeightsDerivatives = np.atleast_1d(lossWeightsDerivatives)
    lossBiasDerivatives = np.atleast_1d(lossBiasDerivatives)

    # Retrieve previous velocities from the cache, or initialize if not present
    velocity_weights = cache.get('velocity_weights', np.zeros_like(weights))
    velocity_bias = cache.get('velocity_bias', np.zeros_like(bias))

    clipped_gradients_weights = clip_gradients(lossWeightsDerivatives)
    clipped_gradients_bias = clip_gradients(lossBiasDerivatives)

    # Update velocities with the momentum term and the current gradient
    velocity_weights = momentum * velocity_weights - lrWeights * clipped_gradients_weights
    velocity_bias = momentum * velocity_bias - lrBias * clipped_gradients_bias

    # Update parameters using the velocity
    weights += velocity_weights
    bias += velocity_bias

    # Return the updated weights, bias, and cache with the updated velocities
    cache['velocity_weights'] = velocity_weights
    cache['velocity_bias'] = velocity_bias

    return weights, bias, cache

def clip_gradients(gradients, clip_value=1.0):
    gradients = np.clip(gradients, -clip_value, clip_value)
    return gradients

def optimization_standard_gd(
        loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, **kwargs
):
    return common_optimization(
        loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, standard_gd_update, **kwargs
    )

def optimization_sgd(
        loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, **kwargs
):

    kwargs['batch_size'] = 1

    return common_optimization(
        loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, sgd_update, **kwargs
    )

def optimization_sgd_momentum(
        loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, momentum, **kwargs
):

    kwargs['batch_size'] = 1
    kwargs['momentum'] = momentum

    return common_optimization(
        loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, sgd_momentum_update, **kwargs
    )

def optimization_minibatch_gd(
        loss_derivative: Callable, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, batch_size, **kwargs
):

    kwargs['batch_size'] = batch_size

    return common_optimization(
        loss_derivative, weights, bias, targets, test_targets, trainImgs, testImgs, train_source_images, train_modulated_images, train_labels,
          test_source_images, test_modulated_images, test_labels, num_epochs,
        lrWeights, lrBias, num_shots, phase_modulation, standard_gd_update, **kwargs
    )



