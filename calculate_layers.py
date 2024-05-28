neuron_count = 0
neuron_per_layer = 86
layer_count = 0

while neuron_per_layer != 3:
    neuron_count += neuron_per_layer
    neuron_per_layer -= 1
    layer_count += 1
    print(neuron_count, neuron_per_layer, layer_count)