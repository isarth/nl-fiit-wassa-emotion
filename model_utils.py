from keras.models import Model
from keras.layers import LSTM, Dense, Input, Dropout, Activation, Embedding, Reshape, Concatenate, Conv1D, MaxPooling1D
from keras.layers.wrappers import Bidirectional
from keras.callbacks import EarlyStopping
from keras.regularizers import l1_l2
from keras.layers.noise import GaussianNoise
import numpy as np
from attention import Attention


# val_f1_c
def get_callbacks(early_stop_monitor='val_acc', early_stop_patience=2, early_stop_mode='auto'):
    earlystop = EarlyStopping(monitor=early_stop_monitor, min_delta=0.003, patience=early_stop_patience, verbose=1, mode=early_stop_mode)

    return [earlystop]


def create_embedding_layer(embeddings_index, words_to_index, vocab_length=100, output_dim=300):
    emb_matrix = np.zeros((vocab_length + 1, output_dim))

    for word, index in words_to_index.items():
        if word in embeddings_index:
            emb_matrix[index, :] = embeddings_index[word]

    embedding_layer = Embedding(vocab_length + 1, output_dim, trainable=True)
    embedding_layer.build((None,))
    embedding_layer.set_weights([emb_matrix])

    return embedding_layer


def get_SM_model(input_shape, classes=6):
    sentences = Input(shape=input_shape, dtype='float32')

    x = Reshape((input_shape[0] * input_shape[1],))(sentences)

    x = Dense(units=input_shape[0] * input_shape[1], activation="tanh")(x)
    # x = Dropout(rate=0.2)(x)
    x = Dense(units=input_shape[0] * input_shape[1], activation="tanh")(x)
    # x = Dropout(rate=0.2)(x)
    x = Dense(units=classes, activation="softmax")(x)

    return Model(inputs=sentences, outputs=x)


def get_SM_model_2(input_shape, classes=6):
    sentence = Input(shape=input_shape, dtype='float32')

    x = GaussianNoise(0.05)(sentence)
    x_d = Dropout(0.1)(x)
    x = Dense(units=2048, activation="relu")(x_d)
    y = Dense(units=2048, activation="tanh")(x_d)
    x = Concatenate(axis=-1)([x, y])
    # x = Dropout(rate=0.1)(x)
    x = Dense(units=2048, activation="relu")(x)
    x = Dense(units=classes, activation="softmax")(x)

    # x = Dense(units=2048, activation="relu")(sentence)
    # x = Dense(units=classes, activation="softmax")(x)

    # x = GaussianNoise(0.05)(sentence)
    # x = Dropout(0.1)(x)
    #
    # x = Dense(units=512, activation="relu")(x)
    # x = Dense(units=classes, activation="softmax")(x)

    return Model(inputs=sentence, outputs=x)


def get_model(input_shape, embedding_layer, classes=6, units=1024):
    sentence_indices = Input(shape=input_shape, dtype='int32')

    embeddings = embedding_layer(sentence_indices)
    noised_embeddings = GaussianNoise(0.2)(embeddings)
    dropped_embeddings = Dropout(rate=0.2)(noised_embeddings)

    # recurrent_regularizer=l1_l2(0.01,0.01)
    # activity_regularizer=l1_l2(0.01, 0.01)
    # kernel_regularizer=l1_l2(0.01, 0.01)
    # bias_regularizer=l1_l2(0.01, 0.01)

    x = Bidirectional(LSTM(units=units, return_sequences=False))(dropped_embeddings)
    # x = Attention(input_shape[0])(x)
    x = Dropout(rate=0.3)(x)
    # x = Bidirectional(LSTM(units=units))(x)
    # x = Dropout(rate=0.5)(x)
    x = Dense(units=classes, activation="softmax")(x)

    return Model(inputs=sentence_indices, outputs=x)


def get_sample_weights(model, train_x, train_y, filename):
    predictions = model.predict(train_x)
    samples_weights = np.zeros((train_x.shape[0]))
    # for sample in predictions:
    return NotImplementedError


def get_sample_weights_prim(train_y, class_weight):
    weights = np.zeros(train_y.shape[0])
    for index, sample in enumerate(train_y):
        weights[index] = class_weight[sample]
    return weights
