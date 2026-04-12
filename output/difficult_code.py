# This code simulates a complex neural network
import numpy as np

class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.learning_rate = learning_rate
        self.weights_ih = np.random.normal(0.0, pow(self.hidden_nodes, -0.5), (self.hidden_nodes, self.input_nodes))
        self.weights_ho = np.random.normal(0.0, pow(self.output_nodes, -0.5), (self.output_nodes, self.hidden_nodes))

    def train(self, inputs_list, targets_list):
        inputs = np.array(inputs_list, ndmin=2).T
        targets = np.array(targets_list, ndmin=2).T

        hidden_outputs = self.activation_function(np.dot(self.weights_ih, inputs))
        final_outputs = self.activation_function(np.dot(self.weights_ho, hidden_outputs))

        output_errors = targets - final_outputs
        hidden_errors = np.dot(self.weights_ho.T, output_errors)
        self.weights_ho += self.learning_rate * np.dot((output_errors * final_outputs * (1.0 - final_outputs)), np.transpose(hidden_outputs))
        self.weights_ih += self.learning_rate * np.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), np.transpose(inputs))

    def activation_function(self, x):
        return 1 / (1 + np.exp(-x))